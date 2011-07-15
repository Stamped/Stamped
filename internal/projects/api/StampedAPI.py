#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from abc import abstractmethod

# TODO: input validation and output formatting
# NOTE: this is the place where all input validation should occur. any 
# db-specific validation should occur elsewhere. this validation incluedes, 
# but is not limited to:
#    * ensuring that a given ID is "valid"
#    * ensuring that a given relationship is "valid"
#    * ensuring that for methods which accept a user ID and should be 
#      considered "priveleged", then the request is coming from a properly 
#      authenticated user. e.g., either an administrator or the user who is 
#      currently logged into the application.

class StampedAPI(AStampedAPI):
    """
        Database-agnostic implementation of the internal API for accessing 
        and manipulating all Stamped backend databases.
    """
    
    def __init__(self):
        AStampedAPI.__init__(self)
        self._validated = False
    
    def _validate(self):
        assert hasattr(self, '_accountDB')    and isinstance(self._userDB, AAccountDB)
        assert hasattr(self, '_entityDB')     and isinstance(self._entityDB, AEntityDB)
        assert hasattr(self, '_userDB')       and isinstance(self._userDB, AUserDB)
        assert hasattr(self, '_stampDB')      and isinstance(self._stampDB, AStampDB)
        assert hasattr(self, '_commentDB')    and isinstance(self._commentDB, ACommentDB)
        assert hasattr(self, '_favoriteDB')   and isinstance(self._favoriteDB, AFavoriteDB)
        assert hasattr(self, '_collectionDB') and isinstance(self._collectionDB, ACollectionDB)
        assert hasattr(self, '_friendshipDB') and isinstance(self._friendshipDB, AFriendshipDB)
        
        self._validated = True
    
    @property
    def isValid(self):
        return self._validated
    
    # ######## #
    # Accounts #
    # ######## #
    
    def addAccount(user):
        return self._userDB.addUser(user)
    
    def addAccounts(users):
        return self._userDB.addUsers(users)
    
    def getAccount(userID):
        return self._accountDB.getAccount(userID)
    
    def updateAccount(account):
        return self._accountDB.updateAccount(account)
    
    def removeAccount(userID):
        return self._accountDB.removeAccount(userID)
    
    def flagAccount(userID):
        return self._accountDB.flagAccount(userID)
    
    def unflagAccount(userID):
        return self._accountDB.unflagAccount(userID)
    
    # ##### #
    # Users #
    # ##### #
    
    def getUser(userID):
        return self._userDB.getUser(userID)
    
    def getUsers(userIDs):
        return self._userDB.lookupUsers(userIDs, None)
    
    def getUserByName(username):
        return self._userDB.lookupUsers(None, [ username ])
    
    def getUsersByNames(usernames):
        return self._userDB.lookupUsers(None, usernames)
    
    def searchUsers(query, limit=20):
        return self._userDB.searchUsers(query, limit)
    
    def getPrivacy(userID):
        return self._userDB.getPrivacy(userID)
    
    # ############# #
    # Relationships #
    # ############# #
    
    def addFriendship(relationship):
        return self._friendshipDB.addFriendship(relationship)
    
    def checkFriendship(relationship):
        return self._friendshipDB.checkFriendship(relationship)
    
    def removeFriendship(relationship):
        return self._friendshipDB.removeFriendship(relationship)
    
    def getFriends(userID):
        return self._friendshipDB.getFriends(userID)
    
    def getFollowers(userID):
        return self._friendshipDB.getFollowers(userID)
    
    def approveFriendship(relationship):
        return self._friendshipDB.approveFriendship(relationship)
    
    def addBlock(relationship):
        return self._friendshipDB.addBlock(relationship)
    
    def checkBlock(relationship):
        return self._friendshipDB.checkBlock(relationship)
    
    def removeBlock(relationship):
        return self._friendshipDB.removeBlock(relationship)
    
    def getBlocks(userID):
        return self._friendshipDB.getBlocks(userID)
    
    # ######### #
    # Favorites #
    # ######### #
    
    def addFavorite(userID, stampID):
        # TODO: construct a favorite object from (userID, stampID)
        raise NotImplementedError
        return self._favoriteDB.addFavorite(favorite)
    
    def getFavorite(favoriteID):
        return self._favoriteDB.getFavorite(favoriteID)
    
    def removeFavorite(favoriteID):
        return self._favoriteDB.removeFavorite(favoriteID)
    
    def completeFavorite(favoriteID):
        return self._favoriteDB.completeFavorite(favoriteID)
    
    def getFavoriteIDs(userID):
        return self._favoriteDB.getFavoriteIds(favoriteID)
    
    def getFavorites(userID):
        return self._favoriteDB.getFavoriteIds(favoriteID)
    
    # ######## #
    # Entities #
    # ######## #
    
    def addEntity(entity):
        pass
    
    def addEntities(entities):
        pass
    
    def getEntity(entityID):
        pass
    
    def updateEntity(entity):
        pass
    
    def removeEntity(entityID):
        pass
    
    def searchEntities(query, limit=20):
        pass
    
    # ###### #
    # Stamps #
    # ###### #
    
    def addStamp(stamp):
        pass
    
    def addStamps(stamps):
        pass
    
    def getStamp(stampID):
        pass
    
    def getStamps(stampIDs):
        pass
    
    def updateStamp(stampID):
        pass
    
    def removeStamp(stampID):
        pass
    
    # ########### #
    # Collections #
    # ########### #
    
    def getInboxStampIDs(userID, limit=None):
        pass
    
    def getInboxStamps(userID, limit=None):
        pass
    
    def getUserStampIDs(userID):
        pass
    
    def getUserStamps(userID):
        pass
    
    def getUserMentions(userID):
        pass

