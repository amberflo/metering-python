import json
import logging
from gzip import compress
from requests import Session

from metering.validators import require_string


class ApiError(Exception):
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text

    def __str__(self):
        return "{0}: {1}".format(self.status_code, self.text)


def _gzip(payload):
    return compress(json.dumps(payload).encode())


class ApiSession:
    """
    This class is a thin wrapper around `requests.Session`, to facilitate
    implementing the individual API clients. It handles:

    - Standard headers (including authorization)
    - Root URL for the APIs
    - Parsing responses (returning either the JSON for good responses or an
      exception for errors)

    Public methods expose the usual HTTP methods.
    """

    root_url = "https://app.amberflo.io"

    def __init__(self, api_key):
        require_string("api_key", api_key)

        self.session = Session()
        self.session.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-KEY": api_key,
        }
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        self.session.close()

    def get(self, path, params=None):
        response = self.session.get(self.root_url + path, params=params)
        return self._parse(response)

    def post(self, path, json, params=None):
        response = self.session.post(self.root_url + path, json=json, params=params)
        return self._parse(response)

    def put(self, path, json, params=None):
        response = self.session.put(self.root_url + path, json=json, params=params)
        return self._parse(response)

    def delete(self, path):
        response = self.session.delete(self.root_url + path)
        return self._parse(response)

    def _parse(self, response):
        """
        Returns the parsed JSON response or raise an exception on errors.
        """
        if response.status_code != 200:
            self.logger.error("received error: %s", response.text)
            raise ApiError(
                response.status_code,
                response.text,
            )
        return response.json()


class IngestSession:
    """
    Similar to the `ApiSession`, but for the data ingestion API.  I.e.:
    - Requests are gzip encoded
    - Returns the raw response text
    """

    root_url = "https://app.amberflo.io"

    def __init__(self, api_key):
        require_string("api_key", api_key)

        self.session = Session()
        self.session.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-KEY": api_key,
            "Content-Encoding": "gzip",
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
            self.logger.error("received error: %s", response.text)
            raise ApiError(
                response.status_code,
                response.text,
            )
        return response.text
