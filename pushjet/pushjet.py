# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import requests
from functools import wraps
from .errors import WriteAccessError, NonexistentError

import sys
if sys.version_info[0] >= 3:
    from urllib.parse import urljoin
    unicode_type = str
else:
    from urlparse import urljoin
    unicode_type = unicode

API_URL = 'https://api.pushjet.io/'

class NoNoneDict(dict):
    def __setitem__(self, key, value):
        if value is not None:
            dict.__setitem__(self, key, value)

def api_request(endpoint, method, params=None, data=None):
    url = urljoin(API_URL, endpoint)
    r = requests.request(method, url, params=params, data=data)
    print r.request.body
    print r.status_code
    print r.text
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
        self.secret_key = unicode_type(secret_key)
        self.public_key = unicode_type(public_key)
        self.refresh()
    
    def _request(self, endpoint, method, is_secret, params=None, data=None):
        params = params or {}
        if is_secret:
            params['secret'] = self.secret_key
        else:
            params['service'] = self.public_key
        return api_request(endpoint, method, params, data)

    @requires_secret_key
    def send(self, message, title=None, link=None, importance=None):
        data = NoNoneDict({
            'message': message,
            'title': title,
            'link': link,
            'level': importance
        })
        self._request('message', 'POST', is_secret=True, data=data)

    @requires_secret_key
    def edit(self, name=None, icon_url=None):
        data = NoNoneDict({
            'icon': icon_url,
            'name': name
        })
        if not data:
            return
        self._request('service', 'PATCH', is_secret=True, data=data)
        self.name = unicode_type(name)
        self.icon_url = unicode_type(icon_url)

    @requires_secret_key
    def delete(self):
        self._request('services', 'DELETE', is_secret=True)
    
    def _update_from_data(self, data):
        self.name       = data['name']
        self.icon_url   = data['icon'] or None
        self.created    = data['created']
        self.public_key = data['public']
        self.secret_key = data.get('secret', self.secret_key)

    def refresh(self):
        key_name = 'secret'
        secret = True
        if self.public_key is not None:
            key_name = 'public'
            secret=False
        
        status, response = self._request('service', 'GET', is_secret=secret)
        if status == 404:
            raise NonexistentError("A service with the provided {} key "
                "does not exist (anymore, at least).".format(key_name))
        self._update_from_data(response['service'])

    @classmethod
    def create(cls, name, icon_url=None):
        data = NoNoneDict({
            'name': name,
            'icon': icon_url
        })
        _, response = api_request('service', 'POST', data=data)
        return cls(_from_data=response['service'])

class Device(object):
    def __init__(self, uuid):
        self.uuid = unicode_type(uuid)
    
    def _request(self, endpoint, method, params=None, data=None):
        params = (params or {})
        params['uuid'] = self.uuid
        return api_request(endpoint, method, params, data)

    def subscribe(self, service):
        data = {}
        data['service'] = service.public_key if isinstance(service, Service) else service
        self._request('subscription', 'POST', data=data)
    
    def unsubscribe(self, service):
        data = {}
        data['service'] = service.public_key if isinstance(service, Service) else service
        self._request('subscription', 'POST', data=data)

    def get_subscriptions(self):
        _, response = self._request('subscription', 'GET')
        subscriptions = []
        for subscription_dict in response['subscriptions']:
            subscriptions.append(Subscription(subscription_dict))
        return subscriptions
    
    def get_messages(self):
        _, response = self._request('message', 'GET')
        messages = []
        for message_dict in response['messages']:
            messages.append(Message(message_dict))
        return messages

class Subscription(object):
    def __init__(self, subscription_dict):
        self.service = Service(_from_data=subscription_dict['service'])
        self.time_subscribed = subscription_dict['timestamp']
        self.last_checked = subscription_dict['timestamp_checked']
        self.device_uuid = subscription_dict['uuid'] # Not sure this is needed, but...

class Message(object):
    def __init__(self, message_dict):
        self.message = message_dict['message']
        self.title = message_dict['title']
        self.link = message_dict['link'] or None
        self.time_sent = message_dict['timestamp']
        self.importance = message_dict['level']
        self.service = Service(_from_data=message_dict['service'])
