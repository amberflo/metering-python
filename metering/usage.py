from enum import Enum

from metering import validators
from metering.api_client import GenericApiClient


class AggregationType(Enum):
    SUM = "SUM"
    COUNT = "COUNT"
    MIN = "MIN"
    MAX = "MAX"


class TimeGroupingInterval(Enum):
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"


class Take:
    def __init__(self, limit, is_ascending=False):
        validators.require_positive_int(
            "limit",
            limit,
            allow_none=False,
        )
        validators.require(
            "is_ascending",
            is_ascending,
            bool,
            allow_none=False,
        )
        self.limit = limit
        self.is_ascending = is_ascending

    @property
    def payload(self):
        return {
            "limit": self.limit,
            "isAscending": self.is_ascending,
        }


class TimeRange:
    def __init__(self, start_time_in_seconds, end_time_in_seconds=None):
        validators.require_positive_int(
            "start_time_in_seconds",
            start_time_in_seconds,
            allow_none=False,
        )
        validators.require_positive_int(
            "end_time_in_seconds",
            end_time_in_seconds,
        )
        self.start_time_in_seconds = start_time_in_seconds
        self.end_time_in_seconds = end_time_in_seconds

    @property
    def payload(self):
        payload = {"startTimeInSeconds": self.start_time_in_seconds}
        if self.end_time_in_seconds:
            payload["endTimeInSeconds"]: self.end_time_in_seconds
        return payload


class UsageApiClient:
    path = "/usage/"

    def __init__(self, api_key):
        self.client = GenericApiClient(api_key)

    def get_usage(self, payload):
        """
        Gets usage data.
        """
        return self.client.post(self.path, payload)


def create_usage_payload(
    aggregation,
    meter_api_name,
    time_grouping_interval,
    time_range,
    group_by=None,
    usage_filter=None,
    take=None,
):
    """
    aggregation: AggregationType.

    meter_api_name: String.

    time_grouping_interval: TimeGroupingInterval.

    time_range: TimeRange.

    group_by: Optional. List of Strings.

    usage_filter: Optional. Dictionary of String to List of Strings.

    take: Optional. Take.
    """
    validators.require("aggregation", aggregation, AggregationType, allow_none=False)
    validators.require_string("meter_api_name", meter_api_name, allow_none=False)
    validators.require(
        "time_grouping_interval",
        time_grouping_interval,
        TimeGroupingInterval,
        allow_none=False,
    )
    validators.require("time_range", time_range, TimeRange, allow_none=False)

    validators.require("take", take, Take)
    validators.require_string_list("group_by", group_by)
    validators.require_string_list_dictionary("usage_filter", usage_filter)

    payload = {
        "aggregation": aggregation.value,
        "meterApiName": meter_api_name,
        "timeGroupingInterval": time_grouping_interval.value,
        "timeRange": time_range.payload,
    }

    if group_by:
        payload["groupBy"] = group_by

    if usage_filter:
        payload["filter"] = usage_filter

    if take:
        payload["take"] = take.payload

    return payload
