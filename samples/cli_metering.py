#!/usr/bin/env python3

"""
This is an example of a simple CLI tool for ingesting individual meter records.
This uses the Amberflo Ingestion API directly (in a synchronous manner).

For batch ingestion in the background, see `./ingest_meter.py`.

USAGE:
    ./cli_metering.py \
        --api-key $API_KEY \
        --meter-api-name 'ApiCall' \
        --meter-value '1' \
        --customer-id 'cus-123' \
        --dimensions '{"Name": "region", "Value": "us-east-1"}'
"""

import argparse
import ast
import logging
import time
from uuid import uuid4

from metering.ingest import IngestApiClient, create_ingest_payload


logging.basicConfig(level=logging.DEBUG)


def get_options():
    parser = argparse.ArgumentParser(description="Send a meter event to Amberflo")
    parser.add_argument(
        "--api-key",
        help="The Amberflo API key",
        required=True,
    )
    parser.add_argument(
        "--meter-api-name",
        help="The meter name to send",
        required=True,
    )
    parser.add_argument(
        "--meter-value",
        help="The meter value to send",
        required=True,
        type=float,
    )
    parser.add_argument(
        "--customer-id",
        help="The customer id to send the meter for",
        required=True,
    )
    parser.add_argument(
        "--dimensions",
        help="the dimensions to send (JSON-encoded)",
        type=ast.literal_eval,
        default={},
    )
    return parser.parse_args()


def main(options):
    client = IngestApiClient(options.api_key)

    # dedup happens on a full record
    unique_id = str(uuid4())
    current_time = int(round(time.time() * 1000))

    message = create_ingest_payload(
        options.meter_api_name,
        float(options.meter_value),
        meter_time_in_millis=current_time,
        customer_id=options.customer_id,
        unique_id=unique_id,
    )
    print(">", message)
    print("<", client.send(message))

    # adding dimensions
    message = create_ingest_payload(
        options.meter_api_name,
        float(options.meter_value),
        meter_time_in_millis=current_time,
        customer_id=options.customer_id,
        unique_id=unique_id,
        dimensions=options.dimensions,
    )
    print(">", message)
    print("<", client.send(message))


if __name__ == "__main__":
    options = get_options()
    main(options)
