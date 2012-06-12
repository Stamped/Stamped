#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from AEntitySink import AEntitySink
from utils       import abstract

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
    def addAccount(self, account):
        raise NotImplementedError
    
    @abstract
    def updateAccountSettings(self, authUserId, data):
        raise NotImplementedError
    
    @abstract
    def getAccount(self, authUserId):
        raise NotImplementedError
    
    @abstract
    def updateProfile(self, authUserId, data):
        raise NotImplementedError
    
    @abstract
    def updateProfileImage(self, authUserId, url):
        raise NotImplementedError
    
    @abstract
    def removeAccount(self, userId):
        raise NotImplementedError
    
    @abstract
    def verifyAccountCredentials(self, params):
        raise NotImplementedError
    
    @abstract
    def resetPassword(self, params):
        raise NotImplementedError
    
    # ##### #
    # Users #
    # ##### #
    
    @abstract
    def getUser(self, userRequest, authUserId):
        raise NotImplementedError
    
    @abstract
    def getUsers(self, userIds, screenNames, authUserId):
        raise NotImplementedError
    
    @abstract
    def searchUsers(self, query, limit, authUserId):
        raise NotImplementedError
    
    @abstract
    def getPrivacy(self, userRequest):
        raise NotImplementedError
    
    # ############# #
    # Relationships #
    # ############# #
    
    @abstract
    def addFriendship(self, authUserId, userRequest):
        raise NotImplementedError
    
    @abstract
    def removeFriendship(self, authUserId, userRequest):
        raise NotImplementedError
    
    @abstract
    def approveFriendship(self, data, auth):
        raise NotImplementedError
    
    @abstract
    def checkFriendship(self, authUserId, userRequest):
        raise NotImplementedError
    
    @abstract
    def getFriends(self, userRequest):
        raise NotImplementedError
    
    @abstract
    def getFollowers(self, userRequest):
        raise NotImplementedError
    
    @abstract
    def addBlock(self, authUserId, userRequest):
        raise NotImplementedError
    
    @abstract
    def removeBlock(self, authUserId, userRequest):
        raise NotImplementedError
    
    @abstract
    def checkBlock(self, authUserId, userRequest):
        raise NotImplementedError
    
    @abstract
    def getBlocks(self, authUserId):
        raise NotImplementedError
    
    # ######## #
    # Entities #
    # ######## #
    
    @abstract
    def addEntity(self, entity):
        raise NotImplementedError
    
    @abstract
    def getEntity(self, entityId, authUserId=None):
        raise NotImplementedError

    @abstract
    def updateCustomEntity(self, authUserId, entityId, data):
        raise NotImplementedError
    
    @abstract
    def updateEntity(self, data, auth):
        raise NotImplementedError
    
    @abstract
    def removeEntity(self, entityId):
        raise NotImplementedError
    
    @abstract
    def removeCustomEntity(self, authUserId, entityId):
        raise NotImplementedError
    
    @abstract
    def searchEntities(self, query, coordinates=None, authUserId=None):
        raise NotImplementedError
    
    # ###### #
    # Stamps #
    # ###### #
    
    @abstract
    def addStamp(self, authUserId, entityId, data):
        raise NotImplementedError
    
    @abstract
    def getStamp(self, stampId, authUserId):
        raise NotImplementedError
    
    @abstract
    def updateStamp(self, authUserId, stampId, data):  
        raise NotImplementedError
    
    @abstract
    def removeStamp(self, authUserId, stampId):
        raise NotImplementedError
    
    # ######## #
    # Comments #
    # ######## #
    
    @abstract
    def addComment(self, authUserId, stampId, blurb):
        raise NotImplementedError
    
    @abstract
    def removeComment(self, authUserId, commentId):
        raise NotImplementedError
    
    @abstract
    def getComments(self, stampId, authUserId, **kwargs): 
        raise NotImplementedError
    
    # ########### #
    # Collections #
    # ########### #
    
    @abstract
    def getInboxStamps(self, authUserId, **kwargs):
        raise NotImplementedError
    
    @abstract
    def getUserStamps(self, userRequest, authUserId, **kwargs):
        raise NotImplementedError
    
    @abstract
    def getUserMentions(self, params):
        raise NotImplementedError
    
    # ##### #
    # Todos #
    # ##### #
    
    @abstract
    def addTodo(self, authUserId, entityId, stampId=None):
        raise NotImplementedError
    
    @abstract
    def removeTodo(self, authUserId, entityId):
        raise NotImplementedError
    
    @abstract
    def getTodos(self, authUserId, **kwargs):
        raise NotImplementedError
    
    # ######## #
    # Activity #
    # ######## #
    
    @abstract
    def getActivity(self, authUserId, **kwargs):
        raise NotImplementedError

    # ##### #
    # Menus #
    # ##### #
    
    @abstract
    def getMenu(self, entityId):
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
    
    @abstract
    def getStats(self):
        raise NotImplementedError
    
    @abstract
    def addClientLogsEntry(self, entry):
        raise NotImplementedError

