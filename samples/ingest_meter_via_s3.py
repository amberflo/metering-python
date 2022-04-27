#!/usr/bin/env python3

import os
from time import time
from random import random

from metering.ingest import ThreadedProducer, IngestS3Client, create_ingest_payload


def now_in_millis():
    return int(round(time() * 1000))


def main():
    # 1. obtain your S3 secrets
    params = {
        "bucket_name": os.environ.get("BUCKET_NAME"),
        "access_key": os.environ.get("ACCESS_KEY"),
        "secret_key": os.environ.get("SECRET_KEY"),
    }

    # 2. initialize the threaded ingestion client
    client = ThreadedProducer(params, IngestS3Client)

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
