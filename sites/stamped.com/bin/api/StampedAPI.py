#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from abc import abstractmethod
from datetime import datetime

from errors import InvalidArgument
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
#      considered "priveleged", then the request is coming from roperly 
#      authenticated user. e.g., either an administrator or the user who is 
#      currently logged into the application.

class StampedAPI(AStampedAPI):
    """
        Database-agnostic implementation of the internal API for accessing 
        and manipulating all Stamped backend databases.
    """
    
    def __init__(self, desc):
        AStampedAPI.__init__(self, desc)
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
        ### TODO: Add validation to ensure no duplicate screen_names
        account = Account()
        account.first_name = params.first_name
        account.last_name = params.last_name
        account.email = params.email
        account.password = params.password
        account.screen_name = params.screen_name
        account.display_name = "%s %s." % (params.first_name, params.last_name[0])
        
        account.locale = {
            'language': 'en',
            'time_zone': None
        }
        
        account.color_primary = None
        account.profile_image = None   
        account.privacy = True
        
        if account.isValid == False:
            raise InvalidArgument('Invalid input')
        
        result = {}
        result['user_id'] = self._accountDB.addAccount(account)
        result['first_name'] = account.first_name
        result['last_name'] = account.last_name
        result['email'] = account.email
        result['screen_name'] = account.screen_name
        result['display_name'] = account.display_name
        return result
    
    def updateAccount(self, params):
        account = self._accountDB.getAccount(params.authenticated_user_id)
        
        if params.email != None:
            account.email = params.email
        if params.password != None:
            account.password = params.password
        if params.screen_name != None:
            account.screen_name = params.screen_name
        if params.privacy != None:
            account.privacy = params.privacy
        
        if params.language != None:
            account.locale['language'] = params.language
        if params.time_zone != None:
            account.locale['time_zone'] = params.time_zone
        
        if not account.isValid:
            raise InvalidArgument('Invalid input')
            
        result = {}
        result['user_id'] = self._accountDB.updateAccount(account)
        result['first_name'] = account.first_name
        result['last_name'] = account.last_name
        result['email'] = account.email
        result['screen_name'] = account.screen_name
        result['privacy'] = account.privacy
        result['locale'] = {}
        if 'language' in account.locale:
            result['locale']['language'] = account.locale['language']
        else:
            result['locale']['language'] = None
        if 'time_zone' in account.locale:
            result['locale']['time_zone'] = account.locale['time_zone']
        else:
            result['locale']['time_zone'] = None
        return result
    
    def getAccount(self, userID):
        account = self._accountDB.getAccount(userID)
        result = {}
        result['user_id'] = account.user_id
        result['first_name'] = account.first_name
        result['last_name'] = account.last_name
        result['email'] = account.email
        result['screen_name'] = account.screen_name
        result['privacy'] = account.privacy
        result['locale'] = {}
        if 'language' in account.locale:
            result['locale']['language'] = account.locale['language']
        else:
            result['locale']['language'] = None
        if 'time_zone' in account.locale:
            result['locale']['time_zone'] = account.locale['time_zone']
        else:
            result['locale']['time_zone'] = None
        return result
        
    def updateProfile(self, params):
        account = self._accountDB.getAccount(params.authenticated_user_id)
        
        if params.first_name != None:
            account.first_name = params.first_name
        if params.last_name != None:
            account.last_name = params.last_name
        if params.bio != None:
            account.bio = params.bio
        if params.website != None:
            account.website = params.website
        if params.color != None:
            color = params.color.split(',')
            account.color_primary = color[0]
            if len(color) == 2:
                account.color_secondary = color[1]
        
        if not account.isValid:
            raise InvalidArgument('Invalid input')
            
        result = {}
        result['user_id'] = self._accountDB.updateAccount(account)
        result['first_name'] = account.first_name
        result['last_name'] = account.last_name
        result['display_name'] = account.display_name
        if 'bio' in account:
            result['bio'] = account.bio
        else:
            result['bio'] = None
        if 'website' in account:
            result['website'] = account.website
        else:
            result['website'] = None
        result['color_primary'] = account.color_primary
        if 'color_secondary' in account:
            result['color_secondary'] = account.color_secondary
        else:
            result['color_secondary'] = None
        return result
        
    def updateProfileImage(self, params):
        ### TODO: Grab image and do something with it. Currently just sets as url.
        
        account = self._accountDB.getAccount(params.authenticated_user_id)
        if params.profile_image != None:
            account.profile_image = params.profile_image
        
        if not account.isValid:
            raise InvalidArgument('Invalid input')
            
        result = {}
        result['user_id'] = self._accountDB.updateAccount(account)
        result['profile_image'] = account.profile_image
        return result
        raise NotImplementedError
        
    def verifyAccountCredentials(self, userID):
        return True
    
    def removeAccount(self, params):
        if self._accountDB.removeAccount(params.authenticated_user_id):
            return True
        else:
            return False
    
    def resetPassword(self, params):
        raise NotImplementedError
    
    # ##### #
    # Users #
    # ##### #
    
    def getUser(self, userID=None, screenName=None):
        if userID:
            user = self._userDB.getUser(userID)
        elif screenName:
            user = self._userDB.lookupUsers(None, [screenName])
            if len(user) == 0:
                return 'error', 400
            else:
                user = user[-1]
        else:
            return 'error', 400
        
        result = {}
        result['user_id'] = user.user_id
        result['first_name'] = user.first_name
        result['last_name'] = user.last_name
        result['screen_name'] = user.screen_name
        result['display_name'] = user.display_name
        result['profile_image'] = user.profile_image
        
        if 'bio' in user:
            result['bio'] = user.bio
        else:
            result['bio'] = None
        if 'website' in user:
            result['website'] = user['website']
        else:
            result['website'] = None
        
        result['color_primary'] = user.color_primary
        if 'color_secondary' in user:
            result['color_secondary'] = user.color_secondary
        else:
            result['color_secondary'] = None
        
        result['privacy'] = user.privacy
            
        ### TODO: Pull in recent stamps
        result['recent_stamps'] = None
        
        return result
    
    def getUserByName(self, screenName):
        return self.getUser(None, screenName)
        
    
    def getUsers(self, userIDs=None, screenNames=None):
        if userIDs:
            userIDs = userIDs.split(',')
            users = self._userDB.lookupUsers(userIDs, None)
        elif screenNames:
            screenNames = screenNames.split(',')
            users = self._userDB.lookupUsers(None, screenNames)
        else:
            return 'error', 400
        
        result = []
        for user in users:
            data = {}
            
            data['user_id'] = user.user_id
            data['first_name'] = user.first_name
            data['last_name'] = user.last_name
            data['screen_name'] = user.screen_name
            data['display_name'] = user.display_name
            data['profile_image'] = user.profile_image
            if 'bio' in user:
                data['bio'] = user.bio
            else:
                data['bio'] = None
            if 'website' in user:
                data['website'] = user.flags['website']
            else:
                data['website'] = None
            data['color_primary'] = user.color_primary
            if 'color_secondary' in user:
                data['color_secondary'] = user.color_secondary
            else:
                data['color_secondary'] = None
            data['privacy'] = user.privacy
            ### TODO: Pull in recent stamps
            data['last_stamp'] = None
            result.append(data)
        
        return result
    
    def getUsersByName(self, screenNames):
        return self.getUsers(None, screenNames)
    
    def searchUsers(self, query, limit=20):
        users = self._userDB.searchUsers(query, limit)
        
        result = []
        for user in users:
            data = {}
            
            data['user_id'] = user.user_id
            data['first_name'] = user.first_name
            data['last_name'] = user.last_name
            data['screen_name'] = user.screen_name
            data['display_name'] = user.display_name
            data['profile_image'] = user.profile_image
            if 'bio' in user:
                data['bio'] = user.bio
            else:
                data['bio'] = None
            if 'website' in user:
                data['website'] = user.flags['website']
            else:
                data['website'] = None
            data['color_primary'] = user.color_primary
            if 'color_secondary' in user:
                data['color_secondary'] = user.color_secondary
            else:
                data['color_secondary'] = None
            data['privacy'] = user.privacy
            ### TODO: Pull in recent stamps
            data['last_stamp'] = None
            result.append(data)
        
        return result
    
    def getPrivacy(self, userID):
        if self._userDB.checkPrivacy(userID):
            return True
        else:
            return False
    
    # ############# #
    # Relationships #
    # ############# #
    
    def addFriendship(self, params):
        friendship = Friendship()
        friendship.user_id = params.authenticated_user_id
        
        if params.user_id != None:
            friendship.friend_id = params.user_id
        elif params.screen_name != None:
            raise NotImplementedError
        else:
            return 'error', 400
        
        if not friendship.isValid:
            raise InvalidArgument('Invalid input')
        
        self._friendshipDB.addFriendship(friendship)
        
        result = {}
        result['user_id'] = friendship.friend_id
        result['screen_name'] = self._userDB.getUser(friendship.friend_id)['screen_name']
        
        return result
    
    def removeFriendship(self, params):
        friendship = Friendship()
        friendship.user_id = params.authenticated_user_id
        
        if params.user_id != None:
            friendship.friend_id = params.user_id
        elif params.screen_name != None:
            raise NotImplementedError
        else:
            return 'error', 400
        
        if not friendship.isValid:
            raise InvalidArgument('Invalid input')
            
        if self._friendshipDB.removeFriendship(friendship):
            return True
        else:
            return False
    
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
        friendship.user_id = params.authenticated_user_id
        
        if params.user_id != None:
            friendship.friend_id = params.user_id
        elif params.screen_name != None:
            raise NotImplementedError
        else:
            return 'error', 400
        
        if not friendship.isValid:
            raise InvalidArgument('Invalid input')
        
        self._friendshipDB.addBlock(friendship)
        
        result = {}
        result['user_id'] = friendship.friend_id
        result['screen_name'] = self._userDB.getUser(friendship.friend_id)['screen_name']
        
        return result
    
    def removeBlock(self, params):
        friendship = Friendship()
        friendship.user_id = params.authenticated_user_id
        
        if params.user_id != None:
            friendship.friend_id = params.user_id
        elif params.screen_name != None:
            raise NotImplementedError
        else:
            return 'error', 400
        
        if not friendship.isValid:
            raise InvalidArgument('Invalid input')
            
        if self._friendshipDB.removeBlock(friendship):
            return True
        else:
            return False
    
    def checkFriendship(self, userID, friendID):
        friendship = Friendship({'user_id': userID, 'friend_id': friendID})
        if self._friendshipDB.checkFriendship(friendship):
            return True
        else:
            return False
    
    def getFriends(self, userID):
        return {'user_ids': self._friendshipDB.getFriends(userID)}
    
    def getFollowers(self, userID):
        return {'user_ids': self._friendshipDB.getFollowers(userID)}
    
    def checkBlock(self, userID, friendID):
        friendship = Friendship({'user_id': userID, 'friend_id': friendID})
        if self._friendshipDB.checkBlock(friendship):
            return True
        else:
            return False
    
    def getBlocks(self, userID):
        return {'user_ids': self._friendshipDB.getBlocks(userID)}
    
    # ######### #
    # Favorites #
    # ######### #
    
    def addFavorite(self, params):
        favorite = Favorite()
        
        user = self._userDB.getUser(params.authenticated_user_id)
        favorite.user_id = user.user_id
        
        entity = self._entityDB.getEntity(params.entity_id)
        favorite.entity = {}
        favorite.entity['entity_id'] = entity.entity_id
        favorite.entity['title'] = entity.title
        favorite.entity['category'] = entity.category
        favorite.entity['subtitle'] = entity.subtitle
        if 'details' in entity and 'place' in entity.details and 'coordinates' in entity.details['place']:
            favorite.entity['coordinates'] = {}
            favorite.entity['coordinates']['lat'] = entity.details['place']['coordinates']['lat']
            favorite.entity['coordinates']['lng'] = entity.details['place']['coordinates']['lng']
        
        if params.stamp_id != None:
            stamp = self._stampDB.getStamp(params.stamp_id)
            favorite.stamp = {}
            favorite.stamp['stamp_id'] = stamp.stamp_id
            favorite.stamp['display_name'] = stamp.user['display_name']
                
        favorite.timestamp = {
            'created': datetime.utcnow()
        }   
        
        favorite.complete = False
        
        if not favorite.isValid:
            raise InvalidArgument('Invalid input')
        
        result = {}
        result['favorite_id'] = self._favoriteDB.addFavorite(favorite)
        result['user_id'] = favorite.user_id
        result['entity'] = favorite.entity
        if 'stamp' in favorite:
            result['stamp'] = favorite.stamp
        else:
            result['stamp'] = None
            
        result['timestamp'] = {}
        if 'created' in favorite.timestamp:
            result['timestamp']['created'] = str(favorite.timestamp['created'])
            
        result['complete'] = favorite.complete
        
        return result
    
    def removeFavorite(self, params):
        if self._favoriteDB.removeFavorite(params.favorite_id):
            return True
        return False
    
    def getFavorites(self, userID):        
        favorites = self._favoriteDB.getFavorites(userID)
        
        result = []
        for favorite in favorites:
            data = {}
            data['favorite_id'] = favorite.favorite_id
            data['user_id'] = favorite.user_id
            data['entity'] = favorite.entity
            if 'stamp' in favorite:
                data['stamp'] = favorite.stamp
            else:
                data['stamp'] = None
                
            data['timestamp'] = {}
            if 'created' in favorite.timestamp:
                data['timestamp']['created'] = str(favorite.timestamp['created'])
            else:
                data['timestamp']['created'] = None
            if 'modified' in favorite.timestamp:
                data['timestamp']['modified'] = str(favorite.timestamp['modified'])
            else:
                data['timestamp']['modified'] = None
                
            if 'complete' in favorite:
                data['complete'] = favorite.complete
            else:
                data['complete'] = False
            
            result.append(data)
        
        return result
    
    # ######## #
    # Entities #
    # ######## #
    
    def addEntity(self, params):
        entity = Entity()
        entity.title = params.title
        entity.subtitle = 'Other'
        entity.desc = params.desc
        entity.category = params.category
        
        if params.image != None:
            entity.image = params.image
            
        if params.address != None or params.coordinates != None:
            entity.details = {
                'place': {}
            }
            if params.address != None:
                entity.details['place']['address'] = params.address
            if params.coordinates != None:
                coordinates = params.coordinates.split(',')
                entity.details['place']['coordinates'] = {
                    'lat': coordinates[0],
                    'lng': coordinates[1]
                }
            
        entity.timestamp = {
            'created': datetime.utcnow()
        }
        
        ### TODO: Log data of user who created it
        
        if not entity.isValid:
            raise InvalidArgument('Invalid input')
        
        result = {}
        result['entity_id'] = self._entityDB.addEntity(entity)
        result['title'] = entity.title
        result['category'] = entity.category
        result['subtitle'] = entity.subtitle
        
        if 'image' in entity:
            result['image'] = entity.image
        else:
            result['image'] = None
            
        result['details'] = {}
        if 'details' in entity and 'place' in entity.details:
            result['details']['place'] = {}
            if 'address' in entity.details['place']:
                result['details']['place']['address'] = entity.details['place']['address']
            if 'coordinates' in entity.details['place']:
                result['details']['place']['coordinates'] = entity.details['place']['coordinates']
        
        if 'modified' in entity.timestamp:
            result['last_modified'] = str(entity.timestamp['modified'])
        elif 'created' in entity.timestamp:
            result['last_modified'] = str(entity.timestamp['created'])
        else:
            result['last_modified'] = None
        
        return result
    
    def getEntity(self, entityID):
        entity = self._entityDB.getEntity(entityID)
        
        result = {}
        result['entity_id'] = entity.entity_id
        result['title'] = entity.title
        result['category'] = entity.category
        result['subtitle'] = entity.subtitle
        if 'desc' in entity:
            result['desc'] = entity.desc
        
        if 'image' in entity:
            result['image'] = entity.image
        else:
            result['image'] = None
            
        result['details'] = {}
        if 'details' in entity and 'place' in entity.details:
            result['details']['place'] = {}
            if 'address' in entity.details['place']:
                result['details']['place']['address'] = entity.details['place']['address']
            if 'coordinates' in entity.details['place']:
                result['details']['place']['coordinates'] = entity.details['place']['coordinates']
        
        if 'modified' in entity.timestamp:
            result['last_modified'] = str(entity.timestamp['modified'])
        elif 'created' in entity.timestamp:
            result['last_modified'] = str(entity.timestamp['created'])
        else:
            result['last_modified'] = None
        
        return result
    
    def updateEntity(self, params):
        entity = self._entityDB.getEntity(params.entity_id)
        
        if params.title != None:
            entity.title = params.title
        if params.desc != None:
            entity.desc = params.desc
        if params.category != None:
            entity.category = params.category
            
        if params.image != None:
            entity.image = params.image            
            
        if params.address != None or params.coordinates != None:
            if 'details' not in entity:
                entity.details = {}
            if 'place' not in entity.details:
                entity.details['place'] = {}
            if params.address != None:
                entity.details['place']['address'] = params.address
            if params.coordinates != None:
                coordinates = params.coordinates.split(',')
                entity.details['place']['coordinates'] = {
                    'lat': coordinates[0],
                    'lng': coordinates[1]
                }
                
        entity.timestamp['modified'] = datetime.utcnow()
        
        if not entity.isValid:
            raise InvalidArgument('Invalid input')
                    
        result = {}
        result['entity_id'] = self._entityDB.updateEntity(entity)
        result['title'] = entity.title
        result['category'] = entity.category
        result['subtitle'] = entity.subtitle
        if 'desc' in entity:
            result['desc'] = entity.desc
        
        if 'image' in entity:
            result['image'] = entity.image
        else:
            result['image'] = None
            
        result['details'] = {}
        if 'details' in entity and 'place' in entity.details:
            result['details']['place'] = {}
            if 'address' in entity.details['place']:
                result['details']['place']['address'] = entity.details['place']['address']
            if 'coordinates' in entity.details['place']:
                result['details']['place']['coordinates'] = entity.details['place']['coordinates']
        
        if 'modified' in entity.timestamp:
            result['last_modified'] = str(entity.timestamp['modified'])
        elif 'created' in entity.timestamp:
            result['last_modified'] = str(entity.timestamp['created'])
        else:
            result['last_modified'] = None
        
        return result
    
    def removeEntity(self, params):
        if self._entityDB.removeEntity(params.entity_id):
            return True
        else:
            return False
        
    def searchEntities(self, query, limit=20):
        entities = self._entityDB.matchEntities(query, limit)
        result = []
        
        for entity in entities:
            data = {}
            data['entity_id'] = entity.entity_id
            data['title'] = entity.title
            data['category'] = entity.category
            data['subtitle'] = entity.subtitle
            if 'desc' in entity:
                data['desc'] = entity.desc
            else:
                data['desc'] = None

            result.append(data)
        
        return result
    
    # ###### #
    # Stamps #
    # ###### #
    
    def addStamp(self, params):        
        stamp = Stamp()
        
        user = self._userDB.getUser(params.authenticated_user_id)
        stamp.user = {}
        stamp.user['user_id'] = user.user_id
        stamp.user['screen_name'] = user.screen_name
        stamp.user['display_name'] = user.display_name
        stamp.user['profile_image'] = user.profile_image
        stamp.user['color_primary'] = user.color_primary
        if 'color_secondary' in user:
            stamp.user['color_secondary'] = user.color_secondary
        stamp.user['privacy'] = user.privacy
        
        entity = self._entityDB.getEntity(params.entity_id)
        stamp.entity = {}
        stamp.entity['entity_id'] = entity.entity_id
        stamp.entity['title'] = entity.title
        stamp.entity['category'] = entity.category
        stamp.entity['subtitle'] = entity.subtitle
        if 'details' in entity and 'place' in entity.details and 'coordinates' in entity.details['place']:
            stamp.entity['coordinates'] = {}
            stamp.entity['coordinates']['lat'] = entity.details['place']['coordinates']['lat']
            stamp.entity['coordinates']['lng'] = entity.details['place']['coordinates']['lng']
        
        if params.blurb != None:
            stamp.blurb = params.blurb
        if params.image != None:
            stamp.image = params.image
            
        if params.credit != None:
            stamp.credit = []
            for userID in params.credit.split(','):
                stamp.credit.append(userID)
                
        stamp.timestamp = {
            'created': datetime.utcnow()
        }

        if not stamp.isValid:
            raise InvalidArgument('Invalid input')
        
        stampId = self._stampDB.addStamp(stamp)
        stamp = self._stampDB.getStamp(stampId)
        
        result = {}
        result['stamp_id'] = stamp['stamp_id']
        result['entity'] = stamp['entity']
        result['user'] = stamp['user']
        
        if 'blurb' in stamp:
            result['blurb'] = stamp.blurb
        else:
            result['blurb'] = None
        
        if 'image' in stamp:
            result['image'] = stamp.image
        else:
            result['image'] = None
        
        if 'credit' in stamp:
            result['credit'] = stamp.credit
        else:
            result['credit'] = None
        
        if 'mentions' in stamp:
            result['mentions'] = stamp.mentions
        else:
            result['mentions'] = None
                
        if 'modified' in stamp.timestamp:
            result['last_modified'] = str(stamp.timestamp['modified'])
        elif 'created' in stamp.timestamp:
            result['last_modified'] = str(stamp.timestamp['created'])
        else:
            result['last_modified'] = None
        
        return result
            
    def updateStamp(self, params):        
        stamp = self._stampDB.getStamp(params.stamp_id)
        
        if params.blurb != None:
            stamp.blurb = params.blurb
        if params.image != None: 
            stamp.image = params.image
            
        if params.credit != None:
            if not stamp.credit:
                stamp.credit = []
            for userID in params.credit.split(','):
                stamp.credit.append(userID)
                
        if 'timestamp' not in stamp:
            stamp['timestamp'] = {}
        stamp.timestamp['modified'] = datetime.utcnow()

        if not stamp.isValid:
            raise InvalidArgument('Invalid input')
        
        stampId = self._stampDB.updateStamp(stamp)
        stamp = self._stampDB.getStamp(stampId)
            
        result = {}
        result['stamp_id'] = stamp['stamp_id']
        result['entity'] = stamp['entity']
        result['user'] = stamp['user']
        
        if 'image' in stamp:
            result['image'] = stamp.image
        else:
            result['image'] = None
        
        if 'credit' in stamp:
            result['credit'] = stamp.credit
        else:
            result['credit'] = None
        
        if 'mentions' in stamp:
            result['mentions'] = stamp.mentions
        else:
            result['mentions'] = None
                
        if 'modified' in stamp.timestamp:
            result['last_modified'] = str(stamp.timestamp['modified'])
        elif 'created' in stamp.timestamp:
            result['last_modified'] = str(stamp.timestamp['created'])
        else:
            result['last_modified'] = None
        
        return result
    
    def removeStamp(self, params):
        if self._stampDB.removeStamp(params.stamp_id, params.authenticated_user_id):
            return True
        else:
            return False
    
    def getStamp(self, stampID):
        stamp = self._stampDB.getStamp(stampID)
        
        result = {}
        result['stamp_id'] = stamp.stamp_id
        result['entity'] = stamp['entity']
        result['user'] = stamp['user']
        
        if 'image' in stamp:
            result['image'] = stamp.image
        else:
            result['image'] = None
        
        if 'credit' in stamp:
            result['credit'] = stamp.credit
        else:
            result['credit'] = None
        
        if 'mentions' in stamp:
            result['mentions'] = stamp.mentions
        else:
            result['mentions'] = None
                
        if 'modified' in stamp.timestamp:
            result['last_modified'] = str(stamp.timestamp['modified'])
        elif 'created' in stamp.timestamp:
            result['last_modified'] = str(stamp.timestamp['created'])
        else:
            result['last_modified'] = None
        
        return result
        
    
    def getStamps(self, stampIDs):
        stampIDs = stampIDs.split(',')
        stamps = []
        for stamp in self._stampDB.getStamps(stampIDs):
            stamps.append(stamp.getDataAsDict())
        return stamps
    
    # ######## #
    # Comments #
    # ######## #
    
    def addComment(self, params):
        comment = Comment()
        
        user = self._userDB.getUser(params.authenticated_user_id)
        comment.user = {}
        comment.user['user_id'] = user.user_id
        comment.user['screen_name'] = user.screen_name
        comment.user['display_name'] = user.display_name
        comment.user['profile_image'] = user.profile_image
        comment.user['color_primary'] = user.color_primary
        if 'color_secondary' in user:
            comment.user['color_secondary'] = user.color_secondary
        comment.user['privacy'] = user.privacy
        
        comment.stamp_id = params.stamp_id
        
        if params.blurb != None:
            comment.blurb = params.blurb
                
        comment.timestamp = {
            'created': datetime.utcnow()
        }
        
        if not comment.isValid:
            raise InvalidArgument('Invalid input')
        
        commentId = self._stampDB.addComment(comment)
        comment = self._stampDB.getComment(commentId)
        
        result = {}
        result['comment_id'] = comment['comment_id']
        result['stamp_id'] = comment['stamp_id']
        result['user'] = comment['user']
        result['blurb'] = comment['blurb']
        
        if 'mentions' in comment:
            result['mentions'] = comment.mentions
        else:
            result['mentions'] = None
        
        if 'restamp_id' in comment:
            result['restamp_id'] = comment.restamp_id
        else:
            result['restamp_id'] = None
                
        if 'created' in comment.timestamp:
            result['last_modified'] = str(comment.timestamp['created'])
        else:
            result['last_modified'] = None
        
        return result
    
    def removeComment(self, params):
        if self._stampDB.removeComment(params.comment_id):
            return True
        else:
            return False
    
    def getComments(self, stampID, userID=None):        
        comments = self._stampDB.getComments(stampID)
            
        result = []
        for comment in comments:
            data = {}
            
            data['comment_id'] = comment.comment_id
            data['stamp_id'] = comment.stamp_id
            data['user'] = comment.user
            data['blurb'] = comment.blurb
            
            if 'mentions' in comment:
                data['mentions'] = comment.mentions
            else:
                data['mentions'] = None
            
            if 'restamp_id' in comment:
                data['restamp_id'] = comment.restamp_id
            else:
                data['restamp_id'] = None
                    
            if 'created' in comment.timestamp:
                data['last_modified'] = str(comment.timestamp['created'])
            else:
                data['last_modified'] = None
            
            result.append(data)
        
        return result
    
    # ########### #
    # Collections #
    # ########### #
    
    def getInboxStampIDs(self, userID, limit=None):
        return self._collectionDB.getInboxStampIDs(userID, limit)
    
    def getUserStampIDs(self, userID, limit=None):
        return self._collectionDB.getUserStampIDs(userID, limit)
    
    def getInboxStamps(self, params):
        # Limit results to 20
        limit = 20
        if params.limit != None:
            try:
                limit = int(params.limit)
                if limit > 20:
                    limit = 20
            except:
                limit = limit
        
        # Limit slice of data returned
        since = None
        if params.since != None:
            try: 
                since = datetime.utcfromtimestamp(int(params.since)-2)
            except:
                since = since
        
        before = None
        if params.before != None:
            try: 
                before = datetime.utcfromtimestamp(int(params.before)+2)
            except:
                before = before
                       
        
        stamps = self._collectionDB.getInboxStamps(params.authenticated_user_id, since=since, before=before, limit=limit)
        result = []
        
        for stamp in stamps:
            data = {}
            
            data['stamp_id'] = stamp.stamp_id
            data['entity'] = stamp['entity']
            data['user'] = stamp['user']
            
            if 'flags' in stamp:
                data['flags'] = stamp['flags']
            
            if 'blurb' in stamp:
                data['blurb'] = stamp.blurb
            else:
                data['blurb'] = None
            
            if 'image' in stamp:
                data['image'] = stamp.image
            else:
                data['image'] = None
            
            if 'credit' in stamp:
                data['credit'] = stamp.credit
            else:
                data['credit'] = None
            
            if 'mentions' in stamp:
                data['mentions'] = stamp.mentions
            else:
                data['mentions'] = None
                
            if 'modified' in stamp.timestamp:
                data['last_modified'] = str(stamp.timestamp['modified'])
            elif 'created' in stamp.timestamp:
                data['last_modified'] = str(stamp.timestamp['created'])
            else:
                data['last_modified'] = None
                
            if 'stats' in stamp and 'num_comments' in stamp.stats:
                data['num_comments'] = stamp.stats['num_comments']
            else:
                data['num_comments'] = 0

            result.append(data)
        
        return result
    
    def getUserStamps(self, userID, limit=None):        
        stamps = self._collectionDB.getUserStamps(userID, limit)
        result = []
        
        for stamp in stamps:
            data = {}
            
            data['stamp_id'] = stamp.stamp_id
            data['entity'] = stamp['entity']
            data['user'] = stamp['user']
            
            if 'flags' in stamp:
                data['flags'] = stamp['flags']
            
            if 'blurb' in stamp:
                data['blurb'] = stamp.blurb
            else:
                data['blurb'] = None
            
            if 'image' in stamp:
                data['image'] = stamp.image
            else:
                data['image'] = None
            
            if 'credit' in stamp:
                data['credit'] = stamp.credit
            else:
                data['credit'] = None
            
            if 'mentions' in stamp:
                data['mentions'] = stamp.mentions
            else:
                data['mentions'] = None
                
            if 'modified' in stamp.timestamp:
                data['last_modified'] = str(stamp.timestamp['modified'])
            elif 'created' in stamp.timestamp:
                data['last_modified'] = str(stamp.timestamp['created'])
            else:
                data['last_modified'] = None
                
            if 'stats' in stamp and 'num_comments' in stamp.stats:
                data['num_comments'] = stamp.stats['num_comments']
            else:
                data['num_comments'] = 0

            result.append(data)
        
        return result
    
    def getUserMentions(self, userID, limit=None):
        return self._collectionDB.getUserMentions(userID, limit)
    
    # ########### #
    # Private API #
    # ########### #
    
    def _addEntity(self, entity):
        self._entityDB.addEntity(entity)
    
    def _addEntities(self, entities):
        self._entityDB.addEntities(entities)

