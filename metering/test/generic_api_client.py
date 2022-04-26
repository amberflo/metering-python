import os
import unittest
from uuid import uuid4

from metering.request import APIError
from metering.api_client import GenericApiClient


API_KEY = os.environ["TEST_API_KEY"]


class TestGenericApiClient(unittest.TestCase):
    def test_good_response_is_parsed(self):
        client = GenericApiClient(API_KEY)
        response = client.get("/customers/", {"customerId": str(uuid4())})
        self.assertIsInstance(response, dict)
        print()
        print(response)
        print()

    def test_error_response_becomes_exception(self):
        invalid_api_key = str(uuid4())
        client = GenericApiClient(invalid_api_key)
        with self.assertRaises(APIError):
            client.get("/customers/", {"customerId": str(uuid4())})
