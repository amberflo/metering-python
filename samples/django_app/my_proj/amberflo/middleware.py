import logging
from metering.ingest import create_ingest_payload

from . import ingest_client, now_in_millis, get_customer_id

logger = logging.getLogger(__name__)


class AmberfloMiddleware:
    """
    This is a simple Django middleware for metering "API processing time".

    See https://docs.djangoproject.com/en/4.0/topics/http/middleware/#writing-your-own-middleware
    """

    meter_api_name = "api_processing_time"

    def __init__(self, get_response):
        """
        Set up the middleware, and the background ingestion client.
        """
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)

        response = self.get_response(request)

        self.process_response(request, response)

        return response

    @staticmethod
    def process_request(request):
        """
        Record the start time of the request.
        """
        request._start_time = now_in_millis()

    def process_response(self, request, response):
        """
        Process request handling duration and send metric (enqueue it for
        background batch sending).

        Get the customer_id of the currently logged in user.
        """

        meter_time_in_millis = now_in_millis()
        delta_in_millis = meter_time_in_millis - request._start_time

        customer_id = get_customer_id(request.user)
        logger.debug(
            "Took %s ms on %s for %s", delta_in_millis, request.path, customer_id
        )

        event = create_ingest_payload(
            meter_api_name=self.meter_api_name,
            meter_value=delta_in_millis,
            meter_time_in_millis=meter_time_in_millis,
            customer_id=customer_id,
        )
        ingest_client.send(event)
