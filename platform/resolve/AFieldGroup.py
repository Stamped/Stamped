#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'AFieldGroup' ]

import Globals
from logs import log, report

try:
    from abc        import ABCMeta, abstractmethod, abstractproperty
    from datetime       import datetime
except:
    report()
    raise

class AFieldGroup(object):
    """
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractproperty
    def groupName(self):
        pass

    @abstractmethod
    def getSource(self, entity):
        pass

    @abstractmethod
    def setSource(self, entity, source):
        pass
    
    @abstractmethod
    def getTimestamp(self, entity):
        pass

    @abstractmethod
    def setTimestamp(self, entity, timestamp):
        pass

    @abstractmethod
    def syncFields(self, entity, destination):
        pass

    @abstractmethod
    def syncDecorations(self, entity, destination):
        pass
    
    @abstractmethod
    def eligible(self, entity):
        pass

    def enrichEntityWithEntityProxy(self, entity, proxy):
        pass
