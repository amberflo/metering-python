import unittest
import time
from metering.client import Client


class TestClient(unittest.TestCase):

    def fail(self, e, batch):
        """Mark the failure handler"""
        self.failed = True

    def setUp(self):
        self.failed = False
        self.client = Client('e9c6a4fc-e275-4eda-b2f8-353ef196ddb7', on_error=self.fail)

    def test_requires_write_key(self):
        with self.assertRaises(AssertionError):
            Client(None)

    def test_empty_flush(self):
        self.client.flush()

    def test_basic_meter(self):
        client = self.client
        success, msg = client.meter(meter_api_name='Testing python library.', meter_value=1,
        meter_time_in_millis=int(round(time.time() * 1000)), 
        customer_id='123')
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg['meterApiName'], 'Testing python library.')
        self.assertTrue(isinstance(msg['meterApiName'], str))

    def test_flush(self):
        client = self.client
        # set up the consumer with more requests than a single batch will allow
        for i in range(1000):
            success, msg = client.meter(meter_api_name='Testing python library.', meter_value=1,
            meter_time_in_millis=int(round(time.time() * 1000)), 
            customer_id='123', dimensions={'test': 'test'})
        # We can't reliably assert that the queue is non-empty here; that's
        # a race condition. We do our best to load it up though.
        client.flush()
        # Make sure that the client queue is empty after flushing
        self.assertTrue(client.queue.empty())

    def test_shutdown(self):
        client = self.client
        # set up the consumer with more requests than a single batch will allow
        for i in range(1000):
            success, msg = client.meter(meter_api_name='Testing python library.', meter_value=1,
            meter_time_in_millis=int(round(time.time() * 1000)), 
            customer_id='123', dimensions={'test': 'test'})
        client.shutdown()
        # we expect two things after shutdown:
        # 1. client queue is empty
        # 2. consumer thread has stopped
        self.assertTrue(client.queue.empty())
        for consumer in client.consumers:
            self.assertFalse(consumer.is_alive())

    def test_synchronous(self):
        client = Client('e9c6a4fc-e275-4eda-b2f8-353ef196ddb7', wait=True)

        success, msg = client.meter(meter_api_name='Testing python library.', meter_value=1,
        meter_time_in_millis=int(round(time.time() * 1000)), 
        customer_id='123', dimensions={'test': 'test'})
        self.assertFalse(client.consumers)
        self.assertTrue(client.queue.empty())
        self.assertTrue(success)

    def test_overflow(self):
        client = Client('e9c6a4fc-e275-4eda-b2f8-353ef196ddb7', max_load=1)
        # Ensure consumer thread is no longer uploading
        client.join()

        for i in range(10):
            client.meter(meter_api_name='Testing python library.', meter_value=1,
            meter_time_in_millis=int(round(time.time() * 1000)), 
            customer_id='123', dimensions={'test': 'test'})

        success, msg = client.meter(meter_api_name='Testing python library.', meter_value=1,
        meter_time_in_millis=int(round(time.time() * 1000)),  
        customer_id='123', dimensions={'test': 'test'})
        # Make sure we are informed that the queue is at capacity
        self.assertFalse(success)

    def test_failure_on_invalid_write_key(self):
        client = Client('bad_key', on_error=self.fail)
        client.meter(meter_api_name='Testing python library.', meter_value=1,
        meter_time_in_millis=int(round(time.time() * 1000)), 
        customer_id='123', dimensions={'test': 'test'})
        client.flush()
        self.assertTrue(self.failed)

if __name__ == '__main__':
    unittest.main()
