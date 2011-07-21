#!/usr/bin/python

__author__ = "Stamped (dev@Stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from abc import abstractmethod
from Favorite import Favorite

class AFavoriteDB(object):
    
    def __init__(self, desc):
        self._desc = desc

    @abstractmethod    
    def addFavorite(self, favorite):
        pass
        
    @abstractmethod
    def getFavorite(self, favoriteId):
        pass
        
    @abstractmethod
    def removeFavorite(self, favorite):
        pass
        
    @abstractmethod
    def completeFavorite(self, favoriteId, complete=True):
        pass
        
    @abstractmethod
    def getFavoriteIDs(self, userId):
        pass
        
    @abstractmethod
    def getFavorites(self, userId):
        pass
        
