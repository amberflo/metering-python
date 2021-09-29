
from metering.version import VERSION
from metering.client import Client

__version__ = VERSION

"""Settings."""
app_key = None
access_key = None
secret_key = None
s3_bucket = None
host = None
on_error = None
debug = False
send = True
wait = False

default_client = None


def meter(*args, **kwargs):
    """Send a meter call."""
    _proxy('meter', *args, **kwargs)

def add_or_update_customer(*args, **kwargs):
    """Setup customer"""
    return _proxy_with_return('add_or_update_customer', *args, **kwargs)

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
        default_client = Client(app_key=app_key, s3_bucket=s3_bucket, access_key= access_key,
                                secret_key= secret_key, debug=debug,
                                on_error=on_error, send=send,
                                wait=wait)

    fn = getattr(default_client, method)
    fn(*args, **kwargs)

def _proxy_with_return(method, *args, **kwargs):
    """Create an analytics client if one doesn't exist and send to it."""
    global default_client
    if not default_client:
        default_client = Client(app_key=app_key,  s3_bucket=s3_bucket, access_key= access_key,
                                secret_key= secret_key, debug=debug,
                                on_error=on_error, send=send,
                                wait=wait)

    fn = getattr(default_client, method)
    return fn(*args, **kwargs)    
