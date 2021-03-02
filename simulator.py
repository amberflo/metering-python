import argparse
import ast
import logging
import time

from uuid import uuid1

import metering

__name__ = 'simulator.py'
__version__ = '0.0.1'
__description__ = 'scripting simulator'

# simulator.py --app_key e9c6a4fc-e275-4eda-b2f8-353ef196ddb7 --meter_name apicall --meter_value 1
#   --customer_id ID_X --customer_id NAME_X
#   --dimensions "[{\"Name\": \"region\", \"Value\": \"us-east-1\"}]"


parser = argparse.ArgumentParser(description='send a amberflo message')
parser.add_argument('--app_key', help='the amberflo app_key', required=True)
parser.add_argument('--meter_name', help='the meter name to send', required=True)
parser.add_argument('--meter_value', help='the meter value to send ', required=True)

parser.add_argument('--customer_id', help='the customer id to send the meter for', required=False)
parser.add_argument('--customer_name', \
    help='the customer name to send the meter for', required=False)
parser.add_argument(
    '--dimensions', help='the dimensions to send (JSON-encoded) FUTURE')



options = parser.parse_args()


def failed(status, msg):
    raise Exception(msg)


def meter():
    i = 0
    dimensions = ast.literal_eval(options.dimensions)
    current_time = int(round(time.time() * 1000))

    while i<1:
        # dedup is happening on a full record
        metering.meter(options.meter_name, \
            int(options.meter_value), \
            utc_time_millis=current_time, \
            customer_id=options.customer_id, \
            customer_name=options.customer_name)
        # adding dimensions
        metering.meter(options.meter_name, \
            int(options.meter_value), \
            utc_time_millis=current_time, \
            customer_id=options.customer_id, \
            customer_name=options.customer_name, \
            dimensions=dimensions)
        # adding unique id
        metering.meter(options.meter_name, \
            int(options.meter_value), \
            utc_time_millis=current_time, \
            customer_id=options.customer_id, \
            customer_name=options.customer_name, \
            dimensions=dimensions, \
            unique_id = uuid1())

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
