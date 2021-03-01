import unittest
import time

from numbers import Number
from uuid import uuid1, UUID

from metering.field_validator import FieldValidator

var_name = 'var'

class TestFieldValidator(unittest.TestCase):
    """Test class for FieldValidator"""

    def test_require_no_value_int_type_none_is_allowed(self):
        #No exception
        FieldValidator.require(var_name, None, int)

    def test_require_no_value_int_type_none_is_not_allowed(self):
        with self.assertRaises(AssertionError):
            FieldValidator.require(var_name, None, int, allow_none = False)

    def test_require_integer_value_int_type(self):
        #No exception
        FieldValidator.require(var_name, 3, int)

    def test_require_double_value_int_type(self):
        with self.assertRaises(AssertionError):
            FieldValidator.require(var_name, 3.5, int)

    def test_require_double_value_double_type(self):
        #No exception
        FieldValidator.require(var_name, 3.5, float)

    def test_require_number_value_number_type(self):
        #No exception
        FieldValidator.require(var_name, 3.5, Number)
        FieldValidator.require(var_name, 3, Number)
        FieldValidator.require(var_name, 35e3, Number)
        FieldValidator.require(var_name, 1j, Number)

    def test_require_string_value_number_type(self):
        with self.assertRaises(AssertionError):
            FieldValidator.require(var_name, "3.5", Number)

    def test_require_float_value_string_type(self):
        with self.assertRaises(AssertionError):
            FieldValidator.require(var_name, 3.5, str)

    def test_require_time_value_number_type(self):
        #No exception
        FieldValidator.require(var_name, time.time(), Number)

    def test_require_time_value_int_type(self):
        #No exception
        FieldValidator.require(var_name, uuid1(), UUID)

    def test_require_string_value_no_value(self):
        with self.assertRaises(AssertionError):
            FieldValidator.require_string_value(var_name, None)

    def test_require_string_value_with_empty_string_value(self):
        with self.assertRaises(AssertionError):
            FieldValidator.require_string_value(var_name, "")

    def test_require_string_value_with_whitespace_string_value(self):
        with self.assertRaises(AssertionError):
            FieldValidator.require_string_value(var_name, "      ")

    def test_require_string_value_with_string_value(self):
        #No exception
        FieldValidator.require_string_value(var_name, "abc")

    def test_require_string_dictionary_no_value(self):
        #No exception
        FieldValidator.require_string_dictionary(var_name, None)

    def test_require_string_dictionary_valid_map_value(self):
        #No exception
        FieldValidator.require_string_dictionary(var_name, {"abc": "value"})

    def test_require_string_dictionary_map_value_is_a_number(self):
        with self.assertRaises(AssertionError):
            FieldValidator.require_string_dictionary(var_name, {"abc": 3})

    def test_require_string_dictionary_map_key_is_a_number(self):
        with self.assertRaises(AssertionError):
            FieldValidator.require_string_dictionary(var_name, {55: "value"})


if __name__ == '__main__':
    unittest.main()
