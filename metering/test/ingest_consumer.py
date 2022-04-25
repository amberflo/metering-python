import unittest
from unittest.mock import patch
from queue import Queue

from metering.api_client import ApiError
from metering.ingest.consumer import ThreadedConsumer


class _DummyBackend:
    def send(self, payload):
        return


class TestIngestThreadedConsumer(unittest.TestCase):
    def setUp(self):
        self.q = Queue()
        self.consumer = ThreadedConsumer(
            self.q,
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
            self.q.put(i)

        with patch.object(_DummyBackend, "send") as mock_send:
            n = self.consumer.consume()
            mock_send.assert_called_once_with([0, 1, 2, 3, 4])

        self.assertEqual(n, 5)
        self.assertEqual(self.q.qsize(), 0)

    def test_consumes_at_most_batch_size_at_a_time(self):
        for i in range(15):
            self.q.put(i)

        with patch.object(_DummyBackend, "send") as mock_send:
            n = self.consumer.consume()
            mock_send.assert_called_once_with([i for i in range(10)])

        self.assertEqual(n, 10)
        self.assertEqual(self.q.qsize(), 5)

    def test_tries_to_send_a_few_times_in_case_of_exceptions(self):
        for i in range(15):
            self.q.put(i)

        with patch.object(_DummyBackend, "send") as mock_send:
            mock_send.side_effect = ApiError(500, "internal server error")
            # does not raise
            n = self.consumer.consume()
            self.assertEqual(mock_send.call_count, 3)

        self.assertEqual(n, -10)
        self.assertEqual(self.q.qsize(), 5)
