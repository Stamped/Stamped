#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from abc import abstractmethod
from datetime import datetime

from Exceptions import InvalidArgument
from AStampedAPI import AStampedAPI

from AAccountDB import AAccountDB
from AEntityDB import AEntityDB
from AUserDB import AUserDB
from AStampDB import AStampDB
from ACommentDB import ACommentDB
from AFavoriteDB import AFavoriteDB
from ACollectionDB import ACollectionDB
from AFriendshipDB import AFriendshipDB

from Account import Account
from Entity import Entity
from User import User
from Stamp import Stamp
from Comment import Comment
from Favorite import Favorite
from Friendship import Friendship
from Collection import Collection

# TODO: input validation and output formatting
# NOTE: this is the place where all input validation should occur. any 
# db-specific validation should occur elsewhere. This validation includes 
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
        assert hasattr(self, '_accountDB')    and isinstance(self._accountDB, AAccountDB)
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
    
    def addAccount(self, params):
        account = Account()
        account.first_name = params.first_name
        account.last_name = params.last_name
        account.username = params.username
        account.email = params.email
        account.password = params.password
        account.locale = params.locale
        account.color = { 'primary_color': params.primary_color }
        
        if params.secondary_color != None:
            account.color['secondary_color'] = params.secondary_color
        if params.img != None:
            account.img = params.img
        if params.website != None:
            account.website = params.website
        if params.bio != None:
            account.bio = params.bio
            
        account.flags = { 'privacy': params.privacy }
        
        if not account.isValid:
            raise InvalidArgument('Invalid input')
        
        result = {}
        result['id'] = self._accountDB.addAccount(account)
        return result
    
    def getAccount(self, userID):
        return self._accountDB.getAccount(userID)
    
    def updateAccount(self, params):
        account = self.getAccount(params.account_id)
        
        if params.first_name != None:
            account.first_name = params.first_name
        if params.last_name != None:
            account.last_name = params.last_name
        if params.username != None:
            account.username = params.username
        if params.email != None:
            account.email = params.email
        if params.password != None:
            account.password = params.password
        if params.locale != None:
            account.locale = params.locale
        if params.primary_color != None:
            account.color['primary_color'] = params.primary_color
        if params.secondary_color != None:
            account.color['secondary_color'] = params.secondary_color
        if params.img != None:
            account.img = params.img
        if params.website != None:
            account.website = params.website
        if params.bio != None:
            account.bio = params.bio
        if params.privacy != None:
            account.flags['privacy'] = params.privacy
        
        if not account.isValid:
            raise InvalidArgument('Invalid input')
            
        result = {}
        result['id'] = self._accountDB.updateAccount(account)
        ### CLARIFY: What do we want to return?
        return result
    
    def removeAccount(self, params):
        self._accountDB.removeAccount(params.account_id)
        ### CLARIFY: What do we want to return?
        return {'id': params.account_id}
    
    def flagAccount(self, userID):
        return self._accountDB.flagAccount(userID)
    
    def unflagAccount(self, userID):
        return self._accountDB.unflagAccount(userID)
    
    # ##### #
    # Users #
    # ##### #
    
    def getUser(self, userID):
        return self._userDB.getUser(userID)
    
    def getUsers(self, userIDs):
        userIDs = userIDs.split(',')
        return self._userDB.lookupUsers(userIDs, None)
    
    def getUserByName(self, username):
        return self._userDB.lookupUsers(None, [ username ])[-1]
    
    def getUsersByName(self, usernames):
        usernames = usernames.split(',')
        return {'users': self._userDB.lookupUsers(None, usernames)}
    
    def searchUsers(self, query, limit=20):
        return {'users': self._userDB.searchUsers(query, limit)}
    
    def getPrivacy(self, userID):
        return self._userDB.checkPrivacy(userID)
    
    # ############# #
    # Relationships #
    # ############# #
    
    def addFriendship(self, params):
        friendship = Friendship()
        friendship.user_id = params.user_id
        friendship.friend_id = params.friend_id
        
        if not friendship.isValid:
            raise InvalidArgument('Invalid input')
        
        self._friendshipDB.addFriendship(friendship)
        return friendship
    
    def removeFriendship(self, params):
        friendship = Friendship()
        friendship.user_id = params.user_id
        friendship.friend_id = params.friend_id
        
        if not friendship.isValid:
            raise InvalidArgument('Invalid input')
        self._friendshipDB.removeFriendship(friendship)
        return friendship
    
    def approveFriendship(self, params):
        friendship = Friendship()
        friendship.user_id = params.user_id
        friendship.friend_id = params.friend_id
        
        if not friendship.isValid:
            raise InvalidArgument('Invalid input')
            
        self._friendshipDB.approveFriendship(friendship)
        return friendship
    
    def addBlock(self, params):
        friendship = Friendship()
        friendship.user_id = params.user_id
        friendship.friend_id = params.friend_id
        
        if not friendship.isValid:
            raise InvalidArgument('Invalid input')
            
        self._friendshipDB.addBlock(friendship)
        return friendship
    
    def removeBlock(self, params):
        friendship = Friendship()
        friendship.user_id = params.user_id
        friendship.friend_id = params.friend_id
        
        if not friendship.isValid:
            raise InvalidArgument('Invalid input')
        
        self._friendshipDB.removeBlock(friendship)
        return friendship        
    
    def checkFriendship(self, userID, friendID):
        friendship = Friendship({'user_id': userID, 'friend_id': friendID})
        return self._friendshipDB.checkFriendship(friendship)
    
    def getFriends(self, userID):
        return self._friendshipDB.getFriends(userID)
    
    def getFollowers(self, userID):
        return self._friendshipDB.getFollowers(userID)
    
    def checkBlock(self, userID, friendID):
        friendship = Friendship({'user_id': userID, 'friend_id': friendID})
        return self._friendshipDB.checkBlock(friendship)
    
    def getBlocks(self, userID):
        return self._friendshipDB.getBlocks(userID)
    
    # ######### #
    # Favorites #
    # ######### #
    
    def addFavorite(self, params):
        # TODO: construct a favorite object from (userID, entityID, stampID)
        raise NotImplementedError
        favorite = Favorite()
        
        user = self.getUser(params.userID)
        favorite.user = {
            'user_id': user.id,
            'user_name': user.username
        }
        
        entity = self.getEntity(params.entityID)
        favorite.entity = {
            'entity_id': entity.id,
            'title': entity.title,
            'category': entity.category,
            'subtitle': entity.desc ### TODO: Change to appropriate subtitle
        }
        if entity.coordinates:
            favorite.entity['coordinates'] = entity.details['place']['coordinates']
        
        if stampID:
            stamp = self.getStamp(params.stampID)
            favorite.stamp = {
                'stamp_id': stamp.id,
                'stamp_blurb': stamp.blurb, 
                'stamp_timestamp': stamp.timestamp,
                'stamp_user_id': stamp.user['user_id'],
                'stamp_user_name': stamp.user['user_name'],
                'stamp_user_img': stamp.user['user_img']
            }
        
        favorite.timestamp = datetime.utcnow()
        
        if not favorite.isValid:
            raise InvalidArgument('Invalid input')
            
        return self._favoriteDB.addFavorite(favorite)
    
    def getFavorite(self, userID, favoriteID):
        ### TODO: Verify userID has permission to access
        return self._favoriteDB.getFavorite(favoriteID)
    
    def removeFavorite(self, userID, favoriteID):
        ### TODO: Verify userID has permission to access
        return self._favoriteDB.removeFavorite(favoriteID)
    
    def completeFavorite(self, userID, favoriteID):
        ### TODO: Verify userID has permission to access
        return self._favoriteDB.completeFavorite(favoriteID)
    
    def getFavoriteIDs(self, userID):
        return self._favoriteDB.getFavoriteIDs(userID)
    
    def getFavorites(self, userID):
        return self._favoriteDB.getFavoriteIds(userID)
    
    # ######## #
    # Entities #
    # ######## #
    
    def addEntity(self, params):
        entity = Entity()
        entity.title = params.title
        entity.desc = params.desc
        entity.category = params.category
        
        if not entity.isValid:
            raise InvalidArgument('Invalid input')
        
        result = {}
        result['id'] = self._entityDB.addEntity(entity)
        return result
    
    def getEntity(self, entityID):
        return self._entityDB.getEntity(entityID)
    
    def updateEntity(self, params):
        entity = self.getEntity(params.entity_id)
        
        if params.title != None:
            entity.title = params.title
        if params.desc != None:
            entity.desc = params.desc
        if params.category != None:
            entity.category = params.category
                    
        result = {}
        result['id'] = self._entityDB.updateEntity(entity)
        ### CLARIFY: What do we want to return?
        return result
    
    def removeEntity(self, params):
        self._entityDB.removeEntity(params.entity_id)
        ### CLARIFY: What do we want to return?
        return {'id': params.entity_id}
        
    def searchEntities(self, query, limit=20):
        entities = {}
        entities['entities'] = self._entityDB.matchEntities(query, limit)
        return entities
    
    # ###### #
    # Stamps #
    # ###### #
    
    def addStamp(self, params):        
        stamp = Stamp()
        
        user = self._userDB.getUser(params.user_id)
        stamp.user = {}
        stamp.user['user_id'] = user.id
        stamp.user['user_name'] = user.first_name
        stamp.user['user_img'] = user.img
        stamp.flags = {}
        stamp.flags['privacy'] = user.flags['privacy']
        
        entity = self._entityDB.getEntity(params.entity_id)
        stamp.entity = {}
        stamp.entity['entity_id'] = entity.id
        stamp.entity['title'] = entity.title
        stamp.entity['category'] = entity.category
        stamp.entity['subtitle'] = entity.desc
        if entity.coordinates:
            stamp.entity['coordinates']['lat'] = entity.coordinates['lat']
            stamp.entity['coordinates']['lng'] = entity.coordinates['lng']
        
        if params.blurb != None:
            stamp.blurb = params.blurb
        if params.img != None:
            stamp.img = params.img
            
        if params.mentions != None:
            stamp.mentions = []
            for userID in params.mentions.split(','):
                stamp.mentions.append(userID)
            
        if params.credit != None:
            stamp.credit = []
            for userID in params.credit.split(','):
                stamp.credit.append(userID)
                
        stamp.timestamp = datetime.utcnow()

        if not stamp.isValid:
            raise InvalidArgument('Invalid input')
        
        result = {}
        result['id'] = self._stampDB.addStamp(stamp)
        return result
    
    def updateStamp(self, params):        
        stamp = self._stampDB.getStamp(params.stamp_id)
        
        if params.blurb != None:
            stamp.blurb = params.blurb
        if params.img != None:
            stamp.img = params.img
            
        if params.mentions != None:
            if not stamp.mentions:
                stamp.mentions = []
            for userID in params.mentions.split(','):
                stamp.mentions.append(userID)
            
        if params.credit != None:
            if not stamp.credit:
                stamp.credit = []
            for userID in params.credit.split(','):
                stamp.credit.append(userID)
                
        stamp.timestamp = datetime.utcnow()

        if not stamp.isValid:
            raise InvalidArgument('Invalid input')
            
        result = {}
        result['id'] = self._stampDB.updateStamp(stamp)
        ### CLARIFY: What do we want to return?
        return result
    
    def removeStamp(self, params):
        self._stampDB.removeStamp(params.stamp_id, params.user_id)
        ### CLARIFY: What do we want to return?
        return {'id': params.stamp_id}
    
    def getStamp(self, stampID):
        return self._stampDB.getStamp(stampID)
    
    def getStamps(self, stampIDs):
        stampIDs = stampIDs.split(',')
        return self._stampDB.getStamps(stampIDs)
    
    # ########### #
    # Collections #
    # ########### #
    
    def getInboxStampIDs(self, userID, limit=None):
        return self._collectionDB.getInboxStampIDs(userID, limit)
    
    def getInboxStamps(self, userID, limit=None):
        return self._collectionDB.getInboxStamps(userID, limit)
    
    def getUserStampIDs(self, userID, limit=None):
        return self._collectionDB.getUserStampIDs(userID, limit)
    
    def getUserStamps(self, userID, limit=None):
        return self._collectionDB.getUserStamps(userID, limit)
    
    def getUserMentions(self, userID, limit=None):
        return self._collectionDB.getUserMentions(userID, limit)

