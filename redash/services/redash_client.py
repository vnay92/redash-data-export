import logging
import requests


class RedashClient:

    __host = 'http://localhost:5000/'

    __base_query = {}

    __base_headers = {}

    def __init__(self, api_key, host=None):
        self.logger = logging.getLogger(__name__)
        if host is not None:
            self.__host = host

        self.__api_key = api_key
        self.__base_query = {
            'api_key': api_key
        }

        self.logger.info('Redas Client Inititlized')

    def call_api(self, url, method, params):
        params.update(self.__base_query)
        url = f'{self.__host}api/{url}'

        self.logger.info("Making a call to Redash")
        self.logger.info(f'{url}, {method}, {params}')
        res = requests.request(method=method, url=url, params=params)

        return res.json()

    def get(self, url):
        return self.call_api(url=url, method='GET', params={})

    def post(self, url, payload):
        return self.call_api(url=url, method='POST', params=payload)
