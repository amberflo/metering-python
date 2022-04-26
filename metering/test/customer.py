import os
import unittest
from uuid import uuid4

from metering.customer import CustomerApiClient
from metering.customer_payload_factory import CustomerPayloadFactory

API_KEY = os.environ["TEST_API_KEY"]

customer_id_key = "customerId"
customer_name_key = "customerName"
traits_key = "traits"


class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.client = CustomerApiClient(API_KEY)
        self.customer_id = str(uuid4())
        self.customer_name = "Test Customer Name"
        self.traits = {"region": "midwest"}

    def _delete(self, customer_id):
        """
        Delete customer, though we don't exposed this on the SDK.
        """
        path = "{}{}".format(self.client.path, customer_id)
        response = self.client.client.delete(path)
        self.assertEqual(response[customer_id_key], customer_id)

    def test_can_create_list_and_delete_customers(self):
        # create
        message = CustomerPayloadFactory.create(
            customer_id=self.customer_id, customer_name=self.customer_name
        )
        response = self.client.add_or_update_customer(message)
        self.assertEqual(response[customer_id_key], self.customer_id)
        self.assertEqual(response[customer_name_key], self.customer_name)

        # list
        response = self.client.list()
        self.assertIsInstance(response, list)

        # get by id
        response = self.client.get(self.customer_id)
        self.assertEqual(response[customer_id_key], self.customer_id)
        self.assertEqual(response[customer_name_key], self.customer_name)

        # delete
        self._delete(self.customer_id)

    def test_can_upsert_with_traits(self):
        # upsert (add)
        message = CustomerPayloadFactory.create(
            customer_id=self.customer_id,
            customer_name=self.customer_name,
            traits=self.traits,
        )
        response = self.client.add_or_update_customer(message)
        self.assertEqual(response[customer_id_key], self.customer_id)
        self.assertEqual(response[customer_name_key], self.customer_name)
        self.assertEqual(response[traits_key], self.traits)

        # upsert (update)
        message = CustomerPayloadFactory.create(
            customer_id=self.customer_id, customer_name="Another Test Name"
        )
        response = self.client.add_or_update_customer(message)
        self.assertEqual(response[customer_id_key], self.customer_id)
        self.assertEqual(response[customer_name_key], "Another Test Name")
        self.assertFalse(response.get(traits_key))

        # delete
        self._delete(self.customer_id)

    def test_can_create_customer_in_stripe(self):
        """
        NOTE: Needs API_KEY with Stripe integration configured
        """
        # upsert (add)
        message = CustomerPayloadFactory.create(
            customer_id=self.customer_id,
            customer_name=self.customer_name,
        )
        response = self.client.add_or_update_customer(
            message, create_customer_in_stripe=True
        )
        self.assertEqual(response[customer_id_key], self.customer_id)
        self.assertIn("stripeId", response[traits_key])

        # delete
        self._delete(self.customer_id)
