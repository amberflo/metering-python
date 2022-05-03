#!/usr/bin/env python3

"""
This sample shows an example of meter record ingestion. Ingestion is done in
batches on a background thread for high-throughput. This pattern is
particularly useful in the context of a web server, as it moves the ingestion
outside of the request-response cycle.

See https://docs.amberflo.io/reference/post_ingest
"""

import os
from time import time
from random import random

from metering.ingest import ThreadedProducer, create_ingest_payload


def now_in_millis():
    return int(round(time() * 1000))


def main():
    # 1. obtain your API key
    params = {
        "api_key": os.environ.get("API_KEY"),
    }

    # 2. initialize the threaded ingestion client
    client = ThreadedProducer(params)

    # 3. send some meter events
    dimensions = {"region": "us-east-1"}
    customer_id = "sample-customer-123"

    for i in range(100):
        event = create_ingest_payload(
            meter_api_name="sample-meter",
            meter_value=5 + random(),
            meter_time_in_millis=now_in_millis(),
            customer_id=customer_id,
            dimensions=dimensions,
        )
        client.send(event)

    # 4. ensure all events are sent and safely stop the background threads
    client.shutdown()


if __name__ == "__main__":
    main()
