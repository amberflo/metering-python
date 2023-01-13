# amberflo-metering-python

<p>
    <a href="https://github.com/amberflo/metering-python/actions">
        <img alt="CI Status" src="https://github.com/amberflo/metering-python/actions/workflows/tests.yml/badge.svg?branch=main">
    </a>
    <a href="https://pypi.org/project/amberflo-metering-python/">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/amberflo-metering-python">
    </a>
</p>

[Amberflo](https://amberflo.io) is the simplest way to integrate metering into your application.

This is the official Python 3 client that wraps the [Amberflo REST API](https://docs.amberflo.io/docs).

## :heavy_check_mark: Features

- Add and update customers
- Assign and update product plans to customers
- List invoices of a customer
- Get a new customer portal session for a customer
- Add and list prepaid orders to customers
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

```python
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

```python
import os
from time import time
from metering.ingest import create_ingest_client

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

```python
import os
from time import time
from metering.usage import (AggregationType, Take, TimeGroupingInterval,
                            TimeRange, UsageApiClient, create_usage_query)

client = UsageApiClient(os.environ.get("API_KEY"))

since_two_days_ago = TimeRange(int(time()) - 60 * 60 * 24 * 2)

query = create_usage_query(
    meter_api_name="my_meter",
    aggregation=AggregationType.SUM,
    time_grouping_interval=TimeGroupingInterval.DAY,
    time_range=since_two_days_ago,
    group_by=["customerId"],
    usage_filter={"customerId": ["some-customer-321", "sample-customer-123"]},
    take=Take(limit=10, is_ascending=False),
)
report = client.get(query)
```

## :zap: High throughput ingestion

Amberflo.io libraries are built to support high throughput environments. That
means you can safely send hundreds of meter records per second. For example,
you can chose to deploy it on a web server that is serving hundreds of requests
per second.

However, every call does not result in a HTTP request, but is queued in memory
instead. Messages are batched and flushed in the background, allowing for much
faster operation. The size of batch and rate of flush can be customized.

**Flush on demand:** For example, at the end of your program, you'll want to
flush to make sure there's nothing left in the queue. Calling this method will
block the calling thread until there are no messages left in the queue. So,
you'll want to use it as part of your cleanup scripts and avoid using it as
part of the request lifecycle.

**Error handling:** The SDK allows you to set up a `on_error` callback function
for handling errors when trying to send a batch.

Here is a complete example, showing the default values of all options:

```python
def on_error_callback(error, batch):
    ...

client = create_ingest_client(
    api_key=API_KEY,
    max_queue_size=100000,  # max number of items in the queue before rejecting new items
    threads=2,  # number of worker threads doing the sending
    retries=2,  # max number of retries after failures
    batch_size=100,  # max number of meter records in a batch
    send_interval_in_secs=0.5,  # wait time before sending an incomplete batch
    sleep_interval_in_secs=0.1,  # wait time after failure to send or queue empty
    on_error=on_error_callback,  # handle failures to send a batch
)

...

client.meter(...)

client.flush()  # block and make sure all messages are sent
```

### What happens if there are just too many messages?

If the module detects that it can't flush faster than it's receiving messages,
it'll simply stop accepting new messages. This allows your program to
continually run without ever crashing due to a backed up metering queue.

### Ingesting through the S3 bucket

The SDK provides a `metering.ingest.IngestS3Client` so you can send your meter
records to us via the S3 bucket.

Use of this feature is enabled if you install the library with the `s3` option:
```
pip install amberflo-metering-python[s3]
```

Just pass the S3 bucket credentials to the factory function:
```python
client = create_ingest_client(
    bucket_name=os.environ.get("BUCKET_NAME"),
    access_key=os.environ.get("ACCESS_KEY"),
    secret_key=os.environ.get("SECRET_KEY"),
)
```

## :book: Documentation

General documentation on how to use Amberflo is available at [Product Walkthrough](https://docs.amberflo.io/docs/product-walkthrough).

The full REST API documentation is available at [API Reference](https://docs.amberflo.io/reference).

## :scroll: Samples

Code samples covering different scenarios are available in the [./samples](https://github.com/amberflo/metering-python/blob/main/samples/README.md) folder.

## :construction_worker: Contributing

Feel free to open issues and send a pull request.

Also, check out [CONTRIBUTING.md](https://github.com/amberflo/metering-python/blob/main/CONTRIBUTING.md).

## :bookmark_tabs: Reference

### API Clients

#### [Ingest](https://docs.amberflo.io/reference/post_ingest)

```python
from metering.ingest import (
    create_ingest_payload,
    create_ingest_client,
)
```

#### [Customer](https://docs.amberflo.io/reference/post_customers)

```python
from metering.customer import (
    CustomerApiClient,
    create_customer_payload,
)
```

#### [Usage](https://docs.amberflo.io/reference/post_usage)

```python
from metering.usage import (
    AggregationType,
    Take,
    TimeGroupingInterval,
    TimeRange,
    UsageApiClient,
    create_usage_query,
    create_all_usage_query,
)
```

#### [Customer Portal Session](https://docs.amberflo.io/reference/post_session)

```python
from metering.customer_portal_session import (
    CustomerPortalSessionApiClient,
    create_customer_portal_session_payload,
)
```

#### [Customer Prepaid Order](https://docs.amberflo.io/reference/post_payments-pricing-amberflo-customer-prepaid)

```python
from metering.customer_prepaid_order import (
    BillingPeriod,
    BillingPeriodUnit,
    CustomerPrepaidOrderApiClient,
    create_customer_prepaid_order_payload,
)
```

#### [Customer Product Invoice](https://docs.amberflo.io/reference/get_payments-billing-customer-product-invoice)

```python
from metering.customer_product_invoice import (
    CustomerProductInvoiceApiClient,
    create_all_invoices_query,
    create_latest_invoice_query,
    create_invoice_query,
)
```

#### [Customer Product Plan](https://docs.amberflo.io/reference/post_payments-pricing-amberflo-customer-pricing)

```python
from metering.customer_product_plan import (
    CustomerProductPlanApiClient,
    create_customer_product_plan_payload,
)
```

### Exceptions

```python
from metering.exceptions import ApiError
```

### Logging

`amberflo-metering-python` uses the standard Python logging framework. By
default, logging is and set at the `WARNING` level.

The following loggers are used:

- `metering.ingest.producer`
- `metering.ingest.s3_client`
- `metering.ingest.consumer`
- `metering.session.ingest_session`
- `metering.session.api_session`
