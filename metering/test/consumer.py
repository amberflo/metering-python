import unittest
import mock
import time
import json

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

from metering.consumer import Consumer, MAX_MSG_SIZE
from metering.request import APIError


class TestConsumer(unittest.TestCase):

    def test_next(self):
        q = Queue()
        consumer = Consumer(q, 'demo', 'changeme')
        q.put(1)
        next = consumer.next()
        self.assertEqual(next, [1])

    def test_next_limit(self):
        q = Queue()
        flush_at = 50
        consumer = Consumer(q, 'demo', 'changeme', flush_at)
        for i in range(10000):
            q.put(i)
        next = consumer.next()
        self.assertEqual(next, list(range(flush_at)))

    def test_dropping_oversize_msg(self):
        q = Queue()
        consumer = Consumer(q, 'demo', 'changeme')
        oversize_msg = {'m': 'x' * MAX_MSG_SIZE}
        q.put(oversize_msg)
        next = consumer.next()
        self.assertEqual(next, [])
        self.assertTrue(q.empty())

    def test_upload(self):
        q = Queue()
        consumer = Consumer(q, 'demo', 'changeme')
        meter = {
            'type': 'meter',
            'event': 'python event',
            'userId': 'userId'
        }
        q.put(meter)
        success = consumer.upload()
        self.assertTrue(success)


    def test_request(self):
        consumer = Consumer(None, 'demo', 'changeme')
        meter = {
            'type': 'meter',
            'event': 'python event',
            'userId': 'userId'
        }
        consumer.request([meter])

    def test_pause(self):
        consumer = Consumer(None, 'demo', 'changeme')
        consumer.pause()
        self.assertFalse(consumer.running)

