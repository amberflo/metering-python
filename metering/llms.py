import atexit
import logging
import os
from time import time
from metering.ingest import create_ingest_client
from metering.ingest.api_client import create_ingest_payload


INPUT_TOKENS_METER_API_NAME = "input_tokens"
OUTPUT_TOKENS_METER_API_NAME = "output_tokens"
ANTHROPIC_PROVIDER = "anthropic"
OPENAI_PROVIDER = "openai"
COHERE_PROVIDER = "cohere"
VERTEXAI_PROVIDER = "vertexai"
UNKNOWN_PROVIDER = "unknown"

logger = logging.getLogger(__name__)

_default_client = None


def customer_id_getter(kwargs):
    return kwargs.get("customer_id", "test_customer")


def aflo_dimensions_getter(kwargs):
    return kwargs.get("aflo_dimensions", {})


def _get_default_client():
    global _default_client
    if not _default_client:
        _default_client = create_ingest_client(api_key=os.environ.get("API_KEY"))
        atexit.register(_default_client.shutdown)
    return _default_client


def meter_llm(
    customer_id_getter=customer_id_getter,
    dimensions_getter=aflo_dimensions_getter,
    metering_client=None,
):
    if metering_client is None:
        metering_client = _get_default_client()

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Try and grab a customer_id and dimensions from the function arguments
            customer_id = customer_id_getter(kwargs)
            aflo_dimensions = dimensions_getter(kwargs)

            llm_response = func(*args, **kwargs)

            events = extract_ingest_messages(
                llm_response=llm_response,
                customer_id=customer_id,
                aflo_dimensions=aflo_dimensions,
            )
            for event in events:
                try:
                    logger.debug(f"Sending event: {event}")
                    metering_client.send(event)
                except Exception as e:
                    logger.error(f"Failed to send event: {event} with error: {e}")

            return llm_response

        return wrapper

    return decorator


def _create_event(
    meter_api_name: str, meter_value: float, customer_id: str, dimensions: dict
):
    """Helper function to create a single ingestion payload aka an event."""

    return create_ingest_payload(
        meter_api_name=meter_api_name,
        meter_value=meter_value,
        meter_time_in_millis=int(round(time() * 1000)),
        customer_id=customer_id,
        dimensions=dimensions,
    )


def extract_ingest_messages(
    llm_response: object, customer_id: str, aflo_dimensions: dict
):
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
        logger.debug("No usage found in llm response")
        return []  # If no usage found, don't raise exception but return None

    if getattr(llm_response, "usage", None):
        # Anthropic
        if getattr(llm_response, "type", None) == "message":
            dimensions = _build_dimensions(
                llm_response.model,
                llm_response.type,
                ANTHROPIC_PROVIDER,
                aflo_dimensions,
            )
            return [
                _create_event(
                    INPUT_TOKENS_METER_API_NAME,
                    llm_response.usage.input_tokens,
                    customer_id,
                    dimensions,
                ),
                _create_event(
                    OUTPUT_TOKENS_METER_API_NAME,
                    llm_response.usage.output_tokens,
                    customer_id,
                    dimensions,
                ),
            ]

        # OpenAI Chat
        if getattr(llm_response, "object", None) == "chat.completion":
            dimensions = _build_dimensions(
                llm_response.model,
                llm_response.object,
                OPENAI_PROVIDER,
                aflo_dimensions,
            )
            return [
                _create_event(
                    INPUT_TOKENS_METER_API_NAME,
                    llm_response.usage.prompt_tokens,
                    customer_id,
                    dimensions,
                ),
                _create_event(
                    OUTPUT_TOKENS_METER_API_NAME,
                    llm_response.usage.completion_tokens,
                    customer_id,
                    dimensions,
                ),
            ]

        # OpenAI Embedding
        if (
            getattr(llm_response, "data", None)
            and getattr(llm_response.data, "object", None) == "embedding"
        ):
            dimensions = _build_dimensions(
                llm_response.model,
                llm_response.data.object,
                OPENAI_PROVIDER,
                aflo_dimensions,
            )
            return [
                _create_event(
                    INPUT_TOKENS_METER_API_NAME,
                    llm_response.usage.prompt_tokens,
                    customer_id,
                    dimensions,
                )
            ]

        # Cohere v2 chat
        if getattr(llm_response.usage, "billed_units", None):
            dimensions = _build_dimensions(
                "unknown model", "text", COHERE_PROVIDER, aflo_dimensions
            )
            return [
                _create_event(
                    INPUT_TOKENS_METER_API_NAME,
                    llm_response.usage.billed_units.input_tokens,
                    customer_id,
                    dimensions,
                ),
                _create_event(
                    OUTPUT_TOKENS_METER_API_NAME,
                    llm_response.usage.billed_units.output_tokens,
                    customer_id,
                    dimensions,
                ),
            ]

    # Cohere v1 chat
    if getattr(llm_response, "meta", None) and getattr(
        llm_response.meta, "billed_units", None
    ):
        dimensions = _build_dimensions(
            "unknown model", "text", COHERE_PROVIDER, aflo_dimensions
        )
        return [
            _create_event(
                INPUT_TOKENS_METER_API_NAME,
                llm_response.meta.billed_units.input_tokens,
                customer_id,
                dimensions,
            ),
            _create_event(
                OUTPUT_TOKENS_METER_API_NAME,
                llm_response.meta.billed_units.output_tokens,
                customer_id,
                dimensions,
            ),
        ]

    # Google VertexAI
    if getattr(llm_response, "usageMetadata", None):
        dimensions = _build_dimensions(
            "unknown model",
            "vertexCompletion",
            VERTEXAI_PROVIDER,
            aflo_dimensions,
        )
        return [
            _create_event(
                INPUT_TOKENS_METER_API_NAME,
                llm_response.usageMetadata.promptTokenCount,
                customer_id,
                dimensions,
            ),
            _create_event(
                OUTPUT_TOKENS_METER_API_NAME,
                llm_response.usageMetadata.candidatesTokenCount,
                customer_id,
                dimensions,
            ),
        ]

    logger.debug("No known llm provider matched")
    return []


def _build_dimensions(model: str, object: str, provider: str, dimensions: dict = {}):

    base_llm_dimensions = {
        "model": model,
        "object": object,
        "provider": provider,
    }
    return {**base_llm_dimensions, **(dimensions)}
