import unittest
import time

from metering.meter_message_factory import MeterFactory
from uuid import uuid4

# consts
meter_name_key = 'meter_name'
meter_value_key = 'meter_value'
timestamp_key = 'time'
customer_id_key = 'tenant_id'
customer_name_key = 'tenant'
unique_id_key = 'unique_id'
dimensions_key = 'dimensions'

class TestMeterFactory(unittest.TestCase):
    """Test class for MeterFactory"""

    meter_name = "my meter"
    meter_float_value = 1.2
    customer_id = "123"
    customer_name = "moishe oofnik" # https://muppet.fandom.com/wiki/Moishe_Oofnik
    unique_id = uuid4()
    timestamp = int(round(time.time() * 1000))

    def test_no_meter_name(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_name=None, meter_value=self.meter_float_value,
            utc_time_millis=self.timestamp, customer_id=None, customer_name=None)

    def test_no_meter_value(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_name=self.meter_name, meter_value=None,
            utc_time_millis=self.timestamp, customer_id=None, customer_name=None)

    def test_empty_meter_name(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_name='', meter_value=self.meter_float_value,
            utc_time_millis=self.timestamp, customer_id=None, customer_name=None)

    def test_empty_meter_value(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_name=self.meter_name, meter_value='',
            utc_time_millis=self.timestamp, customer_id=None, customer_name=None)

    def test_customer_id_is_an_int(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_name=self.meter_name, meter_value=self.meter_float_value,
            utc_time_millis=self.timestamp, customer_id = 3, customer_name=None)

    def test_unique_id_is_an_int(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_name=self.meter_name, meter_value=self.meter_float_value,
            utc_time_millis=self.timestamp, unique_id = 3, customer_id=None, customer_name=None)

    def test_unique_id_is_an_string(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_name=self.meter_name, meter_value=self.meter_float_value,
            utc_time_millis=self.timestamp, unique_id = "3", customer_id=None, customer_name=None)

    def test_timestamp_is_an_string(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_name=self.meter_name, meter_value=self.meter_float_value,
            utc_time_millis = "3", customer_id=None, customer_name=None)

    def test_with_meter_name_and_value_only(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_name=self.meter_name, meter_value=self.meter_float_value,
            utc_time_millis=None, customer_id=None, customer_name=None)

    def test_with_meter_name_value_and_time_only(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_name=self.meter_name,
            meter_value=self.meter_float_value, utc_time_millis=self.timestamp, 
            customer_id=None, customer_name=None)

    def test_with_meter_name_value_time_and_customer_id_only(self):
        with self.assertRaises(AssertionError):
            MeterFactory.create(meter_name=self.meter_name,
            meter_value=self.meter_float_value, utc_time_millis=self.timestamp, 
            customer_id=self.customer_id, customer_name=None)

    def test_with_meter_name_value_time_and_customer_id_and_name_only(self):
        message = MeterFactory.create(meter_name=self.meter_name,
        meter_value=self.meter_float_value, utc_time_millis=self.timestamp,
        customer_id=self.customer_id, customer_name=self.customer_name)

        self.assertEqual(message[meter_name_key], self.meter_name)
        self.assertEqual(message[meter_value_key], self.meter_float_value)
        self.assertEqual(message[customer_id_key], self.customer_id)
        self.assertEqual(message[customer_name_key], self.customer_name)
        self.assertIsNotNone(message[unique_id_key])
        self.assertEqual(message[timestamp_key], self.timestamp)

    def test_with_unique_id(self):
        message = MeterFactory.create(meter_name=self.meter_name,
        meter_value=self.meter_float_value, utc_time_millis=self.timestamp,
        customer_id=self.customer_id, customer_name=self.customer_name,
        unique_id=self.unique_id)

        self.assertEqual(message[meter_name_key], self.meter_name)
        self.assertEqual(message[meter_value_key], self.meter_float_value)
        self.assertEqual(message[customer_id_key], self.customer_id)
        self.assertEqual(message[customer_name_key], self.customer_name)
        self.assertEqual(message[unique_id_key], str(self.unique_id))
        self.assertEqual(message[timestamp_key], self.timestamp)

    def test_with_customer_id_and_name(self):
        message = MeterFactory.create(meter_name=self.meter_name,
        meter_value=self.meter_float_value, utc_time_millis=self.timestamp,
        customer_id=self.customer_id, customer_name=self.customer_name)

        self.assertEqual(message[meter_name_key], self.meter_name)
        self.assertEqual(message[meter_value_key], self.meter_float_value)
        self.assertEqual(message[customer_id_key], self.customer_id)
        self.assertIsNotNone(message[unique_id_key])
        self.assertEqual(message[timestamp_key], self.timestamp)
        self.assertEqual(message[customer_name_key], self.customer_name)

    def test_with_dimensions(self):
        dimensions = {"key1": "value"}
        message = MeterFactory.create(meter_name=self.meter_name,
        meter_value=self.meter_float_value, utc_time_millis=self.timestamp, 
        customer_id=self.customer_id, customer_name=self.customer_name,
        dimensions=dimensions)

        self.assertEqual(message[meter_name_key], self.meter_name)
        self.assertEqual(message[meter_value_key], self.meter_float_value)
        self.assertIsNotNone(message[unique_id_key])
        self.assertEqual(message[timestamp_key], self.timestamp)
        self.assertEqual(message[customer_id_key], self.customer_id)
        self.assertEqual(message[customer_name_key], self.customer_name)
        self.assertEqual(message[dimensions_key], dimensions)

if __name__ == '__main__':
    unittest.main()
