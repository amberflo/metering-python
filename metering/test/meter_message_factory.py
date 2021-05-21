import unittest
import time

from metering.meter_message_factory import MeterFactory
from uuid import uuid4

# consts
meter_api_name_key = 'meterApiName'
meter_value_key = 'meterValue'
timestamp_key = 'meterTimeInMillis'
customer_id_key = 'customerId'
unique_id_key = 'uniqueId'
dimensions_key = 'dimensions'

class TestMeterFactory(unittest.TestCase):
    """Test class for MeterFactory"""

    meter_api_name = "my meter"
    meter_float_value = 1.2
    customer_id = "123"
    unique_id = uuid4()
    timestamp = int(round(time.time() * 1000))

    def test_no_meter_name(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_api_name=None, meter_value=self.meter_float_value,
            meter_time_in_millis=self.timestamp, customer_id=None)

    def test_no_meter_value(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_api_name=self.meter_api_name, meter_value=None,
            meter_time_in_millis=self.timestamp, customer_id=None)

    def test_empty_meter_name(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_api_name='', meter_value=self.meter_float_value,
            meter_time_in_millis=self.timestamp, customer_id=None)

    def test_empty_meter_value(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_api_name=self.meter_api_name, meter_value='',
            meter_time_in_millis=self.timestamp, customer_id=None)

    def test_customer_id_is_an_int(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_api_name=self.meter_api_name, meter_value=self.meter_float_value,
            meter_time_in_millis=self.timestamp, customer_id = 3)

    def test_unique_id_is_an_int(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_api_name=self.meter_api_name, meter_value=self.meter_float_value,
            meter_time_in_millis=self.timestamp, unique_id = 3, customer_id=None)

    def test_unique_id_is_an_string(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_api_name=self.meter_api_name, meter_value=self.meter_float_value,
            meter_time_in_millis=self.timestamp, unique_id = "3", customer_id=None)

    def test_timestamp_is_an_string(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_api_name=self.meter_api_name, meter_value=self.meter_float_value,
            meter_time_in_millis = "3", customer_id=None)

    def test_with_meter_name_and_value_only(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_api_name=self.meter_api_name, meter_value=self.meter_float_value,
            meter_time_in_millis=None, customer_id=None)

    def test_with_meter_name_value_and_time_only(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_api_name=self.meter_api_name,
            meter_value=self.meter_float_value, meter_time_in_millis=self.timestamp, 
            customer_id=None)

    def test_with_meter_name_value_time_and_customer_id_and_name_only(self):
        message = MeterFactory.create(meter_api_name=self.meter_api_name,
        meter_value=self.meter_float_value, meter_time_in_millis=self.timestamp,
        customer_id=self.customer_id)

        self.assertEqual(message[meter_api_name_key], self.meter_api_name)
        self.assertEqual(message[meter_value_key], self.meter_float_value)
        self.assertEqual(message[customer_id_key], self.customer_id)
        self.assertIsNotNone(message[unique_id_key])
        self.assertEqual(message[timestamp_key], self.timestamp)

    def test_with_unique_id(self):
        message = MeterFactory.create(meter_api_name=self.meter_api_name,
        meter_value=self.meter_float_value, meter_time_in_millis=self.timestamp,
        customer_id=self.customer_id, 
        unique_id=self.unique_id)

        self.assertEqual(message[meter_api_name_key], self.meter_api_name)
        self.assertEqual(message[meter_value_key], self.meter_float_value)
        self.assertEqual(message[customer_id_key], self.customer_id)
        self.assertEqual(message[unique_id_key], str(self.unique_id))
        self.assertEqual(message[timestamp_key], self.timestamp)

    def test_with_dimensions(self):
        dimensions = {"key1": "value"}
        message = MeterFactory.create(meter_api_name=self.meter_api_name,
        meter_value=self.meter_float_value, meter_time_in_millis=self.timestamp, 
        customer_id=self.customer_id, 
        dimensions=dimensions)

        self.assertEqual(message[meter_api_name_key], self.meter_api_name)
        self.assertEqual(message[meter_value_key], self.meter_float_value)
        self.assertIsNotNone(message[unique_id_key])
        self.assertEqual(message[timestamp_key], self.timestamp)
        self.assertEqual(message[customer_id_key], self.customer_id)
        self.assertEqual(message[dimensions_key], dimensions)

if __name__ == '__main__':
    unittest.main()
