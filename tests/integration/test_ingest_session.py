import os
import unittest
from uuid import uuid4

from metering.exceptions import ApiError
from metering.session import IngestSession


API_KEY = os.environ.get("TEST_API_KEY")


@unittest.skipIf(API_KEY is None, "Needs Amberflo's API key")
class TestIngestSession(unittest.TestCase):

    payload = {
        "customerId": "my-customer",
        "meterApiName": "my-meter",
        "meterValue": 5,
        "meterTimeInMillis": 1619445706909,
    }

    def test_good_response_is_parsed(self):
        client = IngestSession(API_KEY)
        response = client.post("/ingest/", self.payload)
        self.assertIsInstance(response, str)

    def test_error_response_becomes_exception(self):
        invalid_api_key = str(uuid4())
        client = IngestSession(invalid_api_key)
        with self.assertRaises(ApiError):
            client.post("/ingest/", self.payload)
