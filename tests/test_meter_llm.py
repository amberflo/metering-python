import unittest
from metering.meter_llm import process_llm_response
from metering.constants import (
    LlmProvider,
    INPUT_TOKENS_METER_API_NAME,
    OUTPUT_TOKENS_METER_API_NAME,
)

meter_api_name_key = "meterApiName"
meter_value_key = "meterValue"
timestamp_key = "meterTimeInMillis"
customer_id_key = "customerId"
unique_id_key = "uniqueId"
dimensions_key = "dimensions"
customer_id = "user123"
EMPTY_DIMENSIONS = {}


class AnthropicResponse:
    class Usage:
        def __init__(self, input_tokens: int, output_tokens: int):
            self.input_tokens = input_tokens
            self.output_tokens = output_tokens

    def __init__(self, type: str, model: str):
        self.type = type
        self.model = model
        self.usage = self.Usage(10, 12)


class OpenAiChatResponse:
    class Usage:
        def __init__(self, prompt_tokens: int, completion_tokens: int):
            self.prompt_tokens = prompt_tokens
            self.completion_tokens = completion_tokens

    def __init__(
        self, model: str, prompt_tokens: int, completion_tokens: int, user: str
    ):
        self.object = "chat.completion"
        self.model = model
        self.usage = self.Usage(prompt_tokens, completion_tokens)
        self.user = user


class OpenAiEmbeddingResponse:
    class Data:
        def __init__(self, object: str):
            self.object = object

    class Usage:
        def __init__(self, prompt_tokens: int):
            self.prompt_tokens = prompt_tokens

    def __init__(self, model: str, object: str):
        self.model = model
        self.data = self.Data(object)
        self.usage = self.Usage(9)


class CohereV1Response:
    class BilledUnits:
        def __init__(self, input_tokens: int, output_tokens: int):
            self.input_tokens = input_tokens
            self.output_tokens = output_tokens

    class Meta:
        def __init__(self, billed_units):
            self.billed_units = billed_units

    def __init__(self):
        self.meta = self.Meta(self.BilledUnits(9, 12))


class CohereV2Response:
    class BilledUnits:
        def __init__(self, input_tokens: int, output_tokens: int):
            self.input_tokens = input_tokens
            self.output_tokens = output_tokens

    class Usage:
        def __init__(self, billed_units):
            self.billed_units = billed_units

    def __init__(self):
        self.usage = self.Usage(self.BilledUnits(9, 12))


class VertexAiResponse:
    class UsageMetadata:
        def __init__(self, promptTokenCount: int, candidatesTokenCount: int):
            self.promptTokenCount = promptTokenCount
            self.candidatesTokenCount = candidatesTokenCount

    def __init__(self, promptTokenCount: int, candidatesTokenCount: int):
        self.usageMetadata = self.UsageMetadata(promptTokenCount, candidatesTokenCount)


class TestProcessLLMReponse(unittest.TestCase):
    def test_anthropic_response(self):
        response = AnthropicResponse("message", "claude-3-5-sonnet-20241022")
        input_tokens_event, output_tokens_event = process_llm_response(
            llm_response=response,
            customer_id=customer_id,
            aflo_dimensions=EMPTY_DIMENSIONS,
        )

        expected_dimensions = {
            "model": response.model,
            "object": response.type,
            "provider": LlmProvider.ANTHROPIC.value,
        }

        self.assertIsNotNone(input_tokens_event[meter_value_key])
        self.assertIsNotNone(input_tokens_event[unique_id_key])
        self.assertIsNotNone(input_tokens_event[timestamp_key])
        self.assertIsNotNone(input_tokens_event[customer_id_key])
        self.assertIsNotNone(input_tokens_event[dimensions_key])
        self.assertEqual(
            input_tokens_event[meter_api_name_key], INPUT_TOKENS_METER_API_NAME
        )
        self.assertEqual(input_tokens_event[meter_value_key], 10)
        self.assertEqual(input_tokens_event[dimensions_key], expected_dimensions)
        self.assertEqual(input_tokens_event[customer_id_key], customer_id)

        self.assertIsNotNone(output_tokens_event[meter_value_key])
        self.assertIsNotNone(output_tokens_event[unique_id_key])
        self.assertIsNotNone(output_tokens_event[timestamp_key])
        self.assertIsNotNone(output_tokens_event[customer_id_key])
        self.assertIsNotNone(output_tokens_event[dimensions_key])
        self.assertEqual(
            output_tokens_event[meter_api_name_key], OUTPUT_TOKENS_METER_API_NAME
        )
        self.assertEqual(output_tokens_event[meter_value_key], 12)
        self.assertEqual(output_tokens_event[dimensions_key], expected_dimensions)
        self.assertEqual(output_tokens_event[customer_id_key], customer_id)

    def test_openai_chat_completion_response(self):
        response = OpenAiChatResponse(
            model="gpt-4o-mini", prompt_tokens=9, completion_tokens=12, user=customer_id
        )
        input_tokens_event, output_tokens_event = process_llm_response(
            llm_response=response,
            customer_id=customer_id,
            aflo_dimensions=EMPTY_DIMENSIONS,
        )

        expected_dimensions = {
            "model": response.model,
            "object": response.object,
            "provider": LlmProvider.OPENAI.value,
        }

        self.assertIsNotNone(input_tokens_event[meter_value_key])
        self.assertIsNotNone(input_tokens_event[unique_id_key])
        self.assertIsNotNone(input_tokens_event[timestamp_key])
        self.assertIsNotNone(input_tokens_event[customer_id_key])
        self.assertIsNotNone(input_tokens_event[dimensions_key])
        self.assertEqual(
            input_tokens_event[meter_api_name_key], INPUT_TOKENS_METER_API_NAME
        )
        self.assertEqual(input_tokens_event[meter_value_key], 9)
        self.assertEqual(input_tokens_event[dimensions_key], expected_dimensions)
        self.assertEqual(input_tokens_event[customer_id_key], customer_id)

        self.assertIsNotNone(output_tokens_event[meter_value_key])
        self.assertIsNotNone(output_tokens_event[unique_id_key])
        self.assertIsNotNone(output_tokens_event[timestamp_key])
        self.assertIsNotNone(output_tokens_event[customer_id_key])
        self.assertIsNotNone(output_tokens_event[dimensions_key])
        self.assertEqual(
            output_tokens_event[meter_api_name_key], OUTPUT_TOKENS_METER_API_NAME
        )
        self.assertEqual(output_tokens_event[meter_value_key], 12)
        self.assertEqual(output_tokens_event[dimensions_key], expected_dimensions)
        self.assertEqual(output_tokens_event[customer_id_key], customer_id)

    def test_openai_embedding_response(self):
        response = OpenAiEmbeddingResponse(
            model="text-embedding-ada-002", object="embedding"
        )
        input_tokens_event, output_tokens_event = process_llm_response(
            llm_response=response,
            customer_id=customer_id,
            aflo_dimensions=EMPTY_DIMENSIONS,
        )

        expected_dimensions = {
            "model": response.model,
            "object": response.data.object,
            "provider": LlmProvider.OPENAI.value,
        }

        self.assertIsNotNone(input_tokens_event[meter_value_key])
        self.assertIsNotNone(input_tokens_event[unique_id_key])
        self.assertIsNotNone(input_tokens_event[timestamp_key])
        self.assertIsNotNone(input_tokens_event[customer_id_key])
        self.assertIsNotNone(input_tokens_event[dimensions_key])
        self.assertEqual(
            input_tokens_event[meter_api_name_key], INPUT_TOKENS_METER_API_NAME
        )
        self.assertEqual(input_tokens_event[meter_value_key], 9)
        self.assertEqual(input_tokens_event[dimensions_key], expected_dimensions)
        self.assertEqual(input_tokens_event[customer_id_key], customer_id)

        self.assertEqual(output_tokens_event, None)

    def test_cohere_v1_response(self):
        response = CohereV1Response()
        input_tokens_event, output_tokens_event = process_llm_response(
            llm_response=response,
            customer_id=customer_id,
            aflo_dimensions=EMPTY_DIMENSIONS,
        )

        expected_dimensions = {
            "model": "unknown model",
            "object": "text",
            "provider": LlmProvider.COHERE.value,
        }

        self.assertIsNotNone(input_tokens_event[meter_value_key])
        self.assertIsNotNone(input_tokens_event[unique_id_key])
        self.assertIsNotNone(input_tokens_event[timestamp_key])
        self.assertIsNotNone(input_tokens_event[customer_id_key])
        self.assertIsNotNone(input_tokens_event[dimensions_key])
        self.assertEqual(
            input_tokens_event[meter_api_name_key], INPUT_TOKENS_METER_API_NAME
        )
        self.assertEqual(input_tokens_event[meter_value_key], 9)
        self.assertEqual(input_tokens_event[dimensions_key], expected_dimensions)
        self.assertEqual(input_tokens_event[customer_id_key], customer_id)

        self.assertIsNotNone(output_tokens_event[meter_value_key])
        self.assertIsNotNone(output_tokens_event[unique_id_key])
        self.assertIsNotNone(output_tokens_event[timestamp_key])
        self.assertIsNotNone(output_tokens_event[customer_id_key])
        self.assertIsNotNone(output_tokens_event[dimensions_key])
        self.assertEqual(
            output_tokens_event[meter_api_name_key], OUTPUT_TOKENS_METER_API_NAME
        )
        self.assertEqual(output_tokens_event[meter_value_key], 12)
        self.assertEqual(output_tokens_event[dimensions_key], expected_dimensions)
        self.assertEqual(output_tokens_event[customer_id_key], customer_id)

    def test_cohere_v2_response(self):
        response = CohereV2Response()
        input_tokens_event, output_tokens_event = process_llm_response(
            llm_response=response,
            customer_id=customer_id,
            aflo_dimensions=EMPTY_DIMENSIONS,
        )

        expected_dimensions = {
            "model": "unknown model",
            "object": "text",
            "provider": LlmProvider.COHERE.value,
        }

        self.assertIsNotNone(input_tokens_event[meter_value_key])
        self.assertIsNotNone(input_tokens_event[unique_id_key])
        self.assertIsNotNone(input_tokens_event[timestamp_key])
        self.assertIsNotNone(input_tokens_event[customer_id_key])
        self.assertIsNotNone(input_tokens_event[dimensions_key])
        self.assertEqual(
            input_tokens_event[meter_api_name_key], INPUT_TOKENS_METER_API_NAME
        )
        self.assertEqual(input_tokens_event[meter_value_key], 9)
        self.assertEqual(input_tokens_event[dimensions_key], expected_dimensions)
        self.assertEqual(input_tokens_event[customer_id_key], customer_id)

        self.assertIsNotNone(output_tokens_event[meter_value_key])
        self.assertIsNotNone(output_tokens_event[unique_id_key])
        self.assertIsNotNone(output_tokens_event[timestamp_key])
        self.assertIsNotNone(output_tokens_event[customer_id_key])
        self.assertIsNotNone(output_tokens_event[dimensions_key])
        self.assertEqual(
            output_tokens_event[meter_api_name_key], OUTPUT_TOKENS_METER_API_NAME
        )
        self.assertEqual(output_tokens_event[meter_value_key], 12)
        self.assertEqual(output_tokens_event[dimensions_key], expected_dimensions)
        self.assertEqual(output_tokens_event[customer_id_key], customer_id)

    def test_vertexai_response(self):
        response = VertexAiResponse(promptTokenCount=9, candidatesTokenCount=12)
        input_tokens_event, output_tokens_event = process_llm_response(
            llm_response=response,
            customer_id=customer_id,
            aflo_dimensions=EMPTY_DIMENSIONS,
        )

        expected_dimensions = {
            "model": "unknown model",
            "object": "vertexCompletion",
            "provider": LlmProvider.VERTEXAI.value,
        }

        self.assertIsNotNone(input_tokens_event[meter_value_key])
        self.assertIsNotNone(input_tokens_event[unique_id_key])
        self.assertIsNotNone(input_tokens_event[timestamp_key])
        self.assertIsNotNone(input_tokens_event[customer_id_key])
        self.assertIsNotNone(input_tokens_event[dimensions_key])
        self.assertEqual(
            input_tokens_event[meter_api_name_key], INPUT_TOKENS_METER_API_NAME
        )
        self.assertEqual(input_tokens_event[meter_value_key], 9)
        self.assertEqual(input_tokens_event[dimensions_key], expected_dimensions)
        self.assertEqual(input_tokens_event[customer_id_key], customer_id)

        self.assertIsNotNone(output_tokens_event[meter_value_key])
        self.assertIsNotNone(output_tokens_event[unique_id_key])
        self.assertIsNotNone(output_tokens_event[timestamp_key])
        self.assertIsNotNone(output_tokens_event[customer_id_key])
        self.assertIsNotNone(output_tokens_event[dimensions_key])
        self.assertEqual(
            output_tokens_event[meter_api_name_key], OUTPUT_TOKENS_METER_API_NAME
        )
        self.assertEqual(output_tokens_event[meter_value_key], 12)
        self.assertEqual(output_tokens_event[dimensions_key], expected_dimensions)
        self.assertEqual(output_tokens_event[customer_id_key], customer_id)
