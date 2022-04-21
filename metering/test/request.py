import os
import unittest
import time
import requests

from metering.request import RequestManager

API_KEY = os.environ['TEST_API_KEY']


class TestRequests(unittest.TestCase):
    """Test class for RequestManager"""

    timestamp = int(round(time.time() * 1000))

    def test_valid_request(self):
        res = RequestManager(API_KEY, batch=[{
            'meterTimeInMillis': self.timestamp,
            'customerId': '123',
            'meterApiName': 'python event',
            'meterValue': 3
        }]).post()
        self.assertEqual(res.status_code, 200)

    def test_should_not_timeout(self):
        res = RequestManager(API_KEY, batch=[{
            'meterTimeInMillis': self.timestamp,
            'customerId': '123',
            'meterApiName': 'python event',
            'meterValue': 3
            }], timeout=15).post()
        self.assertEqual(res.status_code, 200)

    def test_should_timeout(self):
        with self.assertRaises(requests.ReadTimeout):
            RequestManager(API_KEY, batch=[{
                'meterTimeInMillis': self.timestamp,
                'customerId': '123',
                'meterApiName': 'python event',
                'meterValue': 3
            }], timeout=0.0001).post()

if __name__ == '__main__':
    unittest.main()
