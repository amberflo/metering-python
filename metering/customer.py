from metering import validators
from metering.session import ApiSession


class CustomerApiClient:
    path = "/customers/"

    def __init__(self, api_key):
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
        params = {"customerId": customer_id}
        return self.client.get(self.path, params=params)

    def add(self, payload, create_in_stripe=False):
        """
        Add a new customer.

        `create_in_stripe` will add a `stripeId` trait to the customer.

        See: https://docs.amberflo.io/reference/post_customers
        """
        params = {"autoCreateCustomerInStripe": "true"} if create_in_stripe else None
        return self.client.post(self.path, payload, params=params)

    def update(self, payload):
        """
        Update an existing customer.

        This has PUT semantics (i.e. it discards existing data).

        See: https://docs.amberflo.io/reference/put_customers-customer-id
        """
        return self.client.put(self.path, payload)

    def add_or_update(self, payload, create_in_stripe=False):
        """
        Convenience method. Performs a `get` followed by either `add` or `update`.

        The update has PUT semantics (i.e. it discards existing data).

        `create_in_stripe` is only used when `add` is called.
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


class CustomerProductPlanApiClient:
    path = "/payments/pricing/amberflo/customer-pricing"
    path_all = path + "/list"

    def __init__(self, api_key):
        self.client = ApiSession(api_key)

    def list(self, customer_id):
        """
        List the entire history of product plans of the given customer.
        """
        params = {"CustomerId": customer_id}
        return self.client.get(self.path_all, params=params)

    def get(self, customer_id):
        """
        Get the latest product plan of the given customer.
        """
        params = {"CustomerId": customer_id}
        return self.client.get(self.path, params=params)

    def add_or_update(self, payload):
        """
        Relates the customer to a product plan.

        See https://docs.amberflo.io/reference/post_payments-pricing-amberflo-customer-pricing
        """
        return self.client.post(self.path, payload)


DEFAULT_PRODUCT_ID = "1"

ONE_DAY = 60 * 60 * 24


def create_customer_product_plan_payload(
    customer_id,
    product_plan_id,
    product_id=DEFAULT_PRODUCT_ID,
    end_time_in_seconds=None,
    start_time_in_seconds=None,
):
    """
    customer_id: String.

    product_plan_id: String.

    product_id: Optional. String.

    start_time_in_seconds: Optional. Integer.

    end_time_in_seconds: Optional. Integer.

    See https://docs.amberflo.io/reference/post_payments-pricing-amberflo-customer-pricing
    """
    validators.require_string("customer_id", customer_id, allow_none=False)
    validators.require_string("product_plan_id", product_plan_id, allow_none=False)
    validators.require_string("product_id", product_id, allow_none=False)

    validators.require_positive_int(
        "start_time_in_seconds",
        start_time_in_seconds,
    )
    validators.require_positive_int(
        "end_time_in_seconds",
        end_time_in_seconds,
    )

    if start_time_in_seconds is not None and end_time_in_seconds is not None:
        msg = "'end_time_in_seconds' must come at least 1 day after the 'start_time_in_seconds'"
        assert end_time_in_seconds >= start_time_in_seconds + ONE_DAY, msg

    payload = {
        "customerId": customer_id,
        "productPlanId": product_plan_id,
        "productId": product_id,
    }

    if start_time_in_seconds:
        payload["startTimeInSeconds"] = start_time_in_seconds

    if end_time_in_seconds:
        payload["endTimeInSeconds"] = end_time_in_seconds

    return payload
