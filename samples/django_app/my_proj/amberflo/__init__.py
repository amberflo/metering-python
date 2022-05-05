from time import time

from django.conf import settings

from metering.ingest import create_ingest_client


# Single global instance for background batch ingestion of meter records.
ingest_client = create_ingest_client(api_key=settings.AMBERFLO_API_KEY)


def now_in_millis():
    """
    Returns the current unix epoch time in milliseconds.
    """
    return int(round(time() * 1000))


def get_customer_id(user):
    """
    Get the "customer_id" in order to associate the meter records to your
    users.
    """
    if user.is_authenticated:
        return user.get_username()
    return "__anonnymous__"
