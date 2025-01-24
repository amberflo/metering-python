from metering.ingest.api_client import create_ingest_payload
from time import time


def create_input_tokens_event(response, user):
    """
    Takes either the ChatCompletion or embeddings object from openai and transforms it into
    a meter event that can be ingested into Amberflo.
    Requires Amberflo Meter and Amberflo customer to be pre-created

    This function creates a payload for the provisioned meter: input_tokens
    Please reach out to Amberflo for us to provision the meter
    """

    if response.usage is None:
        raise Exception("OpenAi 'usage' not found in response")

    if response.object == "chat.completion":
        input_tokens = response.usage.prompt_tokens
        dimensions = {
            "model": response.model,
            "object": response.object,
            "provider": "openai",
        }

        input_tokens_event = create_ingest_payload(
            meter_api_name="input_tokens",
            meter_value=input_tokens,
            meter_time_in_millis=int(round(time() * 1000)),
            customer_id=user,
            dimensions=dimensions,
        )
        return input_tokens_event

    if response.data.object == "embedding":
        input_tokens = response.usage.prompt_tokens
        dimensions = {
            "model": response.model,
            "object": response.object,
            "provider": "openai",
        }
        input_tokens_event = create_ingest_payload(
            meter_api_name="input_tokens",
            meter_value=input_tokens,
            meter_time_in_millis=int(round(time() * 1000)),
            customer_id=user,
            dimensions=dimensions,
        )
        return input_tokens_event


def create_output_tokens_event(response, user):
    """
    Similar to the above function but creates a payload for the provisioned meter: output_tokens
    Please reach out to Amberflo for us to provision the meter
    """

    if response.usage is None:
        raise Exception("OpenAi 'usage' not found in response")

    if response.object == "chat.completion":
        output_tokens = response.usage.completion_tokens
        dimensions = {
            "model": response.model,
            "object": response.object,
            "provider": "openai",
        }

        output_tokens_event = create_ingest_payload(
            meter_api_name="output_tokens",
            meter_value=output_tokens,
            meter_time_in_millis=int(round(time() * 1000)),
            customer_id=user,
            dimensions=dimensions,
        )
        return output_tokens_event
