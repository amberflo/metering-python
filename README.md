# amberflo-metering-python

<p>
    <a href="https://github.com/amberflo/metering-python/actions">
        <img alt="CI Status" src="https://github.com/amberflo/metering-python/actions/workflows/tests.yml/badge.svg?branch=part-5-reorganize-tests-samples">
    </a>
    <a href="https://pypi.org/project/amberflo-metering-python/">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/amberflo-metering-python">
    </a>
</p>

[Amberflo](https://amberflo.io) is the simplest way to integrate metering into your application.

This is the official Python 3 client that wraps the [Amberflo REST API](https://docs.amberflo.io/docs).

## :heavy_check_mark: Features

- Add and update Customers
- Assign and update Product Plans to Customers
- Send meter events
    - In asynchronous batches for high throughput (with optional flush on demand)
    - Or synchronously
    - Using the Amberflo API or the Amberflo supplied AWS S3 bucket
- Query usage
- Fine grained logging control

## :rocket: Quick Start

1. [Sign up for free](https://ui.amberflo.io/) and get an API key.

2. Install the SDK

```
pip install amberflo-metering-python
```

3. Create a customer

```python3
import os
from metering.customer import CustomerApiClient, create_customer_payload

client = CustomerApiClient(os.environ.get("API_KEY"))

message = create_customer_payload(
    customer_id="sample-customer-123",
    customer_email="customer-123@sample.com",
    customer_name="Sample Customer",
    traits={
        "region": "us-east-1",
    },
)
customer = client.add_or_update(message)
```

4. Ingest meter events

```python3
import os
from time import time
from metering.ingest import create_ingest_client, create_ingest_payload

client = create_ingest_client(api_key=os.environ["API_KEY"])

dimensions = {"region": "us-east-1"}
customer_id = "sample-customer-123"

client.meter(
    meter_api_name="sample-meter",
    meter_value=5,
    meter_time_in_millis=int(time() * 1000),
    customer_id=customer_id,
    dimensions=dimensions,
)
```

5. Query usage

```python3
import os
from time import time
from metering.usage import (AggregationType, Take, TimeGroupingInterval,
                            TimeRange, UsageApiClient, create_usage_query)

client = UsageApiClient(os.environ.get("API_KEY"))

since_two_days_ago = TimeRange(int(time()) - 60 * 60 * 24 * 2)

request = create_usage_query(
    meter_api_name="my_meter",
    aggregation=AggregationType.SUM,
    time_grouping_interval=TimeGroupingInterval.DAY,
    time_range=since_two_days_ago,
    group_by=["customerId"],
    usage_filter={"customerId": ["some-customer-321", "sample-customer-123"]},
    take=Take(limit=10, is_ascending=False),
)
report = client.get(request)
```

## :zap: High throughput ingestion

Amberflo.io libraries are built to support high throughput environments. That
means you can safely send hundreds of meter records per second. For example,
you can chose to deploy it on a web server that is serving hundreds of requests
per second.

However, every call does not result in a HTTP request, but is queued in memory
instead. Messages are batched and flushed in the background, allowing for much
faster operation. The size of batch and rate of flush can be customized.

The SDK allows you to set up a `on_error` callback function for handling errors
when trying to send a batch.

```python3
def on_error_callback(error, batch):
    ...

client = ThreadedProducer(
    {'api_key': API_KEY},
    max_queue_size=200000,  # max number of items in the queue before rejecting new items
    threads=3,  # number of worker threads doing the sending
    retries=4,  # max number of retries after failures
    batch_size=1000,  # max number of meter records in a batch
    send_interval_in_secs=0.7,  # wait time before sending an incomplete batch
    sleep_interval_in_secs=0.5,  # wait time after failure to send or queue empty
    on_error=on_error_callback,  # handle failures to send a batch
)

...

client.send(meter_event)
```

### Ingesting through the S3 bucket

The SDK provides a `metering.ingest.IngestS3Client` so you can send your meter
records to us via the S3 bucket.

Use of this feature is enabled if you install the library with the `s3` option:
```
pip install amberflo-metering-python[s3]
```

## :book: Documentation

General documentation on how to use Amberflo is available at [Product Walkthrough](https://docs.amberflo.io/docs/product-walkthrough).

The full REST API documentation is available at [API Reference](https://docs.amberflo.io/reference).

## :scroll: Samples

Code samples covering different scenarios are available in the [./samples](https://github.com/amberflo/metering-python/blob/main/samples/README.md) folder.

## :construction_worker: Contributing

Feel free to open issues and send a pull request.

Also, check out [CONTRIBUTING.md](https://github.com/amberflo/metering-python/blob/main/CONTRIBUTING.md).
