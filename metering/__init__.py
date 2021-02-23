
from metering.version import VERSION
from metering.client import Client

__version__ = VERSION

"""Settings."""
app_key = 'e9c6a4fc-e275-4eda-b2f8-353ef196ddb7'
host = None
on_error = None
debug = False
send = True
wait = False

default_client = None


def meter(*args, **kwargs):
    """Send a meter call."""
    _proxy('meter', *args, **kwargs)




def flush():
    """Tell the client to flush."""
    _proxy('flush')


def join():
    """Block program until the client clears the queue"""
    _proxy('join')


def shutdown():
    """Flush all messages and cleanly shutdown the client"""
    _proxy('flush')
    _proxy('join')


def _proxy(method, *args, **kwargs):
    """Create an analytics client if one doesn't exist and send to it."""
    global default_client
    if not default_client:
        default_client = Client(app_key=app_key, debug=debug,
                                on_error=on_error, send=send,
                                wait=wait)

    fn = getattr(default_client, method)
    fn(*args, **kwargs)
