from datetime import date

from metering import validators
from metering.session import ApiSession
from metering.constants import DEFAULT_PRODUCT_ID


class CustomerProductInvoiceApiClient:
    """
    See https://docs.amberflo.io/reference/get_payments-billing-customer-product-invoice
    """

    path = "/payments/billing/customer-product-invoice"
    path_all = path + "/all"

    def __init__(self, api_key):
        """
        Initialize the API client session.
        """
        self.client = ApiSession(api_key)

    def get_all(self, query):
        """
        Get all invoices of the specified customer.

        Create a query using the `create_all_invoices_query` function.

        See https://docs.amberflo.io/reference/get_payments-billing-customer-product-invoice-all
        """
        return self.client.get(self.path_all, params=query)

    def get(self, query):
        """
        Get a existing invoice of the specified customer.

        Create a query using either the functions:
        - `create_latest_invoice_query` (for the currently open invoice), or
        - `create_invoice_query` (for a previous invoice)

        See https://docs.amberflo.io/reference/get_payments-billing-customer-product-invoice
        """
        return self.client.get(self.path, params=query)


def create_all_invoices_query(
    customer_id,
    product_id=None,
    from_cache=True,
    with_payment_status=True,
):
    """
    customer_id: String.

    product_id: Optional. String.

    from_cache: Optional. Boolean. Defaults to True.

    with_payment_status: Optional. Boolean. Defaults to True.

    See https://docs.amberflo.io/reference/get_payments-billing-customer-product-invoice-all
    """
    validators.require_string("customer_id", customer_id, allow_none=False)
    validators.require_string("product_id", product_id)
    validators.require("from_cache", from_cache, bool, allow_none=False)
    validators.require(
        "with_payment_status", with_payment_status, bool, allow_none=False
    )

    payload = {
        "customerId": customer_id,
        "productId": product_id or DEFAULT_PRODUCT_ID,
        "fromCache": from_cache,
        "withPaymentStatus": with_payment_status,
    }
    return payload


def create_latest_invoice_query(
    customer_id,
    product_id=None,
    from_cache=True,
    with_payment_status=True,
):
    """
    customer_id: String.

    product_id: Optional. String.

    from_cache: Optional. Boolean. Defaults to True.

    with_payment_status: Optional. Boolean. Defaults to True.

    See https://docs.amberflo.io/reference/get_payments-billing-customer-product-invoice
    """

    payload = create_all_invoices_query(
        customer_id,
        product_id=product_id,
        from_cache=from_cache,
        with_payment_status=with_payment_status,
    )
    payload["latest"] = "true"
    return payload


def create_invoice_query(
    customer_id,
    product_plan_id,
    invoice_start_date,
    product_id=None,
    from_cache=True,
    with_payment_status=True,
):
    """
    customer_id: String.

    product_plan_id: String.

    invoice_start_date: Date.

    product_id: Optional. String.

    from_cache: Optional. Boolean. Defaults to True.

    with_payment_status: Optional. Boolean. Defaults to True.

    See https://docs.amberflo.io/reference/get_payments-billing-customer-product-invoice
    """

    payload = create_all_invoices_query(
        customer_id,
        product_id=product_id,
        from_cache=from_cache,
        with_payment_status=with_payment_status,
    )

    validators.require_string("product_plan_id", product_plan_id, allow_none=False)
    validators.require("invoice_start_date", invoice_start_date, date, allow_none=False)

    payload["productPlanId"] = product_plan_id
    payload["year"] = invoice_start_date.year
    payload["month"] = invoice_start_date.month
    payload["day"] = invoice_start_date.day

    return payload
