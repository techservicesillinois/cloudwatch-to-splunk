import json
import logging
import sys

from datetime import datetime
from dateutil.tz import tzlocal

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
    logging.info(f'AWS Lambda using Python {sys.version}')
    logging.info(f'Date: {datetime.now(tzlocal()).isoformat()}')
    log_json(event, 'event', logging.INFO)
    logging.info(context)
    return
