#!/usr/bin/python

__author__    = "Stamped (dev@Stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class AFavoriteDB(object):
    
    @abstract    
    def addFavorite(self, favorite):
        pass
    
    @abstract
    def getFavorite(self, userId, entityId):
        pass
    
    @abstract
    def removeFavorite(self, userId, entityId):
        pass
    
    @abstract
    def completeFavorite(self, entityId, userId, complete=True):
        pass
    
    @abstract
    def getFavorites(self, userId, **kwargs):
        pass

