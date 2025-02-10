import requests
import os
import json

"""
Use this script to provision the input_tokens and output_tokens meters.

This script will:
1. Provision the input_tokens and output_tokens meters.
2. Create a dummy customer called "test_customer".

It is advised to not run this script more than once=
"""


def provision_meters():
    URL = "https://app.amberflo.io/provisioning"
    # Provision the meters
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-api-key": os.environ.get("API_KEY"),
    }
    data = {"templateId": "llm"}

    return requests.post(URL, headers=headers, json=data)


def create_test_customer():
    URL = "https://app.amberflo.io/customers"

    payload = json.dumps(
        {
            "customerId": "test_customer",
            "customerName": "test_customer",
            "address": {
                "line1": "",
                "city": "",
                "state": "",
                "country": "",
                "postalCode": "",
            },
        }
    )
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-api-key": os.environ.get("API_KEY"),
    }

    requests.request(
        "POST",
        URL,
        headers=headers,
        data=payload,
    )


def validate_meters_do_not_exist():
    URL = "https://app.amberflo.io/meters"

    payload = {}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-api-key": os.environ.get("API_KEY"),
    }

    response = requests.request(
        "GET",
        URL,
        headers=headers,
        data=payload,
    )
    meters = json.loads(response.text)
    for meter in meters:
        if (
            meter["meterApiName"] == "input_tokens"
            or meter["meterApiName"] == "output_tokens"
        ):
            print(
                meter["meterApiName"] + " already exists. Provisioning not necessary."
            )
            return False
    return True


def validate_default_customer_does_not_exist():
    URL = "https://app.amberflo.io/customers/test_customer"

    payload = {}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-api-key": os.environ.get("API_KEY"),
    }

    response = requests.request(
        "GET",
        URL,
        headers=headers,
        data=payload,
    )
    customers = json.loads(response.text)
    if len(customers) != 0:
        return False
    return True


def main():
    if validate_meters_do_not_exist():
        print("provisioning meters")
        provision_meters()
    if validate_default_customer_does_not_exist():
        print("Customer does not exist. Creating customer.")
        create_test_customer()
    else:
        print("Test customer already exists. Creation not necessary.")
    print("Exiting")


if __name__ == "__main__":
    main()
