import time
from metering.usage import UsageClient, AggregationType, TimeGroupingInterval, TimeRange, Take
from metering.usage_payload_factory import UsagePayloadFactory


def call_usage():
    # obtain your Amberflo API Key
    api_key = 'my-api-key'

    # initialize the usage client
    client = UsageClient(api_key)

    # Example: group by customers for a specific meter and customer
    # setup usage query params
    # visit following link for description of payload:
    # https://amberflo.readme.io/reference#usage

    start_time_in_seconds = int(round(time.time())) - (24 * 60 * 60)
    time_range = TimeRange(start_time_in_seconds=start_time_in_seconds)
    take = Take(limit=10, is_ascending=False)
    group_by = ['customerId']
    usage_filter = {'customerId': '1234'}
    message = UsagePayloadFactory.create(
        meter_api_name="my_meter",
        aggregation=AggregationType(AggregationType.SUM),
        time_grouping_interval=TimeGroupingInterval(TimeGroupingInterval.DAY),
        time_range=time_range,
        group_by=group_by,
        usage_filter=usage_filter,
        take=take)

    response = client.get_usage(message)
    print(response)

call_usage()
