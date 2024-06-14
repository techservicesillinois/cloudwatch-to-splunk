import json
import logging
import sys

logging.getLogger().setLevel(logging.INFO)

from datetime import datetime

#####

def handler(event, context):
    logging.info(f'Hello from AWS Lambda using Python {sys.version}')
    logging.info(f'Current date: {datetime.now().isoformat()}')
    logging.info(json.dumps(event))
    return
