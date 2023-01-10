import json
import logging
from gzip import compress
from requests import Session

from metering.version import USER_AGENT
from metering.validators import require_string
from metering.exceptions import ApiError


def _gzip(payload):
    return compress(json.dumps(payload).encode())


class IngestSession:
    """
    This class is a thin wrapper around `requests.Session`, to facilitate
    implementing the individual ingestion API client, which has special
    requirements.  It handles:

    - Standard headers (including authorization)
    - Root URL for the APIs
    - Processing responses (returning the raw text for good responses or an
      exception for errors)
    - Gzip-encoding the payloads

    Public methods expose the usual HTTP methods.
    """

    root_url = "https://ingest.amberflo.io"

    def __init__(self, api_key):
        require_string("api_key", api_key)

        self.session = Session()
        self.session.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-KEY": api_key,
            "Content-Encoding": "gzip",
            "User-Agent": USER_AGENT,
        }
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        self.session.close()

    def post(self, path, payload, params=None):
        data = _gzip(payload)
        response = self.session.post(self.root_url + path, data=data, params=params)
        return self._parse(response)

    def _parse(self, response, raw=False):
        """
        Returns the raw response or raise an exception on errors.
        """
        if response.status_code != 200:
            self.logger.error("%s: %s", response.status_code, response.text)
            raise ApiError(
                response.status_code,
                response.text,
            )
        return response.text
