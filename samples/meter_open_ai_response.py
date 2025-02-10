#!/usr/bin/env python3

"""
This sample shows an example of how to use the meter_llm decorator to intercept a call to openai,
transform the reponse into Amberflo events, and then ingest the events into Amberflo.
"""

from openai import OpenAI
from typing import Optional
from metering.meter_llm import meter_llm


@meter_llm()
def meter_open_ai_response(
    customer_id: Optional[str] = None, aflo_dimensions: Optional[dict] = None
):
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "write me a haiku about metering and analytics",
            },
        ],
        user=customer_id,
    )
    return response


def main():
    meter_open_ai_response()


if __name__ == "__main__":
    main()
