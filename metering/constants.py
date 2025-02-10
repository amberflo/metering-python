from enum import Enum


class LlmProvider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    COHERE = "cohere"
    VERTEXAI = "vertexai"
    UNKNOWN = "unknown"


DEFAULT_PRODUCT_ID = "1"
INPUT_TOKENS_METER_API_NAME = "input_tokens"
OUTPUT_TOKENS_METER_API_NAME = "output_tokens"
