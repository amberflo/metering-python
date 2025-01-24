import unittest
from unittest.mock import Mock
from llm.openai.transform_open_ai_response import (
    create_input_tokens_event,
    create_output_tokens_event,
)


meter_api_name_key = "meterApiName"
meter_value_key = "meterValue"
timestamp_key = "meterTimeInMillis"
customer_id_key = "customerId"
unique_id_key = "uniqueId"
dimensions_key = "dimensions"


class TestTransformOpenAiResponse(unittest.TestCase):

    user = "user123"

    fake_response = Mock()
    fake_response.object = "chat.completion"
    fake_response.model = "gpt-4o-mini"
    fake_response.usage = Mock(prompt_tokens=9, completion_tokens=12, total_tokens=21)
    fake_response.choices = [
        Mock(
            index=0,
            message=Mock(
                role="assistant", content="Hello there, how may I assist you today?"
            ),
            logprobs=None,
            finish_reason="stop",
        )
    ]
    fake_response.user = user

    def test_create_input_tokens_event(self):
        input_tokens_event = create_input_tokens_event(
            response=self.fake_response, user=self.user
        )

        expected_dimensions = {
            "model": self.fake_response.model,
            "object": self.fake_response.object,
            "provider": "openai",
        }

        self.assertIsNotNone(input_tokens_event[meter_value_key])
        self.assertIsNotNone(input_tokens_event[unique_id_key])
        self.assertIsNotNone(input_tokens_event[timestamp_key])
        self.assertIsNotNone(input_tokens_event[customer_id_key])
        self.assertIsNotNone(input_tokens_event[dimensions_key])
        self.assertEqual(input_tokens_event[meter_api_name_key], "input_tokens")
        self.assertEqual(input_tokens_event[meter_value_key], 9)
        self.assertEqual(input_tokens_event[dimensions_key], expected_dimensions)
        self.assertEqual(input_tokens_event[customer_id_key], self.user)

    def test_create_output_tokens_event(self):
        output_tokens_event = create_output_tokens_event(
            response=self.fake_response, user=self.user
        )

        expected_dimensions = {
            "model": self.fake_response.model,
            "object": self.fake_response.object,
            "provider": "openai",
        }
        self.assertIsNotNone(output_tokens_event[meter_value_key])
        self.assertIsNotNone(output_tokens_event[unique_id_key])
        self.assertIsNotNone(output_tokens_event[timestamp_key])
        self.assertIsNotNone(output_tokens_event[customer_id_key])
        self.assertIsNotNone(output_tokens_event[dimensions_key])
        self.assertEqual(output_tokens_event[meter_api_name_key], "output_tokens")
        self.assertEqual(output_tokens_event[meter_value_key], 12)
        self.assertEqual(output_tokens_event[dimensions_key], expected_dimensions)
        self.assertEqual(output_tokens_event[customer_id_key], self.user)
