import unittest
import time
from uuid import uuid4

from metering.ingest import create_meter_payload

meter_api_name_key = "meterApiName"
meter_value_key = "meterValue"
timestamp_key = "meterTimeInMillis"
customer_id_key = "customerId"
unique_id_key = "uniqueId"
dimensions_key = "dimensions"


class TestMeterPayloadFactory(unittest.TestCase):
    """Test class for MeterFactory"""

    meter_api_name = "my meter"
    meter_float_value = 1.2
    customer_id = "123"
    unique_id = str(uuid4())
    timestamp = int(round(time.time() * 1000))

    def test_no_meter_name(self):
        with self.assertRaises(AssertionError):
            create_meter_payload(
                meter_api_name=None,
                meter_value=self.meter_float_value,
                meter_time_in_millis=self.timestamp,
                customer_id=self.customer_id,
            )

    def test_no_meter_value(self):
        with self.assertRaises(AssertionError):
            create_meter_payload(
                meter_api_name=self.meter_api_name,
                meter_value=None,
                meter_time_in_millis=self.timestamp,
                customer_id=self.customer_id,
            )

    def test_empty_meter_name(self):
        with self.assertRaises(AssertionError):
            create_meter_payload(
                meter_api_name="",
                meter_value=self.meter_float_value,
                meter_time_in_millis=self.timestamp,
                customer_id=self.customer_id,
            )

    def test_empty_meter_value(self):
        with self.assertRaises(AssertionError):
            create_meter_payload(
                meter_api_name=self.meter_api_name,
                meter_value="",
                meter_time_in_millis=self.timestamp,
                customer_id=self.customer_id,
            )

    def test_customer_id_is_an_int(self):
        with self.assertRaises(AssertionError):
            create_meter_payload(
                meter_api_name=self.meter_api_name,
                meter_value=self.meter_float_value,
                meter_time_in_millis=self.timestamp,
                customer_id=3,
            )

    def test_customer_id_is_none(self):
        with self.assertRaises(AssertionError):
            create_meter_payload(
                meter_api_name=self.meter_api_name,
                meter_value=self.meter_float_value,
                meter_time_in_millis=self.timestamp,
                customer_id=None,
            )

    def test_unique_id_is_an_int(self):
        with self.assertRaises(AssertionError):
            create_meter_payload(
                meter_api_name=self.meter_api_name,
                meter_value=self.meter_float_value,
                meter_time_in_millis=self.timestamp,
                customer_id=self.customer_id,
                unique_id=3,
            )

    def test_timestamp_is_an_string(self):
        with self.assertRaises(AssertionError):
            create_meter_payload(
                meter_api_name=self.meter_api_name,
                meter_value=self.meter_float_value,
                meter_time_in_millis="3",
                customer_id=self.customer_id,
            )

    def test_timestamp_is_none(self):
        with self.assertRaises(AssertionError):
            create_meter_payload(
                meter_api_name=self.meter_api_name,
                meter_value=self.meter_float_value,
                meter_time_in_millis=None,
                customer_id=self.customer_id,
            )

    def test_with_meter_name_value_time_and_customer_id_and_name_only(self):
        message = create_meter_payload(
            meter_api_name=self.meter_api_name,
            meter_value=self.meter_float_value,
            meter_time_in_millis=self.timestamp,
            customer_id=self.customer_id,
        )

        self.assertEqual(message[meter_api_name_key], self.meter_api_name)
        self.assertEqual(message[meter_value_key], self.meter_float_value)
        self.assertEqual(message[customer_id_key], self.customer_id)
        self.assertIsNotNone(message[unique_id_key])
        self.assertEqual(message[timestamp_key], self.timestamp)

    def test_with_unique_id(self):
        message = create_meter_payload(
            meter_api_name=self.meter_api_name,
            meter_value=self.meter_float_value,
            meter_time_in_millis=self.timestamp,
            customer_id=self.customer_id,
            unique_id=self.unique_id,
        )

        self.assertEqual(message[meter_api_name_key], self.meter_api_name)
        self.assertEqual(message[meter_value_key], self.meter_float_value)
        self.assertEqual(message[customer_id_key], self.customer_id)
        self.assertEqual(message[unique_id_key], self.unique_id)
        self.assertEqual(message[timestamp_key], self.timestamp)

    def test_with_dimensions(self):
        dimensions = {"key1": "value"}
        message = create_meter_payload(
            meter_api_name=self.meter_api_name,
            meter_value=self.meter_float_value,
            meter_time_in_millis=self.timestamp,
            customer_id=self.customer_id,
            dimensions=dimensions,
        )

        self.assertEqual(message[meter_api_name_key], self.meter_api_name)
        self.assertEqual(message[meter_value_key], self.meter_float_value)
        self.assertIsNotNone(message[unique_id_key])
        self.assertEqual(message[timestamp_key], self.timestamp)
        self.assertEqual(message[customer_id_key], self.customer_id)
        self.assertEqual(message[dimensions_key], dimensions)
