import unittest
import json
import requests

from datetime import datetime, date
from metering.request import RequestManager, DatetimeSerializer


class TestRequests(unittest.TestCase):

    def test_valid_request(self):
        res = RequestManager('e9c6a4fc-e275-4eda-b2f8-353ef196ddb7', batch=[{
            'tenant_id': 'myself',
            'meter_name': 'python event',
            'meter_value': 3
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
        res = RequestManager('e9c6a4fc-e275-4eda-b2f8-353ef196ddb7', batch=[{
            'tenant_id': 'myself',
            'meter_name': 'python event',
            'meter_value': 3
            }], timeout=15).post()
        self.assertEqual(res.status_code, 200)

    def test_should_timeout(self):
        with self.assertRaises(requests.ReadTimeout):
            RequestManager('e9c6a4fc-e275-4eda-b2f8-353ef196ddb7', batch=[{
                'tenant_id': 'myself',
                'meter_name': 'python event',
                'meter_value': 3
            }], timeout=0.0001).post()

if __name__ == '__main__':
    unittest.main()