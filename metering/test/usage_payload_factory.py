import unittest
import time

from metering.usage_payload_factory import UsagePayloadFactory
from metering.usage import AggregationType, TimeGroupingInterval, TimeRange, Take

# consts
meter_api_name_key = 'meterApiName'
aggregation_key = 'aggregation'
time_grouping_interval_key = 'timeGroupingInterval'
group_by_key = 'groupBy'
time_range_key = 'timeRange'
start_time_in_seconds_key = 'startTimeInSeconds'
end_time_in_seconds_key = 'endTimeInSeconds'
take_key = 'take'
limit_key = 'limit'
is_ascending_key = 'isAscending'
filter_key = 'filter'


class TestUsagePayloadFactory(unittest.TestCase):
    """Test class for UsagePayloadFactory"""

    meter_api_name = "my_meter"
    start_time_in_seconds = int(round(time.time())) - (24 * 60 * 60)
    aggregation = AggregationType(AggregationType.SUM)
    time_grouping_interval = TimeGroupingInterval(TimeGroupingInterval.DAY)
    time_range = TimeRange(start_time_in_seconds=start_time_in_seconds)
    take = Take(limit=10, is_ascending=False)
    group_by = ['customerId']
    usage_filter = {'customerId': '1234'}

    def test_with_required_arguments(self):
        message = UsagePayloadFactory.create(
            meter_api_name=self.meter_api_name,
            aggregation=self.aggregation,
            time_grouping_interval=self.time_grouping_interval,
            time_range=self.time_range,
            group_by=None, usage_filter=None,  take=None)

        self.assertEqual(message[meter_api_name_key], self.meter_api_name)
        self.assertEqual(message[aggregation_key], self.aggregation.value)
        self.assertEqual(message[time_grouping_interval_key],
                         self.time_grouping_interval.value)
        self.assertEqual(
            message[time_range_key][start_time_in_seconds_key], self.time_range.start_time_in_seconds)
        self.assertEqual(
            end_time_in_seconds_key in message[time_range_key], False)
        self.assertEqual(group_by_key in message, False)
        self.assertEqual(filter_key in message, False)
        self.assertEqual(take_key in message, False)

    def test_with_group_by_and_filter_and_take(self):
        message = UsagePayloadFactory.create(
            meter_api_name=self.meter_api_name,
            aggregation=self.aggregation,
            time_grouping_interval=self.time_grouping_interval,
            time_range=self.time_range,
            group_by=self.group_by, usage_filter=self.usage_filter,  take=self.take)

        print(message)

        self.assertEqual(message[meter_api_name_key], self.meter_api_name)
        self.assertEqual(message[aggregation_key], self.aggregation.value)
        self.assertEqual(message[time_grouping_interval_key],
                         self.time_grouping_interval.value)
        self.assertEqual(
            message[time_range_key][start_time_in_seconds_key], self.time_range.start_time_in_seconds)
        self.assertEqual(
            end_time_in_seconds_key in message[time_range_key], False)
        self.assertEqual(message[group_by_key], self.group_by)
        self.assertEqual(message[filter_key], self.usage_filter)
        self.assertEqual(message[take_key][limit_key], self.take.limit)
        self.assertEqual(message[take_key]
                         [is_ascending_key], self.take.is_ascending)

    def test_no_meter_api_name(self):
        with self.assertRaises(AssertionError):
            UsagePayloadFactory.create(meter_api_name=None, aggregation=self.aggregation,
                                       time_grouping_interval=self.time_grouping_interval,
                                       time_range=self.time_range, group_by=None, usage_filter=None,  take=None)

    def test_no_aggregation(self):
        with self.assertRaises(AssertionError):
            UsagePayloadFactory.create(meter_api_name=self.meter_api_name, aggregation=None,
                                       time_grouping_interval=self.time_grouping_interval,
                                       time_range=self.time_range, group_by=None, usage_filter=None,  take=None)

    def test_no_time_grouping_interval(self):
        with self.assertRaises(AssertionError):
            UsagePayloadFactory.create(meter_api_name=self.meter_api_name, aggregation=self.aggregation,
                                       time_grouping_interval=None,
                                       time_range=self.time_range, group_by=None, usage_filter=None,  take=None)

    def test_no_time_range(self):
        with self.assertRaises(AssertionError):
            UsagePayloadFactory.create(meter_api_name=self.meter_api_name, aggregation=self.aggregation,
                                       time_grouping_interval=self.time_grouping_interval,
                                       time_range=None, group_by=None, usage_filter=None,  take=None)


if __name__ == '__main__':
    unittest.main()
