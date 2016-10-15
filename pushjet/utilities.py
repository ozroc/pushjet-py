# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
import sys
from functools import wraps
from .errors import WriteAccessError

DEFAULT_API_URL = 'https://api.pushjet.io/'

# Help class(...es? Nah. Just singular for now.)

class NoNoneDict(dict):
    def __setitem__(self, key, value):
        if value is not None:
            dict.__setitem__(self, key, value)

# Decorators

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

# Helper functions

UUID_RE = re.compile(r'^[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12}$')
PUBLIC_KEY_RE = re.compile(r'^[A-Za-z0-9]{4}-[A-Za-z0-9]{6}-[A-Za-z0-9]{12}-[A-Za-z0-9]{5}-[A-Za-z0-9]{9}$')
SECRET_KEY_RE = re.compile(r'^[A-Za-z0-9]{32}$')

is_valid_uuid = lambda s: UUID_RE.match(s) is not None
is_valid_public_key = lambda s: PUBLIC_KEY_RE.match(s) is not None
is_valid_secret_key = lambda s: SECRET_KEY_RE.match(s) is not None

def repr_format(s):
    s = s.replace('\n', ' ').replace('\r', '')
    original_length = len(s)
    s = s[:30]
    s += '...' if len(s) != original_length else ''
    s = s.encode(sys.stdout.encoding, errors='replace')
    return s
