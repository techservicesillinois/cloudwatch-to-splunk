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

logging.getLogger().setLevel(logging.INFO)

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
    return

#####

def main():
    '''Main routine.'''

#   os.set_blocking(sys.stdin.fileno(), 1)
#   print(type(sys.stdin), file=sys.stderr)
#   print(dir(sys.stdin), file=sys.stderr)
#   print(os.get_blocking(sys.stdin.fileno()), file=sys.stderr)

    return handler(dict(), dict())

#####

if __name__ == '__main__':
    sys.exit(main())
