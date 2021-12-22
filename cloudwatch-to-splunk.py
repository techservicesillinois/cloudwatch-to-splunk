#!  /usr/bin/env python3

# pylint: disable=logging-fstring-interpolation

#   FIXME: This is a temporary docstring.
'''
Eventual lambda function to send data from AWS CloudWatch to a supported
Splunk endpoint. For now, sends pre-formatted data to the endpoint.
'''

import argparse
import configparser
import logging
import os
import sys

import requests

from splunk_endpoint import SplunkEndpoint

_NAME_CONFIG = 'splunk.config'
_PATH_CONFIG_DIR_LIST = [ '.', os.environ.get('HOME') ]

logger = logging.getLogger()
print(logger)
logger.setLevel(logging.INFO)

#####

#   pylint: disable=unused-argument
def main(argv):
    '''Main routine.'''
    #   Standard output is to be line-buffered.
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)

    parser = argparse.ArgumentParser()

    parser.add_argument \
        ('--endpoint', dest='endpoint', action='store', required=True,
         help='destination Splunk endpoint')

    parser.add_argument \
        ('--verbose', dest='verbose', action='count', default=0,
         help='verbosity level')

    #   pylint: disable=unused-variable
    arg = parser.parse_args()

    #   Suppress unwanted log messages from urllib3 module.
    logging.getLogger('urllib3').setLevel(logging.INFO)

    #   Initialize logging configuration.
    logging.basicConfig(level=logging.DEBUG)

    #   Process configuration file.
    config = get_config()

    if not config:
        return 1

    try:
        #   Look up endpoint by name in configuration file and
        #   extract needed data from the pertinent section.
        section_name = f'endpoint:{arg.endpoint}'

        splunk_kwarg_dict = \
            {
            'token'     : config.get(section_name, 'token'),
            'type'      : config.get(section_name, 'type'),
            'url'       : config.get(section_name, 'url'),
            }

    #   pylint: disable=try-except-raise
    except configparser.Error as exc:
        print(exc.message, file=sys.stderr)
        return 1

    #   Build SplunkEndpoint object with connection data.
    splunk = SplunkEndpoint(**splunk_kwarg_dict)

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

    #   Make Splunk request from hardcoded payload.
    response = splunk.request(payload)

    return 0

#####

def get_config(path=None):
    '''Get ConfigParser object.'''
    config = configparser.ConfigParser()

    for dir_config in _PATH_CONFIG_DIR_LIST:
        path_config = os.path.join(dir_config, _NAME_CONFIG)

        if os.path.exists(path_config):
            config.read(path_config)
            return config

        logging.info(f'{path_config} doesn\'t exist')
    # end for dir_config.

    logging.error(f'{_NAME_CONFIG}: configuration file not found')
    return None

#####

if __name__ == '__main__':
    sys.exit(main(sys.argv))
