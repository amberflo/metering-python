from datetime import datetime

import json
from gzip import GzipFile
from io import BytesIO
from requests import sessions
from dateutil.tz import tzutc
from metering.logger import Logger

_session = sessions.Session()
ingest_url = 'https://app.amberflo.io/ingest-endpoint'


class RequestManager:

    def __init__(self, api_key, gzip=False, timeout=15, **kwargs):
        self.api_key = api_key
        self.gzip = gzip
        self.timeout = timeout
        kwargs["sentAt"] = datetime.utcnow().replace(tzinfo=tzutc()).isoformat()
        self.body = kwargs

    def post(self):
        log = Logger()

        data = json.dumps(self.body['batch'], cls=json.JSONEncoder)
        log.debug('making request: %s', data)
        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion',
            'X-API-Key': self.api_key
        }

        # import ipdb; ipdb.set_trace()
        if self.gzip:
            headers['Content-Encoding'] = 'gzip'
            buf = BytesIO()
            with GzipFile(fileobj=buf, mode='w') as gz:
                # 'data' was produced by json.dumps(),
                # whose default encoding is utf-8.
                gz.write(data.encode('utf-8'))
            data = buf.getvalue()

        res = _session.post(ingest_url, data=data, headers=headers, timeout=self.timeout)
        print("data uploaded")
        if res.status_code == 200:
            log.debug('data uploaded successfully')
            return res

        try:
            payload = res.json()
            log.debug('received response: %s', payload)
            raise APIError(res.status_code, res.text, payload['unique_id'])
        except ValueError:
            raise APIError(res.status_code, 'unknown', res.text)


class APIError(Exception):

    def __init__(self, status, code, message):
        self.message = message
        self.status = status
        self.code = code

    def __str__(self):
        msg = "[Amberflo] {0}: {1} ({2})"
        return msg.format(self.code, self.message, self.status)
