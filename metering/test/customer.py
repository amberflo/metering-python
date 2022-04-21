import unittest
from time import time

from metering.customer import CustomerApiClient
from metering.customer_payload_factory import CustomerPayloadFactory

key = 'e9c6a4fc-e275-4eda-b2f8-353ef196ddb7'
customer_id_key = 'customerId'
customer_name_key = 'customerName'
traits_key = 'traits'


class TestCustomer(unittest.TestCase):
    customer_id = '123-python'
    customer_name = 'python-sdk-client'
    traits = {'region': 'midwest'}

    def test_valid_request(self):
        message = CustomerPayloadFactory.create(
            customer_id=self.customer_id,
            customer_name=self.customer_name,
            traits=None
        )
        client = CustomerApiClient(key)
        response = client.add_or_update_customer(message)
        print(response)
        self.assertEqual(response[customer_id_key], self.customer_id)
        self.assertEqual(response[customer_name_key], self.customer_name)

    def test_with_traits(self):
        message = CustomerPayloadFactory.create(
            customer_id=self.customer_id,
            customer_name=self.customer_name,
            traits=self.traits
        )
        client = CustomerApiClient(key)
        response = client.add_or_update_customer(message)
        print(response)
        self.assertEqual(response[customer_id_key], self.customer_id)
        self.assertEqual(response[customer_name_key], self.customer_name)
        self.assertEqual(response[traits_key], self.traits)

    def test_can_create_customer_in_stripe(self):
        """
        NOTE: Needs APP_KEY with Stripe integration configured
        """
        n = int(time() * 1000)  # ensure this is a new customer
        customer_id = f'stripe-cus-{n}'
        customer_name = f'Stripe Cus {n}'
        message = CustomerPayloadFactory.create(
            customer_id=customer_id,
            customer_name=customer_name,
        )
        client = CustomerApiClient(key)
        response = client.add_or_update_customer(message, create_customer_in_stripe=True)
        print(response)
        self.assertEqual(response[customer_id_key], customer_id)
        self.assertEqual(response[customer_name_key], customer_name)
        self.assertIn('stripeId', response[traits_key])


if __name__ == '__main__':
    unittest.main()
