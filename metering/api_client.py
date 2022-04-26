from requests import Session

from metering.logger import Logger
from metering.request import APIError


class GenericApiClient:
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
        self.session = Session()
        self.session.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-KEY": api_key,
        }
        self.logger = Logger()

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
            raise APIError(
                response.status_code,
                response.text,
                response.text,
            )
        return response.json()
