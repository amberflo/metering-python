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

# simulator.py --type track --writeKey changeme --userId demo --event agentcall


parser = argparse.ArgumentParser(description='send a amberflo message')

parser.add_argument('--writeKey', help='the amberflo writeKey')
parser.add_argument('--type', help='The amberflo message type')

parser.add_argument('--userId', help='the user id to send the event as')
parser.add_argument(
    '--anonymousId', help='the anonymous user id to send the event as')
parser.add_argument(
    '--context', help='additional context for the event (JSON-encoded)')

parser.add_argument('--event', help='the event name to send with the event')
parser.add_argument(
    '--properties', help='the event properties to send (JSON-encoded)')

parser.add_argument(
    '--name', help='name of the screen or page to send with the message')

parser.add_argument(
    '--traits', help='the identify/group traits to send (JSON-encoded)')

parser.add_argument('--groupId', help='the group id')

options = parser.parse_args()


def failed(status, msg):
    raise Exception(msg)


def track():
    metering.track(options.userId, options.event, anonymous_id=options.anonymousId,
                    properties=json_hash(options.properties), context=json_hash(options.context))


def page():
    metering.page(options.userId, name=options.name, anonymous_id=options.anonymousId,
                   properties=json_hash(options.properties), context=json_hash(options.context))


def screen():
    metering.screen(options.userId, name=options.name, anonymous_id=options.anonymousId,
                     properties=json_hash(options.properties), context=json_hash(options.context))


def identify():
    metering.identify(options.userId, anonymous_id=options.anonymousId,
                       traits=json_hash(options.traits), context=json_hash(options.context))


def group():
    metering.group(options.userId, options.groupId, json_hash(options.traits),
                    json_hash(options.context), anonymous_id=options.anonymousId)


def unknown():
    print()


metering.write_key = options.writeKey
metering.on_error = failed
metering.debug = True

log = logging.getLogger('segment')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

switcher = {
    "track": track,
    "page": page,
    "screen": screen,
    "identify": identify,
    "group": group
}

func = switcher.get(options.type)
if func:
    func()
    metering.shutdown()
else:
    print("Invalid Message Type " + options.type)
