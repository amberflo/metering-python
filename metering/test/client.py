from datetime import date, datetime
import unittest
import six
import mock
import time

from metering.version import VERSION
from metering.client import Client


class TestClient(unittest.TestCase):

    def fail(self, e, batch):
        """Mark the failure handler"""
        self.failed = True

    def setUp(self):
        self.failed = False
        self.client = Client('demo', 'changeme', on_error=self.fail)

    def test_requires_write_key(self):
        self.assertRaises(AssertionError, Client)

    def test_empty_flush(self):
        self.client.flush()

    def test_basic_meter(self):
        client = self.client
        success, msg = client.meter('customerTestCae', 'Testing python library.', 1, [])
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg['meter_name'], 'Testing python library.')
        self.assertTrue(isinstance(msg['meter_name'], str))

    def test_flush(self):
        client = self.client
        # set up the consumer with more requests than a single batch will allow
        for i in range(1000):
            success, msg = client.meter('customerTestCae', 'Testing python library.', 1, [{'Name': 'test', 'Value': 'test'}])
        # We can't reliably assert that the queue is non-empty here; that's
        # a race condition. We do our best to load it up though.
        client.flush()
        # Make sure that the client queue is empty after flushing
        self.assertTrue(client.queue.empty())

    def test_shutdown(self):
        client = self.client
        # set up the consumer with more requests than a single batch will allow
        for i in range(1000):
            success, msg = client.meter('customerTestCae', 'Testing python library.', 1, [{'Name': 'test', 'Value': 'test'}])
        client.shutdown()
        # we expect two things after shutdown:
        # 1. client queue is empty
        # 2. consumer thread has stopped
        self.assertTrue(client.queue.empty())
        for consumer in client.consumers:
            self.assertFalse(consumer.is_alive())

    def test_synchronous(self):
        client = Client('demo', 'changeme', wait=True)

        success, message = client.meter('customerTestCae', 'Testing python library.', 1, [{'Name': 'test', 'Value': 'test'}])
        self.assertFalse(client.consumers)
        self.assertTrue(client.queue.empty())
        self.assertTrue(success)

    def test_overflow(self):
        client = Client('demo', 'changeme', max_load=1)
        # Ensure consumer thread is no longer uploading
        client.join()

        for i in range(10):
            client.meter('customerTestCae', 'Testing python library.', 1, [{'Name': 'test', 'Value': 'test'}])

        success, msg = client.meter('customerTestCae', 'Testing python library.', 1, [{'Name': 'test', 'Value': 'test'}])
        # Make sure we are informed that the queue is at capacity
        self.assertFalse(success)

    def test_success_on_invalid_write_key(self):
        client = Client('bad_key', '', on_error=self.fail)
        client.meter('customerTestCae', 'Testing python library.', 1, [{'Name': 'test', 'Value': 'test'}])
        client.flush()
        self.assertFalse(self.failed)
