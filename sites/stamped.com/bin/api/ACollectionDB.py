#!/usr/bin/python

__author__ = "Stamped (dev@Stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped, Inc."
__license__ = "TODO"

import Globals
from utils import abstract

class ACollectionDB(object):
    
    @abstract
    def getInboxStampIDs(self, userId, limit=None):
        pass
    
    @abstract
    def getInboxStamps(self, userId, limit=None):
        pass
    
    @abstract
    def getUserStampIDs(self, userId, limit=None):
        pass
    
    @abstract
    def getUserStamps(self, userId, limit=None):
        pass
    
    @abstract
    def getMentions(self, userId, limit=None):
        pass

