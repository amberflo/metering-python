from metering import validators
from metering.session import ApiSession


class CustomerApiClient:
    """
    See: https://docs.amberflo.io/reference/post_customers
    """

    path = "/customers/"

    def __init__(self, api_key):
        """
        Initialize the API client session.
        """
        self.client = ApiSession(api_key)

    def list(self):
        """
        List all customers.
        """
        return self.client.get(self.path)

    def get(self, customer_id):
        """
        Get customer by id.
        """
        validators.require_string("customer_id", customer_id, allow_none=False)
        params = {"customerId": customer_id}
        return self.client.get(self.path, params=params)

    def add(self, payload, create_in_stripe=False):
        """
        Add a new customer.

        Create a payload using the `create_customer_payload` function.

        `create_in_stripe` will add a `stripeId` trait to the customer.

        See: https://docs.amberflo.io/reference/post_customers
        """
        validators.require("create_in_stripe", create_in_stripe, bool, allow_none=False)
        params = {"autoCreateCustomerInStripe": "true"} if create_in_stripe else None
        return self.client.post(self.path, payload, params=params)

    def update(self, payload):
        """
        Update an existing customer.

        Create a payload using the `create_customer_payload` function.

        This has PUT semantics (i.e. it discards existing data).

        See: https://docs.amberflo.io/reference/put_customers-customer-id
        """
        return self.client.put(self.path, payload)

    def add_or_update(self, payload, create_in_stripe=False):
        """
        Convenience method. Performs a `get` followed by either `add` or `update`.

        The update has PUT semantics (i.e. it discards existing data).

        `create_in_stripe` is only used when `add` is called.

        Create a payload using the `create_customer_payload` function.
        """
        customer = self.get(payload["customerId"])

        if "customerId" in customer:
            return self.update(payload)
        else:
            return self.add(payload, create_in_stripe)


def create_customer_payload(
    customer_id,
    customer_name,
    customer_email=None,
    enabled=None,
    traits=None,
):
    """
    customer_id: String.

    customer_name: String.

    customer_email: Optional. String. Defaults to `None`

    enabled: Optional. Boolean. Defaults to `True`
        Setting it to false deactivates the customer.

    traits: Optional. Dictionary of String to String. Defaults to `None`
        Reference metadata to integrate with external systems like billing.
        Can also be used to filter usage data.

    See: https://docs.amberflo.io/reference/post_customers
    """

    validators.require_string("customer_id", customer_id, allow_none=False)
    validators.require_string("customer_name", customer_name, allow_none=False)
    validators.require_string("customer_email", customer_email)
    validators.require("enabled", enabled, bool)
    validators.require_string_dictionary("traits", traits)

    payload = {
        "customerId": customer_id,
        "customerName": customer_name,
    }

    if customer_email is not None:
        payload["customerEmail"] = customer_email

    if enabled is not None:
        payload["enabled"] = enabled

    if traits is not None:
        payload["traits"] = traits

    return payload
