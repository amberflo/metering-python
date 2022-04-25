import unittest
from time import sleep
from unittest.mock import patch

from metering.ingest import ThreadedProducer


class _DummyBackend:
    def send(self, payload):
        sleep(0.01)


class TestIngestConsumer(unittest.TestCase):
    def setUp(self):
        self.client = ThreadedProducer(
            {},
            _DummyBackend,
            max_queue_size=100,
            threads=2,
            batch_size=10,
        )

    def test_normal_usage(self):
        with patch.object(_DummyBackend, "send") as mock_send:
            for i in range(90):
                self.client.send(i)

            self.client.shutdown()

            # send method on back-end was called
            self.assertTrue(mock_send.called)

        # queue is empty
        self.assertTrue(self.client.queue.empty())

        # threads have stopped
        for c in self.client.consumers:
            self.assertFalse(c.thread.is_alive())

    def test_flush_and_join(self):
        for i in range(90):
            self.client.send(i)

        self.client.flush()

        # queue is empty
        self.assertTrue(self.client.queue.empty())

        # threads are still alive
        for c in self.client.consumers:
            self.assertTrue(c.thread.is_alive())

        self.client.join()

        # threads have stopped
        for c in self.client.consumers:
            self.assertFalse(c.thread.is_alive())

    def test_join_without_flush(self):
        for i in range(90):
            self.client.send(i)

        self.client.join()

        # threads have stopped
        for c in self.client.consumers:
            self.assertFalse(c.thread.is_alive())

        # queue is not empty
        self.assertFalse(self.client.queue.empty())

    def test_empty_shutdown(self):
        # does not raise
        self.client.shutdown()


class TestIngestConsumerQueueIsFull(unittest.TestCase):
    def test_full_queue(self):
        self.client = ThreadedProducer(
            {},
            _DummyBackend,
            max_queue_size=1,
            threads=0,
        )

        self.assertTrue(self.client.send(1))
        self.assertFalse(self.client.send(2))
