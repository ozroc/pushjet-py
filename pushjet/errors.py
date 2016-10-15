# -*- coding: utf-8 -*-

from __future__ import unicode_literals

class PushjetError(Exception):
    pass

class WriteAccessError(PushjetError):
    pass

class NonexistentError(PushjetError):
    pass

class AlreadySubscribedError(PushjetError):
    pass
