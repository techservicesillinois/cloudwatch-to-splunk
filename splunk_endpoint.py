#!  /usr/bin/env python3

import argparse
import configparser
import json
import logging
import os
import requests
import sys

logger = logging.getLogger()
print(logger)
logger.setLevel(logging.INFO)

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
            logging.debug(f'{k:<12} = {v}')
        
        try:
            qualifier = self._auth_token_qualifier_dict[self.type]
            logging.debug('{:<12} = {}'.format('qualifier', qualifier))

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
