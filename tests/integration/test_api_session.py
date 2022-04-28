import os
import unittest
from uuid import uuid4

from metering.exceptions import ApiError
from metering.session import ApiSession


API_KEY = os.environ.get("TEST_API_KEY")


@unittest.skipIf(API_KEY is None, "Needs Amberflo's API key")
class TestApiSession(unittest.TestCase):

    params = {"customerId": str(uuid4())}

    def test_good_response_is_parsed(self):
        client = ApiSession(API_KEY)
        response = client.get("/customers/", self.params)
        self.assertIsInstance(response, dict)

    def test_error_response_becomes_exception(self):
        invalid_api_key = str(uuid4())
        client = ApiSession(invalid_api_key)
        with self.assertRaises(ApiError):
            client.get("/customers/", self.params)
