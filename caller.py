#!  /usr/bin/env python3

import argparse
import configparser
import json
import logging
import os
import requests
import sys

_NAME_CONFIG = 'splunk.config'
_PATH_CONFIG_DIR_LIST = [ '.', os.environ.get('HOME') ]

#####

class SplunkEndpoint:

    _auth_token_qualifier_dict = \
        {
        'dsphec'    : 'dsphec',
        'hec'       : None,
        }

    #####

    def __init__(self, **kwarg_dict):
        # FIXME: Should validate kwargs_dict.
        for k, v in kwarg_dict.items():
            setattr(self, k, v)
            logging.info(f'{k:<12} = {v}')
        
        try:
            qualifier = self._auth_token_qualifier_dict[self.type]
            logging.info('{:<12} = {}'.format('qualifier', qualifier))

        except Exception as exc:
            # FIXME: clean this up.
            raise

        self.headers = \
            {
            'content-type'  : 'application/json; charset=utf8',
            }

        if qualifier:
            self.headers.update({ 'authorization' : f'Splunk {qualifier}:{self.token}' })

        else:
            self.headers.update({ 'authorization' : f'Splunk {self.token}' })

        logging.info('headers')

        for k, v in sorted(self.headers.items()):
            logging.info('{:<4}{:<16} = {}'.format('', k, v))
        return

    #####

    def __str__(self):
        #   pylint: disable=logging-fstring-interpolation
        return f'[{self.__class__.__name__}:0x{id(self):x}:{self.type}:{self.url}]'

    #####

    def request(self, payload):
        response = requests.post(self.url, headers=self.headers, data=json.dumps(payload))

        logging.info(f'request:  {response.request.method} {response.request.url}')
        logging.info('----- request headers')

        for k, v in sorted(response.request.headers.items(), key=lambda x: x[0].lower()):
            logging.info(f'{k:<16} = {v}')

        logging.info(f'----- request body')

        print(json.dumps(json.loads(response.request.body), indent=2))
        print()

        logging.info(f'response: {response.status_code} {response.reason}')
        logging.info('----- response headers')

        for k, v in sorted(response.headers.items(), key=lambda x: x[0].lower()):
            logging.info(f'{k:<16} = {v}')

        if response.status_code != 200:
            #   FIXME: Should raise exception.
            return None

        #   Retrieve response body as object
        logging.info('----- response body')
        data = response.json()
        print(json.dumps(data, indent=2))
        return data

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
