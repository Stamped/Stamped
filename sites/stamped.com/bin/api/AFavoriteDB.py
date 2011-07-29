#!/usr/bin/python

__author__ = "Stamped (dev@Stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from utils import abstract
from Favorite import Favorite

class AFavoriteDB(object):
    
    @abstract    
    def addFavorite(self, favorite):
        pass
    
    @abstract
    def getFavorite(self, favoriteId):
        pass
    
    @abstract
    def removeFavorite(self, favorite):
        pass
    
    @abstract
    def completeFavorite(self, favoriteId, complete=True):
        pass
    
    @abstract
    def getFavoriteIDs(self, userId):
        pass
    
    @abstract
    def getFavorites(self, userId):
        pass

