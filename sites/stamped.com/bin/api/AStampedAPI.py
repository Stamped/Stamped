#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from utils import abstract
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
    
    @abstract
    def addAccount(self, params):
        raise NotImplementedError
    
    @abstract
    def updateAccount(self, params):
        raise NotImplementedError
    
    @abstract
    def getAccount(self, params):
        raise NotImplementedError
    
    @abstract
    def updateProfile(self, params):
        raise NotImplementedError
    
    @abstract
    def updateProfileImage(self, params):
        raise NotImplementedError
    
    @abstract
    def verifyAccountCredentials(self, params):
        raise NotImplementedError
    
    @abstract
    def removeAccount(self, params):
        raise NotImplementedError
    
    @abstract
    def resetPassword(self, params):
        raise NotImplementedError
    
    # ##### #
    # Users #
    # ##### #
    
    @abstract
    def getUser(self, params):
        raise NotImplementedError
    
    @abstract
    def getUsers(self, params):
        raise NotImplementedError
    
    @abstract
    def getUsersByName(self, params):
        raise NotImplementedError
    
    @abstract
    def searchUsers(self, params):
        raise NotImplementedError
    
    @abstract
    def getPrivacy(self, params):
        raise NotImplementedError
    
    # ############# #
    # Relationships #
    # ############# #
    
    @abstract
    def addFriendship(self, params):
        raise NotImplementedError
    
    @abstract
    def removeFriendship(self, params):
        raise NotImplementedError
    
    @abstract
    def approveFriendship(self, params):
        raise NotImplementedError
    
    @abstract
    def addBlock(self, params):
        raise NotImplementedError
    
    @abstract
    def removeBlock(self, params):
        raise NotImplementedError
    
    @abstract
    def checkFriendship(self, params):
        raise NotImplementedError
    
    @abstract
    def getFriends(self, params):
        raise NotImplementedError
    
    @abstract
    def getFollowers(self, params):
        raise NotImplementedError
    
    @abstract
    def checkBlock(self, params):
        raise NotImplementedError
    
    @abstract
    def getBlocks(self, params):
        raise NotImplementedError
    
    # ######### #
    # Favorites #
    # ######### #
    
    @abstract
    def addFavorite(self, params):
        raise NotImplementedError
    
    @abstract
    def removeFavorite(self, params):
        raise NotImplementedError
    
    @abstract
    def getFavorites(self, params):
        raise NotImplementedError
    
    # ######## #
    # Entities #
    # ######## #
    
    @abstract
    def addEntity(self, params):
        raise NotImplementedError
    
    @abstract
    def getEntity(self, params):
        raise NotImplementedError
    
    @abstract
    def updateEntity(self, params):
        raise NotImplementedError
    
    @abstract
    def removeEntity(self, params):
        raise NotImplementedError
    
    @abstract
    def searchEntities(self, params):
        raise NotImplementedError
    
    # ###### #
    # Stamps #
    # ###### #
    
    @abstract
    def addStamp(self, params):
        raise NotImplementedError
    
    @abstract
    def getStamp(self, params):
        raise NotImplementedError
    
    @abstract
    def getStamps(self, params):
        raise NotImplementedError
    
    @abstract
    def updateStamp(self, params):
        raise NotImplementedError
    
    @abstract
    def removeStamp(self, params):
        raise NotImplementedError
    
    # ######## #
    # Comments #
    # ######## #
    
    @abstract
    def addComment(self, params):
        raise NotImplementedError
    
    @abstract
    def removeComment(self, params):
        raise NotImplementedError
    
    @abstract
    def getComments(self, params):
        raise NotImplementedError
    
    # ########### #
    # Collections #
    # ########### #
    
    @abstract
    def getInboxStampIDs(self, params):
        raise NotImplementedError
    
    @abstract
    def getInboxStamps(self, params):
        raise NotImplementedError
    
    @abstract
    def getUserStampIDs(self, params):
        raise NotImplementedError
    
    @abstract
    def getUserStamps(self, params):
        raise NotImplementedError
    
    @abstract
    def getUserMentions(self, params):
        raise NotImplementedError
    
    # ########### #
    # Private API #
    # ########### #
    
    def _processItem(self, item):
        return self._addEntity(item)
    
    def _processItems(self, items):
        return self._addEntities(items)
    
    @abstract
    def _addEntity(self, entity):
        raise NotImplementedError
    
    @abstract
    def _addEntities(self, entities):
        raise NotImplementedError

