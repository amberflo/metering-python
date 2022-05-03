from metering import validators
from metering.session import ApiSession
from metering.constants import DEFAULT_PRODUCT_ID


class CustomerProductPlanApiClient:
    """
    See https://docs.amberflo.io/reference/post_payments-pricing-amberflo-customer-pricing
    """

    path = "/payments/pricing/amberflo/customer-pricing"
    path_all = path + "/list"

    def __init__(self, api_key):
        """
        Initialize the API client session.
        """
        self.client = ApiSession(api_key)

    def list(self, customer_id):
        """
        List the entire history of product plans of the given customer.
        """
        validators.require_string("customer_id", customer_id, allow_none=False)
        params = {"CustomerId": customer_id}
        return self.client.get(self.path_all, params=params)

    def get(self, customer_id):
        """
        Get the latest product plan of the given customer.
        """
        validators.require_string("customer_id", customer_id, allow_none=False)
        params = {"CustomerId": customer_id}
        return self.client.get(self.path, params=params)

    def add_or_update(self, payload):
        """
        Relates the customer to a product plan.

        Create a payload using the `create_customer_product_plan_payload` function.

        See https://docs.amberflo.io/reference/post_payments-pricing-amberflo-customer-pricing
        """
        return self.client.post(self.path, payload)


ONE_DAY_IN_SECONDS = 60 * 60 * 24


def create_customer_product_plan_payload(
    customer_id,
    product_plan_id,
    product_id=None,
    end_time_in_seconds=None,
    start_time_in_seconds=None,
):
    """
    customer_id: String.

    product_plan_id: String.

    product_id: Optional. String.

    start_time_in_seconds: Optional. Integer. Unix epoch time.

    end_time_in_seconds: Optional. Integer. Unix epoch time.

    See https://docs.amberflo.io/reference/post_payments-pricing-amberflo-customer-pricing
    """
    validators.require_string("customer_id", customer_id, allow_none=False)
    validators.require_string("product_plan_id", product_plan_id, allow_none=False)
    validators.require_string("product_id", product_id)

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
        assert end_time_in_seconds >= start_time_in_seconds + ONE_DAY_IN_SECONDS, msg

    payload = {
        "customerId": customer_id,
        "productPlanId": product_plan_id,
        "productId": product_id or DEFAULT_PRODUCT_ID,
    }

    if start_time_in_seconds:
        payload["startTimeInSeconds"] = start_time_in_seconds

    if end_time_in_seconds:
        payload["endTimeInSeconds"] = end_time_in_seconds

    return payload
