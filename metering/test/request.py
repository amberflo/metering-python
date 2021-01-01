from datetime import datetime, date
import unittest
import json
import requests

from metering.request import RequestManager, DatetimeSerializer


class TestRequests(unittest.TestCase):

    def test_valid_request(self):
        res = RequestManager('demo', 'changeme', batch=[{
            'userId': 'demo',
            'password': 'changeme',
            'event': 'python event',
            'type': 'meter'
        }]).post()
        self.assertEqual(res.status_code, 200)

    def test_datetime_serialization(self):
        data = {'created': datetime(2012, 3, 4, 5, 6, 7, 891011)}
        result = json.dumps(data, cls=DatetimeSerializer)
        self.assertEqual(result, '{"created": "2012-03-04T05:06:07.891011"}')

    def test_date_serialization(self):
        today = date.today()
        data = {'created': today}
        result = json.dumps(data, cls=DatetimeSerializer)
        expected = '{"created": "%s"}' % today.isoformat()
        self.assertEqual(result, expected)

    def test_should_not_timeout(self):
        res = RequestManager('demo', 'changeme', batch=[{
            'userId': 'userId',
            'event': 'python event',
            'type': 'meter'}], timeout=15).post()
        self.assertEqual(res.status_code, 200)

    def test_should_timeout(self):
        with self.assertRaises(requests.ReadTimeout):
            RequestManager('demo', 'changeme', batch=[{
                'userId': 'userId',
                'event': 'python event',
                'type': 'meter'
            }], timeout=0.0001).post()
