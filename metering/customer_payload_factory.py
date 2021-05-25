from metering.field_validator import FieldValidator


class CustomerPayloadFactory(object):
    '''This class is responsible on creating a valid customer payload message.'''

    @staticmethod
    def create(customer_id, customer_name, traits=None):
        '''
        Params:
        1. customer_id - Required. String.
        2. customer_name - Required. String.
        3. traits - Optional. Dictionary of String to String. 
            It can be used to integrate with other systems and filter usage data
        '''

        # Validate the input
        FieldValidator.require_string_value('customer_id', customer_id)
        FieldValidator.require_string_value('customer_name', customer_name)
        FieldValidator.require_string_dictionary('traits', traits)

        message_dictionary = {
            'customerId': customer_id,
            'customerName': customer_name
        }

        if traits:
            message_dictionary['traits'] = traits

        return message_dictionary
