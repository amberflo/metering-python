import json
from enum import Enum
import requests

from metering.logger import Logger
from metering.request import APIError

usage_url = 'https://app.amberflo.io/usage'


class AggregationType(Enum):
    SUM = 'Sum'
    MIN = 'Min'
    MAX = 'Max'

class TimeGroupingInterval(Enum):
    HOUR= 'HOUR'
    DAY='DAY'
    WEEK='WEEK'
    MONTH='MONTH'

class Take:
    def __init__(self, limit, is_ascending):
        self.limit = limit
        self.is_ascending = is_ascending


class TimeRange:
    def __init__(self, start_time_in_seconds, end_time_in_seconds=None):
        self.start_time_in_seconds = start_time_in_seconds
        self.end_time_in_seconds = end_time_in_seconds

class UsageClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'X-API-KEY': self.api_key
                        }
        self.logger = Logger()

    def get_usage(self, payload):
        log = self.logger
        response = requests.post(
            usage_url, data=json.dumps(payload), headers=self.headers)
        log.debug('calling usage api', payload)

        if response.status_code == 200:
            log.debug('API call successful')
            return response.json()

        log.debug('received response: %s', response.text)
        raise APIError(response.status_code, response.text, response.text)
