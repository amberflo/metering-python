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

# simulator.py --type track --password changeme --userId demo --event agentcall


parser = argparse.ArgumentParser(description='send a amberflo message')

parser.add_argument('--password', help='the amberflo password')
parser.add_argument('--type', help='The amberflo message type')

parser.add_argument('--userId', help='the user id to send the event as')

parser.add_argument(
    '--context', help='additional context for the event (JSON-encoded)')

parser.add_argument('--meter_name', help='the meter name to send')
parser.add_argument('--meter_value', help='the meter value to send ')
parser.add_argument(
    '--properties', help='the event properties to send (JSON-encoded)')




parser.add_argument('--groupId', help='the group id')

options = parser.parse_args()


def failed(status, msg):
    raise Exception(msg)


def track():
    metering.track(options.userId, options.meter_name,int(options.meter_value), dimensions=json_hash(options.context)) 


def unknown():
    print()


metering.write_key = options.password
metering.on_error = failed
metering.debug = True

log = logging.getLogger('segment')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

switcher = {
    "track": track
}

func = switcher.get(options.type)
if func:
    func()
    metering.shutdown()
else:
    print("Invalid Message Type " + options.type)
