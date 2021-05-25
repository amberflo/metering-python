from numbers import Number
from metering.field_validator import FieldValidator
from metering.usage import AggregationType, TimeGroupingInterval, TimeRange, Take


class UsagePayloadFactory(object):
    '''This class is responsible on creating a valid usage payload message.'''

    @staticmethod
    def create(meter_api_name, aggregation, time_grouping_interval, time_range, group_by=None, usage_filter=None, take=None):
        # Validate the input
        FieldValidator.require_string_value('meter_api_name', meter_api_name)
        FieldValidator.require('aggregation', aggregation,
                               AggregationType, allow_none=False)
        FieldValidator.require(
            'time_grouping_interval', time_grouping_interval, TimeGroupingInterval, allow_none=False)

        FieldValidator.require('time_range', time_range,
                               TimeRange, allow_none=False)
        FieldValidator.require(
            'start_time_in_seconds', time_range.start_time_in_seconds, Number, allow_none=False)
        FieldValidator.require(
            'end_time_in_seconds', time_range.end_time_in_seconds, Number, allow_none=True)

        FieldValidator.require('take', take, Take, allow_none=True)
        FieldValidator.require('group_by', group_by, list, allow_none=True)
        FieldValidator.require_string_dictionary('filter', usage_filter)

        message_dictionary = {
            'meterApiName': meter_api_name,
            'aggregation': aggregation.value,
            'timeGroupingInterval': time_grouping_interval.value,
            'timeRange': {
                'startTimeInSeconds': time_range.start_time_in_seconds,                
            }
        }

        if group_by:
            message_dictionary['groupBy'] = group_by

        if time_range.end_time_in_seconds:
             message_dictionary['timeRange']['endTimeInSeconds']= time_range.end_time_in_seconds

        if usage_filter:
            message_dictionary['filter'] = usage_filter
        
        if take:
            FieldValidator.require('limit', take.limit,
                                   Number, allow_none=False)
            FieldValidator.require(
                'is_ascending', take.is_ascending, bool, allow_none=True)
            message_dictionary['take'] = {
                'limit': take.limit,
                'isAscending': take.is_ascending
            }

        return message_dictionary
