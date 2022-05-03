from enum import Enum

from metering import validators
from metering.session import ApiSession
from metering.constants import DEFAULT_PRODUCT_ID

DEFAULT_OFFER_VERSION = -1


class CustomerPrepaidOrderApiClient:
    """
    See https://docs.amberflo.io/reference/post_payments-pricing-amberflo-customer-prepaid
    """

    path = "/payments/pricing/amberflo/customer-prepaid"
    path_list = path + "/list"

    def __init__(self, api_key):
        """
        Initialize the API client session.
        """
        self.client = ApiSession(api_key)

    def list_active(self, customer_id, product_id=DEFAULT_PRODUCT_ID):
        """
        List active prepaid orders of the given customer.

        See https://docs.amberflo.io/reference/get_payments-pricing-amberflo-customer-prepaid-list
        """
        validators.require_string("customer_id", customer_id, allow_none=False)
        validators.require_string("product_id", product_id, allow_none=False)
        params = {
            "CustomerId": customer_id,
            "ProductId": product_id,
        }
        return self.client.get(self.path_list, params=params)

    def add(self, payload):
        """
        Add a new prepaid order to a customer.

        Create a payload using the `create_customer_prepaid_order_payload` function.

        See https://docs.amberflo.io/reference/post_payments-pricing-amberflo-customer-prepaid
        """
        return self.client.post(self.path, payload)


class BillingPeriodUnit(Enum):
    DAY = "DAY"
    MONTH = "MONTH"
    YEAR = "YEAR"


class BillingPeriod:
    """
    Time-span of a billing cycle.

    Examples:
    - 3 months
    - 15 days
    """

    def __init__(self, count, unit):
        validators.require_positive_int("count", count, allow_none=False)
        validators.require("unit", unit, BillingPeriodUnit, allow_none=False)
        self.count = count
        self.unit = unit

    @property
    def payload(self):
        return {
            "interval": self.unit.value,
            "intervalsCount": self.count,
        }


def create_customer_prepaid_order_payload(
    id,
    customer_id,
    start_time_in_seconds,
    prepaid_price,
    prepaid_offer_version=None,
    original_worth=None,
    recurrence_frequency=None,
    external_payment=False,
    product_id=None,
):
    """
    id: String.

    customer_id: String.

    start_time_in_seconds: Positive integer. Unix epoch time.

    prepaid_offer_version: Optional. Positive integer.

    prepaid_price: Number.

    original_worth: Optional. Number.

    recurrence_frequency: Optional. BillingPeriod.

    external_payment: Optional. Boolean. Defaults to False.

    product_id: Optional. String.

    See https://docs.amberflo.io/reference/post_payments-pricing-amberflo-customer-prepaid
    """
    validators.require_string("id", id, allow_none=False)
    validators.require_string("customer_id", customer_id, allow_none=False)
    validators.require_positive_int(
        "start_time_in_seconds", start_time_in_seconds, allow_none=False
    )
    validators.require_positive_int("prepaid_offer_version", prepaid_offer_version)
    validators.require_positive_number("prepaid_price", prepaid_price, allow_none=False)
    validators.require_positive_number("original_worth", original_worth)
    validators.require("recurrence_frequency", recurrence_frequency, BillingPeriod)
    validators.require("external_payment", external_payment, bool, allow_none=False)
    validators.require_string("product_id", product_id)

    payload = {
        "id": id,
        "customerId": customer_id,
        "productId": product_id or DEFAULT_PRODUCT_ID,
        "startTimeInSeconds": start_time_in_seconds,
        "prepaidOfferVersion": prepaid_offer_version or DEFAULT_OFFER_VERSION,
        "prepaidPrice": prepaid_price,
        "externalPayment": external_payment,
    }

    if recurrence_frequency:
        payload["recurrenceFrequency"] = recurrence_frequency.payload

    if original_worth:
        payload["originalWorth"] = original_worth

    return payload
