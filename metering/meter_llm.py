import os
from time import time
from metering import create_ingest_client
from metering.ingest.api_client import create_ingest_payload
from metering.constants import (
    LlmProvider,
    INPUT_TOKENS_METER_API_NAME,
    OUTPUT_TOKENS_METER_API_NAME,
)


def customer_id_getter(kwargs):
    return kwargs.get("customer_id", "test_customer")


def aflo_dimensions_getter(kwargs):
    return kwargs.get("aflo_dimensions", {})


def meter_llm(
    customer_id_getter=customer_id_getter,
    dimensions_getter=aflo_dimensions_getter,
    metering_client=None,
):
    if metering_client is None:
        metering_client = create_ingest_client(os.environ.get("API_KEY"))

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Try and grab a customer_id and dimensions from the function arguments
            customer_id = customer_id_getter(kwargs)
            aflo_dimensions = dimensions_getter(kwargs)

            llm_response = func(*args, **kwargs)
            print(llm_response)
            events = process_llm_response(
                llm_response=llm_response,
                customer_id=customer_id,
                aflo_dimensions=aflo_dimensions,
            )
            events = [event for event in events if event is not None]
            for event in events:
                print(event)
                # Uncomment to actually send event to Aflo
                metering_client.send(event)

            print("Shutting down metering client")
            metering_client.shutdown()
            print("Metering client shut down")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def create_payloads(
    meter_api_name: str, meter_value: float, customer_id: str, dimensions: dict
):
    """Helper function to create ingestion payloads."""

    return create_ingest_payload(
        meter_api_name=meter_api_name,
        meter_value=meter_value,
        meter_time_in_millis=int(round(time() * 1000)),
        customer_id=customer_id,
        dimensions=dimensions,
    )


def process_llm_response(llm_response: object, customer_id: str, aflo_dimensions: dict):
    """
    Processes certain LLM provider chat completion or embedding response and returns token usage payloads.
    We currently support Anthropic Messages, OpenAI Chat, OpenAI Embedding, Cohere v1 Chat, Cohere v2 Chat,
    and Google VertexAI generateContent responses.
    """
    if not any(
        [
            getattr(llm_response, "usage", None),
            getattr(llm_response, "meta", None)
            and getattr(llm_response.meta, "billed_units", None),
            getattr(llm_response, "usageMetadata", None),
        ]
    ):
        return None, None  # If no usage found, don't raise exception but return None

    if getattr(llm_response, "usage", None):
        # Anthropic
        if getattr(llm_response, "type", None) == "message":
            dimensions = build_dimensions(
                llm_response.model,
                llm_response.type,
                LlmProvider.ANTHROPIC.value,
                aflo_dimensions,
            )
            return (
                create_payloads(
                    INPUT_TOKENS_METER_API_NAME,
                    llm_response.usage.input_tokens,
                    customer_id,
                    dimensions,
                ),
                create_payloads(
                    OUTPUT_TOKENS_METER_API_NAME,
                    llm_response.usage.output_tokens,
                    customer_id,
                    dimensions,
                ),
            )

        # OpenAI Chat
        if getattr(llm_response, "object", None) == "chat.completion":
            dimensions = build_dimensions(
                llm_response.model,
                llm_response.object,
                LlmProvider.OPENAI.value,
                aflo_dimensions,
            )
            return (
                create_payloads(
                    INPUT_TOKENS_METER_API_NAME,
                    llm_response.usage.prompt_tokens,
                    customer_id,
                    dimensions,
                ),
                create_payloads(
                    OUTPUT_TOKENS_METER_API_NAME,
                    llm_response.usage.completion_tokens,
                    customer_id,
                    dimensions,
                ),
            )

        # OpenAI Embedding
        if (
            getattr(llm_response, "data", None)
            and getattr(llm_response.data, "object", None) == "embedding"
        ):
            dimensions = build_dimensions(
                llm_response.model,
                llm_response.data.object,
                LlmProvider.OPENAI.value,
                aflo_dimensions,
            )
            return (
                create_payloads(
                    INPUT_TOKENS_METER_API_NAME,
                    llm_response.usage.prompt_tokens,
                    customer_id,
                    dimensions,
                ),
                None,
            )

        # Cohere v2 chat
        if getattr(llm_response.usage, "billed_units", None):
            dimensions = build_dimensions(
                "unknown model", "text", LlmProvider.COHERE.value, aflo_dimensions
            )
            return (
                create_payloads(
                    INPUT_TOKENS_METER_API_NAME,
                    llm_response.usage.billed_units.input_tokens,
                    customer_id,
                    dimensions,
                ),
                create_payloads(
                    OUTPUT_TOKENS_METER_API_NAME,
                    llm_response.usage.billed_units.output_tokens,
                    customer_id,
                    dimensions,
                ),
            )

    # Cohere v1 chat
    if getattr(llm_response, "meta", None) and getattr(
        llm_response.meta, "billed_units", None
    ):
        dimensions = build_dimensions(
            "unknown model", "text", LlmProvider.COHERE.value, aflo_dimensions
        )
        return (
            create_payloads(
                INPUT_TOKENS_METER_API_NAME,
                llm_response.meta.billed_units.input_tokens,
                customer_id,
                dimensions,
            ),
            create_payloads(
                OUTPUT_TOKENS_METER_API_NAME,
                llm_response.meta.billed_units.output_tokens,
                customer_id,
                dimensions,
            ),
        )

    # Google VertexAI
    if getattr(llm_response, "usageMetadata", None):
        dimensions = build_dimensions(
            "unknown model",
            "vertexCompletion",
            LlmProvider.VERTEXAI.value,
            aflo_dimensions,
        )
        return (
            create_payloads(
                INPUT_TOKENS_METER_API_NAME,
                llm_response.usageMetadata.promptTokenCount,
                customer_id,
                dimensions,
            ),
            create_payloads(
                OUTPUT_TOKENS_METER_API_NAME,
                llm_response.usageMetadata.candidatesTokenCount,
                customer_id,
                dimensions,
            ),
        )

    # TODO @vgeorgewillv add logger
    print("No known provider matched")
    return None, None  # If no known provider matched


def build_dimensions(model: str, object: str, provider: str, dimensions: dict = None):

    base_llm_dimensions = {
        "model": model,
        "object": object,
        "provider": provider,
    }
    return {**base_llm_dimensions, **(dimensions)}
