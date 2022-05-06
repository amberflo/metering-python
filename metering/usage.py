from enum import Enum

from metering import validators
from metering.session import ApiSession


class UsageApiClient:
    """
    See: https://docs.amberflo.io/reference/post_usage
    """

    path = "/usage/"
    path_batch = path + "batch"
    path_all = path + "all"

    def __init__(self, api_key):
        """
        Initialize the API client session.
        """
        self.client = ApiSession(api_key)

    def get(self, query):
        """
        Gets usage data. Supports either a single request or a list of requests
        and returns a single report or a list of reports accordingly.

        Create a query using the `create_usage_query` function.

        See: https://docs.amberflo.io/reference/post_usage
        """
        if isinstance(query, list):
            return self.client.post(self.path_batch, query)
        else:
            return self.client.post(self.path, query)

    def get_all(self, query):
        """
        Get usage reports for all meters. Because it incudes all meters,
        this is more limited than `get`. Returns a list of usage reports.

        Create a query using the `create_all_usage_query` function.
        """
        return self.client.get(self.path_all, params=query)


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
        """
        limit: Positive integer.

        is_ascending: Boolean. Defaults to false.
        """
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
        """
        start_time_in_seconds: Positive integer. Unix epoch time.

        end_time_in_seconds: Optional. Positive integer. Unix epoch time.
        """
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
            payload["endTimeInSeconds"] = self.end_time_in_seconds
        return payload


def create_usage_query(
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

    See: https://docs.amberflo.io/reference/post_usage
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


def create_all_usage_query(
    time_grouping_interval,
    time_range,
    filter_by_customer_id=None,
    group_by_customer_id=False,
):
    """
    time_grouping_interval: TimeGroupingInterval.

    time_range: TimeRange.

    filter_by_customer_id. Optional. String.

    group_by_customer_id. Optional. Boolean.

    See: https://docs.amberflo.io/reference/post_usage-batch
    """
    validators.require(
        "time_grouping_interval",
        time_grouping_interval,
        TimeGroupingInterval,
        allow_none=False,
    )
    validators.require("time_range", time_range, TimeRange, allow_none=False)

    validators.require_string("filter_by_customer_id", filter_by_customer_id)
    validators.require(
        "group_by_customer_id", group_by_customer_id, bool, allow_none=False
    )

    params = time_range.payload

    params["timeGroupingInterval"] = time_grouping_interval.value

    if group_by_customer_id:
        params["groupBy"] = "customerId"

    if filter_by_customer_id:
        params["customerId"] = filter_by_customer_id

    return params
