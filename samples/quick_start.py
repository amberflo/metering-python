#!/usr/bin/env python3

"""
This sample shows how to ingest meter records on quick and dirty scripts.

It uses the provided convenience functions and default ingest client.

See https://docs.amberflo.io/reference/post_ingest
"""

import os
from time import time
from random import random
import logging

import metering

logging.basicConfig(level=logging.DEBUG)


def now_in_millis():
    return int(round(time() * 1000))


def main():
    # 1. obtain your API key
    metering.app_key = os.environ.get("TEST_API_KEY")

    # 2. send some meter events
    dimensions = {"region": "us-east-1"}
    customer_id = "sample-customer-123"

    for i in range(100):
        metering.meter(
            meter_api_name="sample-meter",
            meter_value=5 + random(),
            meter_time_in_millis=now_in_millis(),
            customer_id=customer_id,
            dimensions=dimensions,
        )

    # 3. ensure all events are sent and safely stop the background threads
    metering.shutdown()


if __name__ == "__main__":
    main()
