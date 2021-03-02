from uuid import uuid1, UUID
from numbers import Number
from metering.field_validator import FieldValidator

class MeterFactory(object):
    '''This class is responsible on creating a valid meter message.'''


    @staticmethod
    def create(meter_name, meter_value, utc_time_millis, customer_id=None, customer_name=None, 
    dimensions=None, unique_id=None):
        '''
        Params:
        1. meter_name - String. Required (also can't be a whitespace)
        2. meter_value - Number (double/long). Required.
        3. utc_time_millis - Optional Int (default to the current time when we call this method).
            This argument decribes the meter event. Pay attention for this argument as two meters
            (with the same name) that are sent to Amberflo at the exact same time (and have the
            same unique id) will be deduped by the server.
        4. customer_id - Optional. String.
        5. customer_name - Optional. String
        6. dimensions - Optional. Dictionary of String to String. Here you can specify more
            partition properies which which can help you analize your data.
        7. Unique_id - Optional UUID (defualt to a random uuid). This parameter can help the
            server tell if the meter is indeed a dup or not in case there are two meters with
            the same name that are sent to the server at the same time.
        '''

        # Validate the input
        FieldValidator.require('customer_id', customer_id ,str)
        FieldValidator.require('customer_name', customer_name ,str)
        FieldValidator.require_string_value('meter_name', meter_name)
        FieldValidator.require('meter_value', meter_value, Number, allow_none=False)
        FieldValidator.require_string_dictionary('dimensions', dimensions)
        FieldValidator.require('utc_time_nanos', utc_time_millis, Number, allow_none=False)
        FieldValidator.require('unique_id', unique_id, UUID)

        # Create the message
        # We use uuid1 as it also take into account the mac address in order to produce
        # a random value.
        # https://stackoverflow.com/questions/1785503/when-should-i-use-uuid-uuid1-vs-uuid-uuid4-in-python
        processed_unique = str(unique_id or uuid1())
        processed_timestamp = str(utc_time_millis)

        message_dictionary = {
            'unique_id': processed_unique,
            'meter_name': meter_name,
            'meter_value': meter_value,
            'time': processed_timestamp
        }

        MeterFactory.__add_string_if_populated('tenant_id', customer_id, message_dictionary)
        MeterFactory.__add_string_if_populated('tenant_name', customer_name, message_dictionary)

        if dimensions is not None and dimensions:
            dimensions_list = []
            for key, value in dimensions.items():
                dimensions_list.append({'Name': key, 'Value': value})
            message_dictionary['dimensions'] = dimensions_list

        return message_dictionary

    @staticmethod
    def __add_string_if_populated(key_name, value, message_dictionary):
        if (value is not None and value):
            message_dictionary[key_name] = value
