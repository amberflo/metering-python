import unittest
import time
from metering.usage import UsageClient, AggregationType, TimeGroupingInterval, TimeRange, Take
from metering.usage_payload_factory import UsagePayloadFactory

metadata_key = 'metadata'
seconds_since_epoch_intervals_key = 'secondsSinceEpochIntervals'
client_meters_key = 'clientMeters'
key = 'e9c6a4fc-e275-4eda-b2f8-353ef196ddb7'


class TestUsage(unittest.TestCase):
    meter_api_name = "my_meter"
    start_time_in_seconds = int(round(time.time())) - (24 * 60 * 60)
    aggregation = AggregationType(AggregationType.SUM)
    time_grouping_interval = TimeGroupingInterval(TimeGroupingInterval.DAY)
    time_range = TimeRange(start_time_in_seconds=start_time_in_seconds)
    take = Take(limit=10, is_ascending=False)
    group_by = ['customerId']
    usage_filter = {'customerId': '1234'}

    def test_valid_usage_query(self):
        message = UsagePayloadFactory.create(
            meter_api_name=self.meter_api_name,
            aggregation=self.aggregation,
            time_grouping_interval=self.time_grouping_interval,
            time_range=self.time_range,
            group_by=None, usage_filter=None,  take=None)
        client = UsageClient(key)
        response = client.get_usage(message)
        print(response)
        self.assertEqual(metadata_key in response, True)
        self.assertEqual(seconds_since_epoch_intervals_key in response, True)
        self.assertEqual(client_meters_key in response, True)

    def test_with_filter_and_group_and_take(self):
        message = UsagePayloadFactory.create(
            meter_api_name=self.meter_api_name,
            aggregation=self.aggregation,
            time_grouping_interval=self.time_grouping_interval,
            time_range=self.time_range,
            group_by=self.group_by, usage_filter=self.usage_filter,  take=self.take)
        client = UsageClient(key)
        response = client.get_usage(message)
        print(response)
        self.assertEqual(metadata_key in response, True)
        self.assertEqual(seconds_since_epoch_intervals_key in response, True)
        self.assertEqual(client_meters_key in response, True)


if __name__ == '__main__':
    unittest.main()
