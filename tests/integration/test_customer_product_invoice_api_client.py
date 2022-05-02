import os
from datetime import date
import unittest

from metering.session import ApiSession
from metering.customer_product_invoice import (
    CustomerProductInvoiceApiClient,
    create_all_invoices_query,
    create_latest_invoice_query,
    create_invoice_query,
)

API_KEY = os.environ.get("TEST_API_KEY")


@unittest.skipIf(API_KEY is None, "Needs Amberflo's API key")
class TestCustomerProductInvoiceApiClient(unittest.TestCase):
    def setUp(self):
        self.customer_id = ApiSession(API_KEY).get("/customers/")[0]["customerId"]
        self.client = CustomerProductInvoiceApiClient(API_KEY)

    def test_get_all(self):
        message = create_all_invoices_query(
            customer_id=self.customer_id,
        )
        response = self.client.get_all(message)
        self.assertIsInstance(response, list)
        self.assertIn("invoiceKey", response[0])

    def test_get(self):
        message = create_latest_invoice_query(
            customer_id=self.customer_id,
        )
        response = self.client.get(message)
        self.assertIsInstance(response, dict)
        self.assertIn("invoiceKey", response)

        invoice_start_date = date(
            response["invoiceKey"]["year"],
            response["invoiceKey"]["month"],
            response["invoiceKey"]["day"],
        )
        product_plan_id = response["invoiceKey"]["productPlanId"]

        message = create_invoice_query(
            customer_id=self.customer_id,
            invoice_start_date=invoice_start_date,
            product_plan_id=product_plan_id,
        )
        response = self.client.get(message)
        self.assertIsInstance(response, dict)
        self.assertIn("invoiceKey", response)
