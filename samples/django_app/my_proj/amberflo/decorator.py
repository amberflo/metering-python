import logging
from functools import wraps

from metering.ingest import create_ingest_payload

from . import ingest_client, now_in_millis, get_customer_id

logger = logging.getLogger(__name__)


def count_api_calls(view_func):
    """
    Decorator to count API calls by customer.
    """

    @wraps(view_func)
    def inner(request, *args, **kwargs):
        customer_id = get_customer_id(request.user)
        logger.debug("Count one call of %s for %s", request.path, customer_id)
        event = create_ingest_payload(
            meter_api_name="api_call_count",
            meter_value=1,
            meter_time_in_millis=now_in_millis(),
            customer_id=customer_id,
        )
        ingest_client.send(event)
        return view_func(request, *args, **kwargs)

    return inner
