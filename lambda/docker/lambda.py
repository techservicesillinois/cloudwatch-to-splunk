import base64
import gzip
import io
import json
import logging
import sys

from datetime import date, datetime
from dateutil.tz import tzlocal

import boto3
import botocore

logging.getLogger().setLevel(logging.INFO)

#####

class CustomJSONEncoder(json.JSONEncoder):
    '''
    Custom JSON encoder subclass to serialize objects not handled by
    JSONEncoder base class.
    '''

    #####

    def default(self, o):
        logging.warning(dir(logging.Formatter))
        logging.warning(logging.Formatter)
        #   Serialize date and datetime objects.
        if isinstance(o, (date, datetime)):
            return o.isoformat()

        #   Let superclass handle other object types.
        return super().default(o)

#####

def log_json(obj: object, prefix: str, level) -> None:
    '''Log object in pretty-formatted JSON.'''
    for line in json.dumps(obj, cls=CustomJSONEncoder, indent=4).splitlines():
        #   pylint: disable=logging-fstring-interpolation
        logging.log(level, f'{prefix}: {line}')

    return

#####

def handler(event, context):
    '''Lambda handler.'''
    logging.info(f'AWS Lambda using Python {sys.version}')
    logging.info(f'Date: {datetime.now(tzlocal()).isoformat()}')
#   logging.info(f'Lambda function ARN: {context.invoked_function_arn}')
#   logging.info(f'Lambda request ID:   {context.aws_request_id}')
#   logging.info(f'CloudWatch log stream: {context.log_stream_name}')
#   logging.info(f'CloudWatch log group:  {context.log_group_name}')
#   return

    logging.info(f'boto3 version: {boto3.__version__}')
    logging.info(f'botocore version: {botocore.__version__}')

    log_json(event,   'event',   logging.INFO)
#   log_json(context, 'context', logging.INFO)
    logging.info(context)

    #   TODO: Find better name than event_data.
    event_data_encoded = event['awslogs']['data']
    logging.debug(f'data_encoded: {event_data_encoded}')

    #   TODO: Use context manager.
    #   Create buffer for base 64-decoded data.
    buffer = io.BytesIO(base64.b64decode(event_data_encoded))

    #   Unzip data into a Python object.
    with gzip.GzipFile(fileobj=buffer, mode='r') as stream:
        event_data = json.loads(stream.read())

#   log_json(event_data, 'event_data', logging.DEBUG)
    log_json(event_data, 'event_data', logging.INFO)

    log_group = event_data['logGroup']

    logging.info(f'log_group: {log_group}')
    return
