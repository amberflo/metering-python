
from metering.version import VERSION
from metering.client import Client

__version__ = VERSION

"""Settings."""
user_name = None
password = None
host = None
on_error = None
debug = False
send = True
sync_mode = False

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
        default_client = Client(user_name,password, host=host, debug=debug,
                                on_error=on_error, send=send,
                                sync_mode=sync_mode)

    fn = getattr(default_client, method)
    fn(*args, **kwargs)
