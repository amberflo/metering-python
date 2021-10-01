from datetime import datetime

import sys
import json
from gzip import GzipFile
from io import BytesIO
import uuid
import boto3
from requests import sessions
from dateutil.tz import tzutc
from metering.logger import Logger

_session = sessions.Session()
ingest_url = 'https://app.amberflo.io/ingest'


class RequestManager:

    def __init__(self, api_key,s3_bucket=None, access_key=None,
                    secret_key=None, gzip=False, timeout=15, **kwargs):
        self.api_key = api_key
        self.s3_bucket = s3_bucket
        self.access_key = access_key
        self.secret_key = secret_key
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

        response = _session.post(ingest_url, data=data, headers=headers, timeout=self.timeout)
        print("data uploaded")
        if response.status_code == 200:
            log.debug('data uploaded successfully')
            return response

        try:
            log.debug('received response: %s', response.text)
            raise APIError(response.status_code, response.text, response.text)
        except ValueError:
            raise APIError(response.status_code, 'unknown', response.text)

    def send_to_s3(self):
        log = Logger()

        try: 
            data = json.dumps(self.body['batch'], cls=json.JSONEncoder)
            fileName = str(uuid.uuid4()) + '-' +  str(datetime.now()).replace(' ','T')
            if self.access_key:
                s3 = boto3.resource(
                    's3',
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key
                )
            else:
                s3 = boto3.resource('s3')
            response = s3.Object(self.s3_bucket, fileName).put(Body=data)
            status_code = response["ResponseMetadata"]["HTTPStatusCode"]
            if status_code == 200:
                print("data uploaded to s3")
                log.debug('data uploaded to s3 successfully')
                return response
            print(response)
        except:
            log.debug('Some error occurred : %s', sys.exc_info()[1])


class APIError(Exception):

    def __init__(self, status, code, message):
        self.message = message
        self.status = status
        self.code = code

    def __str__(self):
        msg = "[Amberflo] {0}: {1} ({2})"
        return msg.format(self.code, self.message, self.status)
