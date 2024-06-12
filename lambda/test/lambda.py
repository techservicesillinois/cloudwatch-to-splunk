#!  /usr/bin/env python3

'''Lambda function to inject CloudWatch log messages into Splunk.'''

import base64
import gzip
import io
import json
import logging
import os
import sys
import time

from datetime import date, datetime
#from typing import Any, TYPE_CHECKING
from typing import Any

import requests

import boto3
import botocore

SSM_PREFIX = os.environ.get('SSM_PREFIX', '/cloudwatch_to_splunk')

#   6 * 60 * 1000   # TODO: Python might not do timing in ms.
#   (360000)
SPLUNK_CACHE_TTL = os.environ.get('SPLUNK_CACHE_TTL')

#   Get and validate log level from environment.
LOG_LEVEL = logging.getLevelNamesMapping() \
    .get(os.environ.get('LOG_LEVEL'))

if LOG_LEVEL:
    #   Set specified log level.
    logging.getLogger().setLevel(LOG_LEVEL)

else:
    #   Set default log level.
    LOG_LEVEL = logging.DEBUG
    logging.getLogger().setLevel(LOG_LEVEL)
    logging.warning('LOG_LEVEL missing or invalid; using default')

#   Suppress noisy debug logging from botocore and urllib.
logging.getLogger('botocore').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)

SESSION = boto3.session.Session()
CLIENT_SSM = SESSION.client('ssm')

SSM_PARAM_NAMES = \
    [
    'hec_endpoint',
    'hec_token',
    'sourcetype',
    ]

#####

class CustomJSONEncoder(json.JSONEncoder):
    '''
    Custom JSON encoder subclass to serialize objects not handled by
    JSONEncoder base class.
    '''

    #####

    def default(self, o):
        #   Serialize date and datetime objects.
        if isinstance(o, (date, datetime)):
            return o.isoformat()

        #   Let superclass handle other object types.
        return super().default(o)

#####

class SplunkLogger:
    '''Class to manage logging to Splunk.'''

    #####

    def __init__(self, log_group: str, ssm_params: dict[str, Any]):
        self.hec_endpoint = ssm_params['hec_endpoint']
        self.hec_token = ssm_params['hec_token']
        self.log_group = log_group
        self.max_batch_count = 0
        self.max_retries = 3
        self.sourcetype = ssm_params['sourcetype']

        logging.info(self)
        return

    #####

    def __str__(self: object):
        return f'[{self.__class__.__name__}:{self.log_group}:0x{id(self):x}]'

    #####

    #   pylint: disable=logging-fstring-interpolation
    def send(self: object, event_data):
        '''Send event data to Splunk endpoint.'''
        with io.StringIO() as stream_post:
            #   Iterate over each log event from event object.
            for log_event in event_data['logEvents']:
                #   Use current timestamp if none found in log_event.
                timestamp = \
                    log_event.get('timestamp', int(datetime.timestamp(datetime.now())))

                #   Add JSON object for this log event to POST data for Splunk.
                log = \
                    {
                    'host'          : event_data['logGroup'],
                    'source'        : event_data['logStream'],
                    'sourcetype'    : self.sourcetype,
                    'time'          : timestamp,
                    'event'         : dict(message=log_event['message']),
                    }

                print(json.dumps(log), file=stream_post)
            #   end for log_event.

            ingest_data = stream_post.getvalue()
        #   end with io.stringIO().

        logging.info('*' * 60)
        for line in ingest_data.splitlines():
            logging.info(line)
        logging.info('*' * 60)

        #   Set HTTP headers for POST.
        headers = dict()
        headers.update(dict(Authorization=f'Splunk {self.hec_token}'))
        logging.info(f'request.headers: {headers}')

        url = self.hec_endpoint

        try:
            logging.info(f'POST \'{url}\'')
            response = requests.post(url, headers=headers, data=ingest_data)

            for line in ingest_data.splitlines():
                logging.warning(line)

            logging.info(f'response.encoding: {response.encoding}')
            logging.info(f'response.headers:  {response.headers}')

            response.raise_for_status()

        except Exception as exc:
            logging.error(exc)

        else:
            logging.info(f'{response.status_code} {response.reason}')

        #   print('content', response.content)
            log_json(response.json(), 'response.json()', logging.INFO)

        return

#####

#   pylint: disable=logging-fstring-interpolation
def get_ssm_params(log_group: str) -> dict[str, Any]:
    '''
    Get parameters from SSM parameter store or from cache for this log group.
    '''
    #   Form SSM parameter prefix for this CloudWatch log group.
    ssm_prefix = SSM_PREFIX + log_group

    ssm_param_names = list()

    #   Set full SSM path of SSM parameters for this CloudWatch log group.
    for param in SSM_PARAM_NAMES:
        ssm_param_names.append(os.path.join(ssm_prefix, param))

    log_json(ssm_param_names, 'ssm_param_names', logging.DEBUG)

    #   Get SSM parameters.
    try:
        ssm_response = CLIENT_SSM.get_parameters \
            (Names=ssm_param_names, WithDecryption=True)

    except Exception as exc:
        #   TODO: Should this include SSM response?
        raise exc

    #   Log SSM response.
    log_json(ssm_response, 'ssm_response', logging.DEBUG)

    if len(ssm_response['InvalidParameters']) > 0:
        #   pylint: disable=line-too-long,disable=logging-fstring-interpolation
        #   FIXME: Add caching.
        logging.error(f'log group \'{log_group}\': some SSM parameters not set; required values are: {", ".join(sorted(SSM_PARAM_NAMES))}')
        return None

    #   TODO: len must be same as SSM_PARAM_NAMES.
    logging.info(f'# of SSM parameters: {len(ssm_response["Parameters"])}')

    ssm_params = dict()

    #   TODO: if not ssm_response['Parameters']
    #   TODO: Check for string "*** NO VALUE SET ***".

    for param in ssm_response['Parameters']:
        # FIXME: manage trailing slash.
        name = param['Name'].removeprefix(ssm_prefix + '/')

        #   TODO: check name != param['Name']
        ssm_params.update({ name : param['Value'] })

    log_json(ssm_params, 'ssm_params', logging.DEBUG)
    return ssm_params

#####

def log_json(obj: object, prefix: str, level) -> None:
    '''Log object in pretty-formatted JSON.'''
    for line in json.dumps(obj, cls=CustomJSONEncoder, indent=4).splitlines():
        #   pylint: disable=logging-fstring-interpolation
        logging.log(level, f'{prefix}: {line}')

    return

#####

#   pylint: disable=logging-fstring-interpolation
def handler(event: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    '''Lambda handler.'''
    logging.info(f'boto3 version: {boto3.__version__}')
    logging.info(f'botocore version: {botocore.__version__}')

    log_json(event,   'event',   logging.INFO)
    log_json(context, 'context', logging.INFO)

    #   TODO: Find better name than event_data.
    event_data_encoded = event['awslogs']['data']
    logging.debug(f'data_encoded: {event_data_encoded}')

    #   TODO: Use context manager.
    #   Create buffer for base 64-decoded data.
    buffer = io.BytesIO(base64.b64decode(event_data_encoded))

    #   Unzip data into a Python object.
    with gzip.GzipFile(fileobj=buffer, mode='r') as stream:
        event_data = json.loads(stream.read())

    log_json(event_data, 'event_data', logging.DEBUG)

    log_group = event_data['logGroup']

    logging.info(f'log_group: {log_group}')

    ssm_params = get_ssm_params(log_group)
    log_json(ssm_params, 'ssm_params', logging.INFO)

    sys.exit(5)

    #   TODO: Logger can be returned from cache.
    logger = SplunkLogger(log_group, ssm_params)
    logger.send(event_data)
    return

#####

def main():
    '''Main routine.'''

#   os.set_blocking(sys.stdin.fileno(), 1)
#   print(type(sys.stdin), file=sys.stderr)
#   print(dir(sys.stdin), file=sys.stderr)
#   print(os.get_blocking(sys.stdin.fileno()), file=sys.stderr)

    count = 0

    try:
        #   FIXME: This should be blocking read.
        while True:
            buf = sys.stdin.read(-1)

            if len(buf) == 0:
                time.sleep(0.25)
                continue

            count += 1

            logging.info(f'{"-"*10} BEGIN REQUEST {count} {"-"*10}')
            logging.debug(f'read {len(buf)} bytes from stdin')

            request = json.loads(buf)

            log_json(request, 'request', logging.DEBUG)

            handler(request['event'], request['context'])

            logging.info(f'{"-"*10} END REQUEST {count} {"-"*10}')

            #   TODO: error handling takes place here.

    except KeyboardInterrupt as exc:
        logging.error(exc.__class__.__name__)
        return 1

    return 0

#####

if __name__ == '__main__':
    sys.exit(main())
