import metering
import argparse
import json
import logging

__name__ = 'simulator.py'
__version__ = '0.0.1'
__description__ = 'scripting simulator'


def json_hash(str):
    if str:
        return json.loads(str)

# simulator.py --user_name demo --password changeme --tenant customerXXX --meter_name apicall --meter_value 1


parser = argparse.ArgumentParser(description='send a amberflo message')
parser.add_argument('--user_name', help='the amberflo username', required=True)
parser.add_argument('--password', help='the amberflo password', required=True)
parser.add_argument('--tenant', help='the tenant to send the meter for', required=True)

parser.add_argument('--meter_name', help='the meter name to send', required=True)
parser.add_argument('--meter_value', help='the meter value to send ', required=True)
parser.add_argument(
    '--dimensions', help='the dimensions to send (JSON-encoded) FUTURE')



options = parser.parse_args()


def failed(status, msg):
    raise Exception(msg)


def track():
    i = 0
    while i<1:
        metering.track(options.tenant, options.meter_name,int(options.meter_value), dimensions=json_hash(options.dimensions)) 
        i = i + 1


def unknown():
    print()


metering.password = options.password
metering.user_name = options.user_name
metering.on_error = failed
metering.debug = True

log = logging.getLogger('amberflo')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

switcher = {
    "track": track
}

func = switcher.get("track")
if func:
    func()
    metering.shutdown()
else:
    print("Invalid Message Type " + options.type)
