# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import requests

API_URL = 'https://api.pushjet.io/'    

class Service(object):
    def __init__(self, secret=None, public=None):
        pass
    
    def send(self, message, title=None, link=None, importance=None):
        pass

    def update(self, name=None, icon_url=None):
        pass

    def delete(self):
        pass
    
    def refresh(self):
        pass

    @classmethod
    def create(name, icon_url=None):
        pass
