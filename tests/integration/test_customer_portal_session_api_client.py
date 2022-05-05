import os
import unittest

from metering.session import ApiSession
from metering.customer_portal_session import (
    CustomerPortalSessionApiClient,
    create_customer_portal_session_payload,
)

API_KEY = os.environ.get("TEST_API_KEY")


@unittest.skipIf(API_KEY is None, "Needs Amberflo's API key")
class TestCustomerPortalSessionApiClient(unittest.TestCase):
    def setUp(self):
        self.customer_id = ApiSession(API_KEY).get("/customers/")[0]["customerId"]
        self.client = CustomerPortalSessionApiClient(API_KEY)

    def test_get_new_session(self):
        message = create_customer_portal_session_payload(
            customer_id=self.customer_id,
        )
        response = self.client.get(message)
        self.assertIsInstance(response, dict)
        self.assertIn("url", response)
        self.assertIn("sessionToken", response)
