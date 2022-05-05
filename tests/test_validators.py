import unittest

from metering.validators import (
    require,
    require_positive_int,
    require_positive_number,
    require_string,
    require_string_dictionary,
    require_string_list,
    require_string_list_dictionary,
)

name = "name"


class TestValidators(unittest.TestCase):
    def test_require(self):
        # does not raise
        require(name, "foo", str, allow_none=False)

        with self.assertRaises(AssertionError):
            require(name, "foo", int, allow_none=False)

        # does not raise
        require(name, None, str, allow_none=True)

        with self.assertRaises(AssertionError):
            require(name, None, str, allow_none=False)

    def test_require_positive_int(self):
        # does not raise
        require_positive_int(name, 100, allow_none=False)

        with self.assertRaises(AssertionError):
            require_positive_int(name, "100", allow_none=False)

        with self.assertRaises(AssertionError):
            require_positive_int(name, -100, allow_none=False)

        with self.assertRaises(AssertionError):
            require_positive_int(name, -100, allow_none=True)

        # does not raise
        require_positive_int(name, None, allow_none=True)

        with self.assertRaises(AssertionError):
            require_positive_int(name, None, allow_none=False)

    def test_require_positive_number(self):
        # does not raise
        require_positive_number(name, 100.0, allow_none=False)
        require_positive_number(name, 100, allow_none=False)

        with self.assertRaises(AssertionError):
            require_positive_number(name, "100", allow_none=False)

        with self.assertRaises(AssertionError):
            require_positive_number(name, -100, allow_none=False)

        with self.assertRaises(AssertionError):
            require_positive_number(name, -100, allow_none=True)

        # does not raise
        require_positive_number(name, None, allow_none=True)

        with self.assertRaises(AssertionError):
            require_positive_number(name, None, allow_none=False)

    def test_require_string(self):
        # does not raise
        require_string(name, "foo", allow_none=False)

        with self.assertRaises(AssertionError):
            require_string(name, "", allow_none=False)

        with self.assertRaises(AssertionError):
            require_string(name, "   ", allow_none=False)

        with self.assertRaises(AssertionError):
            require_string(name, None, allow_none=False)

        # does not raise
        require_string(name, None, allow_none=True)

        with self.assertRaises(AssertionError):
            require_string(name, "", allow_none=True)

        with self.assertRaises(AssertionError):
            require_string(name, "   ", allow_none=True)

    def test_require_string_list(self):
        # does not raise
        require_string_list(name, ["foo"], allow_none=False)

        # does not raise
        require_string_list(name, None, allow_none=True)

        with self.assertRaises(AssertionError):
            require_string_list(name, None, allow_none=False)

        with self.assertRaises(AssertionError):
            require_string_list(name, ["foo", 100], allow_none=False)

        with self.assertRaises(AssertionError):
            require_string_list(name, ["foo", None], allow_none=True)

    def test_require_string_list_dictionary(self):
        # does not raise
        require_string_list_dictionary(name, {"bar": ["foo"]}, allow_none=False)

        # does not raise
        require_string_list_dictionary(name, None, allow_none=True)

        with self.assertRaises(AssertionError):
            require_string_list_dictionary(name, {1: ["foo"]}, allow_none=False)

        with self.assertRaises(AssertionError):
            require_string_list_dictionary(
                name, {"bar": ["foo", 100]}, allow_none=False
            )

        with self.assertRaises(AssertionError):
            require_string_list_dictionary(
                name, {"bar": ["foo", None]}, allow_none=True
            )

    def test_require_string_dictionary(self):
        # does not raise
        require_string_dictionary(name, {"bar": "foo"}, allow_none=False)

        # does not raise
        require_string_dictionary(name, None, allow_none=True)

        with self.assertRaises(AssertionError):
            require_string_dictionary(name, {1: "foo"}, allow_none=False)

        with self.assertRaises(AssertionError):
            require_string_dictionary(name, {"bar": 100}, allow_none=False)

        with self.assertRaises(AssertionError):
            require_string_dictionary(name, {"bar": None}, allow_none=True)
