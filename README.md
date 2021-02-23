# metering-python
Amberflo.io metering client in python

simulator.py --app_key e9c6a4fc-e275-4eda-b2f8-353ef196ddb7 --tenant customerXXX --meter_name apicall --meter_value 1



# dedup is happening on a full record
metering.meter(options.tenant, options.meter_name,int(options.meter_value), dimensions=dimensions) 
# addint a timestamp
metering.meter(options.tenant, options.meter_name,int(options.meter_value), \
    dimensions=dimensions,timestamp=str(int(round(time.time() * 1000)))) 
# adding unique id
metering.meter(options.tenant, options.meter_name,int(options.meter_value), dimensions=dimensions_with_unique_id) 
