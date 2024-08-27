import unittest
from time import time

from metering.constants import DEFAULT_PRODUCT_ID
from metering.customer_prepaid_order import (
    create_customer_prepaid_order_payload,
    DEFAULT_OFFER_VERSION,
    BillingPeriod,
    BillingPeriodUnit,
)


class TestCreateCustomerPrepaidOrderPayload(unittest.TestCase):

    prepaid_id = "bar"
    customer_id = "foo"
    start_time_in_seconds = int(time())
    prepaid_price = 100.0

    def test_with_required_arguments(self):
        message = create_customer_prepaid_order_payload(
            id=self.prepaid_id,
            customer_id=self.customer_id,
            start_time_in_seconds=self.start_time_in_seconds,
            prepaid_price=self.prepaid_price,
        )

        self.assertEqual(message["id"], self.prepaid_id)
        self.assertEqual(message["customerId"], self.customer_id)
        self.assertEqual(message["startTimeInSeconds"], self.start_time_in_seconds)
        self.assertEqual(message["prepaidPrice"], self.prepaid_price)

        self.assertEqual(message["prepaidOfferVersion"], DEFAULT_OFFER_VERSION)
        self.assertEqual(message["productId"], DEFAULT_PRODUCT_ID)
        self.assertFalse(message["externalPayment"])

        self.assertNotIn("recurrenceFrequency", message)
        self.assertNotIn("originalWorth", message)

    def test_with_optional_arguments(self):
        message = create_customer_prepaid_order_payload(
            id=self.prepaid_id,
            customer_id=self.customer_id,
            start_time_in_seconds=self.start_time_in_seconds,
            prepaid_price=self.prepaid_price,
            prepaid_offer_version=12345,
            product_id="product-id",
            original_worth=120.0,
            recurrence_frequency=BillingPeriod(3, BillingPeriodUnit.DAY),
            external_payment=True,
        )

        self.assertEqual(message["id"], self.prepaid_id)
        self.assertEqual(message["customerId"], self.customer_id)
        self.assertEqual(message["startTimeInSeconds"], self.start_time_in_seconds)
        self.assertEqual(message["prepaidPrice"], self.prepaid_price)

        self.assertEqual(message["prepaidOfferVersion"], 12345)
        self.assertEqual(message["productId"], "product-id")
        self.assertTrue(message["externalPayment"])

        self.assertEqual(
            message["recurrenceFrequency"],
            {"interval": "DAY", "intervalsCount": 3},
        )
        self.assertEqual(message["originalWorth"], 120.0)
