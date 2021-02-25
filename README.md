# metering-python
Amberflo.io metering client in python

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

# Usage
## dedup is happening on a full record
metering.meter(options.meter_name, \
    int(options.meter_value), \
    customer_id=options.customer_id, \
    customer_name=options.customer_name, \
    dimensions=dimensions)
## addint a timestamp
metering.meter(options.meter_name, \
    int(options.meter_value), \
    customer_id=options.customer_id, \
    customer_name=options.customer_name, \
    dimensions=dimensions, \
    utc_time_millis=time.time_ns() // 1_000_000)
## adding unique id
metering.meter(options.meter_name, \
    int(options.meter_value), \
    customer_id=options.customer_id, \
    customer_name=options.customer_name, \
    dimensions=dimensions, \
    unique_id = uuid1())
