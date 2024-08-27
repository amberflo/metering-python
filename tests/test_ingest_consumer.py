import unittest
from unittest.mock import patch, Mock
from queue import Queue

from metering.exceptions import ApiError
from metering.ingest.consumer import ThreadedConsumer, backoff_delay


def _dummy_delay(*args, **kwargs):
    while True:
        yield 0.1


class _DummyBackend:
    def send(self, payload):
        return

    def sendCustom(self, payload):
        return


class TestIngestThreadedConsumer(unittest.TestCase):
    def setUp(self):
        self.queue = Queue()
        self.customQueue = Queue()
        self.consumer = ThreadedConsumer(
            self.queue,
            self.customQueue,
            _DummyBackend(),
            retries=2,
            batch_size=10,
            send_interval_in_secs=0.1,
            sleep_interval_in_secs=0.1,
            backoff_delay=_dummy_delay,
        )

    def test_consumes_from_empty_queue(self):
        with patch.object(_DummyBackend, "send") as mock_send:
            n = self.consumer.consume()
            mock_send.assert_not_called()

        self.assertEqual(n, 0)

    def test_consumes_from_empty_queue_custom(self):
        with patch.object(_DummyBackend, "sendCustom") as mock_send:
            n = self.consumer.consumeCustom()
            mock_send.assert_not_called()

        self.assertEqual(n, 0)

    def test_does_not_wait_for_complete_batch_size(self):
        for i in range(5):
            self.queue.put(i)

        with patch.object(_DummyBackend, "send") as mock_send:
            n = self.consumer.consume()
            mock_send.assert_called_once_with([0, 1, 2, 3, 4])

        self.assertEqual(n, 5)
        self.assertEqual(self.queue.qsize(), 0)

    def test_does_not_wait_for_complete_batch_size_custom(self):
        for i in range(5):
            self.customQueue.put(i)

        with patch.object(_DummyBackend, "sendCustom") as mock_send:
            n = self.consumer.consumeCustom()
            mock_send.assert_called_once_with([0, 1, 2, 3, 4])

        self.assertEqual(n, 5)
        self.assertEqual(self.customQueue.qsize(), 0)

    def test_consumes_at_most_batch_size_at_a_time(self):
        for i in range(15):
            self.queue.put(i)

        with patch.object(_DummyBackend, "send") as mock_send:
            n = self.consumer.consume()
            mock_send.assert_called_once_with([i for i in range(10)])

        self.assertEqual(n, 10)
        self.assertEqual(self.queue.qsize(), 5)

    def test_consumes_at_most_batch_size_at_a_time_custom(self):
        for i in range(15):
            self.customQueue.put(i)

        with patch.object(_DummyBackend, "sendCustom") as mock_send:
            n = self.consumer.consumeCustom()
            mock_send.assert_called_once_with([i for i in range(10)])

        self.assertEqual(n, 10)
        self.assertEqual(self.customQueue.qsize(), 5)

    def test_tries_to_send_a_few_times_for_some_errors(self):
        errors = [
            ApiError(500, "internal server error"),
            ApiError(429, "rate limited"),
            Exception("other errors"),
        ]

        for error in errors:
            with self.subTest(str(error)):
                for i in range(10):
                    self.queue.put(i)

                with patch.object(_DummyBackend, "send") as mock_send:
                    mock_send.side_effect = error
                    # does not raise
                    n = self.consumer.consume()
                    self.assertEqual(mock_send.call_count, 3)

                self.assertEqual(n, -10)
                self.assertEqual(self.queue.qsize(), 0)

    def test_tries_to_send_a_few_times_for_some_errors_custom(self):
        errors = [
            ApiError(500, "internal server error"),
            ApiError(429, "rate limited"),
            Exception("other errors"),
        ]

        for error in errors:
            with self.subTest(str(error)):
                for i in range(10):
                    self.customQueue.put(i)

                with patch.object(_DummyBackend, "sendCustom") as mock_send:
                    mock_send.side_effect = error
                    # does not raise
                    n = self.consumer.consumeCustom()
                    self.assertEqual(mock_send.call_count, 3)

                self.assertEqual(n, -10)
                self.assertEqual(self.customQueue.qsize(), 0)

    def test_does_not_retry_on_api_error_400(self):
        errors = [
            ApiError(400, "bad request"),
            ApiError(403, "not authorized"),
        ]

        for error in errors:
            with self.subTest(str(error)):
                for i in range(10):
                    self.queue.put(i)

                with patch.object(_DummyBackend, "send") as mock_send:
                    mock_send.side_effect = error
                    # does not raise
                    n = self.consumer.consume()
                    self.assertEqual(mock_send.call_count, 1)

                self.assertEqual(n, -10)
                self.assertEqual(self.queue.qsize(), 0)

    def test_does_not_retry_on_api_error_400_custom(self):
        errors = [
            ApiError(400, "bad request"),
            ApiError(403, "not authorized"),
        ]

        for error in errors:
            with self.subTest(str(error)):
                for i in range(10):
                    self.customQueue.put(i)

                with patch.object(_DummyBackend, "sendCustom") as mock_send:
                    mock_send.side_effect = error
                    # does not raise
                    n = self.consumer.consumeCustom()
                    self.assertEqual(mock_send.call_count, 1)

                self.assertEqual(n, -10)
                self.assertEqual(self.customQueue.qsize(), 0)


class TestIngestThreadedConsumerWithErrorCallback(unittest.TestCase):
    def setUp(self):
        queue = Queue()
        customQueue = Queue()

        self.on_error_callback = Mock(return_value=None)

        self.consumer = ThreadedConsumer(
            queue,
            customQueue,
            _DummyBackend(),
            retries=2,
            batch_size=10,
            send_interval_in_secs=0.1,
            sleep_interval_in_secs=0.1,
            on_error=self.on_error_callback,
            backoff_delay=_dummy_delay,
        )

        for i in range(15):
            queue.put(i)
            customQueue.put(i)

    def test_error_callback_is_called_if_there_is_an_error(self):
        error = ApiError(500, "internal server error")

        with patch.object(_DummyBackend, "send") as mock_send:
            mock_send.side_effect = error
            self.consumer.consume()

        self.on_error_callback.assert_called_once_with(error, list(range(10)))

    def test_error_callback_is_called_if_there_is_an_error_custom(self):
        error = ApiError(500, "internal server error")

        with patch.object(_DummyBackend, "sendCustom") as mock_send:
            mock_send.side_effect = error
            self.consumer.consumeCustom()

        self.on_error_callback.assert_called_once_with(error, list(range(10)))

    def test_error_callback_is_not_called_if_there_is_no_error(self):
        self.consumer.consume()

        self.on_error_callback.assert_not_called()

    def test_error_callback_is_not_called_if_there_is_no_error_custom(self):
        self.consumer.consumeCustom()

        self.on_error_callback.assert_not_called()


class TestIngestThreadedConsumerShortSendInterval(unittest.TestCase):
    def test_respects_send_interval_even_if_queue_has_items(self):
        queue = Queue()
        customQueue = Queue()
        consumer = ThreadedConsumer(
            queue,
            customQueue,
            _DummyBackend(),
            batch_size=1000,
            send_interval_in_secs=0.001,
            backoff_delay=_dummy_delay,
        )

        for i in range(1000):
            queue.put(i)

        n = consumer.consume()

        self.assertLessEqual(n, 1000)

    def test_respects_send_interval_even_if_queue_has_items_custom(self):
        queue = Queue()
        customQueue = Queue()
        consumer = ThreadedConsumer(
            queue,
            customQueue,
            _DummyBackend(),
            batch_size=1000,
            send_interval_in_secs=0.001,
            backoff_delay=_dummy_delay,
        )

        for i in range(1000):
            customQueue.put(i)

        n = consumer.consumeCustom()

        self.assertLessEqual(n, 1000)


class TestBackoffDelay(unittest.TestCase):
    def test_default_backoff_delay(self):
        expected = [None, 2, 6, 12, 20, 40, 80, 80]
        for e, x in zip(expected, backoff_delay()):
            self.assertEqual(e, x)
