# metering-python
Amberflo.io metering client in python (python 3.5 and above)

Obtain {{my-api-key}} and run:
```
python3 simulator.py --app_key {{my-api-key}} --meter_api_name ApiCalls --meter_value 1 --customer_id ID_X --dimensions "{\"Name\": \"region\", \"Value\": \"us-east-1\"}"
```

# Design
Producer consumer of meter messages.

## Main Classes
1. RequestManager - Knows how to send a batch of meter requests to Amberflo.
2. MeterFactory - A factory which knows how to produce a meter message which we can send to Amberflo.
3. Client - The client is a producer-consumer component
    * It gets meter requests from many threads (producers) and put them in a queue.
    * It uses a consumer (a separate thread) which send the meters to amberflo.
4. Consumer - A thread initated by the client which query the Client's meters queue and send the meters to amberflo (in batches).

# Test
Run the following:
1. Install project + dependencies:
```pip3 install requests pylint backoff==1.10.0 python-dateutil```
```python3 setup.py install```
3. Run unit tests + coverage:
```coverage run --branch --include=metering/\* --omit=*/test* setup.py test```
2. Style check:
```flake8 --max-complexity=10 --statistics metering```

# Ingestion

```python
# dedup is happening on a full record
metering.meter(options.meter_api_name, \
    int(options.meter_value), \
    meter_time_in_millis=int(round(time.time() * 1000)), \
    customer_id=options.customer_id)
# adding dimensions
metering.meter(options.meter_api_name, \
    int(options.meter_value), \
    meter_time_in_millis=int(round(time.time() * 1000)), \
    customer_id=options.customer_id, \
    dimensions=dimensions)
# adding unique id
metering.meter(options.meter_api_name, \
    int(options.meter_value), \
    meter_time_in_millis=int(round(time.time() * 1000)), \
    customer_id=options.customer_id, \
    dimensions=dimensions, \
    unique_id = uuid1())
```

# Calling the Usage API
```python
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

```

# Setting up a customer

```python
import metering


def setup_customer():
    # obtain your Amberflo API Key
    metering.api_key = 'my-api-key'

    # traits are optional. Traits can be used as filters or aggregation buckets.
    customer = metering.add_or_update_customer(
        customer_id='1234',
        customer_name='Stark Industries',
        traits={'region': 'midwest', 'stripeId': 'cus_AJ6bY3VqcaLAEs'})
    print(customer)


setup_customer()
```