import os
import unittest

from metering.session import ApiSession

from metering.customer import (
    CustomerProductPlanApiClient,
    create_customer_product_plan_payload,
)

API_KEY = os.environ["TEST_API_KEY"]


class TestCustomerProductPlanApiClient(unittest.TestCase):
    def setUp(self):
        self.generic = ApiSession(API_KEY)
        self.client = CustomerProductPlanApiClient(API_KEY)

    def test_assign_product_plan_to_customer(self):
        # get existing customer and product plan
        customers = self.generic.get("/customers/")
        product_plans = self.generic.get(
            "/payments/pricing/amberflo/account-pricing/product-plans/list"
        )
        customer_id = customers[0]["customerId"]
        product_plan_id = product_plans[0]["id"]

        # add or update
        message = create_customer_product_plan_payload(
            customer_id=customer_id,
            product_plan_id=product_plan_id,
        )
        response = self.client.add_or_update(message)
        self.assertEqual(response["customerId"], customer_id)
        self.assertEqual(response["productPlanId"], product_plan_id)

        # get latest
        response = self.client.get(customer_id)
        self.assertEqual(response["customerId"], customer_id)
        self.assertEqual(response["productPlanId"], product_plan_id)

        # list all
        response = self.client.list(customer_id)
        self.assertIsInstance(response, list)
