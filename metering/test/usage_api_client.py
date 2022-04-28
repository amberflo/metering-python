import os
import unittest
import time
from metering.usage import (
    AggregationType,
    Take,
    TimeGroupingInterval,
    TimeRange,
    UsageApiClient,
    create_usage_payload,
)

API_KEY = os.environ["TEST_API_KEY"]

metadata_key = "metadata"
seconds_since_epoch_intervals_key = "secondsSinceEpochIntervals"
client_meters_key = "clientMeters"


class TestUsageApiClient(unittest.TestCase):
    meter_api_name = "my_meter"
    start_time_in_seconds = int(round(time.time())) - (24 * 60 * 60)
    aggregation = AggregationType(AggregationType.SUM)
    time_grouping_interval = TimeGroupingInterval(TimeGroupingInterval.DAY)
    time_range = TimeRange(start_time_in_seconds=start_time_in_seconds)
    take = Take(limit=10, is_ascending=False)
    group_by = ["customerId"]
    usage_filter = {"customerId": ["1234"]}

    def setUp(self):
        self.client = UsageApiClient(API_KEY)

    def test_valid_usage_query(self):
        message = create_usage_payload(
            meter_api_name=self.meter_api_name,
            aggregation=self.aggregation,
            time_grouping_interval=self.time_grouping_interval,
            time_range=self.time_range,
            group_by=None,
            usage_filter=None,
            take=None,
        )
        response = self.client.get_usage(message)
        self.assertEqual(metadata_key in response, True)
        self.assertEqual(seconds_since_epoch_intervals_key in response, True)
        self.assertEqual(client_meters_key in response, True)

    def test_with_filter_and_group_and_take(self):
        message = create_usage_payload(
            meter_api_name=self.meter_api_name,
            aggregation=self.aggregation,
            time_grouping_interval=self.time_grouping_interval,
            time_range=self.time_range,
            group_by=self.group_by,
            usage_filter=self.usage_filter,
            take=self.take,
        )
        response = self.client.get_usage(message)
        self.assertEqual(metadata_key in response, True)
        self.assertEqual(seconds_since_epoch_intervals_key in response, True)
        self.assertEqual(client_meters_key in response, True)
