import json
import requests

from metering.logger import Logger
from metering.request import APIError

url = "https://app.amberflo.io/customers"


class CustomerApiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-KEY": self.api_key,
        }
        self.logger = Logger()

    def get(self, customer_id):
        """
        Get customer by id.
        """
        endpoint = "{url}/?customerId={customer_id}".format(
            url=url, customer_id=customer_id
        )
        self.logger.debug("Getting customer")
        response = requests.get(endpoint, headers=self.headers)

        if response.status_code != 200:
            self.logger.error(
                "received response in looking up customer: %s", response.text
            )
            raise APIError(response.status_code, response.text, response.text)

        return response.json()

    def add_or_update_customer(self, payload, create_customer_in_stripe=False):
        """
        Creates a new or updates an existing customer.

        The update has PUT semantics (i.e. it discards existing data).

        `create_customer_in_stripe` is only used when *creating* a new customer.
        """
        customer = self.get(payload["customerId"])

        if "customerId" in customer:
            self.logger.debug("Updating customer")
            response = requests.put(url, data=json.dumps(payload), headers=self.headers)
        else:
            self.logger.debug("Creating customer")
            params = (
                {"autoCreateCustomerInStripe": "true"}
                if create_customer_in_stripe
                else None
            )
            response = requests.post(
                url, data=json.dumps(payload), params=params, headers=self.headers
            )

        if response.status_code == 200:
            self.logger.debug("API call successful")
            return response.json()

        self.logger.error("received error: %s", response.text)
        raise APIError(
            response.status_code,
            response.text,
            response.text,
        )
