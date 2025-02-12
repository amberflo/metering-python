import atexit
import unittest
from unittest.mock import MagicMock, patch
from metering import meter_llm
from metering.llms import extract_ingest_messages

meter_api_name_key = "meterApiName"
meter_value_key = "meterValue"
timestamp_key = "meterTimeInMillis"
customer_id_key = "customerId"
unique_id_key = "uniqueId"
dimensions_key = "dimensions"
customer_id = "user123"
INPUT_TOKENS_METER_API_NAME = "input_tokens"
OUTPUT_TOKENS_METER_API_NAME = "output_tokens"
ANTHROPIC_PROVIDER = "anthropic"
OPENAI_PROVIDER = "openai"
COHERE_PROVIDER = "cohere"
VERTEXAI_PROVIDER = "vertexai"
UNKNOWN_PROVIDER = "unknown"
EMPTY_DIMENSIONS = {}


class AnthropicResponse:
    class Usage:
        def __init__(self, input_tokens: int, output_tokens: int):
            self.input_tokens = input_tokens
            self.output_tokens = output_tokens

    def __init__(self, type: str, model: str):
        self.type = type
        self.model = model
        self.usage = self.Usage(9, 12)


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
        input_tokens_event, output_tokens_event = extract_ingest_messages(
            llm_response=response,
            customer_id=customer_id,
            aflo_dimensions=EMPTY_DIMENSIONS,
        )

        expected_dimensions = {
            "model": response.model,
            "object": response.type,
            "provider": ANTHROPIC_PROVIDER,
        }

        make_input_token_assertions(self, input_tokens_event, expected_dimensions)
        make_output_token_assertions(self, output_tokens_event, expected_dimensions)

    def test_openai_chat_completion_response(self):
        response = OpenAiChatResponse(
            model="gpt-4o-mini", prompt_tokens=9, completion_tokens=12, user=customer_id
        )
        input_tokens_event, output_tokens_event = extract_ingest_messages(
            llm_response=response,
            customer_id=customer_id,
            aflo_dimensions=EMPTY_DIMENSIONS,
        )

        expected_dimensions = {
            "model": response.model,
            "object": response.object,
            "provider": OPENAI_PROVIDER,
        }

        make_input_token_assertions(self, input_tokens_event, expected_dimensions)
        make_output_token_assertions(self, output_tokens_event, expected_dimensions)

    def test_openai_embedding_response(self):
        response = OpenAiEmbeddingResponse(
            model="text-embedding-ada-002", object="embedding"
        )
        input_tokens_event = extract_ingest_messages(
            llm_response=response,
            customer_id=customer_id,
            aflo_dimensions=EMPTY_DIMENSIONS,
        )[0]

        expected_dimensions = {
            "model": response.model,
            "object": response.data.object,
            "provider": OPENAI_PROVIDER,
        }

        make_input_token_assertions(self, input_tokens_event, expected_dimensions)

    def test_cohere_v1_response(self):
        response = CohereV1Response()
        input_tokens_event, output_tokens_event = extract_ingest_messages(
            llm_response=response,
            customer_id=customer_id,
            aflo_dimensions=EMPTY_DIMENSIONS,
        )

        expected_dimensions = {
            "model": "unknown model",
            "object": "text",
            "provider": COHERE_PROVIDER,
        }

        make_input_token_assertions(self, input_tokens_event, expected_dimensions)
        make_output_token_assertions(self, output_tokens_event, expected_dimensions)

    def test_cohere_v2_response(self):
        response = CohereV2Response()
        input_tokens_event, output_tokens_event = extract_ingest_messages(
            llm_response=response,
            customer_id=customer_id,
            aflo_dimensions=EMPTY_DIMENSIONS,
        )

        expected_dimensions = {
            "model": "unknown model",
            "object": "text",
            "provider": COHERE_PROVIDER,
        }

        make_input_token_assertions(self, input_tokens_event, expected_dimensions)
        make_output_token_assertions(self, output_tokens_event, expected_dimensions)

    def test_vertexai_response(self):
        response = VertexAiResponse(promptTokenCount=9, candidatesTokenCount=12)
        input_tokens_event, output_tokens_event = extract_ingest_messages(
            llm_response=response,
            customer_id=customer_id,
            aflo_dimensions=EMPTY_DIMENSIONS,
        )

        expected_dimensions = {
            "model": "unknown model",
            "object": "vertexCompletion",
            "provider": VERTEXAI_PROVIDER,
        }

        make_input_token_assertions(self, input_tokens_event, expected_dimensions)
        make_output_token_assertions(self, output_tokens_event, expected_dimensions)


class TestMeterLLMDecorator(unittest.TestCase):
    @patch("metering.llms.create_ingest_client")  # Mock the client creation
    def test_meter_llm_calls_shutdown_with_passed_client(
        self, mock_create_ingest_client
    ):
        # Mock metering client
        mock_client = MagicMock()
        mock_create_ingest_client.return_value = mock_client

        print(f"Mock client: {mock_client}")

        @meter_llm(metering_client=mock_client)
        def dummy_llm_function():
            return AnthropicResponse("message", "claude-3-5-sonnet-20241022")

        dummy_llm_function()

        mock_client.shutdown.assert_not_called()  # Not called yet
        self.assertEqual(mock_client.send.call_count, 2)  # Two calls to send

        # Simulate process exit and check if shutdown was called
        atexit._run_exitfuncs()  # Manually trigger atexit functions
        mock_client.shutdown.assert_called_once()

    @patch("metering.llms.create_ingest_client")  # Mock the client creation
    def test_meter_llm_calls_shutdown_with_no_client(self, mock_create_ingest_client):
        # Mock metering client
        mock_client = MagicMock()
        mock_create_ingest_client.return_value = mock_client

        @meter_llm()
        def dummy_llm_function():
            return AnthropicResponse("message", "claude-3-5-sonnet-20241022")

        dummy_llm_function()

        # Assert that metering_client.shutdown was registered
        mock_client.shutdown.assert_not_called()  # Not called yet
        self.assertEqual(mock_client.send.call_count, 2)  # Two calls to send

        # Simulate process exit and check if shutdown was called
        atexit._run_exitfuncs()  # Manually trigger atexit functions
        mock_client.shutdown.assert_called_once()


def make_input_token_assertions(self, input_tokens_event, expected_dimensions):
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


def make_output_token_assertions(self, output_tokens_event, expected_dimensions):
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
