import metering
import argparse
import json
import logging
import time
from uuid import uuid4

__name__ = 'simulator.py'
__version__ = '0.0.1'
__description__ = 'scripting simulator'


def json_hash(str):
    if str:
        return json.loads(str)

# simulator.py --app_key e9c6a4fc-e275-4eda-b2f8-353ef196ddb7 --tenant customerXXX --meter_name apicall --meter_value 1 --dimensions "[{\"Name\": \"region\", \"Value\": \"us-east-1\"}]"


parser = argparse.ArgumentParser(description='send a amberflo message')
parser.add_argument('--app_key', help='the amberflo app_key', required=True)
parser.add_argument('--tenant', help='the tenant to send the meter for', required=True)

parser.add_argument('--meter_name', help='the meter name to send', required=True)
parser.add_argument('--meter_value', help='the meter value to send ', required=True)
parser.add_argument(
    '--dimensions', help='the dimensions to send (JSON-encoded) FUTURE')



options = parser.parse_args()


def failed(status, msg):
    raise Exception(msg)


def meter():
    i = 0
    dimensions = json_hash(options.dimensions)
    dimensions_with_unique_id = dimensions.copy()
    dimensions_with_unique_id.append({'Name': 'unique_id', 'Value': str(uuid4())}) 
    while i<1:
        # dedup is happening on a full record
        metering.meter(options.tenant, options.meter_name,int(options.meter_value), dimensions=dimensions) 
        # addint a timestamp
        metering.meter(options.tenant, options.meter_name,int(options.meter_value), \
            dimensions=dimensions,timestamp=str(int(round(time.time() * 1000)))) 
        # adding unique id
        metering.meter(options.tenant, options.meter_name,int(options.meter_value), dimensions=dimensions_with_unique_id) 

        i = i + 1
        time.sleep(3)


def unknown():
    print()


metering.app_key = options.app_key
metering.on_error = failed
metering.debug = True

log = logging.getLogger('amberflo')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

switcher = {
    "meter": meter
}

func = switcher.get("meter")
if func:
    func()
    metering.shutdown()
else:
    print("Invalid Message Type " + options.type)
