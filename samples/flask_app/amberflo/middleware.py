import logging
from flask import request

from metering.ingest import create_ingest_payload

from . import ingest_client, now_in_millis, get_customer_id

logger = logging.getLogger(__name__)


meter_api_name = "api_processing_time"


def init_amberflo(app):
    """
    This is a simple Flask middleware for metering "API processing time".

    See https://flask.palletsprojects.com/en/2.1.x/reqcontext/
    and https://flask.palletsprojects.com/en/2.1.x/api/#flask.Flask.after_request
    """
    app.before_request(_before_request)
    app.after_request(_after_request)


def _before_request():
    """
    Record the start time of the request.
    """
    request._start_time = now_in_millis()


def _after_request(response):
    """
    Process request handling duration and send metric (enqueue it for
    background batch sending).

    Get the customer_id of the currently logged in user.
    """

    meter_time_in_millis = now_in_millis()
    delta_in_millis = meter_time_in_millis - request._start_time

    customer_id = get_customer_id(request)
    logger.debug("Took %s ms on %s for %s", delta_in_millis, request.path, customer_id)

    event = create_ingest_payload(
        meter_api_name=meter_api_name,
        meter_value=delta_in_millis,
        meter_time_in_millis=meter_time_in_millis,
        customer_id=customer_id,
    )
    ingest_client.send(event)

    return response
