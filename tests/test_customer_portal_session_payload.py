import unittest
from time import time

from metering.customer_portal_session import create_customer_portal_session_payload


class TestCreateCustomerProductPlanPayload(unittest.TestCase):

    customer_id = "foo"
    expiration_epoch_in_milliseconds = int(time() + 60 * 60 * 8)
    return_url = "https://example.com"

    def test_with_required_arguments(self):
        message = create_customer_portal_session_payload(
            customer_id=self.customer_id,
        )

        self.assertEqual(message["customerId"], self.customer_id)

        self.assertNotIn("expirationEpochMilliSeconds", message)
        self.assertNotIn("returnUrl", message)

    def test_with_all_arguments(self):
        message = create_customer_portal_session_payload(
            customer_id=self.customer_id,
            expiration_epoch_in_milliseconds=self.expiration_epoch_in_milliseconds,
            return_url=self.return_url,
        )

        self.assertEqual(message["customerId"], self.customer_id)
        self.assertEqual(message["returnUrl"], self.return_url)
        self.assertEqual(
            message["expirationEpochMilliSeconds"],
            self.expiration_epoch_in_milliseconds,
        )
