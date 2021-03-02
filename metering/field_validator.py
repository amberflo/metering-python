class FieldValidator(object):
    '''This class contains logic to help you validate the fields type and content at run time'''

    @staticmethod
    def require_string_dictionary(name, field, allow_none=True):
        '''Verifies that a given field is a dict<String, String>'''

        FieldValidator.require(name, field, dict, allow_none)

        # If we reached here and the field is none we can return.
        if field is None:
            return

        key_name = name + ".key"
        value_name = name + ".value"
        for key, value in field.items():
            FieldValidator.require_string_value(key_name, key)
            FieldValidator.require_string_value(value_name, value)

    @staticmethod
    def require_string_value(name, field):
        '''Verifies that a given field is string which contains a non whitespace value'''

        FieldValidator.require(name, field, str, allow_none = False)

        if FieldValidator.__is_blank(field):
            raise AssertionError('String must have a none whitespace value')


    @staticmethod
    def require(name, field, data_type, allow_none=True):
        '''Verifies that a given field is of the provided data_type (or a sub class of it).'''

        if field is None:
            if allow_none:
                return None

            msg = '{0} must have a value'.format(name)
            raise AssertionError(msg)

        """Require that the named `field` has the right `data_type`"""
        if not isinstance(field, data_type):
            msg = '{0} must have {1}, got: {2}'.format(name, data_type, field)
            raise AssertionError(msg)


    @staticmethod
    def __is_blank(string_value):
        return not (string_value and string_value.strip())
