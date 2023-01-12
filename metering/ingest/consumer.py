import time
import backoff
import logging
import random
import string
from queue import Empty
from time import sleep
from threading import Thread

from metering.exceptions import ApiError


def _random_string(n=5):
    return "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(n)
    )


def _should_give_up(error):
    """
    Retry on API errors:
    - server errors (500s)
    - rate limited (429)
    And on all other (non-http) errors.
    """
    if isinstance(error, ApiError):
        return (400 <= error.status_code < 500) and error.status_code != 429
    return False


# Sequence of times to wait between requests.
_backoff_delays = [None, 2, 6, 12, 20, 40, 80]


def backoff_delay(*args, **kwargs):
    for d in _backoff_delays:
        yield d

    while True:
        yield _backoff_delays[-1]


class ThreadedConsumer:
    """
    This is a fairly generic `consumer thread` implementation for
    batch-processing items in the background, though the only interface it
    supports for the worker backend is a single `send(batch)` method.

    This class is not intended to be used directly. Rather, see
    `metering.ingest.producer.ThreadedProducer`.
    """

    def __init__(
        self,
        queue,
        backend,
        retries=6,
        batch_size=100,
        send_interval_in_secs=0.5,
        sleep_interval_in_secs=0.1,
        on_error=None,
        backoff_delay=backoff_delay,
    ):
        """
        backend:
            Instance that implements the `send(batch)` method and performs the
            actual work.

        queue:
            Queue from which to consume new items.

        retries:
            Number of additional attempts to consume a batch to perform, using
            exponential back-off.  Items in a failed batch are lost.

        batch_size:
            Maximum number of items to inclued in a single batch.

        send_interval_in_secs:
            How long to wait for new items before sending an incomplete batch.

        sleep_interval_in_secs:
            How long to wait after a failure to consume a batch happens (or
            after empty batches).

        on_error:
            Callback function to handle errors when sending a batch of items.
            It will be called as `on_error(exception_instance, items_in_batch)`.
            It should be thread-safe, as it might be used by multiple consumers
            at the same time.

        backoff_delay:
            Generator function yielding the amount of time in seconds to wait
            for the next attempt to make the request.
            Default sequence: None, 2, 6, 12, 20, 40, 80, 80, 80...
            Note that we use "full jitter" on these values, so on average the
            wait time will be half of the nominal one.
            (see https://github.com/litl/backoff#jitter)
        """
        self.queue = queue
        self.backend = backend
        self.retries = retries
        self.batch_size = batch_size
        self.send_interval = send_interval_in_secs
        self.sleep_interval = sleep_interval_in_secs
        self.on_error = on_error
        self.backoff_delay = backoff_delay
        self.name = _random_string()
        self.thread = Thread(target=self._run, daemon=True, name=self.name)
        self.logger = logging.getLogger(__name__)

    def start(self):
        """
        Start the worker thread.
        """
        self.running = True
        self.thread.start()

    def join(self):
        """
        Stop the worker thread cleanly, without trying to empty the queue
        first.
        """
        self.running = False
        self.thread.join()

    def _run(self):
        self.logger.debug("Consumer is running")

        while self.running:
            if self.consume() < 1:
                sleep(self.sleep_interval)

        self.logger.debug("Consumer is finished")

    def consume(self):
        """
        Consumes the next batch of items from the queue. Returns the number of
        items consumed.  In case of failure, returns the negative of this
        number.
        """
        batch = self._next_batch()
        if not batch:
            self.logger.debug("Empty batch, nothing to do")
            return 0

        n = len(batch)

        try:
            self._send(batch)
            self.logger.debug("Sent batch of %s", len(batch))
        except Exception as e:
            self.logger.exception("Failed to send batch of %s: %s", len(batch), e)
            if self.on_error:
                self.on_error(e, batch)
            n = -n
        finally:
            for item in batch:
                self.queue.task_done()

        return n

    def _next_batch(self):
        """
        Returns the next batch of items to be consumed.
        """
        batch = []

        start_time = time.monotonic()

        while len(batch) < self.batch_size:
            elapsed = time.monotonic() - start_time
            if elapsed >= self.send_interval:
                break

            try:
                item = self.queue.get(block=True, timeout=self.send_interval - elapsed)
                batch.append(item)
            except Empty:
                break

        return batch

    def _send(self, batch):
        """
        Try sending with back-off strategy.
        """

        @backoff.on_exception(
            self.backoff_delay,
            Exception,
            max_tries=self.retries + 1,
            giveup=_should_give_up,
        )
        def send():
            self.backend.send(batch)

        send()
