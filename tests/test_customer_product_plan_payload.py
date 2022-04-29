import unittest
from time import time

from metering.constants import DEFAULT_PRODUCT_ID
from metering.customer_product_plan import create_customer_product_plan_payload


class TestCreateCustomerProductPlanPayload(unittest.TestCase):

    customer_id = "foo"
    product_plan_id = "bar"
    product_id = "bum"
    start_time_in_seconds = int(time())
    end_time_in_seconds = start_time_in_seconds + 100000

    def test_with_required_arguments(self):
        message = create_customer_product_plan_payload(
            customer_id=self.customer_id,
            product_plan_id=self.product_plan_id,
        )

        self.assertEqual(message["customerId"], self.customer_id)
        self.assertEqual(message["productPlanId"], self.product_plan_id)
        self.assertEqual(message["productId"], DEFAULT_PRODUCT_ID)

        self.assertNotIn("startTimeInSeconds", message)
        self.assertNotIn("endTimeInSeconds", message)

    def test_with_all_arguments(self):
        message = create_customer_product_plan_payload(
            customer_id=self.customer_id,
            product_plan_id=self.product_plan_id,
            product_id=self.product_id,
            start_time_in_seconds=self.start_time_in_seconds,
            end_time_in_seconds=self.end_time_in_seconds,
        )

        self.assertEqual(message["customerId"], self.customer_id)
        self.assertEqual(message["productPlanId"], self.product_plan_id)
        self.assertEqual(message["productId"], self.product_id)
        self.assertEqual(message["startTimeInSeconds"], self.start_time_in_seconds)
        self.assertEqual(message["endTimeInSeconds"], self.end_time_in_seconds)

    def test_with_invalid_end_time(self):
        with self.assertRaises(AssertionError):
            create_customer_product_plan_payload(
                customer_id=self.customer_id,
                product_plan_id=self.product_plan_id,
                product_id=self.product_id,
                start_time_in_seconds=self.start_time_in_seconds,
                end_time_in_seconds=self.start_time_in_seconds + 10000,
            )
