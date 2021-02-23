from uuid import uuid4
import logging
import numbers
import atexit
import time
from six import string_types
from six import integer_types
from metering.utils import clean
from metering.consumer import Consumer
from metering.request import RequestManager

try:
    import queue
except ImportError:
    import Queue as queue


ID_TYPES = (numbers.Number, string_types)


class Client(object):
    """Create a new Segment client."""
    log = logging.getLogger('amberflo')

    def __init__(self, app_key=None,
                 max_load=100000, debug=False, send=True, on_error=None, max_batch_size=100,
                 send_interval=0.5, gzip=False, max_retries=3,
                 wait=False, timeout=15, thread=1):
        require('app_key', app_key, string_types)
        self.queue = queue.Queue(max_load)
        self.app_key = app_key
        self.on_error = on_error
        self.wait = wait
        self.gzip = gzip
        self.send = send
        self.timeout = timeout

        if debug:
            self.log.setLevel(logging.DEBUG)
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
            for n in range(thread):
                self.consumers = []
                consumer = Consumer(
                    self.queue, app_key=app_key, on_error=on_error,
                    flush_at=max_batch_size, send_interval=send_interval,
                    gzip=gzip, retries=max_retries, timeout=timeout,
                )
                self.consumers.append(consumer)

                # if we've disabled sending, just don't start the consumer
                if send:
                    consumer.start()

    def meter(self, tenant=None, meter_name=None, meter_value=None, dimensions=None,
              timestamp=None):
        dimensions = dimensions or []
        require('tenant', tenant ,string_types)
        require('meter_name', meter_name, string_types)
        require('meter_value', meter_value, integer_types)
        require('dimensions', dimensions, list)

        if timestamp is None:
            timestamp = str(int(round(time.time() * 1000)))
        msg = {
            'tenant': tenant,
            'meter_name': meter_name,
            'meter_value': meter_value,
            'time': timestamp,
            'dimensions': dimensions,
        }

        return self._enqueue(msg)

   
    def _enqueue(self, msg):
        """Push a new `msg` onto the queue, return `(success, msg)`"""
        timestamp = msg['time']
        if timestamp is None:
            timestamp = str(int(round(time.time() * 1000)))
        message_id = msg.get('messageId')
        if message_id is None:
            message_id = uuid4()

        require('time', timestamp, str)

        # add common
       # timestamp = guess_timezone(timestamp)
       # msg['time'] = timestamp.isoformat()
       # msg['messageId'] = stringify_id(message_id)
      
        msg = clean(msg)
        self.log.debug('queueing: %s', msg)

        # if send is False, return msg as if it was successfully queued
        if not self.send:
            return True, msg

        if self.wait:
            self.log.debug('enqueued with blocking %s.', msg['meter_name'])
            RequestManager(self.app_key,
                           gzip=self.gzip,
                           timeout=self.timeout, batch=[msg]).post()

            return True, msg

        try:
            self.queue.put(msg, block=False)
            return True, msg
        except queue.Full:
            self.log.warning('analytics-python queue is full')
            return False, msg

    def flush(self):
        """Forces a flush from the internal queue to the server"""
        queue = self.queue
        size = queue.qsize()
        queue.join()
        # Note that this message may not be precise, because of threading.
        self.log.debug('successfully flushed about %s items.', size)

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


def require(name, field, data_type):
    """Require that the named `field` has the right `data_type`"""
    if not isinstance(field, data_type):
        msg = '{0} must have {1}, got: {2}'.format(name, data_type, field)
        raise AssertionError(msg)


def stringify_id(val):
    if val is None:
        return None
    if isinstance(val, string_types):
        return val
    return str(val)
