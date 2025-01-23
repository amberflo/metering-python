#!/usr/bin/env python3

"""
This sample shows an example of how to create a meter to meter OpenAi tokens consumed,
create a customer for use in Amebrflo, call OpenAi for chat completion, 
and then ingest the tokens consumed from the response into Amberflo.
"""

import os
import requests
import json
from openai import OpenAI
from metering.ingest import create_ingest_client
from metering.llm.openai.transform_open_ai_response import (
    transform_open_ai_chat_completion,
)


def create_open_ai_chat_completion_meter():
    url = "https://app.amberflo.io/meters"

    payload = json.dumps(
        {
            "label": "openAiChatCompletionMeter",
            "meterApiName": "openAiChatCompletionMeter",
            "meterType": "sum_of_all_usage",
            "dimensions": ["model", "object"],
        }
    )
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.text


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

    # 2. create the meter - once created the below line can be commented out, as meters need to be created once
    meter_response = create_open_ai_chat_completion_meter()

    # 3. execute the openai call
    open_ai_response = call_open_ai_chat_completion(user=USER)

    # 4. transform the event for ingestion into Amberflo
    event = transform_open_ai_chat_completion(
        response=open_ai_response,
        meter_api_name=meter_response["meterApiName"],
        user=USER,
    )

    # 5. send the transformed event
    client.send(event)

    # 6. ensure all events are sent and safely stop the background threads
    client.shutdown()


if __name__ == "__main__":
    main()
