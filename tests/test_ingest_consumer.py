import unittest
from unittest.mock import patch, Mock
from queue import Queue

from metering.exceptions import ApiError
from metering.ingest.consumer import ThreadedConsumer


class _DummyBackend:
    def send(self, payload):
        return


class TestIngestThreadedConsumer(unittest.TestCase):
    def setUp(self):
        self.queue = Queue()
        self.consumer = ThreadedConsumer(
            self.queue,
            _DummyBackend(),
            retries=2,
            batch_size=10,
            send_interval_in_secs=0.1,
            sleep_interval_in_secs=0.1,
        )

    def test_consumes_from_empty_queue(self):
        with patch.object(_DummyBackend, "send") as mock_send:
            n = self.consumer.consume()
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

    def test_consumes_at_most_batch_size_at_a_time(self):
        for i in range(15):
            self.queue.put(i)

        with patch.object(_DummyBackend, "send") as mock_send:
            n = self.consumer.consume()
            mock_send.assert_called_once_with([i for i in range(10)])

        self.assertEqual(n, 10)
        self.assertEqual(self.queue.qsize(), 5)

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


class TestIngestThreadedConsumerWithErrorCallback(unittest.TestCase):
    def setUp(self):
        queue = Queue()

        self.on_error_callback = Mock(return_value=None)

        self.consumer = ThreadedConsumer(
            queue,
            _DummyBackend(),
            retries=2,
            batch_size=10,
            send_interval_in_secs=0.1,
            sleep_interval_in_secs=0.1,
            on_error=self.on_error_callback,
        )

        for i in range(15):
            queue.put(i)

    def test_error_callback_is_called_if_there_is_an_error(self):
        error = ApiError(500, "internal server error")

        with patch.object(_DummyBackend, "send") as mock_send:
            mock_send.side_effect = error
            self.consumer.consume()

        self.on_error_callback.assert_called_once_with(error, list(range(10)))

    def test_error_callback_is_not_called_if_there_is_no_error(self):
        self.consumer.consume()

        self.on_error_callback.assert_not_called()
