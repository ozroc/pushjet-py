# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import requests
from functools import wraps
from .errors import WriteAccessError, NonexistentError

import sys
if sys.version_info[0] >= 3:
    from urllib.parse import urljoin
else:
    from urlparse import urljoin

API_URL = 'https://api.pushjet.io/'

def api_request(endpoint, method, params=None, data=None):
    url = urljoin(API_URL, endpoint)
    r = requests.request(method, url, params=params, data=data)
    status = r.status_code
    try:
        response = r.json()
    except ValueError:
        response = {}
    else:
        # Workaround for a bug in the Pushjet implementation.
        if 'error' in response:
            status = 404
    return status, response

def requires_secret_key(func):
    @wraps(func)
    def with_secret_key_requirement(self, *args, **kwargs):
        if self.secret_key is None:
            raise WriteAccessError("The Service doesn't have a secret "
                "key provided, and therefore lacks write permission.")
        func(self, *args, **kwargs)

    return with_secret_key_requirement

class Service(object):
    def __init__(self, secret_key=None, public_key=None, _from_data=None):
        if _from_data is not None:
            self._update_from_data(_from_data)
            return
        if secret_key is None and public_key is None:
            raise ValueError("Either a secret key or public key "
                "must be provided.")
        self.secret_key = secret_key
        self.public_key = public_key
        self.refresh()

    @requires_secret_key
    def send(self, message, title=None, link=None, importance=None):
        pass

    @requires_secret_key
    def edit(self, name=None, icon_url=None):
        if name is None and icon_url is None:
            return
        data = {'secret': self.secret_key}
        if name is not None:
            data['name'] = name
        if icon_url is not None:
            data['icon'] = icon_url
        
        api_request('service', 'PATCH', data=data)
        self.name = name
        self.icon_url = icon_url

    @requires_secret_key
    def delete(self):
        api_request('services', 'DELETE', data={'secret': self.secret_key})
    
    def _update_from_data(self, data):
        self.name       = data['name']
        self.icon_url   = data['icon'] or None
        self.created    = data['created']
        self.public_key = data['public']
        if 'secret' in data:
            self.secret_key = data['secret']

    def refresh(self):
        params = {}
        if self.secret_key is not None:
            key_name = 'secret'
            params['secret'] = self.secret_key
        else:
            key_name = 'public'
            params['service'] = self.public_key
        
        status, response = api_request('service', 'GET', params=params)
        if status == 404:
            raise NonexistentError("A service with the provided {} key "
                "does not exist (anymore, at least).".format(key_name))
        self._update_from_data(response['service'])

    @classmethod
    def create(cls, name, icon_url=None):
        data = {'name': name}
        if icon_url is not None:
            data['icon'] = icon_url
        _, response = api_request('service', 'POST', data=data)
        
        return cls(_from_data=response['service'])
