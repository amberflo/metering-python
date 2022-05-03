import os
from time import time
from uuid import uuid4
import unittest

from metering.session import ApiSession
from metering.customer_prepaid_order import (
    BillingPeriod,
    BillingPeriodUnit,
    CustomerPrepaidOrderApiClient,
    create_customer_prepaid_order_payload,
)

API_KEY = os.environ.get("TEST_API_KEY")


@unittest.skipIf(API_KEY is None, "Needs Amberflo's API key")
class TestCustomerPrepaidOrderApiClient(unittest.TestCase):
    def setUp(self):
        self.customer_id = ApiSession(API_KEY).get("/customers/")[0]["customerId"]
        self.client = CustomerPrepaidOrderApiClient(API_KEY)

    @unittest.skipIf(os.environ.get("CI"), "This is a bit too flaky for CI")
    def test_add_prepaid_order(self):
        message = create_customer_prepaid_order_payload(
            id=str(uuid4()),
            customer_id=self.customer_id,
            start_time_in_seconds=int(time()),
            prepaid_price=100,
            external_payment=True,
        )
        response = self.client.add(message)
        self.assertIsInstance(response, dict)
        self.assertIsNone(response["recurrenceFrequency"])

    @unittest.skipIf(os.environ.get("CI"), "This is a bit too flaky for CI")
    def test_add_prepaid_order_with_recurrence(self):
        message = create_customer_prepaid_order_payload(
            id=str(uuid4()),
            customer_id=self.customer_id,
            start_time_in_seconds=int(time()),
            prepaid_price=100,
            external_payment=True,
            recurrence_frequency=BillingPeriod(10, BillingPeriodUnit.DAY),
        )
        response = self.client.add(message)
        self.assertIsInstance(response, dict)
        self.assertEqual(
            response["recurrenceFrequency"], {"interval": "day", "intervalsCount": 10}
        )

    def test_list_active_prepaid_orders(self):
        response = self.client.list_active(self.customer_id)
        self.assertIsInstance(response, list)
