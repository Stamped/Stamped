#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils, logs
from datetime import datetime
from errors import *
from auth import convertPasswordForStorage

from AStampedAPI import AStampedAPI

from AAccountDB import AAccountDB
from AEntityDB import AEntityDB
from APlacesEntityDB import APlacesEntityDB
from AUserDB import AUserDB
from AStampDB import AStampDB
from ACommentDB import ACommentDB
from AFavoriteDB import AFavoriteDB
from ACollectionDB import ACollectionDB
from AFriendshipDB import AFriendshipDB
from AActivityDB import AActivityDB

from Account import Account
from Entity import *
from User import User
from Stamp import Stamp
from Comment import Comment
from Favorite import Favorite
from Friendship import Friendship
from Activity import Activity

# TODO: input validation and output formatting
# NOTE: this is the place where all input validation should occur. any 
# db-specific validation should occur elsewhere. This validation includes 
# but is not limited to:
#    * ensuring that a given ID is "valid"
#    * ensuring that a given relationship is "valid"
#    * ensuring that for methods which accept a user ID and should be 
#      considered "priveleged", then the request is coming from properly 
#      authenticated user. e.g., either an administrator or the user who is 
#      currently logged into the application.

class StampedAPI(AStampedAPI):
    """
        Database-agnostic implementation of the internal API for accessing 
        and manipulating all Stamped backend databases.
    """
    
    def __init__(self, desc, **kwargs):
        AStampedAPI.__init__(self, desc)
        self._validated = False
        self.output = kwargs.pop('output', False)
    
    def _validate(self):
        
        self._validated = True
    
    
    """
       #                                                    
      # #    ####   ####   ####  #    # #    # #####  ####  
     #   #  #    # #    # #    # #    # ##   #   #   #      
    #     # #      #      #    # #    # # #  #   #    ####  
    ####### #      #      #    # #    # #  # #   #        # 
    #     # #    # #    # #    # #    # #   ##   #   #    # 
    #     #  ####   ####   ####   ####  #    #   #    ####  
    """
    
    def addAccount(self, data, auth):

        display_name = "%s %s." % (data['first_name'], data['last_name'][0])
        data['display_name'] = display_name

        account = Account(data)
        account.password = convertPasswordForStorage(account['password'])
        account.timestamp.created = datetime.utcnow()

        if self._userDB.checkScreenNameExists(account.screen_name):
            raise Exception("Screen name is already taken")

        result = self._accountDB.addAccount(account)

        if self.output == 'http':
            return result.exportFlat()
        return result
    
    def updateAccount(self, data, auth):
        account = self._accountDB.getAccount(auth['authenticated_user_id'])
        account.importData(data)
            
        self._accountDB.updateAccount(account)

        if self.output == 'http':
            return account.exportFlat()
        return account
    
    def getAccount(self, data, auth):
        account = self._accountDB.getAccount(auth['authenticated_user_id'])
        
        if self.output == 'http':
            return account.exportFlat()
        return account
    
    def updateProfile(self, data, auth):
        account = self._accountDB.getAccount(auth['authenticated_user_id'])
        account.importData(data)
            
        self._accountDB.updateAccount(account)
        
        if self.output == 'http':
            return account.exportProfile()
        return account
    
    def updateProfileImage(self, data, auth):
        ### TODO: Grab image and do something with it. Currently just sets as url.
        
        account = self._accountDB.getAccount(auth['authenticated_user_id'])
        account.importData(data)
            
        self._accountDB.updateAccount(account)
        
        if self.output == 'http':
            return account.exportProfileImage()
        return account
        raise NotImplementedError
    
    def removeAccount(self, data, auth):
        return self._accountDB.removeAccount(auth['authenticated_user_id'])
    
    def verifyAccountCredentials(self, data, auth):
        raise NotImplementedError
    
    def resetPassword(self, params):
        raise NotImplementedError
    

    """
    #     #                             
    #     #  ####  ###### #####   ####  
    #     # #      #      #    # #      
    #     #  ####  #####  #    #  ####  
    #     #      # #      #####       # 
    #     # #    # #      #   #  #    # 
     #####   ####  ###### #    #  ####  
    """

    ### PRIVATE

    def _returnUser(self, user):
        if self.output == 'http':
            return user.exportFlat()
        return user

    def _returnUsers(self, users):
        if self.output == 'http':
            result = []
            for user in users:
                result.append(user.exportFlat())
            return result
        return users

    def _getUserFromIdOrScreenName(self, data):
        user_id         = data.pop('user_id', None)
        screen_name     = data.pop('screen_name', None)

        if user_id == None and screen_name == None:
            raise Exception("Required field missing")

        if user_id != None:
            return self._userDB.getUser(user_id)
        return self._userDB.getUserByScreenName(screen_name)

    ### PUBLIC
    
    def getUser(self, data, auth):
        user = self._getUserFromIdOrScreenName(data)
        
        if user.privacy == True:
            authenticated_user_id = data.pop('authenticated_user_id', None)
            if authenticated_user_id == None:
                raise Exception("You must be logged in to view this account")
            #self._friendshipDB.checkFriendship
        
        return self._returnUser(user)
    
    def getUsers(self, data, auth):
        user_ids        = data.pop('user_ids', None)
        screen_names    = data.pop('screen_names', None)

        users = self._userDB.lookupUsers(user_ids, screen_names, limit=100)

        return self._returnUsers(users)
    
    def searchUsers(self, data, auth):
        limit = data.pop('user_ids', 20)
        limit = self._setLimit(limit, cap=20)
        
        users = self._userDB.searchUsers(data['q'], limit)

        return self._returnUsers(users)
    
    def getPrivacy(self, data, auth):
        user = self._getUserFromIdOrScreenName(data)
        
        if user.privacy == True:
            return True
        return False

    
    """
    #######                                      
    #       #####  # ###### #    # #####   ####  
    #       #    # # #      ##   # #    # #      
    #####   #    # # #####  # #  # #    #  ####  
    #       #####  # #      #  # # #    #      # 
    #       #   #  # #      #   ## #    # #    # 
    #       #    # # ###### #    # #####   ####  
    """
    
    def addFriendship(self, data, auth):
        user = self._getUserFromIdOrScreenName(data)

        friendship = Friendship({
            'user_id':      auth['authenticated_user_id'],
            'friend_id':    user['user_id']
        })

        # Check if friendship already exists
        if self._friendshipDB.checkFriendship(friendship) == True:
            logs.info("Friendship exists")
            return self._returnUser(user)

        # Check if authenticating user is being blocked
        if self._friendshipDB.checkBlock(friendship) == True:
            logs.info("Block exists")
            raise Exception

        # Check if friend has private account
        if user.privacy == True:
            ### TODO: Create queue for friendship requests
            raise NotImplementedError

        # Create friendship
        self._friendshipDB.addFriendship(friendship)
        
        result = {}
        result['user_id'] = friendship.friend_id
        result['screen_name'] = self._userDB.getUser(friendship.friend_id)['screen_name']
        
        return self._returnUser(user)
    
    def removeFriendship(self, data, auth):
        user = self._getUserFromIdOrScreenName(data)

        friendship = Friendship({
            'user_id':      auth['authenticated_user_id'],
            'friend_id':    user['user_id']
        })

        # Check if friendship doesn't exist
        if self._friendshipDB.checkFriendship(friendship) == False:
            logs.info("Friendship does not exist")
            return self._returnUser(user)
            
        self._friendshipDB.removeFriendship(friendship)

        return self._returnUser(user)
    
    def approveFriendship(self, data, auth):
        raise NotImplementedError
    
    def checkFriendship(self, data, auth):
        user = self._getUserFromIdOrScreenName(data)

        friendship = Friendship({
            'user_id':      auth['authenticated_user_id'],
            'friend_id':    user['user_id']
        })

        if self._friendshipDB.checkFriendship(friendship):
            return True
        return False
    
    def getFriends(self, data, auth):
        user = self._getUserFromIdOrScreenName(data)

        # Note: This function returns data even if user is private

        friends = self._friendshipDB.getFriends(user['user_id'])

        result = {'user_ids': friends}
        return result
    
    def getFollowers(self, data, auth):
        user = self._getUserFromIdOrScreenName(data)

        # Note: This function returns data even if user is private

        followers = self._friendshipDB.getFollowers(user['user_id'])

        result = {'user_ids': followers}
        return result
    
    def addBlock(self, data, auth):
        user = self._getUserFromIdOrScreenName(data)
        
        friendship = Friendship({
            'user_id':      auth['authenticated_user_id'],
            'friend_id':    user['user_id']
        })

        reverseFriendship = Friendship({
            'user_id':      user['user_id'],
            'friend_id':    auth['authenticated_user_id'],
        })

        # Check if block already exists
        if self._friendshipDB.checkBlock(friendship) == True:
            logs.info("Block exists")
            return self._returnUser(user)

        # Add block
        self._friendshipDB.addBlock(friendship)

        # Destroy friendships
        self._friendshipDB.removeFriendship(friendship)
        self._friendshipDB.removeFriendship(reverseFriendship)

        return self._returnUser(user)
    
    def checkBlock(self, data, auth):
        user = self._getUserFromIdOrScreenName(data)
        
        friendship = Friendship({
            'user_id':      auth['authenticated_user_id'],
            'friend_id':    user['user_id']
        })

        if self._friendshipDB.checkBlock(friendship):
            return True
        return False
    
    def getBlocks(self, data, auth):

        blocks = self._friendshipDB.getBlocks(auth['authenticated_user_id'])

        result = {'user_ids': blocks}
        return result
    
    def removeBlock(self, data, auth):
        user = self._getUserFromIdOrScreenName(data)

        friendship = Friendship({
            'user_id':      auth['authenticated_user_id'],
            'friend_id':    user['user_id']
        })

        # Check if block already exists
        if self._friendshipDB.checkBlock(friendship) == False:
            logs.info("Block does not exist")
            return self._returnUser(user)
            
        self._friendshipDB.removeBlock(friendship)

        return self._returnUser(user)

    
    """
    #######                             
    #         ##   #    # ######  ####  
    #        #  #  #    # #      #      
    #####   #    # #    # #####   ####  
    #       ###### #    # #           # 
    #       #    #  #  #  #      #    # 
    #       #    #   ##   ######  ####  
    """
    
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
            favorite.stamp['user_id'] = stamp.user['user_id']
                
        favorite.timestamp = {
            'created': datetime.utcnow()
        }   
        
        favorite.complete = False
        
        if not favorite.isValid:
            raise InvalidArgument('Invalid input')
            
        favoriteId = self._favoriteDB.addFavorite(favorite)
        favorite = self._favoriteDB.getFavorite(favoriteId)
        
        return self._returnFavorite(favorite)
    
    def removeFavorite(self, params):
        if self._favoriteDB.removeFavorite(params.favorite_id):
            return True
        return False
    
    def getFavorites(self, params):        
        favorites = self._favoriteDB.getFavorites(params.authenticated_user_id)
        
        result = []
        for favorite in favorites:
            result.append(self._returnFavorite(favorite))
        
        return result
    

    """
    #######                                      
    #       #    # ##### # ##### # ######  ####  
    #       ##   #   #   #   #   # #      #      
    #####   # #  #   #   #   #   # #####   ####  
    #       #  # #   #   #   #   # #           # 
    #       #   ##   #   #   #   # #      #    # 
    ####### #    #   #   #   #   # ######  ####  
    """
    
    def addEntity(self, data, auth):
        # First try to import as a full entity
        try:
            entity = Entity(data)
        except:
            # If that fails, try to import as a flat entity
            try:
                entity = EntityFlat(data).convertToEntity()
            except:
                raise

        entity.timestamp.created = datetime.utcnow()
        if 'authenticated_user_id' in auth:
            entity.sources.userGenerated.user_id = auth['authenticated_user_id']

        result = self._entityDB.addEntity(entity)

        if self.output == 'http':
            return result.exportFlat()
        return result
    
    def getEntity(self, data, auth):
        entity = self._entityDB.getEntity(data['entity_id'])
        
        ### TODO: Check if user has access to this entity

        if self.output == 'http':
            return entity.exportFlat()
        return entity
    
    def updateEntity(self, data, auth):
        entity = self._entityDB.getEntity(data['entity_id'])
        
        ### TODO: Check if user has access to this entity

        # First try to import as a full entity
        try:
            for k, v in data.iteritems():
                entity[k] = v
        except:
            # If that fails, try to import as a flat entity
            try:
                entityFlat = EntityFlat(entity.exportFlat())
                for k, v in data.iteritems():
                    entityFlat[k] = v
                entity.importData(entityFlat.convertToEntity.exportSparse())
            except:
                raise
        
        entity.timestamp.modified = datetime.utcnow()

        self._entityDB.updateEntity(entity)

        if self.output == 'http':
            return entity.exportFlat()
        return entity
    
    def removeEntity(self, data, auth):
        ### TODO: Verify user has permission to delete
        if self._entityDB.removeEntity(data['entity_id']):
            return True
        return False
    
    def searchEntities(self, params):
        ### TODO: Customize query based on authenticated_user_id / coordinates
        
        entities = self._entityDB.searchEntities(params.q, limit=10)
        result = []
        
        for entity in entities:
            data = {}
            data['entity_id'] = entity.entity_id
            data['title'] = entity.title
            data['category'] = entity.category
            data['subtitle'] = entity.subtitle
            
            result.append(data)
        
        return result
    

    """
     #####                                    
    #     # #####   ##   #    # #####   ####  
    #         #    #  #  ##  ## #    # #      
     #####    #   #    # # ## # #    #  ####  
          #   #   ###### #    # #####       # 
    #     #   #   #    # #    # #      #    # 
     #####    #   #    # #    # #       ####  
    """

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
            for screenName in params.credit.split(','):
                stamp.credit.append(screenName)
                
        stamp.timestamp = {
            'created': datetime.utcnow()
        }

        if not stamp.isValid:
            raise InvalidArgument('Invalid input')
        
        stampId = self._stampDB.addStamp(stamp)
        stamp = self._stampDB.getStamp(stampId)
        
        return self._returnStamp(stamp)
            
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
        
        return self._returnStamp(stamp)
    
    def removeStamp(self, params):
        if self._stampDB.removeStamp(params.stamp_id, params.authenticated_user_id):
            return True
        else:
            return False
    
    def getStamp(self, params):
        ### TODO: Check privacy of stamp
        stamp = self._stampDB.getStamp(params.stamp_id)        
        return self._returnStamp(stamp)
    
    def getStamps(self, stampIDs):
        stampIDs = stampIDs.split(',')
        stamps = []
        for stamp in self._stampDB.getStamps(stampIDs):
            stamps.append(stamp.getDataAsDict())
        return stamps
    

    """
     #####                                                  
    #     #  ####  #    # #    # ###### #    # #####  ####  
    #       #    # ##  ## ##  ## #      ##   #   #   #      
    #       #    # # ## # # ## # #####  # #  #   #    ####  
    #       #    # #    # #    # #      #  # #   #        # 
    #     # #    # #    # #    # #      #   ##   #   #    # 
     #####   ####  #    # #    # ###### #    #   #    ####  
    """
    
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
        
        return self._returnComment(comment)
    
    def removeComment(self, params):
        if self._stampDB.removeComment(params.comment_id):
            return True
        else:
            return False
    
    def getComments(self, params): 
        ### TODO: Check privacy of stamp       
        comments = self._stampDB.getComments(params.stamp_id)
            
        result = []
        for comment in comments:
            result.append(self._returnComment(comment))
        
        return result
    

    """
     #####                                                                  
    #     #  ####  #      #      ######  ####  ##### #  ####  #    #  ####  
    #       #    # #      #      #      #    #   #   # #    # ##   # #      
    #       #    # #      #      #####  #        #   # #    # # #  #  ####  
    #       #    # #      #      #      #        #   # #    # #  # #      # 
    #     # #    # #      #      #      #    #   #   # #    # #   ## #    # 
     #####   ####  ###### ###### ######  ####    #   #  ####  #    #  ####  
    """
    
    def getInboxStamps(self, params):
        # Limit results to 20
        limit = self._setLimit(params.limit, cap=20)
        
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
                       
        
        stamps = self._collectionDB.getInboxStamps(
                    params.authenticated_user_id, 
                    since=since, 
                    before=before, 
                    limit=limit)
        result = []
        
        for stamp in stamps:
            result.append(self._returnStamp(stamp))
        
        return result
    
    def getUserStamps(self, params):
        # Limit results to 20
        limit = self._setLimit(params.limit, cap=20)
        
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
                
        stamps = self._collectionDB.getUserStamps(
                    params.user_id, 
                    since=since, 
                    before=before, 
                    limit=limit)
        result = []
        
        for stamp in stamps:
            result.append(self._returnStamp(stamp))
        
        return result
    
    def getUserMentions(self, userID, limit=None):
        ### TODO: Implement
        raise NotImplementedError
        return self._collectionDB.getUserMentions(userID, limit)
    

    """
       #                                        
      # #    ####  ##### # #    # # ##### #   # 
     #   #  #    #   #   # #    # #   #    # #  
    #     # #        #   # #    # #   #     #   
    ####### #        #   # #    # #   #     #   
    #     # #    #   #   #  #  #  #   #     #   
    #     #  ####    #   #   ##   #   #     #   
    """
    
    def getActivity(self, params):
        # Limit results to 20
        limit = self._setLimit(params.limit, cap=20)
        
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
        
        activity = self._activityDB.getActivity(params.authenticated_user_id, \
            since=since, before=before, limit=limit)
        result = []
        for item in activity:
            result.append(self._returnActivity(item))
        
        return result
    
    # ########### #
    # Private API #
    # ########### #
    """
    ######                                      
    #     # #####  # #    #   ##   ##### ###### 
    #     # #    # # #    #  #  #    #   #      
    ######  #    # # #    # #    #   #   #####  
    #       #####  # #    # ######   #   #      
    #       #   #  #  #  #  #    #   #   #      
    #       #    # #   ##   #    #   #   ###### 
    """
    
    def _addEntity(self, entity):
        if entity is not None:
            utils.log("[%s] adding 1 entity" % (self, ))
            try:
                entity_id = self._entityDB.addEntity(entity)
                
                if 'place' in entity:
                    entity.entity_id = entity_id
                    self._placesEntityDB.addEntity(entity)
            except Exception as e:
                utils.log("[%s] error adding 1 entities:" % (self, ))
                utils.printException()
                # don't let error propagate
    
    def _addEntities(self, entities):
        entities = filter(lambda e: e is not None, entities)
        numEntities = utils.count(entities)
        if numEntities <= 0:
            return
        
        utils.log("[%s] adding %d entities" % (self, numEntities))
        
        try:
            entity_ids = self._entityDB.addEntities(entities)
            assert len(entity_ids) == len(entities)
            place_entities = []
            
            for i in xrange(len(entities)):
                entity = entities[i]
                if 'place' in entity:
                    entity.entity_id = entity_ids[i]
                    place_entities.append(entity)
            
            if len(place_entities) > 0:
                self._placesEntityDB.addEntities(place_entities)
        except Exception as e:
            utils.log("[%s] error adding %d entities:" % (self, utils.count(entities)))
            utils.printException()
            # don't let error propagate
    
    def _setLimit(self, limit, cap=20):
        result = cap
        if limit != None:
            try:
                result = int(limit)
                if result > cap:
                    result = cap
            except:
                result = cap
        return result
    
    # ################# #
    # Result Formatting #
    # ################# #
    """
    #######                                                         
    #        ####  #####  #    #   ##   ##### ##### # #    #  ####  
    #       #    # #    # ##  ##  #  #    #     #   # ##   # #    # 
    #####   #    # #    # # ## # #    #   #     #   # # #  # #      
    #       #    # #####  #    # ######   #     #   # #  # # #  ### 
    #       #    # #   #  #    # #    #   #     #   # #   ## #    # 
    #        ####  #    # #    # #    #   #     #   # #    #  ####  
    """
    
    def _returnStamp(self, stamp, mini=False):
        result = {}
        result['stamp_id'] = stamp['stamp_id']
        
        ### TODO: Explicitly define user, expand if passed full object
        result['user'] = stamp['user']
        
        ### TODO: Explicitly define entity, expand if passed full object
        result['entity'] = self._returnEntity(Entity(stamp['entity']), mini=True)
        
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
                
        if 'created' in stamp.timestamp:
            result['created'] = str(stamp.timestamp['created'])
        else:
            result['created'] = None
            
        if mini == True:
            pass
            
        else:
            if 'comment_preview' in stamp and len(stamp.comment_preview) > 0:
                result['comment_preview'] = []
                for comment in stamp.comment_preview:
                    result['comment_preview'].append(self._returnComment(comment))
            else:
                result['comment_preview'] = []
                    
            if 'stats' in stamp and 'num_comments' in stamp.stats:
                result['num_comments'] = stamp.stats['num_comments']
            else:
                result['num_comments'] = 0
                
            if 'flags' in stamp:
                result['flags'] = stamp['flags']

        return result
    
    def _returnUser(self, user, stamp=None):
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
            
        ### TODO: expand if passed full object
        result['last_stamp'] = None
        
        return result
    
    def _returnEntity(self, entity, mini=False):
        result = {}
        result['entity_id'] = entity['entity_id']
        result['title'] = entity['title']
        result['category'] = entity['category']
        result['subtitle'] = entity['subtitle']
        
        if 'place' in entity:
            entity_id = entity['entity_id']
            logs.debug("Entity: %s" % entity.getDataAsDict())
            e2 = self._placesEntityDB.getEntity(entity_id)
            entity['coordinates'] = e2.coordinates
        
        if mini == True:
            if 'coordinates' in entity:
                result['coordinates'] = "%s,%s" % (
                    entity['coordinates']['lat'],
                    entity['coordinates']['lng']
                )
        else:
            result['subcategory'] = entity['subcategory']
            
            if 'desc' in entity:
                result['desc'] = entity.desc
            else:
                result['desc'] = None
        
            if 'image' in entity:
                result['image'] = entity.image
            else:
                result['image'] = None
            
            # "Place" Details
            if 'address' in entity:
                result['address'] = entity.address
            if 'neighborhood' in entity:
                result['neighborhood'] = entity.neighborhood
            
            if 'coordinates' in entity:
                result['coordinates'] = "%s,%s" % (entity.lat, entity.lng)
            
            # "Contact" Details
            if 'phone' in entity:
                result['phone'] = entity.phone
            if 'site' in entity:
                result['site'] = entity.site
            if 'hoursOfOperation' in entity:
                result['hours'] = entity.hoursOfOperation
            
            # "Restaurant" Details
            if 'cuisine' in entity:
                result['cuisine'] = entity.cuisine
            
            # Affiliate Data
            if 'openTable' in entity:
                result['opentable_url'] = "http://www.opentable.com/reserve/%s&ref=9166" % (entity.reserveURL)
            
            if 'timestamp' in entity:
                if 'modified' in entity.timestamp:
                    result['last_modified'] = str(entity.timestamp['modified'])
                elif 'created' in entity.timestamp:
                    result['last_modified'] = str(entity.timestamp['created'])
                else:
                    result['last_modified'] = None
        
        return result
    
    def _returnFavorite(self, favorite, user=None, entity=None, stamp=None):
        result = {}
        result['favorite_id'] = favorite.favorite_id
        
        ### TODO: Explicitly define user, expand if passed full object
        result['user_id'] = favorite.user_id
        
        ### TODO: Explicitly define entity, expand if passed full object
        result['entity'] = favorite.entity
        
        ### TODO: Explicitly define stamp, expand if passed full object
        if 'stamp' in favorite:
            result['stamp'] = favorite.stamp
        else:
            result['stamp'] = None
            
        result['timestamp'] = {}
        if 'created' in favorite.timestamp:
            result['timestamp']['created'] = str(favorite.timestamp['created'])
        else:
            result['timestamp']['created'] = None
        if 'modified' in favorite.timestamp:
            result['timestamp']['modified'] = str(favorite.timestamp['modified'])
        else:
            result['timestamp']['modified'] = None
            
        if 'complete' in favorite:
            result['complete'] = favorite.complete
        else:
            result['complete'] = False
        
        return result
    
    def _returnComment(self, comment, user=None):
        result = {}
        result['comment_id'] = comment['comment_id']
        result['stamp_id'] = comment['stamp_id']
        
        ### TODO: Explicitly define user, expand if passed full object
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
            result['created'] = str(comment.timestamp['created'])
        else:
            result['created'] = None
        
        return result
    
    def _returnAccount(self, account):
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
    
    def _returnActivity(self, activity):
        result = {}
        result['activity_id'] = activity['activity_id']
        result['genre'] = activity['genre']
        
        ### TODO: Explicitly define user, expand if passed full object
        result['user'] = activity['user']
        
        ### TODO: Explicitly define stamp, expand if passed full object
        if 'stamp' in activity:
            result['stamp'] = self._returnStamp(Stamp(activity['stamp']), mini=True)
        else:
            result['stamp'] = None
        
        ### TODO: Explicitly define comment, expand if passed full object
        if 'comment' in activity:
            result['comment'] = self._returnComment(Comment(activity['comment']))
        else:
            result['comment'] = None
        
        ### TODO: Explicitly define favorite, expand if passed full object
        if 'favorite' in activity:
            result['favorite'] = self._returnFavorite(Favorite(activity['favorite']))
        else:
            result['favorite'] = None
                
        if 'created' in activity.timestamp:
            result['created'] = str(activity.timestamp['created'])
        else:
            result['created'] = None

        return result

