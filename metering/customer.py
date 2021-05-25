import json
import requests

from metering.logger import Logger
from metering.request import APIError

url = 'https://app.amberflo.io/customers'


class CustomerApiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'X-API-KEY': self.api_key
                        }
        self.logger = Logger()

    def add_or_update_customer(self, payload):
        log = self.logger
        log.debug('calling customers api', payload)

        endpoint = "{url}/?customerId={customerId}".format(
            url=url, customerId=payload['customerId'])
        response = requests.get(endpoint,  headers=self.headers)

        if response.status_code == 200:
            updated_response = None
            customer = response.json()
            if 'customerId' in customer:
                log.debug('Updating customer')
                updated_response = requests.put(
                    url,  data=json.dumps(payload), headers=self.headers)
            else:
                log.debug('Creating customer')
                updated_response = requests.post(
                    url,  data=json.dumps(payload), headers=self.headers)

            if updated_response.status_code == 200:
                log.debug('API call successful')
                return updated_response.json()

            log.error('received error: %s', updated_response.text)
            raise APIError(updated_response.status_code,
                           updated_response.text, updated_response.text)

        else:
            log.error('received response in looking up customer: %s',
                      response.text)
            raise APIError(response.status_code, response.text, response.text)
