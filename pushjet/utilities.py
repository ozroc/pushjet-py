# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from functools import wraps
from .errors import WriteAccessError

DEFAULT_API_URL = 'https://api.pushjet.io/'

class NoNoneDict(dict):
    def __setitem__(self, key, value):
        if value is not None:
            dict.__setitem__(self, key, value)

def requires_secret_key(func):
    @wraps(func)
    def with_secret_key_requirement(self, *args, **kwargs):
        if self.secret_key is None:
            raise WriteAccessError("The Service doesn't have a secret "
                "key provided, and therefore lacks write permission.")
        return func(self, *args, **kwargs)
    return with_secret_key_requirement

def api_bound(func):
    @wraps(func)
    def with_api_argument(self, *args, **kwargs):
        self._api_url = kwargs.pop('_api_url', DEFAULT_API_URL)
        return func(self, *args, **kwargs)
    return with_api_argument

def wraps_class(cls):
    """Nitpicky quality-of-life decorator to make wrapped classes more informative."""
    def add_note(func):
        func.__doc__ = "For documentation, see help(pushjet.{}).".format(cls.__name__)
        return func
    return add_note
