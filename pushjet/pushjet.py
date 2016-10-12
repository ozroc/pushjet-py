# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import requests
from functools import wraps

API_URL = 'https://api.pushjet.io/'

def requires_secret(func):
    @wraps(func)
    def with_secret_requirement(self, *args, **kwargs):
        if self.secret is None:
            raise WriteAccessError("The Service doesn't have a secret "
                "key provided, and therefore lacks write permission.")
        func(*args, **kwargs)

    return with_secret_requirement

class Service(object):
    def __init__(self, secret=None, public=None):
        pass
    
    @requires_secret
    def send(self, message, title=None, link=None, importance=None):
        pass

    @requires_secret
    def update(self, name=None, icon_url=None):
        pass

    @requires_secret
    def delete(self):
        pass
    
    def refresh(self):
        pass

    @classmethod
    def create(name, icon_url=None):
        pass
