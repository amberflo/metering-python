import atexit
import logging
from queue import Queue, Full

from metering.ingest.api_client import IngestApiClient, create_ingest_payload
from metering.ingest.consumer import ThreadedConsumer


class ThreadedProducer:
    """
    This is a fairly generic `producer` implementation for batch-processing
    items in the background, though the only interface it supports is a single
    `send(item)` method.
    """

    consumer_class = ThreadedConsumer

    def __init__(
        self,
        backend_params,
        backend_class=IngestApiClient,
        max_queue_size=100000,
        threads=2,
        **consumer_args
    ):
        """
        backend_class:
            Class that implements the work to be perfomed, i.e. `send(batch)`.
            The default backend is the `IngestApiClient`.

        backend_params:
            Parameters for instantiating the backend. For the default backend,
            this is:
                {"api_key": <api-key>}

        max_queue_size:
            Maximum number of items that the queue will hold. If the queue is
            full, new items will be rejected.

        threads:
            Number of consumer threads to use.

        **consumer_args:
            Additional parameters will be passed to the consumer.
        """
        self.backend_params = backend_params
        self.backend_class = backend_class
        self.logger = logging.getLogger(__name__)
        self.queue = Queue(max_queue_size)

        # On program exit, allow the consumer thread to exit cleanly.
        # This prevents exceptions and a messy shutdown when the interpreter is
        # destroyed before the daemon thread finishes execution. However, it is
        # *not* the same as flushing the queue!  To guarantee all messages have
        # been delivered, you'll still need to call flush().
        atexit.register(self.join)

        self.consumers = []

        for _ in range(threads):
            backend = self.backend_class(**backend_params)
            consumer = self.consumer_class(self.queue, backend, **consumer_args)
            consumer.start()
            self.consumers.append(consumer)

    def send(self, payload):
        """
        Enqueue a payload to be sent. Returns whether it was successful or not.

        See `metering.ingest.IngestApiClient.send` for details on the payload.
        """
        try:
            self.queue.put(payload, block=False)
            return True
        except Full:
            self.logger.warning("Queue is full!")

        return False

    def meter(self, *args, **kwargs):
        """
        Build and enqueue a meter record to be sent. Returns whether it was
        successful or not.

        See `metering.ingest.create_ingest_payload` for details on the payload.
        """
        payload = create_ingest_payload(*args, **kwargs)
        return self.send(payload)

    def flush(self):
        """
        Blocks until all messages in the queue are consumed.
        """
        self.queue.join()

    def join(self):
        """
        Ends the consumer threads cleanly.
        """
        for consumer in self.consumers:
            consumer.join()

    def shutdown(self):
        """
        Block until all items are consumed, then ends the consumer threads
        cleanly.
        """
        self.flush()
        self.join()
