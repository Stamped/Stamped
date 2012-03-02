#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class AImageDB(object):
    
    @abstract
    def addProfileImage(self, userId, image):
        pass
    
    @abstract
    def addEntityImage(self, entityId, image):
        pass
    
    @abstract
    def addStampImage(self, stampId, image):
        pass
    
    def __str__(self):
        return self.__class__.__name__

