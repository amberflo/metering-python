import os
import unittest

from metering.session import ApiSession
from metering.customer_product_plan import (
    CustomerProductPlanApiClient,
    create_customer_product_plan_payload,
)

API_KEY = os.environ.get("TEST_API_KEY")


@unittest.skipIf(API_KEY is None, "Needs Amberflo's API key")
class TestCustomerProductPlanApiClient(unittest.TestCase):
    def setUp(self):
        self.generic = ApiSession(API_KEY)
        self.customer_id = self.generic.get("/customers/")[0]["customerId"]

        self.client = CustomerProductPlanApiClient(API_KEY)

    @unittest.skipIf(os.environ.get("CI"), "This is a bit too flaky for CI")
    def test_assign_product_plan_to_customer(self):
        # get existing product plan
        product_plans = self.generic.get(
            "/payments/pricing/amberflo/account-pricing/product-plans/list"
        )
        product_plan_id = product_plans[0]["id"]

        # add or update
        message = create_customer_product_plan_payload(
            customer_id=self.customer_id,
            product_plan_id=product_plan_id,
        )
        response = self.client.add_or_update(message)
        self.assertEqual(response["customerId"], self.customer_id)
        self.assertEqual(response["productPlanId"], product_plan_id)

    def test_get_latest(self):
        response = self.client.get(self.customer_id)
        self.assertEqual(response["customerId"], self.customer_id)
        self.assertIn("productPlanId", response)

    def test_list_all(self):
        response = self.client.list(self.customer_id)
        self.assertIsInstance(response, list)
        self.assertIn("productPlanId", response[0])
