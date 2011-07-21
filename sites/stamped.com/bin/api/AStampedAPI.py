#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from abc import abstractmethod
from AEntitySink import AEntitySink

class AStampedAPI(AEntitySink):
    """
        Defines the internal API for accessing and manipulating all Stamped 
        backend databases.
    """
    
    def __init__(self, desc):
        AEntitySink.__init__(self, desc)
    
    # ######## #
    # Accounts #
    # ######## #
    
    @abstractmethod
    def addAccount(self, acct):
        raise NotImplementedError
    
    @abstractmethod
    def getAccount(self, userID):
        raise NotImplementedError
    
    @abstractmethod
    def updateAccount(self, user):
        raise NotImplementedError
    
    @abstractmethod
    def removeAccount(self, userID):
        raise NotImplementedError
    
    @abstractmethod
    def flagAccount(self, userID):
        raise NotImplementedError
    
    @abstractmethod
    def unflagAccount(self, userID):
        raise NotImplementedError
    
    # ##### #
    # Users #
    # ##### #
    
    @abstractmethod
    def getUser(self, userID):
        raise NotImplementedError
    
    @abstractmethod
    def getUsers(self, userIDs):
        raise NotImplementedError
    
    @abstractmethod
    def getUserByName(self, username):
        raise NotImplementedError
    
    @abstractmethod
    def getUsersByNames(self, usernames):
        raise NotImplementedError
    
    @abstractmethod
    def searchUsers(self, query, limit=20):
        raise NotImplementedError
    
    @abstractmethod
    def getPrivacy(self, userID):
        raise NotImplementedError
    
    # ############# #
    # Relationships #
    # ############# #
    
    @abstractmethod
    def addFriendship(self, relationship):
        raise NotImplementedError
    
    @abstractmethod
    def checkFriendship(self, relationship):
        raise NotImplementedError
    
    @abstractmethod
    def removeFriendship(self, relationship):
        raise NotImplementedError
    
    @abstractmethod
    def getFriends(self, userID):
        raise NotImplementedError
    
    @abstractmethod
    def getFollowers(self, userID):
        raise NotImplementedError
    
    @abstractmethod
    def approveFriendship(self, relationship):
        raise NotImplementedError
    
    @abstractmethod
    def addBlock(self, relationship):
        raise NotImplementedError
    
    @abstractmethod
    def checkBlock(self, relationship):
        raise NotImplementedError
    
    @abstractmethod
    def removeBlock(self, relationship):
        raise NotImplementedError
    
    @abstractmethod
    def getBlocks(self, userID):
        raise NotImplementedError
    
    # ######### #
    # Favorites #
    # ######### #
    
    @abstractmethod
    def addFavorite(self, userID, entityID, stampID):
        raise NotImplementedError
    
    @abstractmethod
    def getFavorite(self, userID, favoriteID):
        raise NotImplementedError
    
    @abstractmethod
    def removeFavorite(self, userID, favoriteID):
        raise NotImplementedError
    
    @abstractmethod
    def completeFavorite(self, userID, favoriteID):
        raise NotImplementedError
    
    @abstractmethod
    def getFavoriteIDs(self, userID):
        raise NotImplementedError
    
    @abstractmethod
    def getFavorites(self, userID):
        raise NotImplementedError
    
    # ######## #
    # Entities #
    # ######## #
    
    @abstractmethod
    def addEntity(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getEntity(self, entityID):
        raise NotImplementedError
    
    @abstractmethod
    def updateEntity(self, entity):
        raise NotImplementedError
    
    @abstractmethod
    def removeEntity(self, entityID):
        raise NotImplementedError
    
    @abstractmethod
    def searchEntities(self, query, limit=20):
        raise NotImplementedError
    
    # ###### #
    # Stamps #
    # ###### #
    
    @abstractmethod
    def addStamp(self, stamp):
        raise NotImplementedError
    
    @abstractmethod
    def getStamp(self, stampID):
        raise NotImplementedError
    
    @abstractmethod
    def getStamps(self, stampIDs):
        raise NotImplementedError
    
    @abstractmethod
    def updateStamp(self, stamp):
        raise NotImplementedError
    
    @abstractmethod
    def removeStamp(self, stampID):
        raise NotImplementedError
    
    # ########### #
    # Collections #
    # ########### #
    
    @abstractmethod
    def getInboxStampIDs(self, userID, limit=None):
        raise NotImplementedError
    
    @abstractmethod
    def getInboxStamps(self, userID, limit=None):
        raise NotImplementedError
    
    @abstractmethod
    def getUserStampIDs(self, userID):
        raise NotImplementedError
    
    @abstractmethod
    def getUserStamps(self, userID):
        raise NotImplementedError
    
    @abstractmethod
    def getUserMentions(self, userID):
        raise NotImplementedError
    
    # ########### #
    # Private API #
    # ########### #
    
    def _processItem(self, item):
        return self._addEntity(item)
    
    def _processItems(self, items):
        return self._addEntities(items)
    
    @abstractmethod
    def _addEntity(self, entity):
        raise NotImplementedError
    
    @abstractmethod
    def _addEntities(self, entities):
        raise NotImplementedError

