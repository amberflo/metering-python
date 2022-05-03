#!/usr/bin/env python3

"""
This sample shows an example of meter record ingestion, using an Elasticsearch
cluster as record source.

Ingestion is done in batches on a background thread for high-throughput.

See https://docs.amberflo.io/reference/post_ingest
"""

import os
from datetime import datetime

from elasticsearch import Elasticsearch

from metering.exceptions import ApiError
from metering.ingest import get_ingest_client, create_ingest_payload
from metering.customer import CustomerApiClient


def get_hits():
    client = Elasticsearch("http://localhost:9200", api_key=("id", "api_key"))

    # This ES query is looking on the last 1 day for logs with the string
    # `*Requesting next set of records*`  on the specified index pattern
    response = client.search(
        index="cwl--aws-lambda-generatelogs-2021*",
        body={
            "query": {
                "bool": {
                    "filter": [
                        {
                            "range": {
                                "@timestamp": {
                                    "from": "now-1d/d",
                                    "to": "now/d",
                                    "format": "epoch_millis",
                                    "boost": 1,
                                }
                            }
                        },
                        {
                            "query_string": {
                                "query": "*Requesting next set of records*",
                                "default_field": "@message",
                                "fields": [],
                                "type": "best_fields",
                                "default_operator": "or",
                                "max_determinized_states": 10000,
                                "fuzziness": "AUTO",
                                "fuzzy_prefix_length": 0,
                                "fuzzy_max_expansions": 50,
                                "phrase_slop": 0,
                                "boost": 1,
                            }
                        },
                    ],
                    "boost": 1,
                }
            },
            "aggregations": {},
        },
    )

    return response["hits"]["hits"]


def main():
    # 1. initialize the threaded ingestion client
    client = get_ingest_client(api_key=os.environ["API_KEY"])

    # 2. initialize Customer Api Client (for creating customers)
    customer_api_client = CustomerApiClient(os.environ["API_KEY"])

    # 3. query elasticsearch
    hits = get_hits()

    # 4. ingest the events
    added_customers = set()  # keep track of customers already added

    for hit in hits:
        data = hit["_source"]

        timestamp = datetime.strptime(
            data["@timestamp"], r"%Y-%m-%dT%H:%M:%S.%fZ"
        ).timestamp()

        meter_time_in_millis = int(round(timestamp * 1000))

        account_id = data["account_id"]
        service_id = data["service_id"]
        host = data["host"]
        environment_name = data["environment_name"]

        # 4.1 create the customer if needed
        if account_id not in added_customers:
            try:
                customer_api_client.add(
                    customer_id=account_id, customer_name=account_id
                )
            except ApiError:
                pass
            added_customers.add(account_id)

        # 4.2 ingest meter record
        event = create_ingest_payload(
            meter_api_name="api_calls_to_salesforce",
            meter_value=1,
            meter_time_in_millis=meter_time_in_millis,
            customer_id=account_id,
            unique_id=meter_time_in_millis,  # use `unique_id` if you want Amberflo to dedup repeated records
            dimensions={
                "service_id": service_id,
                "host": host,
                "environment_name": environment_name,
            },
        )
        client.send(event)

    # 5. ensure all events are sent and safely stop the background threads
    client.shutdown()


if __name__ == "__main__":
    main()
