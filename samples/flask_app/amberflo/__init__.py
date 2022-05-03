import os
from time import time

from metering.ingest import ThreadedProducer


# Single global instance for background batch ingestion of meter records.
ingest_client = ThreadedProducer(
    {
        "api_key": os.environ["AMBERFLO_API_KEY"],
    }
)


def now_in_millis():
    """
    Returns the current unix epoch time in milliseconds.
    """
    return int(round(time() * 1000))


def get_customer_id(request):
    """
    Get the "customer_id" in order to associate the meter records to your
    users.
    """
    return "__anonnymous__"
