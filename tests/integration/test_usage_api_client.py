import os
import unittest
import time
from metering.usage import (
    AggregationType,
    Take,
    TimeGroupingInterval,
    TimeRange,
    UsageApiClient,
    create_usage_request,
    create_all_usage_request,
)

API_KEY = os.environ.get("TEST_API_KEY")

metadata_key = "metadata"
seconds_since_epoch_intervals_key = "secondsSinceEpochIntervals"
client_meters_key = "clientMeters"


@unittest.skipIf(API_KEY is None, "Needs Amberflo's API key")
class TestUsageApiClient(unittest.TestCase):
    meter_api_name = "my_meter"
    start_time_in_seconds = int(round(time.time())) - (24 * 60 * 60)
    aggregation = AggregationType(AggregationType.SUM)
    time_grouping_interval = TimeGroupingInterval(TimeGroupingInterval.DAY)
    time_range = TimeRange(start_time_in_seconds=start_time_in_seconds)
    take = Take(limit=10, is_ascending=False)
    group_by = ["customerId"]
    customer_id = "1234"
    usage_filter = {"customerId": [customer_id]}

    def setUp(self):
        self.client = UsageApiClient(API_KEY)

    def test_usage(self):
        message = create_usage_request(
            meter_api_name=self.meter_api_name,
            aggregation=self.aggregation,
            time_grouping_interval=self.time_grouping_interval,
            time_range=self.time_range,
        )
        response = self.client.get(message)
        self.assertIsInstance(response, dict)
        self.assertIn(metadata_key, response)
        self.assertIn(seconds_since_epoch_intervals_key, response)
        self.assertIn(client_meters_key, response)

    def test_usage_with_filter_and_group_and_take(self):
        message = create_usage_request(
            meter_api_name=self.meter_api_name,
            aggregation=self.aggregation,
            time_grouping_interval=self.time_grouping_interval,
            time_range=self.time_range,
            group_by=self.group_by,
            usage_filter=self.usage_filter,
            take=self.take,
        )
        response = self.client.get(message)
        self.assertIn(metadata_key, response)
        self.assertIn(seconds_since_epoch_intervals_key, response)
        self.assertIn(client_meters_key, response)

    def test_batch_usage(self):
        message = [
            create_usage_request(
                meter_api_name=self.meter_api_name,
                aggregation=self.aggregation,
                time_grouping_interval=self.time_grouping_interval,
                time_range=self.time_range,
            ),
            create_usage_request(
                meter_api_name="my_other_meter",
                aggregation=self.aggregation,
                time_grouping_interval=self.time_grouping_interval,
                time_range=self.time_range,
            ),
        ]
        response = self.client.get(message)
        self.assertIsInstance(response, list)
        for report in response:
            self.assertIn(metadata_key, report)
            self.assertIn(seconds_since_epoch_intervals_key, report)
            self.assertIn(client_meters_key, report)

    def test_all_usage(self):
        message = create_all_usage_request(
            time_grouping_interval=self.time_grouping_interval,
            time_range=self.time_range,
        )
        response = self.client.get_all(message)
        self.assertIsInstance(response, list)
        for report in response:
            self.assertIn(metadata_key, report)
            self.assertIn(seconds_since_epoch_intervals_key, report)
            self.assertIn(client_meters_key, report)

    def test_all_usage_with_group_and_filter(self):
        message = create_all_usage_request(
            time_grouping_interval=self.time_grouping_interval,
            time_range=self.time_range,
            filter_by_customer_id=self.customer_id,
            group_by_customer_id=True,
        )
        response = self.client.get_all(message)
        self.assertIsInstance(response, list)
        for report in response:
            self.assertIn(metadata_key, report)
            self.assertIn(seconds_since_epoch_intervals_key, report)
            self.assertIn(client_meters_key, report)
