import os
from metering.session.api_session import ApiSession

"""
Use this script to provision the input_tokens and output_tokens meters.

This script will:
1. Provision the input_tokens and output_tokens meters.
2. Create a dummy customer called "test_customer".

It is advised to not run this script more than once
"""


def validate_meters_do_not_exist(session: ApiSession):
    response = session.get("/meters")
    for meter in response:
        if (
            meter["meterApiName"] == "input_tokens"
            or meter["meterApiName"] == "output_tokens"
        ):
            print(
                meter["meterApiName"] + " already exists. Provisioning not necessary."
            )
            return False
    return True


def validate_default_customer_does_not_exist(session: ApiSession):
    test_customer = session.get("/customers/test_customer")

    if len(test_customer) != 0:
        return False
    return True


def main():
    session = ApiSession(os.environ.get("API_KEY"))
    if validate_meters_do_not_exist(session):
        print("provisioning meters")
        session.post("/provisioning", {"templateId": "llm"})
    if validate_default_customer_does_not_exist(session):
        print("Customer does not exist. Creating customer.")
        customer_payload = {
            "customerId": "test_customer",
            "customerName": "test_customer",
            "address": {
                "line1": "1939 Kane Street",
                "city": "Gotham City",
                "state": "NY",
                "country": "USA",
                "postalCode": "11111",
            },
        }
        session.post("/customers", json=customer_payload)
    else:
        print("Test customer already exists. Creation not necessary.")
    print("Exiting")


if __name__ == "__main__":
    main()
