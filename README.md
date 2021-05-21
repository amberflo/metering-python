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

# Usage

```
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

