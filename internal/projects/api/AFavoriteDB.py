#!/usr/bin/python

__author__ = "Stamped (dev@Stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from Favorite import Favorite

class AFavoriteDB(object):
    
    def __init__(self, desc):
        self._desc = desc
    
    def addFavorite(self, favorite):
        raise NotImplementedError
    
    def getFavorite(self, favoriteID):
        raise NotImplementedError
    
    def removeFavorite(self, favoriteID):
        raise NotImplementedError
    
    def addFavorites(self, favorites):
        return map(self.addFavorite, favorites)
    
    def getFavorites(self, favoriteIDs):
        return map(self.getFavorite, favoriteIDs)
    
    def removeFavorites(self, favoriteIDs):
        return map(self.removeFavorite, favoriteIDs)
    
    def __len__(self):
        raise NotImplementedError
    
    def __str__(self):
        return self._desc

