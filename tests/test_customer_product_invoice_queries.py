import unittest
from datetime import date

from metering.constants import DEFAULT_PRODUCT_ID
from metering.customer_product_invoice import (
    create_all_invoices_query,
    create_latest_invoice_query,
    create_invoice_query,
)


class TestAllInvoicesQuery(unittest.TestCase):

    customer_id = "foo"
    product_id = "bar"

    def test_with_required_arguments(self):
        message = create_all_invoices_query(
            customer_id=self.customer_id,
        )

        self.assertEqual(message["customerId"], self.customer_id)
        self.assertEqual(message["productId"], DEFAULT_PRODUCT_ID)
        self.assertIn("fromCache", message)
        self.assertIn("withPaymentStatus", message)

    def test_with_all_arguments(self):
        message = create_all_invoices_query(
            customer_id=self.customer_id,
            product_id=self.product_id,
            from_cache=False,
            with_payment_status=False,
        )

        self.assertEqual(message["customerId"], self.customer_id)
        self.assertEqual(message["productId"], self.product_id)
        self.assertFalse(message["fromCache"])
        self.assertFalse(message["withPaymentStatus"])


class TestLatestInvoiceQuery(unittest.TestCase):

    customer_id = "foo"
    product_id = "bar"

    def test_with_required_arguments(self):
        message = create_latest_invoice_query(
            customer_id=self.customer_id,
        )

        self.assertEqual(message["customerId"], self.customer_id)
        self.assertEqual(message["productId"], DEFAULT_PRODUCT_ID)
        self.assertIn("fromCache", message)
        self.assertIn("withPaymentStatus", message)
        self.assertEqual(message["latest"], "true")

    def test_with_all_arguments(self):
        message = create_latest_invoice_query(
            customer_id=self.customer_id,
            product_id=self.product_id,
            from_cache=False,
            with_payment_status=False,
        )

        self.assertEqual(message["customerId"], self.customer_id)
        self.assertEqual(message["productId"], self.product_id)
        self.assertFalse(message["fromCache"])
        self.assertFalse(message["withPaymentStatus"])
        self.assertEqual(message["latest"], "true")


class TestInvoiceQuery(unittest.TestCase):

    customer_id = "foo"
    product_id = "bar"
    product_plan_id = "bim"
    year = 2022
    month = 5
    day = 20
    invoice_start_date = date(year, month, day)

    def test_with_required_arguments(self):
        message = create_invoice_query(
            customer_id=self.customer_id,
            product_plan_id=self.product_plan_id,
            invoice_start_date=self.invoice_start_date,
        )

        self.assertEqual(message["customerId"], self.customer_id)
        self.assertEqual(message["productId"], DEFAULT_PRODUCT_ID)
        self.assertIn("fromCache", message)
        self.assertIn("withPaymentStatus", message)
        self.assertNotIn("latest", message)
        self.assertEqual(message["productPlanId"], self.product_plan_id)
        self.assertEqual(message["year"], self.year)
        self.assertEqual(message["month"], self.month)
        self.assertEqual(message["day"], self.day)

    def test_with_all_arguments(self):
        message = create_invoice_query(
            customer_id=self.customer_id,
            product_plan_id=self.product_plan_id,
            invoice_start_date=self.invoice_start_date,
            product_id=self.product_id,
            from_cache=False,
            with_payment_status=False,
        )

        self.assertEqual(message["customerId"], self.customer_id)
        self.assertEqual(message["productId"], self.product_id)
        self.assertFalse(message["fromCache"])
        self.assertFalse(message["withPaymentStatus"])
        self.assertNotIn("latest", message)
        self.assertEqual(message["productPlanId"], self.product_plan_id)
        self.assertEqual(message["year"], self.year)
        self.assertEqual(message["month"], self.month)
        self.assertEqual(message["day"], self.day)
