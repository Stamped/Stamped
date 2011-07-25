#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
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
    def addAccount(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def updateAccount(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getAccount(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def updateProfile(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def updateProfileImage(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def verifyAccountCredentials(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def removeAccount(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def resetPassword(self, params):
        raise NotImplementedError
    
    # ##### #
    # Users #
    # ##### #
    
    @abstractmethod
    def getUser(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getUsers(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getUsersByName(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def searchUsers(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getPrivacy(self, params):
        raise NotImplementedError
    
    # ############# #
    # Relationships #
    # ############# #
    
    @abstractmethod
    def addFriendship(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def removeFriendship(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def approveFriendship(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def addBlock(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def removeBlock(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def checkFriendship(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getFriends(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getFollowers(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def checkBlock(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getBlocks(self, params):
        raise NotImplementedError
    
    # ######### #
    # Favorites #
    # ######### #
    
    @abstractmethod
    def addFavorite(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def removeFavorite(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getFavorites(self, params):
        raise NotImplementedError
    
    # ######## #
    # Entities #
    # ######## #
    
    @abstractmethod
    def addEntity(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getEntity(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def updateEntity(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def removeEntity(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def searchEntities(self, params):
        raise NotImplementedError
    
    # ###### #
    # Stamps #
    # ###### #
    
    @abstractmethod
    def addStamp(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getStamp(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getStamps(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def updateStamp(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def removeStamp(self, params):
        raise NotImplementedError
    
    # ######## #
    # Comments #
    # ######## #
    
    @abstractmethod
    def addComment(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def removeComment(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getComments(self, params):
        raise NotImplementedError
    
    # ########### #
    # Collections #
    # ########### #
    
    @abstractmethod
    def getInboxStampIDs(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getInboxStamps(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getUserStampIDs(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getUserStamps(self, params):
        raise NotImplementedError
    
    @abstractmethod
    def getUserMentions(self, params):
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

