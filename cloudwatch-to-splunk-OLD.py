#!  /usr/bin/env python3

import argparse
import json
import logging
import os
import requests
import sys

url = 'https://illinois.api.scs.splunk.com/services/collector/event'
dsp_hec_token = '6b7d14a72f0b8dac0427b1f53bb74d33d8a80ccca422b072f1b20d6aa36407aa:7a627ec2-e70a-495d-9fac-e0b7c5423c9f'

headers = {
    'authorization' : f'Splunk dsphec:{dsp_hec_token}',
    'content-type'  : 'application/json; charset=utf8',
    }

payload = {
    'event' : \
        {
        'message'       : 'Jon Roma was here',
        'token_name'    : 'uofiurbiamshibtechsvc',
        },
    'sourcetype'    : '_json',
    'source'        : os.path.basename(__file__),
    'fields'        : \
        {
        'forwarder'     : 'SPS',
        },
}

#####

def main(argv):
    #   Don't buffer standard output.
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', -1)

    #   Create parser.
    parser = argparse.ArgumentParser()

    parser.add_argument \
        ('--verbose', dest='verbose', action='count', default=0,
         help='verbosity level')

    #   Parse arguments.
    arg = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    filename = os.path.basename(__file__)

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    logging.info(f'request:  {response.request.method} {response.request.url}')
    logging.info(f'response: {response.status_code} {response.reason}')

    logging.info('----- request headers')
    for k, v in sorted(response.request.headers.items(), key=lambda x: x[0].lower()):
        logging.info(f'{k:<16} = {v}')

    logging.info('----- response headers')
    for k, v in sorted(response.headers.items(), key=lambda x: x[0].lower()):
        logging.info(f'{k:<16} = {v}')

    if response.status_code != 200:
        return 1

    data = response.json()
    print(json.dumps(data, indent=4))
    return 0

#####

if __name__ == '__main__':
    sys.exit(main(sys.argv))
