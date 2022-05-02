#!/usr/bin/env python3

"""
This sample shows an example of custom usage report. It queries the usage of
"my_meter" per day, for the past two days, for two specific customers, grouping
by customer.

See https://docs.amberflo.io/reference/post_usage
"""

import os
import json
from time import time

from metering.usage import (
    AggregationType,
    Take,
    TimeGroupingInterval,
    TimeRange,
    UsageApiClient,
    create_usage_query,
)


def main():
    # 1. obtain your API key
    api_key = os.environ.get("API_KEY")

    # 2. initialize the usage client
    client = UsageApiClient(api_key)

    # 3. Example report

    # 3.1 report usage since two days ago
    time_range = TimeRange(
        start_time_in_seconds=int(time()) - 60 * 60 * 24 * 2  # two days ago
    )

    # 3.2 limit to the first 10 entries in descending order
    take = Take(limit=10, is_ascending=False)

    # 3.3 group by customer
    group_by = ["customerId"]

    # 3.4 filter for specific customers
    usage_filter = {"customerId": ["1234", "sample-customer-123"]}

    # 4. create usage request
    request = create_usage_query(
        meter_api_name="my_meter",
        aggregation=AggregationType.SUM,
        time_grouping_interval=TimeGroupingInterval.DAY,
        time_range=time_range,
        group_by=group_by,
        usage_filter=usage_filter,
        take=take,
    )

    # 5. get and print your report
    report = client.get(request)
    print(json.dumps(report, indent=4))


if __name__ == "__main__":
    main()
