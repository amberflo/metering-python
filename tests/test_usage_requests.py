import unittest
import time

from metering.usage import (
    AggregationType,
    Take,
    TimeGroupingInterval,
    TimeRange,
    create_usage_request,
    create_all_usage_request,
)

meter_api_name_key = "meterApiName"
aggregation_key = "aggregation"
time_grouping_interval_key = "timeGroupingInterval"
group_by_key = "groupBy"
time_range_key = "timeRange"
start_time_in_seconds_key = "startTimeInSeconds"
end_time_in_seconds_key = "endTimeInSeconds"
take_key = "take"
limit_key = "limit"
is_ascending_key = "isAscending"
filter_key = "filter"

group_by_customer_id_key = "groupBy"
filter_by_customer_id_key = "customerId"


class TestCreateUsageRequest(unittest.TestCase):

    meter_api_name = "my_meter"
    start_time_in_seconds = int(round(time.time())) - (24 * 60 * 60)
    aggregation = AggregationType.SUM
    time_grouping_interval = TimeGroupingInterval.DAY
    time_range = TimeRange(start_time_in_seconds=start_time_in_seconds)
    take = Take(limit=10, is_ascending=False)
    group_by = ["customerId"]
    usage_filter = {"customerId": ["1234"]}

    def test_with_required_arguments(self):
        message = create_usage_request(
            meter_api_name=self.meter_api_name,
            aggregation=self.aggregation,
            time_grouping_interval=self.time_grouping_interval,
            time_range=self.time_range,
            group_by=None,
            usage_filter=None,
            take=None,
        )

        self.assertEqual(message[meter_api_name_key], self.meter_api_name)
        self.assertEqual(message[aggregation_key], self.aggregation.value)
        self.assertEqual(
            message[time_grouping_interval_key], self.time_grouping_interval.value
        )
        self.assertEqual(
            message[time_range_key][start_time_in_seconds_key],
            self.time_range.start_time_in_seconds,
        )
        self.assertNotIn(end_time_in_seconds_key, message[time_range_key])
        self.assertNotIn(group_by_key, message)
        self.assertNotIn(filter_key, message)
        self.assertNotIn(take_key, message)

    def test_with_group_by_and_filter_and_take(self):
        message = create_usage_request(
            meter_api_name=self.meter_api_name,
            aggregation=self.aggregation,
            time_grouping_interval=self.time_grouping_interval,
            time_range=self.time_range,
            group_by=self.group_by,
            usage_filter=self.usage_filter,
            take=self.take,
        )

        self.assertEqual(message[meter_api_name_key], self.meter_api_name)
        self.assertEqual(message[aggregation_key], self.aggregation.value)
        self.assertEqual(
            message[time_grouping_interval_key], self.time_grouping_interval.value
        )
        self.assertEqual(
            message[time_range_key][start_time_in_seconds_key],
            self.time_range.start_time_in_seconds,
        )
        self.assertNotIn(end_time_in_seconds_key, message[time_range_key])
        self.assertEqual(message[group_by_key], self.group_by)
        self.assertEqual(message[filter_key], self.usage_filter)
        self.assertEqual(message[take_key][limit_key], self.take.limit)
        self.assertEqual(message[take_key][is_ascending_key], self.take.is_ascending)

    def test_no_meter_api_name(self):
        with self.assertRaises(AssertionError):
            create_usage_request(
                meter_api_name=None,
                aggregation=self.aggregation,
                time_grouping_interval=self.time_grouping_interval,
                time_range=self.time_range,
                group_by=None,
                usage_filter=None,
                take=None,
            )

    def test_no_aggregation(self):
        with self.assertRaises(AssertionError):
            create_usage_request(
                meter_api_name=self.meter_api_name,
                aggregation=None,
                time_grouping_interval=self.time_grouping_interval,
                time_range=self.time_range,
                group_by=None,
                usage_filter=None,
                take=None,
            )

    def test_no_time_grouping_interval(self):
        with self.assertRaises(AssertionError):
            create_usage_request(
                meter_api_name=self.meter_api_name,
                aggregation=self.aggregation,
                time_grouping_interval=None,
                time_range=self.time_range,
                group_by=None,
                usage_filter=None,
                take=None,
            )

    def test_no_time_range(self):
        with self.assertRaises(AssertionError):
            create_usage_request(
                meter_api_name=self.meter_api_name,
                aggregation=self.aggregation,
                time_grouping_interval=self.time_grouping_interval,
                time_range=None,
                group_by=None,
                usage_filter=None,
                take=None,
            )


class TestCreateAllUsageRequest(unittest.TestCase):

    start_time_in_seconds = int(round(time.time())) - (24 * 60 * 60)
    time_grouping_interval = TimeGroupingInterval.DAY
    time_range = TimeRange(start_time_in_seconds=start_time_in_seconds)
    customer_id = "1234"

    def test_with_required_arguments(self):
        message = create_all_usage_request(
            time_grouping_interval=self.time_grouping_interval,
            time_range=self.time_range,
        )

        self.assertEqual(
            message[time_grouping_interval_key], self.time_grouping_interval.value
        )
        self.assertEqual(
            message[start_time_in_seconds_key],
            self.time_range.start_time_in_seconds,
        )
        self.assertNotIn(group_by_customer_id_key, message)
        self.assertNotIn(filter_by_customer_id_key, message)

    def test_with_filter_and_group(self):
        message = create_all_usage_request(
            time_grouping_interval=self.time_grouping_interval,
            time_range=self.time_range,
            filter_by_customer_id=self.customer_id,
            group_by_customer_id=True,
        )

        self.assertEqual(
            message[time_grouping_interval_key], self.time_grouping_interval.value
        )
        self.assertEqual(
            message[start_time_in_seconds_key],
            self.time_range.start_time_in_seconds,
        )
        self.assertEqual(message[group_by_customer_id_key], "customerId")
        self.assertEqual(message[filter_by_customer_id_key], self.customer_id)
