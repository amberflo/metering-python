from datetime import date, datetime
from dateutil.tz import tzutc
import logging
import json
from gzip import GzipFile
from requests.auth import HTTPBasicAuth
from requests import sessions
from io import BytesIO
import time
from metering.version import VERSION
from metering.utils import remove_trailing_slash

_session = sessions.Session()
token = None
last_login_time = None

def login(user_name,password):
    global token
    global last_login_time
    if token is not None and (time.time() - last_login_time ) < 600:
        return token
    last_login_time = time.time()

    log = logging.getLogger('amberflo')
    log.debug('login')
    login_request = {"AuthParameters" : {"USERNAME" : user_name,"PASSWORD" :
                  password}, "AuthFlow" : "USER_PASSWORD_AUTH", "ClientId" :
                  "9g4vt735jc90ju6u82gmqan3m","UserPoolId" :
                  "us-west-2_2Yhs6Fa2h"}
    headers = {
        'Content-Type': 'application/x-amz-json-1.1',
        'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth'
    }
    url = 'https://cognito-idp.us-west-2.amazonaws.com'
    res = _session.post(url, data=json.dumps(login_request),
                        headers=headers)
    if res.status_code == 200:
        log.debug('login successfully')   
        result = res.json()
        #log.debug('*****************received result: %s', result)
        token = str(result['AuthenticationResult']['IdToken'])
        # log.debug('*****************received token: %s', token)
        return token
    try:
        log.debug('login failed')   
        result = res.json()
        log.debug('received response: %s', result)
        raise APIError(res.status_code, result['code'], result['message'])
    except Exception as e:
        log.debug(e)   

def post(user_name,password, host=None, gzip=False, timeout=15, **kwargs):
    log = logging.getLogger('amberflo')
    token = login(user_name,password)
    #log.debug('*******using token: '+token)
    """Post the `kwargs` to the API"""
    
    body = kwargs
    body["sentAt"] = datetime.utcnow().replace(tzinfo=tzutc()).isoformat()
    url = 'https://app.amberflo.io/ingest/'
    data = json.dumps(body['batch'], cls=DatetimeSerializer)
    log.debug('making request: %s', data)
    headers = {
        'Content-Type': 'application/json',
        'accept': 'application/json',
        'Authorization' :  token,
    }
    if gzip:
        headers['Content-Encoding'] = 'gzip'
        buf = BytesIO()
        with GzipFile(fileobj=buf, mode='w') as gz:
            # 'data' was produced by json.dumps(),
            # whose default encoding is utf-8.
            gz.write(data.encode('utf-8'))
        data = buf.getvalue()

    res = _session.post(url, data=data,
                        headers=headers, timeout=timeout)

    if res.status_code == 200:
        log.debug('data uploaded successfully')
        return res

    try:
        payload = res.json()
        log.debug('received response: %s', payload)
        raise APIError(res.status_code, payload['code'], payload['message'])
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


class DatetimeSerializer(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)
