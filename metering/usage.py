from enum import Enum

from metering.api_client import GenericApiClient


class AggregationType(Enum):
    SUM = "Sum"
    MIN = "Min"
    MAX = "Max"


class TimeGroupingInterval(Enum):
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"


class Take:
    def __init__(self, limit, is_ascending):
        self.limit = limit
        self.is_ascending = is_ascending


class TimeRange:
    def __init__(self, start_time_in_seconds, end_time_in_seconds=None):
        self.start_time_in_seconds = start_time_in_seconds
        self.end_time_in_seconds = end_time_in_seconds


class UsageClient:
    path = "/usage/"

    def __init__(self, api_key):
        self.client = GenericApiClient(api_key)
        self.logger = self.client.logger

    def get_usage(self, payload):
        """
        Gets usage data.
        """
        return self.client.post(self.path, payload)
