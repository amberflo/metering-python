#!/usr/bin/env python3

"""
This sample shows an example of creating or updating a "customer".

See https://docs.amberflo.io/reference/post_customers
"""

import os
import json

from metering.customer import CustomerApiClient, create_customer_payload


def main():
    # 1. obtain your API key
    api_key = os.environ.get("API_KEY")

    # 2. initialize customer client
    client = CustomerApiClient(api_key)

    # 3. create a message
    message = create_customer_payload(
        customer_id="sample-customer-123",
        customer_email="customer-123@sample.com",
        customer_name="Sample Customer",
        # Traits are optional. They can be used as filters or aggregation buckets
        traits={
            "region": "us-east-1",
            "stripeId": "cus_AJ6bY3VqcaLAEs",
        },
    )

    # 4. send it
    customer = client.add_or_update(message)

    # 5. see your customer info
    print(json.dumps(customer, indent=4))


if __name__ == "__main__":
    main()
