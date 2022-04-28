import os
import unittest
from uuid import uuid4

from metering.session import ApiError, ApiSession


API_KEY = os.environ["TEST_API_KEY"]


class TestApiSession(unittest.TestCase):
    def test_good_response_is_parsed(self):
        client = ApiSession(API_KEY)
        response = client.get("/customers/", {"customerId": str(uuid4())})
        self.assertIsInstance(response, dict)

    def test_error_response_becomes_exception(self):
        invalid_api_key = str(uuid4())
        client = ApiSession(invalid_api_key)
        with self.assertRaises(ApiError):
            client.get("/customers/", {"customerId": str(uuid4())})
