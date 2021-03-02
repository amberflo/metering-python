# metering-python
Amberflo.io metering client in python (python 3.5 and above)

simulator.py --app_key e9c6a4fc-e275-4eda-b2f8-353ef196ddb7 --meter_name apicall --meter_value 1 --customer_id ID_X --customer_id NAME_X

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
```pip install requests pylint backoff==1.10.0 python-dateutil```
```python setup.py install```
3. Run unit tests + coverage:
```coverage run --branch --include=metering/\* --omit=*/test* setup.py test```
2. Style check:
```flake8 --max-complexity=10 --statistics metering```

# Usage

```
# dedup is happening on a full record
metering.meter(options.meter_name, \
    int(options.meter_value), \
    utc_time_millis=int(round(time.time() * 1000)), \
    customer_id=options.customer_id, \
    customer_name=options.customer_name)
# adding dimensions
metering.meter(options.meter_name, \
    int(options.meter_value), \
    utc_time_millis=int(round(time.time() * 1000)), \
    customer_id=options.customer_id, \
    customer_name=options.customer_name, \
    dimensions=dimensions)
# adding unique id
metering.meter(options.meter_name, \
    int(options.meter_value), \
    utc_time_millis=int(round(time.time() * 1000)), \
    customer_id=options.customer_id, \
    customer_name=options.customer_name, \
    dimensions=dimensions, \
    unique_id = uuid1())```

