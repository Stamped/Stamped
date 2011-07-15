#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from abc import abstractmethod

class AStampedAPI(object):
    """
        Defines the internal API for accessing and manipulating all Stamped 
        backend databases.
    """
    
    # ######## #
    # Accounts #
    # ######## #
    
    @abstractmethod
    def addAccount(user):
        pass
    
    @abstractmethod
    def addAccounts(users):
        pass
    
    @abstractmethod
    def getAccount(userID):
        pass
    
    @abstractmethod
    def updateAccount(user):
        pass
    
    @abstractmethod
    def removeAccount(userID):
        pass
    
    @abstractmethod
    def flagAccount(userID):
        pass
    
    @abstractmethod
    def unflagAccount(userID):
        pass
    
    # ##### #
    # Users #
    # ##### #
    
    @abstractmethod
    def getUser(userID):
        pass
    
    @abstractmethod
    def getUsers(userIDs):
        pass
    
    @abstractmethod
    def getUserByName(username):
        pass
    
    @abstractmethod
    def getUsersByNames(usernames):
        pass
    
    @abstractmethod
    def searchUsers(query, limit=20):
        pass
    
    @abstractmethod
    def getPrivacy(userID):
        pass
    
    # ############# #
    # Relationships #
    # ############# #
    
    @abstractmethod
    def addFriendship(relationship):
        pass
    
    @abstractmethod
    def checkFriendship(relationship):
        pass
    
    @abstractmethod
    def removeFriendship(relationship):
        pass
    
    @abstractmethod
    def getFriends(userID):
        pass
    
    @abstractmethod
    def getFollowers(userID):
        pass
    
    @abstractmethod
    def approveFriendship(relationship):
        pass
    
    @abstractmethod
    def addBlock(relationship):
        pass
    
    @abstractmethod
    def checkBlock(relationship):
        pass
    
    @abstractmethod
    def removeBlock(relationship):
        pass
    
    @abstractmethod
    def getBlocks(userID):
        pass
    
    # ######### #
    # Favorites #
    # ######### #
    
    @abstractmethod
    def addFavorite(userID, stampID):
        pass
    
    @abstractmethod
    def getFavorite(favoriteID):
        pass
    
    @abstractmethod
    def removeFavorite(favoriteID):
        pass
    
    @abstractmethod
    def completeFavorite(favoriteID):
        pass
    
    @abstractmethod
    def getFavoriteIDs(userID):
        pass
    
    @abstractmethod
    def getFavorites(userID):
        pass
    
    # ######## #
    # Entities #
    # ######## #
    
    @abstractmethod
    def addEntity(entity):
        pass
    
    @abstractmethod
    def addEntities(entities):
        pass
    
    @abstractmethod
    def getEntity(entityID):
        pass
    
    @abstractmethod
    def updateEntity(entity):
        pass
    
    @abstractmethod
    def removeEntity(entityID):
        pass
    
    @abstractmethod
    def searchEntities(query, limit=20):
        pass
    
    # ###### #
    # Stamps #
    # ###### #
    
    @abstractmethod
    def addStamp(stamp):
        pass
    
    @abstractmethod
    def addStamps(stamps):
        pass
    
    @abstractmethod
    def getStamp(stampID):
        pass
    
    @abstractmethod
    def getStamps(stampIDs):
        pass
    
    @abstractmethod
    def updateStamp(stampID):
        pass
    
    @abstractmethod
    def removeStamp(stampID):
        pass
    
    # ########### #
    # Collections #
    # ########### #
    
    @abstractmethod
    def getInboxStampIDs(userID, limit=None):
        pass
    
    @abstractmethod
    def getInboxStamps(userID, limit=None):
        pass
    
    @abstractmethod
    def getUserStampIDs(userID):
        pass
    
    @abstractmethod
    def getUserStamps(userID):
        pass
    
    @abstractmethod
    def getUserMentions(userID):
        pass

