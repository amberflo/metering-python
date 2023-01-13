"""
This module contains functions that perform basic parameter validatorss.
"""


def require_string_dictionary(name, value, allow_none=True):
    """
    Verifies that a given value is a dict[str,str].
    """
    require(name, value, dict, allow_none)

    if value is None:
        return

    key_name = name + ".<key>"
    for k, v in value.items():
        require_string(key_name, k, allow_none=False)
        require_string(name + "." + k, v, allow_none=False)


def require_string_list_dictionary(name, value, allow_none=True):
    """
    Verifies that a given value is a dict[str,list[str]].
    """
    require(name, value, dict, allow_none)

    if value is None:
        return

    key_name = name + ".<key>"
    for k, v in value.items():
        require_string(key_name, k, allow_none=False)
        require_string_list(name + "." + k, v, allow_none=False)


def require_string_list(name, value, allow_none=True):
    """
    Verifies that a given value is a list[str].
    """
    require(name, value, list, allow_none)

    if value is None:
        return

    assert value, "{0!r} may not be an empty list".format(name)

    for i, v in enumerate(value):
        require_string("{}.{}".format(name, i), v, allow_none=False)


def require_string(name, value, allow_none=True):
    """
    Verifies that a given value is a non-empty, non-whitespace string.
    """
    require(name, value, str, allow_none)

    if value is None:
        return

    assert value and value.strip(), "{0!r} may not be an empty string".format(name)


def require_positive_int(name, value, allow_none=True):
    """
    Verifies that a given value is a positive integer.
    """
    require(name, value, int, allow_none)

    if value is None:
        return

    assert value > 0, "{0!r} must be 1 or greater".format(name)


def require_positive_number(name, value, allow_none=True):
    """
    Verifies that a given value is a positive number (integer or float).
    """
    require(name, value, (int, float), allow_none)

    if value is None:
        return

    assert value > 0, "{0!r} must be greater than 0".format(name)


def require(name, value, data_type, allow_none=True):
    """
    Verifies that a given value is of the provided data_type (or a sub class of it).
    """

    assert value is not None or allow_none, "{0!r} may not be None".format(name)

    if value is None:
        return

    assert isinstance(value, data_type), "{0!r} must be {1}, but is: {2}".format(
        name,
        data_type,
        value.__class__,
    )
