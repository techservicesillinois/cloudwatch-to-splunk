'''SplunkEndpoint class.'''

import json
import logging
import requests

logger = logging.getLogger()
print(logger)
logger.setLevel(logging.INFO)

#####

class SplunkEndpoint:
    '''
    SplunkEndpoint class provides a simple interface between an application
    and a variety of Splunk endpoints.
    '''

    _auth_token_qualifier_dict = \
        {
        'dsphec'    : 'dsphec',
        'hec'       : None,
        }

    qualifier = None
    token = None
    type = None
    url = None

    #####

    def __init__(self, **kwarg_dict):
        # FIXME: Should validate kwargs_dict.
        #   pylint: disable=invalid-name
        for k, v in kwarg_dict.items():
            setattr(self, k, v)
            #   pylint: disable=logging-fstring-interpolation
            logging.debug(f'{k:<12} = {v}')

        try:
            qualifier = self._auth_token_qualifier_dict[self.type]
            logging.debug('{:<12} = {}'.format('qualifier', qualifier))

        #   pylint: disable=try-except-raise,unused-variable
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

        #   pylint: disable=invalid-name
        for k, v in sorted(self.headers.items()):
            logging.info('{:<4}{:<16} = {}'.format('', k, v))
        return

    #####

    def __str__(self):
        #   pylint: disable=logging-fstring-interpolation
        return f'[{self.__class__.__name__}:0x{id(self):x}:{self.type}:{self.url}]'

    #####

    def request(self, payload):
        '''Make POST request, sending data to Splunk endpoint.'''
        response = requests.post(self.url, headers=self.headers, data=json.dumps(payload))

        #   pylint: disable=logging-fstring-interpolation
        logging.info(f'request:  {response.request.method} {response.request.url}')
        logging.info('----- request headers')

        #   pylint: disable=invalid-name
        for k, v in sorted(response.request.headers.items(), key=lambda x: x[0].lower()):
            #   pylint: disable=logging-fstring-interpolation
            logging.info(f'{k:<16} = {v}')

        logging.info('----- request body')

        print(json.dumps(json.loads(response.request.body), indent=2))
        print()

        #   pylint: disable=logging-fstring-interpolation
        logging.info(f'response: {response.status_code} {response.reason}')
        logging.info('----- response headers')

        for k, v in sorted(response.headers.items(), key=lambda x: x[0].lower()):
            #   pylint: disable=logging-fstring-interpolation
            logging.info(f'{k:<16} = {v}')

        if response.status_code != 200:
            #   FIXME: Should raise exception.
            return None

        #   Retrieve response body as object
        logging.info('----- response body')
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
