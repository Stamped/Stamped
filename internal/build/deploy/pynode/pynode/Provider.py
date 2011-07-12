#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Utils
from abc import abstractmethod

class Provider(object):
    def __init__(self, resource):
        self.resource = resource
    
    def _installProvider(self):
        return True
    
    @Utils.lazy_property
    def installed(self):
        return self._installProvider()
    
    def __repr__(self):
        return "Provider(%s)" % repr(self.resource)

