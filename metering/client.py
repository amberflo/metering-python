import atexit
from metering.consumer import Consumer
from metering.request import RequestManager
from metering.meter_message_factory import MeterFactory
from metering.field_validator import FieldValidator
from metering.logger import Logger
from metering.customer import CustomerApiClient
from metering.customer_payload_factory import CustomerPayloadFactory


try:
    import queue
except ImportError:
    import Queue as queue

#  consts

# According to https://tools.ietf.org/id/draft-thomson-hybi-http-timeout-00.html:
# Common implementations select times between 30 and 120 seconds, times that
# have been empirically determined to be safe.
DEFAULT_TIME_OUT = 60
class Client(object):
    """Create a new Segment client."""

    # TODO ofer 02/25/2021 - Some magic numbers going on here. We should document them and
    # explain why we use these numbers.
    def __init__(self, app_key, s3_bucket=None, access_key=None, secret_key=None, 
                 max_load=100000, debug=False, send=True, on_error=None, max_batch_size=100,
                 send_interval=0.5, max_retries=3,
                 wait=False, timeout= DEFAULT_TIME_OUT, thread=1):
        '''
            Parameters:
            1. app_key - Required string. You amberflo's app_key.
            2. max_load - Optional int. The max amount of unsent messages in this client's queue,
               before the client start blocking meter calls.
            3. debug - Optional boolean (default to false). If true this class will set the log
               level of this class to debug and output more info.
            4. on_error - given the caller the opertunity to plug logic which will be executed
               in an event of a meters upload failure.
            5. max_batch_size - Optional int. The max amound of meter messages before we actually
               try to send them to amberflo.
            6. send_interval - the max amount of time we wait before flashing the current meter
               messages in the client's queue.
            7. max_retries - Optional int. The max amount of http retires in case of a retriable
               failure.
            8. wait - Optional Boolean (default to false). If true then this class will try to
               send meter requests in a sync fashion (using the caller's thread and without
               queuing the request first).
            9. timeout - Optional int. The http request timeout.
            10. thread - the amount of consumer threads that listen to this client's queue and
                send http request to amberflo.
        '''
        if s3_bucket:
            self.app_key = None
            self.s3_bucket = s3_bucket
            self.access_key = access_key
            self.secret_key = secret_key
        else:
            FieldValidator.require_string_value('app_key', app_key)
            self.app_key = app_key
            self.s3_bucket = None
            self.access_key = None
            self.secret_key = None
        # According to https://docs.python.org/3/library/queue.html:
        # "The queue module implements multi-producer, multi-consumer queues. It is especially
        # useful in threaded programming when information must be exchanged safely between
        # multiple threads. The Queue class in this module implements all the required
        # locking semantics.""
        # So this queue should be safe to use from all python platforms
        # (https://www.python.org/download/alternatives/).
        self.queue = queue.Queue(max_load)
        self.on_error = on_error
        self.wait = wait
        self.send = send
        self.timeout = timeout
        self.log = Logger()

        if debug:
            self.log.debugMode()
        if wait:
            self.consumers = None
        else:
            # On program exit, allow the consumer thread to exit cleanly.
            # This prevents exceptions and a messy shutdown when the
            # interpreter is destroyed before the daemon thread finishes
            # execution. However, it is *not* the same as flushing the queue!
            # To guarantee all messages have been delivered, you'll still need
            # to call flush().
            if send:
                atexit.register(self.join)

            # TODO ofer 02/25/2021 - See if we want to have only one thread. Reasons:
            # 1. Threads in Python that runs on the standard CPython, aren't really running
            #    in parallel. See https://realpython.com/intro-to-python-threading/ for
            #    more info.
            # 2. From 'RFC 2616 - Hypertext Transfer Protocol, section 8 - Connections.':
            #    "Clients that use persistent connections SHOULD limit the number of
            #     simultaneous connections that they maintain to a given server. A
            #     single-user client SHOULD NOT maintain more than 2 connections with
            #     any server or proxy.""
            #    (https://www.w3.org/Protocols/rfc2616/rfc2616-sec8.html#sec8.1.4)
            for n in range(thread):
                self.consumers = []
                consumer = Consumer(
                    self.queue, app_key=app_key, s3_bucket=self.s3_bucket, access_key=self.access_key,
                    secret_key=self.secret_key, on_error=on_error,
                    flush_at=max_batch_size, send_interval=send_interval,
                    gzip=False, retries=max_retries, timeout=timeout,
                )
                self.consumers.append(consumer)

                # if we've disabled sending, just don't start the consumer
                if send:
                    consumer.start()

    def meter(self, meter_api_name, meter_value, meter_time_in_millis, customer_id,
        dimensions=None, unique_id=None):
        '''creates the message and enqueues it'''

        message = MeterFactory.create(meter_api_name=meter_api_name, meter_value=meter_value,
            meter_time_in_millis=meter_time_in_millis, customer_id=customer_id,
            dimensions=dimensions, unique_id=unique_id)

        return self._enqueue(message)

    def add_or_update_customer(self,customer_id, customer_name, traits=None):
        '''creates or updates customer'''
        message = CustomerPayloadFactory.create(
            customer_id=customer_id,
            customer_name=customer_name,
            traits=traits
        )
        client = CustomerApiClient(self.app_key)
        return client.add_or_update_customer(message)


    def _enqueue(self, msg):
        """Push a new `msg` onto the queue, return `(success, msg)`"""
        self.log.debug('queueing: %s', msg)

        # if send is False, return msg as if it was successfully queued
        if not self.send:
            return True, msg

        if self.wait:
            self.log.debug('enqueued with blocking %s.', msg['meterApiName'])
            # Exceptions go back to the client if the client chose to go for a sync mode.
            RequestManager(self.app_key,
                           gzip=False,
                           timeout=self.timeout, batch=[msg]).post()
            return True, msg

        try:
            self.queue.put(msg, block=False)
            return True, msg
        except queue.Full:
            self.log.warn('analytics-python queue is full')
            return False, msg

    def flush(self):
        """Forces a flush from the internal queue to the server"""
        try:
            queue = self.queue
            size = queue.qsize()
            queue.join()
            # Note that this message may not be precise, because of threading.
            self.log.debug('successfully flushed about %s items.', size)
        except RuntimeError:
            self.log.warn('analytics-python queue is full')

    def join(self):
        """Ends the consumer thread once the queue is empty.
        Blocks execution until finished
        """
        for consumer in self.consumers:
            consumer.pause()
            try:
                consumer.join()
            except RuntimeError:
                # consumer thread has not started
                pass

    def shutdown(self):
        """Flush all messages and cleanly shutdown the client"""
        self.flush()
        self.join()
