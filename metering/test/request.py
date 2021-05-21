import unittest
import time
import requests

from metering.request import RequestManager


class TestRequests(unittest.TestCase):
    """Test class for RequestManager"""

    timestamp = int(round(time.time() * 1000))

    def test_valid_request(self):
        res = RequestManager('e9c6a4fc-e275-4eda-b2f8-353ef196ddb7', batch=[{
            'meterTimeInMillis': self.timestamp,
            'customerId': '123',
            'meterApiName': 'python event',
            'meterValue': 3
        }]).post()
        self.assertEqual(res.status_code, 200)

    def test_should_not_timeout(self):
        res = RequestManager('e9c6a4fc-e275-4eda-b2f8-353ef196ddb7', batch=[{
            'meterTimeInMillis': self.timestamp,
            'customerId': '123',
            'meterApiName': 'python event',
            'meterValue': 3
            }], timeout=15).post()
        self.assertEqual(res.status_code, 200)

    def test_should_timeout(self):
        with self.assertRaises(requests.ReadTimeout):
            RequestManager('e9c6a4fc-e275-4eda-b2f8-353ef196ddb7', batch=[{
                'meterTimeInMillis': self.timestamp,
                'customerId': '123',
                'meterApiName': 'python event',
                'meterValue': 3
            }], timeout=0.0001).post()

if __name__ == '__main__':
    unittest.main()
