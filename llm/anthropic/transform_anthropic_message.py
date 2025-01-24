from ingest.api_client import create_ingest_payload
import time


def transform_anthropic_message(response, meter_api_name, user):
    """
    Takes the Message response from anthropic messages api and transforms it into
    a meter event that can be ingested into Amberflo.
    Requires Amberflo Meter and Amberflo customer to be pre-created
    """

    if response["usage"] is None:
        raise Exception("Anthropic 'usage' not found in response")

    totalTokens = response["usage"]["input_tokens"] + response["usage"]["output_tokens"]

    dimensions = {"model": response["model"], "object": response["object"]}

    event = create_ingest_payload(
        meter_api_name=meter_api_name,
        meter_value=totalTokens,
        meter_time_in_millis=int(round(time() * 1000)),
        customer_id=user,
        dimensions=dimensions,
    )

    return event
