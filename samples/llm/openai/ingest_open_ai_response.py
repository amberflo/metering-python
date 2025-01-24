#!/usr/bin/env python3

"""
This sample shows an example of how to call OpenAi for chat completion, 
and then ingest the tokens consumed from the response into Amberflo.
"""

import os
from openai import OpenAI
from metering.ingest import create_ingest_client
from llm.openai.transform_open_ai_response import (
    create_input_tokens_event,
    create_output_tokens_event,
)


def call_open_ai_chat_completion(user):
    client = OpenAI()

    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "write me a hiaku about metering and analytics",
            },
        ],
        user=user,
    )


def main():
    USER = "marketing_department"

    # 1. initialize the threaded ingestion client
    client = create_ingest_client(api_key=os.environ.get("API_KEY"))

    # 2. execute the openai call
    open_ai_response = call_open_ai_chat_completion(user=USER)

    # 3. transform the event for ingestion into Amberflo
    input_token_event = create_input_tokens_event(response=open_ai_response, user=USER)
    output_token_event = create_output_tokens_event(
        response=open_ai_response, user=USER
    )

    # 4. send the transformed events
    client.send(input_token_event)
    client.send(output_token_event)

    # 5. ensure all events are sent and safely stop the background threads
    client.shutdown()


if __name__ == "__main__":
    main()
