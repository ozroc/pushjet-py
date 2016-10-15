# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import requests
from functools import partial

from .utilities import (
    DEFAULT_API_URL,
    NoNoneDict,
    requires_secret_key, api_bound, wraps_class,
    is_valid_uuid, is_valid_public_key, is_valid_secret_key, repr_format
)
from .errors import NonexistentError, AlreadySubscribedError

import sys
if sys.version_info[0] >= 3:
    from urllib.parse import urljoin
    unicode_type = str
else:
    from urlparse import urljoin
    unicode_type = unicode

def api_request(api_url, endpoint, method, params=None, data=None):
    url = urljoin(api_url, endpoint)
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

class Service(object):
    """A Pushjet service to send messages through. To receive messages, devices
    subscribe to these.

    :param secret_key: The service's API key for write access. If provided,
        :func:`~pushjet.Service.send`, :func:`~pushjet.Service.edit`, and
        :func:`~pushjet.Service.delete` become available.
        Either this or the public key parameter must be present.
    :param public_key: The service's public API key for read access only.
        Either this or the secret key parameter must be present.
    
    :ivar name: The name of the service.
    :ivar icon_url: The URL to the service's icon. May be ``None``.
    :ivar created: When the service was created, as seconds from epoch.
    :ivar secret_key: The service's secret API key, or ``None`` if the service is read-only.
    :ivar public_key: The service's public API key, to be used when subscribing to the service.
    """

    def __repr__(self):
        return "<Pushjet Service: \"{}\">".format(repr_format(self.name))

    @api_bound
    def __init__(self, secret_key=None, public_key=None, _from_data=None):
        if _from_data is not None:
            self._update_from_data(_from_data)
            return
        if secret_key is None and public_key is None:
            raise ValueError("Either a secret key or public key "
                "must be provided.")
        elif secret_key and not is_valid_secret_key(secret_key):
            raise ValueError("Invalid secret key provided.")
        elif public_key and not is_valid_public_key(public_key):
            raise ValueError("Invalid public key provided.")
        self.secret_key = unicode_type(secret_key) if secret_key else None
        self.public_key = unicode_type(public_key) if public_key else None
        self.refresh()
    
    def _request(self, endpoint, method, is_secret, params=None, data=None):
        params = params or {}
        if is_secret:
            params['secret'] = self.secret_key
        else:
            params['service'] = self.public_key
        return api_request(self._api_url, endpoint, method, params, data)

    @requires_secret_key
    def send(self, message, title=None, link=None, importance=None):
        """Send a message to the service's subscribers.
        
        :param message: The message body to be sent.
        :param title: (optional) The message's title. Messages can be without title.
        :param link: (optional) An URL to be sent with the message.
        :param importance: (optional) The priority level of the message. May be
            a number between 1 and 5, where 1 is least important and 5 is most.
        """
        data = NoNoneDict({
            'message': message,
            'title': title,
            'link': link,
            'level': importance
        })
        self._request('message', 'POST', is_secret=True, data=data)

    @requires_secret_key
    def edit(self, name=None, icon_url=None):
        """Edit the service's attributes.

        :param name: (optional) A new name to give the service.
        :param icon_url: (optional) A new URL to use as the service's icon URL.
            Set to an empty string to remove the service's icon entirely.
        """
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
        """Delete the service. Irreversible."""
        self._request('service', 'DELETE', is_secret=True)
    
    def _update_from_data(self, data):
        self.name       = data['name']
        self.icon_url   = data['icon'] or None
        self.created    = data['created']
        self.public_key = data['public']
        self.secret_key = data.get('secret', getattr(self, 'secret_key', None))

    def refresh(self):
        """Refresh the server's information, in case it could be edited from elsewhere."""
        key_name = 'public'
        secret = False
        if self.secret_key is not None:
            key_name = 'secret'
            secret = True
        
        status, response = self._request('service', 'GET', is_secret=secret)
        if status == 404:
            raise NonexistentError("A service with the provided {} key "
                "does not exist (anymore, at least).".format(key_name))
        self._update_from_data(response['service'])

    @classmethod
    def create(cls, name, icon_url=None, _api_url=DEFAULT_API_URL):
        """Create a new service.
        
        :param name: The name of the new service.
        :param icon_url: (optional) An URL to an image to be used as the service's icon.
        :return: :class:`.Service`
        """
        data = NoNoneDict({
            'name': name,
            'icon': icon_url
        })
        _, response = api_request(_api_url, 'service', 'POST', data=data)
        return cls(_from_data=response['service'])

class Device(object):
    """The "receiver" for messages. Subscribes to services and receives any
    messages they send.

    :param uuid: The device's unique ID as a UUID. Does not need to be registered
        before using it. A UUID can be generated with ``uuid.uuid4()``, for example.
    :ivar uuid: The UUID the device was initialized with.
    """

    def __repr__(self):
        return "<Pushjet Device: {}>".format(self.uuid)

    @api_bound
    def __init__(self, uuid):
        if not is_valid_uuid(uuid):
            raise ValueError("Invalid UUID provided. Try uuid.uuid4().")
        self.uuid = unicode_type(uuid)
    
    def _request(self, endpoint, method, params=None, data=None):
        params = (params or {})
        params['uuid'] = self.uuid
        return api_request(self._api_url, endpoint, method, params, data)

    def subscribe(self, service):
        """Subscribe the device to a service.
        
        :param service: The service to subscribe to. May be a public key or a :class:`.Service`. 
        """
        data = {}
        data['service'] = service.public_key if isinstance(service, Service) else service
        status, _ = self._request('subscription', 'POST', data=data)
        if status == 409:
            raise AlreadySubscribedError("The device is already subscribed to that service.")
        elif status == 404:
            raise NonexistentError("A service with the provided public key "
                "does not exist (anymore, at least).")
    
    def unsubscribe(self, service):
        """Unsubscribe the device from a service.
        
        :param service: The service to unsubscribe from. May be a public key or a :class:`.Service`. 
        """
        data = {}
        data['service'] = service.public_key if isinstance(service, Service) else service
        self._request('subscription', 'DELETE', data=data)

    def get_subscriptions(self):
        """Get all the subscriptions the device has.

        :return: A list of :class:`.Subscription`\ s.
        """
        _, response = self._request('subscription', 'GET')
        subscriptions = []
        for subscription_dict in response['subscriptions']:
            subscriptions.append(Subscription(subscription_dict))
        return subscriptions
    
    def get_messages(self):
        """Get all new (that is, as of yet unretrieved) messages.
        
        :return: A list of :class:`.Message`\ s.
        """
        _, response = self._request('message', 'GET')
        messages = []
        for message_dict in response['messages']:
            messages.append(Message(message_dict))
        return messages

class Subscription(object):
    """A subscription to a service, with the metadata that entails.

    :ivar service: The service the subscription is to, as a :class:`.Service`.
    :ivar time_subscribed: When the subscription was made, as seconds from epoch.
    :ivar last_checked: When the device last retrieved messages from the subscription,
        as seconds from epoch.
    :ivar device_uuid: The UUID of the device that owns the subscription.
    """

    def __repr__(self):
        return "<Pushjet Subscription to service \"{}\">".format(repr_format(self.service.name))

    def __init__(self, subscription_dict):
        self.service = Service(_from_data=subscription_dict['service'])
        self.time_subscribed = subscription_dict['timestamp']
        self.last_checked = subscription_dict['timestamp_checked']
        self.device_uuid = subscription_dict['uuid'] # Not sure this is needed, but...

class Message(object):
    """A message received from a service.
    
    :ivar message: The message body.
    :ivar title: The message title. May be ``None``.
    :ivar link: The URL the message links to. May be ``None``.
    :ivar time_sent: When the message was sent, as seconds from epoch.
    :ivar importance: The message's priority level between 1 and 5, where 1 is
        least important and 5 is most.
    :ivar service: The :class:`.Service` that sent the message.
    """

    def __repr__(self):
        return "<Pushjet Message: \"\">".format(repr_format(self.title or self.message))

    def __init__(self, message_dict):
        self.message = message_dict['message']
        self.title = message_dict['title'] or None
        self.link = message_dict['link'] or None
        self.time_sent = message_dict['timestamp']
        self.importance = message_dict['level']
        self.service = Service(_from_data=message_dict['service'])

class Api(object):
    """An API with a custom URL. Use this if you're connecting to a self-hosted
    Pushjet API instance, or a non-standard one in general.

    :param url: The URL to the API instance.
    :ivar url: The URL to the API instance, as supplied.
    """

    def __repr__(self):
        return "<Pushjet Api: {}>".format(self.url.encode(sys.stdout.encoding, errors='replace'))

    def __init__(self, url):
        self.url = unicode_type(url)
    
    @property
    @wraps_class(Service)
    def Service(self):
        cls = partial(Service, _api_url=self.url)
        cls.create = partial(Service.create, _api_url=self.url)
        return cls
    
    @property
    @wraps_class(Device)
    def Device(self):
        return partial(Device, _api_url=self.url)
