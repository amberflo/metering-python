import unittest
import time

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

from metering.consumer import Consumer, MAX_MSG_SIZE


class TestConsumer(unittest.TestCase):
    timestamp = int(round(time.time() * 1000))

    def test_next(self):
        q = Queue()
        consumer = Consumer(q, 'e9c6a4fc-e275-4eda-b2f8-353ef196ddb7')
        q.put(1)
        next = consumer.next()
        self.assertEqual(next, [1])

    def test_next_limit(self):
        q = Queue()
        flush_at = 50
        consumer = Consumer(q, 'e9c6a4fc-e275-4eda-b2f8-353ef196ddb7', flush_at)
        for i in range(10000):
            q.put(i)
        next = consumer.next()
        # self.assertEqual(next, list(range(flush_at)))

    def test_dropping_oversize_msg(self):
        '''For the moment we dont hanfle the case of oversized message'''
        q = Queue()
        consumer = Consumer(q, 'e9c6a4fc-e275-4eda-b2f8-353ef196ddb7')
        oversize_msg = {'m': 'x' * MAX_MSG_SIZE}
        q.put(oversize_msg)
        next = consumer.next()
        self.assertEqual(next, [oversize_msg])

    def test_upload(self):
        q = Queue()
        consumer = Consumer(q, 'e9c6a4fc-e275-4eda-b2f8-353ef196ddb7')
        meter = {
            'meterTimeInMillis': self.timestamp,
            'customerId': '123',
            'meterApiName': 'python event',
            'meterValue': 3
        }
        q.put(meter)
        success = consumer.upload()
        self.assertTrue(success)


    def test_request(self):
        consumer = Consumer(None, 'e9c6a4fc-e275-4eda-b2f8-353ef196ddb7')
        meter = {
            'meterTimeInMillis': self.timestamp,
            'customerId': '123',
            'meterApiName': 'python event',
            'meterValue': 3
        }
        consumer.request([meter])

    def test_pause(self):
        consumer = Consumer(None, 'e9c6a4fc-e275-4eda-b2f8-353ef196ddb7')
        consumer.pause()
        self.assertFalse(consumer.running)

if __name__ == '__main__':
    unittest.main()
