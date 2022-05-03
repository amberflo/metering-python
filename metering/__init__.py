from warnings import warn

from metering.version import VERSION
from metering.customer import CustomerApiClient, create_customer_payload
from metering.ingest import create_ingest_client

__version__ = VERSION


app_key = None


def add_or_update_customer(*args, **kwargs):
    """
    Setup customer
    """
    warn(
        "Please use `metering.customer.CustomerApiClient.add_or_update` instead",
        DeprecationWarning,
        stacklevel=2,
    )
    client = CustomerApiClient(app_key)
    payload = create_customer_payload(*args, **kwargs)
    return client.add_or_update(payload)


access_key = None
secret_key = None
s3_bucket = None
on_error = None
default_client = None


def _get_default_client():
    global default_client

    if not default_client:
        default_client = create_ingest_client(
            api_key=app_key,
            bucket_name=s3_bucket,
            access_key=access_key,
            secret_key=secret_key,
            on_error=on_error,
        )

    return default_client


def meter(*args, **kwargs):
    """
    Build and enqueue a meter record to be sent. Returns whether it was
    successful or not.

    See `metering.ingest.create_ingest_payload` for details on the payload.
    """
    return _get_default_client().meter(*args, **kwargs)


def flush():
    """
    Blocks until all messages in the queue are consumed.
    """
    return _get_default_client().flush()


def join():
    """
    Ends the consumer threads cleanly.
    """
    return _get_default_client().join()


def shutdown():
    """
    Block until all items are consumed, then ends the consumer threads
    cleanly.
    """
    return _get_default_client().shutdown()
