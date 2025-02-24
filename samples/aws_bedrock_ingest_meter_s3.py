"""
This sample demonstrates how to ingest AWS Bedrock 
LLM responses as meter events via S3 using boto3.
Ingestion occurs in batches on a background thread to support high throughput, 
making it particularly useful in web server environments by 
offloading ingestion from the request-response cycle.

Instead of the Amberflo API, this approach utilizes the S3 meter record sink.

For more details, see:
https://docs.amberflo.io/docs/s3-ingestion
https://docs.amberflo.io/reference/ingest-meter-records
"""

import boto3
import json
import logging
import os
from time import time
from metering.ingest import create_ingest_client, create_ingest_payload

# Initialize the AWS Bedrock client
REGION = "us-west-2"
bedrock_client = boto3.client("bedrock-runtime", region_name=REGION)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Create Amberflo's ingestion client
# during app initialization
# provide the s3 bucket name, access key, and secret key
# In this sample, environment variables are used
metering_client = create_ingest_client(
    bucket_name=os.environ.get("BUCKET_NAME"),
    access_key=os.environ.get("ACCESS_KEY"),
    secret_key=os.environ.get("SECRET_KEY"),
)


def get_chat_completion(prompt):
    return bedrock_client.invoke_model(
        modelId="anthropic.claude-3-5-haiku-20241022-v1:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 256,
                "temperature": 0.7,
            }
        ),
    )


def now_in_millis():
    return int(round(time() * 1000))


def ingest_llm_response(llm_result, metering_client, llm_context, caller_context):
    input_tokens = llm_result.get("usage", {}).get("input_tokens", 0)
    output_tokens = llm_result.get("usage", {}).get("output_tokens", 0)
    content_items = llm_result.get("content", [])
    content_type = (
        content_items[0].get("type", "unknown") if content_items else "unknown"
    )

    # Construct meter event dimensions
    dimensions = {
        "model": llm_result.get("model"),
        "provider": llm_context.get("provider"),
        "region": llm_context.get("region"),
        "batch": llm_context.get("batch"),
        "model_type": content_type,
        "user_id": caller_context.get("user_id"),
        "app": caller_context.get("app"),
    }

    logger.info(
        "AFLO_LLM: %s, afloDimensions: %s",
        json.dumps(llm_result, indent=4),
        json.dumps(dimensions, indent=4),
    )

    input_token_event = create_ingest_payload(
        meter_api_name="amazon_bedrock_input_tokens",
        meter_time_in_millis=now_in_millis(),
        meter_value=input_tokens,
        customer_id=caller_context.get("department"),
        dimensions=dimensions,
        # unique_id is the LLM response id
        # and can link input and output tokens
        unique_id=llm_result.get("id"),
    )
    metering_client.send(input_token_event)

    output_tokens_event = create_ingest_payload(
        meter_api_name="amazon_bedrock_output_tokens",
        meter_time_in_millis=now_in_millis(),
        meter_value=output_tokens,
        customer_id=caller_context.get("department"),
        dimensions=dimensions,
        unique_id=llm_result.get("id"),
    )
    metering_client.send(output_tokens_event)


def main():

    # Caller context
    caller_context = {
        "user_id": "talha",
        "app": "sales-chatbot",
        "department": "sales",
    }

    # LLM input
    prompt = "Hello, how can I assist you today?"

    # LLM interaction
    # Invoke the AWS Bedrock model
    response = get_chat_completion(prompt)
    llm_result = json.loads(response["body"].read().decode("utf-8"))

    llm_context = {"batch": "false", "provider": "antrhopic", "region": REGION}
    ingest_llm_response(llm_result, metering_client, llm_context, caller_context)

    # Graceful shutdown of the Amberflo ingestion client
    # to be called during app shutdown
    metering_client.shutdown()


if __name__ == "__main__":
    main()
