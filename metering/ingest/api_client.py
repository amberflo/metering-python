from uuid import uuid4, UUID

from metering import validators
from metering.session import IngestSession


class IngestApiClient:
    """
    See: https://docs.amberflo.io/reference/post_ingest
    """

    path = "/ingest/"

    def __init__(self, api_key):
        """
        Initialize the API client session.
        """
        self.client = IngestSession(api_key)

    def send(self, payload):
        """
        Send one or many meter events.

        Create a payload using the `create_ingest_payload` function.

        See: https://docs.amberflo.io/reference/post_ingest
        """
        return self.client.post(self.path, payload)


def create_ingest_payload(
    meter_api_name,
    meter_value,
    meter_time_in_millis,
    customer_id,
    dimensions=None,
    unique_id=None,
):
    """
    meter_api_name: String.

    meter_value: Number.

    meter_time_in_millis: Positive integer. Unix epoch time.
        Pay attention for this argument as two meters (with the same name) that
        are sent to Amberflo at the exact same time (and have the same unique
        id) will be deduped by the server.

    customer_id: String.

    unique_id: Optional. String. Defaults to a uuid4 value.
        This parameter can help the server tell if the meter is indeed a dup or
        not in case there are two meters with the same name that are sent to
        the server at the same time.

    dimensions: Optional. Dictionary of String to String.
        Here you can specify more partition properies which which can help you
        analize your data.

    See: https://docs.amberflo.io/reference/post_ingest
    """

    validators.require_string("meter_api_name", meter_api_name, allow_none=False)
    validators.require("meter_value", meter_value, (int, float), allow_none=False)
    validators.require_positive_int(
        "meter_time_in_millis", meter_time_in_millis, allow_none=False
    )
    validators.require_string("customer_id", customer_id, allow_none=False)

    if isinstance(unique_id, UUID):
        unique_id = str(unique_id)

    validators.require_string("unique_id", unique_id)
    validators.require_string_dictionary("dimensions", dimensions)

    payload = {
        "uniqueId": unique_id or str(uuid4()),
        "meterApiName": meter_api_name,
        "meterValue": meter_value,
        "customerId": customer_id,
        "meterTimeInMillis": meter_time_in_millis,
    }

    if dimensions is not None:
        payload["dimensions"] = dimensions

    return payload
