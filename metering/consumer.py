from re import S
from threading import Thread
import time
import traceback
import backoff

from metering.request import RequestManager, APIError
from metering.logger import Logger

try:
    from queue import Empty
except ImportError:
    from Queue import Empty

MAX_MSG_SIZE = 32 << 10

# Our servers only accept batches less than 500KB. Here limit is set slightly
# lower to leave space for extra data that will be added later, eg. "sentAt".
BATCH_SIZE_LIMIT = 475000

TIME_TO_SLEEP_IF_FAIL_OR_IDLE_SECONDS = 0.1

class Consumer(Thread):
    """Consumes the messages from the client's queue."""

    # TODO ofer 02/25/2021: consider removing the gzip param (should it really
    # be configurable by the client?).
    def __init__(self, queue, app_key, s3_bucket=None, access_key=None, secret_key=None,
                flush_at=100, on_error=None, send_interval=0.5, gzip=False, retries=10,
                timeout=15):
        """Create a consumer thread."""
        Thread.__init__(self)
        # Make consumer a daemon thread so that it doesn't block program exit
        self.daemon = True
        self.flush_at = flush_at
        self.flush_interval = send_interval
        self.app_key = app_key
        self.s3_bucket=s3_bucket
        self.access_key=access_key
        self.secret_key=secret_key
        self.on_error = on_error
        self.queue = queue
        self.gzip = gzip
        # It's important to set running in the constructor: if we are asked to
        # pause immediately after construction, we might set running to True in
        # run() *after* we set it to False in pause... and keep running
        # forever.
        self.running = True
        self.retries = retries
        self.timeout = timeout
        self.log = Logger()

    def run(self):
        """Runs the consumer."""
        self.log.debug('consumer is running...')
        while self.running:
            success = self.upload()
            if not success:
                self.__sleep(TIME_TO_SLEEP_IF_FAIL_OR_IDLE_SECONDS)

        self.log.debug('consumer exited.')

    def pause(self):
        """Pause the consumer."""
        self.running = False

    def upload(self):
        """Upload the next batch of items, return whether successful."""
        success = False
        batch = self.next()
        if len(batch) == 0:
            return False
        try:
            self.request(batch)
            success = True
        except Exception as e:
            self.log.error('error uploading: %s', e)
            success = False
            if self.on_error:
                self.__handle_error(e, batch)
        finally:
            # mark items as acknowledged from queue
            for item in batch:
                self.queue.task_done()
            return success

    def next(self):
        """Return the next batch of items to upload."""
        queue = self.queue
        items = []

        start_time = time.monotonic()

        while len(items) < self.flush_at:
            elapsed = time.monotonic() - start_time
            if elapsed >= self.flush_interval:
                break
            try:
                item = queue.get(
                    block=True, timeout=self.flush_interval - elapsed)
                items.append(item)
            except Empty:
                break

        return items

    def request(self, batch):
        """Attempt to upload the batch and retry before raising an error """
        def fatal_exception(exc):
            if isinstance(exc, APIError):
                # retry on server errors and client errors
                # with 429 status code (rate limited),
                # don't retry on other client errors
                return (400 <= exc.status < 500) and exc.status != 429
            else:
                # retry on all other errors (eg. network)
                return False

        @backoff.on_exception(
            backoff.expo,
            Exception,
            max_tries=self.retries + 1,
            giveup=fatal_exception)
        def send_request():
            try:
                if self.s3_bucket:
                    RequestManager(None,self.s3_bucket, self.access_key, self.secret_key,
                    timeout=self.timeout, batch=batch).send_to_s3()
                else:        
                    RequestManager(self.app_key, gzip=self.gzip,
                        timeout=self.timeout, batch=batch).post()
            except Exception as e:
                print(traceback.format_exc())
                raise e

        send_request()

    def __handle_error(self, exception, batch):
        try:
            self.on_error(exception, batch)
        except RuntimeError:
            self.log.warn(exception)

    def __sleep(self, seconds):
        # Sleep Time is in seconds: https://docs.python.org/2/library/time.html
        try:
            time.sleep(seconds)
        except RuntimeError as exception:
            self.log.warn(exception)
