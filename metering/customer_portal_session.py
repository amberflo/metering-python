from metering import validators
from metering.session import ApiSession


class CustomerPortalSessionApiClient:
    """
    See https://docs.amberflo.io/reference/post_session
    """

    path = "/session"

    def __init__(self, api_key):
        """
        Initialize the API client session.
        """
        self.client = ApiSession(api_key)

    def get(self, payload):
        """
        Get a `url` and `session token` for the customer portal.

        Create a payload using the `create_customer_portal_session_payload` function.

        See https://docs.amberflo.io/reference/post_session
        """
        return self.client.post(self.path, payload)


def create_customer_portal_session_payload(
    customer_id,
    expiration_epoch_in_milliseconds=None,
    return_url=None,
):
    """
    customer_id: String.

    expiration_epoch_in_milliseconds: Optional. Positive integer. Future unix epoch time.
        When the session should expire. Defaults to 24 hours from now.

    return_url: Optional. String.

    See https://docs.amberflo.io/reference/post_session
    """
    validators.require_string("customer_id", customer_id, allow_none=False)
    validators.require_positive_int(
        "expiration_epoch_in_milliseconds", expiration_epoch_in_milliseconds
    )
    validators.require_string("return_url", return_url)

    payload = {
        "customerId": customer_id,
    }

    if expiration_epoch_in_milliseconds:
        payload["expirationEpochMilliSeconds"] = expiration_epoch_in_milliseconds

    if return_url:
        payload["returnUrl"] = return_url

    return payload
