from metering.api_client import GenericApiClient


class CustomerApiClient:
    path = "/customers/"

    def __init__(self, api_key):
        self.client = GenericApiClient(api_key)
        self.logger = self.client.logger

    def list(self):
        """
        List all customers.
        """
        return self.client.get(self.path)

    def get(self, customer_id):
        """
        Get customer by id.
        """
        params = {"customerId": customer_id}
        return self.client.get(self.path, params=params)

    def add(self, payload, create_customer_in_stripe=False):
        """
        Add a new customer.

        `create_customer_in_stripe` will add a `stripeId` trait to the customer.
        """
        params = (
            {"autoCreateCustomerInStripe": "true"}
            if create_customer_in_stripe
            else None
        )
        return self.client.post(self.path, payload, params=params)

    def update(self, payload):
        """
        Update an existing customer.

        This has PUT semantics (i.e. it discards existing data).
        """
        return self.client.put(self.path, payload)

    def add_or_update_customer(self, payload, create_customer_in_stripe=False):
        """
        Convenience method. Performs a `get` followed by either `add` or `update`.

        The update has PUT semantics (i.e. it discards existing data).

        `create_customer_in_stripe` is only used when `add` is called.
        """
        customer = self.get(payload["customerId"])

        if "customerId" in customer:
            return self.update(payload)
        else:
            return self.add(payload, create_customer_in_stripe)
