#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils, logs, re, Blacklist
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

from Schemas import *

EARNED_CREDIT_MULTIPLIER = 2

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

        ### TODO: Implement this!
        # Enable / Disable Functionality
        self._activity      = True
        self._comments      = True
        self._stamps        = True
        self._friends       = True
        self._users         = True
        self._favorites     = True
    
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
    
    def addAccount(self, account):

        ### TODO: Check if email already exists?

        account.timestamp.created = datetime.utcnow()
        account.password = convertPasswordForStorage(account['password'])

        # Set initial stamp limit
        account.stats.num_stamps_left = 100
        account.stats.num_stamps_total = 0
        
        # Validate Screen Name
        account.screen_name = account.screen_name.strip()
        if not re.match("^[\w-]+$", account.screen_name) \
            or len(account.screen_name) < 1 \
            or len(account.screen_name) > 32:
            msg = "Invalid format for screen name"
            logs.warning(msg)
            raise InputError(msg)

        # Check blacklist
        if account.screen_name.lower() in Blacklist.screen_names:
            msg = "Blacklisted screen name"
            logs.warning(msg)
            raise InputError(msg)

        # Validate email address
        account.email = str(account.email).lower().strip()
        if not utils.validate_email(account.email):
            msg = "Invalid format for email address"
            logs.warning(msg)
            raise InputError(msg)

        # Create account
        account = self._accountDB.addAccount(account)

        # Add activity if invitations were sent
        invites = self._inviteDB.getInvites(account.email)
        invitedBy = {}
        for invite in invites:
            invitedBy[invite['user_id']] = 1

            activity                = Activity()
            ### TODO: What genre are we picking for this activity item?
            activity.genre          = 'invite_sent'
            activity.user_id        = invite['user_id']
            activity.link_user_id   = invite['user_id']
            activity.created        = datetime.utcnow()
            
            self._activityDB.addActivity([account.user_id], activity)

        if len(invitedBy) > 0:
            activity                = Activity()
            ### TODO: What genre are we picking for this activity item?
            activity.genre          = 'invite_received'
            activity.user_id        = account.user_id
            activity.link_user_id   = account.user_id
            activity.created        = datetime.utcnow()
            
            self._activityDB.addActivity(invitedBy.keys(), activity)
        
        self._inviteDB.join(account.email)
        
        return account
    
    def removeAccount(self, authUserId):

        ### TODO: Remove all activity, stamps, entities, images, etc. for user
        ### TODO: Verify w/ password?

        account = self._accountDB.getAccount(authUserId)
        self._accountDB.removeAccount(authUserId)

        # Remove email address from invite list
        self._inviteDB.remove(account.email)

        return account

    def updateAccountSettings(self, authUserId, data):
        
        ### TODO: Reexamine how updates are done
        ### TODO: Verify that email address is unique, confirm it

        account = self._accountDB.getAccount(authUserId)

        # Import each item
        for k, v in data.iteritems():
            if k == 'password':
                v = convertPasswordForStorage(v)
            account[k] = v
        
        # Validate Screen Name
        account.screen_name = account.screen_name.strip()
        if not re.match("^[\w-]+$", account.screen_name) \
            or len(account.screen_name) < 1 \
            or len(account.screen_name) > 32:
            msg = "Invalid format for screen name"
            logs.warning(msg)
            raise InputError(msg)

        # Check blacklist
        if account.screen_name.lower() in Blacklist.screen_names:
            msg = "Blacklisted screen name"
            logs.warning(msg)
            raise InputError(msg)

        # Validate email address
        account.email = str(account.email).lower().strip()
        if not utils.validate_email(account.email):
            msg = "Invalid format for email address"
            logs.warning(msg)
            raise InputError(msg)

        self._accountDB.updateAccount(account)

        return account
    
    def getAccount(self, authUserId):
        account = self._accountDB.getAccount(authUserId)
        return account
    
    def updateProfile(self, authUserId, data):
        
        ### TODO: Reexamine how updates are done

        account = self._accountDB.getAccount(authUserId)

        # Import each item
        for k, v in data.iteritems():
            account[k] = v

        self._accountDB.updateAccount(account)

        return account
    
    def customizeStamp(self, authUserId, data):
        
        ### TODO: Reexamine how updates are done

        account = self._accountDB.getAccount(authUserId)

        # Import each item
        account.color_primary   = data['color_primary']
        account.color_secondary = data['color_secondary']

        self._accountDB.updateAccount(account)

        return account
    
    def updateProfileImage(self, authUserId, data):
        image   = self._imageDB.getImage(data)
        user    = self._userDB.getUser(authUserId)
        self._imageDB.addProfileImage(user.screen_name, image)
        
        return True

    def checkAccount(self, login):
        valid = False
        try:
            # Email
            if utils.validate_email(login):
                valid = True
                user = self._accountDB.getAccountByEmail(login)
            # Screen Name
            elif utils.validate_screen_name(login):
                # Check blacklist
                if login.lower() not in Blacklist.screen_names:
                    valid = True
                    user = self._accountDB.getAccountByScreenName(login)
            else:
                raise
            return user
        except:
            if valid == True:
                msg = "Login info does not exist"
                logs.debug(msg)
                raise KeyError(msg)
            else:
                msg = "Invalid input"
                logs.warning(msg)
                raise InputError(msg)

    def updateLinkedAccounts(self, authUserId, linkedAccounts):
        self._accountDB.updateLinkedAccounts(authUserId, linkedAccounts)

        return True
    
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

    def _getUserFromIdOrScreenName(self, userRequest):
        if isinstance(userRequest, SchemaElement):
            userRequest = userRequest.value
        user_id         = userRequest.pop('user_id', None)
        screen_name     = userRequest.pop('screen_name', None)

        if user_id == None and screen_name == None:
            msg = "Required field missing (user id or screen name)"
            logs.warning(msg)
            raise InputError(msg)

        if user_id != None:
            return self._userDB.getUser(user_id)
        return self._userDB.getUserByScreenName(screen_name)

    ### PUBLIC
    
    def getUser(self, userRequest, authUserId):
        user = self._getUserFromIdOrScreenName(userRequest)
        
        if user.privacy == True:
            if authUserId == None:
                msg = "Insufficient privileges to view user"
                logs.warning(msg)
                raise InsufficientPrivilegesError(msg)
            
            friendship = Friendship({
                'user_id':      authUserId,
                'friend_id':    user['user_id']
            })
            
            if not self._friendshipDB.checkFriendship(friendship):
                msg = "Insufficient privileges to view user"
                logs.warning(msg)
                raise InsufficientPrivilegesError(msg)
        
        return user
    
    def getUsers(self, userIds, screenNames, authUserId):

        ### TODO: Add check for privacy settings

        users = self._userDB.lookupUsers(userIds, screenNames, limit=100)

        return users
    
    def findUsersByEmail(self, authUserId, emails):

        ### TODO: Add check for privacy settings?

        users = self._userDB.findUsersByEmail(emails, limit=100)
        
        return users
    
    def findUsersByPhone(self, authUserId, phone):

        ### TODO: Add check for privacy settings?

        users = self._userDB.findUsersByPhone(phone, limit=100)
        
        return users
    
    def findUsersByTwitter(self, authUserId, twitterIds):

        ### TODO: Add check for privacy settings?

        users = self._userDB.findUsersByTwitter(twitterIds, limit=100)
        
        return users
    
    def searchUsers(self, query, limit, authUserId):

        limit = self._setLimit(limit, cap=20)

        ### TODO: Add check for privacy settings
        
        users = self._userDB.searchUsers(query, limit)

        return users
    
    def getPrivacy(self, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)
        
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
    
    def addFriendship(self, authUserId, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)

        friendship = Friendship({
            'user_id':      authUserId,
            'friend_id':    user.user_id
        })

        # Check if friendship already exists
        if self._friendshipDB.checkFriendship(friendship) == True:
            logs.info("Friendship exists")
            return user

        # Check if block exists between authenticating user and user
        if self._friendshipDB.blockExists(friendship) == True:
            logs.info("Block exists")
            raise Exception("Block exists")

        # Check if friend has private account
        if user.privacy == True:
            ### TODO: Create queue for friendship requests
            raise NotImplementedError

        # Create friendship
        self._friendshipDB.addFriendship(friendship)

        # Add activity for followed user
        if self._activity == True:
            activity                = Activity()
            activity.genre          = 'follower'
            activity.user_id        = authUserId
            activity.link_user_id   = authUserId
            activity.created        = datetime.utcnow()
            
            self._activityDB.addActivity(user.user_id, activity)

        # Add stamps to Inbox
        stampIds = self._collectionDB.getUserStampIds(user.user_id)
        self._stampDB.addInboxStampReferencesForUser(authUserId, stampIds)

        # Increment stats for both users
        self._userDB.updateUserStats(authUserId, 'num_friends', \
                    None, increment=1)
        self._userDB.updateUserStats(user.user_id, 'num_followers', \
                    None, increment=1)
        
        return user
    
    def removeFriendship(self, authUserId, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)

        friendship = Friendship({
            'user_id':      authUserId,
            'friend_id':    user['user_id']
        })

        # Check if friendship doesn't exist
        if self._friendshipDB.checkFriendship(friendship) == False:
            logs.info("Friendship does not exist")
            return user
            
        self._friendshipDB.removeFriendship(friendship)

        # Increment stats for both users
        self._userDB.updateUserStats(authUserId, 'num_friends', \
                    None, increment=-1)
        self._userDB.updateUserStats(user.user_id, 'num_followers', \
                    None, increment=-1)

        # Remove stamps from Inbox
        stampIds = self._collectionDB.getUserStampIds(user.user_id)
        self._stampDB.removeInboxStampReferencesForUser(authUserId, stampIds)

        return user
    
    def approveFriendship(self, data, auth):
        raise NotImplementedError
    
    def checkFriendship(self, authUserId, userRequest):
        userA = self._getUserFromIdOrScreenName({
                    'user_id': userRequest.user_id_a,
                    'screen_name': userRequest.screen_name_a
                })
        userB = self._getUserFromIdOrScreenName({
                    'user_id': userRequest.user_id_b,
                    'screen_name': userRequest.screen_name_b
                })

        # If either account is private, make sure authUserId is friend
        if userA.privacy == True and authUserId != userA.user_id:
            check = Friendship({
                'user_id':      authUserId,
                'friend_id':    userA['user_id']
            })
            if not self._friendshipDB.checkFriendship(check):
                msg = "Insufficient privileges to check friendship"
                logs.warning(msg)
                raise InsufficientPrivilegesError(msg)

        if userB.privacy == True and authUserId != userB.user_id:
            check = Friendship({
                'user_id':      authUserId,
                'friend_id':    userB['user_id']
            })
            if not self._friendshipDB.checkFriendship(check):
                msg = "Insufficient privileges to check friendship"
                logs.warning(msg)
                raise InsufficientPrivilegesError(msg)

        friendship = Friendship({
            'user_id':      userA['user_id'],
            'friend_id':    userB['user_id']
        })

        if self._friendshipDB.checkFriendship(friendship):
            return True
        return False
    
    def getFriends(self, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)

        # Note: This function returns data even if user is private

        friends = self._friendshipDB.getFriends(user['user_id'])

        return friends
    
    def getFollowers(self, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)

        # Note: This function returns data even if user is private

        followers = self._friendshipDB.getFollowers(user['user_id'])

        return followers
    
    def addBlock(self, authUserId, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)
        
        friendship = Friendship({
            'user_id':      authUserId,
            'friend_id':    user['user_id']
        })

        reverseFriendship = Friendship({
            'user_id':      user['user_id'],
            'friend_id':    authUserId,
        })

        # Check if block already exists
        if self._friendshipDB.checkBlock(friendship) == True:
            logs.info("Block exists")
            return user

        # Add block
        self._friendshipDB.addBlock(friendship)

        # Destroy friendships
        self._friendshipDB.removeFriendship(friendship)
        self._friendshipDB.removeFriendship(reverseFriendship)

        return user
    
    def checkBlock(self, authUserId, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)
        
        friendship = Friendship({
            'user_id':      authUserId,
            'friend_id':    user['user_id']
        })

        if self._friendshipDB.checkBlock(friendship):
            return True
        return False
    
    def getBlocks(self, authUserId):
        blocks = self._friendshipDB.getBlocks(authUserId)

        return blocks
    
    def removeBlock(self, authUserId, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)

        friendship = Friendship({
            'user_id':      authUserId,
            'friend_id':    user['user_id']
        })

        # Check if block already exists
        if self._friendshipDB.checkBlock(friendship) == False:
            logs.info("Block does not exist")
            return user
            
        self._friendshipDB.removeBlock(friendship)

        ### TODO: Reenable activity items that were hidden before

        return user

    def inviteFriend(self, authUserId, email):
        # Validate email address
        email = str(email).lower().strip()
        if not utils.validate_email(email):
            msg = "Invalid format for email address"
            logs.warning(msg)
            raise InputError(msg)

        # Store email address linked to auth user id
        self._inviteDB.inviteUser(email, authUserId)

        return True
    

    """
    #######                                      
    #       #    # ##### # ##### # ######  ####  
    #       ##   #   #   #   #   # #      #      
    #####   # #  #   #   #   #   # #####   ####  
    #       #  # #   #   #   #   # #           # 
    #       #   ##   #   #   #   # #      #    # 
    ####### #    #   #   #   #   # ######  ####  
    """
    
    def addEntity(self, entity):
        entity.timestamp.created = datetime.utcnow()
        entity = self._entityDB.addEntity(entity)
        return entity
    
    def getEntity(self, entityId, authUserId=None):
        entity = self._entityDB.getEntity(entityId)
        
        ### TODO: Check if user has access to this entity?
        return entity
    
    def updateCustomEntity(self, authUserId, entityId, data):
        ### TODO: Reexamine how updates are done
        entity = self._entityDB.getEntity(entityId)
        
        # Check if user has access to this entity
        if entity.generated_by != authUserId \
            or entity.generated_by == None:
            msg = "Insufficient privileges to update custom entity"
            logs.warning(msg)
            raise InsufficientPrivilegesError(msg)
        
        # Try to import as a full entity
        for k, v in data.iteritems():
            entity[k] = v
        
        entity.timestamp.modified = datetime.utcnow()
        self._entityDB.updateEntity(entity)
        
        return entity

    def updateEntity(self, data, auth):
        entity = self._entityDB.getEntity(data['entity_id'])
        
        # Try to import as a full entity
        for k, v in data.iteritems():
            entity[k] = v
        
        entity.timestamp.modified = datetime.utcnow()
        self._entityDB.updateEntity(entity)
        
        return entity
    
    def removeEntity(self, entityId):
        return self._entityDB.removeEntity(entityId)
    
    def removeCustomEntity(self, authUserId, entityId):
        entity = self._entityDB.getEntity(entityId)

        self._entityDB.removeCustomEntity(entityId, authUserId)

        return entity
    
    def searchEntities(self, 
                       query, 
                       coords=None, 
                       authUserId=None, 
                       category_filter=None, 
                       subcategory_filter=None, 
                       limit=10, 
                       prefix=False):
        coords  = self._parseCoords(coords)
        results = self._entitySearcher.getSearchResults(query=query, 
                                                        coords=coords, 
                                                        limit=limit, 
                                                        category_filter=category_filter, 
                                                        subcategory_filter=subcategory_filter, 
                                                        full=True, 
                                                        prefix=prefix)
        output  = []
        
        for result in results:
            output.append(result[0])
        
        return output
    
    def _parseCoords(self, coords):
        if coords is not None and 'lat' in coords and coords.lat != None:
            try:
                coords = [coords['lat'], coords['lng']]
                if coords[0] == None or coords[1] == None:
                    raise
            except:
                msg = "Invalid coordinates (%s)" % coords
                logs.warning(msg)
                raise InputError(msg)
            
            return coords
        else:
            return None
    
    """
     #####                                    
    #     # #####   ##   #    # #####   ####  
    #         #    #  #  ##  ## #    # #      
     #####    #   #    # # ## # #    #  ####  
          #   #   ###### #    # #####       # 
    #     #   #   #    # #    # #      #    # 
     #####    #   #    # #    # #       ####  
    """

    def _extractMentions(self, text):
        # Define patterns
        ### TODO: Modify these to match screen name pattern defined above
        user_regex = re.compile(r'([^a-zA-Z0-9_])@([a-zA-Z0-9+_]{1,20})', re.IGNORECASE)
        reply_regex = re.compile(r'@([a-zA-Z0-9+_]{1,20})', re.IGNORECASE)
        
        screenNames = []
        mentions = [] 
        
        # Check if string match exists at beginning. Should combine with regex 
        # below once I figure out how :)
        
        ### TODO: Test this -- seeing some issues where it doesn't pick up replies
        reply = reply_regex.match(text)
        if reply:
            data = {}
            data['indices'] = [(reply.start()), reply.end()]
            data['screen_name'] = reply.group(0)[1:]
            try:
                user = self._userDB.getUserByScreenName(data['screen_name'])
                data['user_id'] = user.user_id
                data['screen_name'] = user.screen_name
            except:
                logs.warning("User not found (%s)" % data['screen_name'])
            screenNames.append(data['screen_name'])
            mentions.append(data)
            
        # Run through and grab mentions
        for user in user_regex.finditer(text):
            data = {}
            data['indices'] = [(user.start()+1), user.end()]
            data['screen_name'] = user.group(0)[2:]
            try:
                user = self._userDB.getUserByScreenName(data['screen_name'])
                data['user_id'] = user.user_id
                data['screen_name'] = user.screen_name
            except:
                logs.warning("User not found (%s)" % data['screen_name'])
            if data['screen_name'] not in screenNames:
                screenNames.append(data['screen_name'])
                mentions.append(data)
        
        if len(mentions) > 0:
            return mentions
        return None

    
    def _enrichStampObjects(self, stampData, **kwargs):
        authUserId  = kwargs.pop('authUserId', None)
        entityIds   = kwargs.pop('entityIds', {})
        userIds     = kwargs.pop('userIds', {})

        singleStamp = False
        if not isinstance(stampData, list):
            singleStamp = True
            stampData = [stampData]

        # Users
        if len(userIds) == 0:
            for stamp in stampData:
                # Grab user_id from stamp
                userIds[stamp.user_id] = 1

                # Grab user_id from credit
                for credit in stamp.credit:
                    userIds[credit.user_id] = 1
                
                # Grab user_id from comments
                for comment in stamp.comment_preview:
                    userIds[comment.user_id] = 1
                
            users = self._userDB.lookupUsers(userIds.keys(), None)

            for user in users:
                userIds[user.user_id] = user.exportSchema(UserMini())

        # Entities
        if len(entityIds) == 0:
            for stamp in stampData:
                # Grab entity_id from stamp
                entityIds[stamp.entity_id] = 1
                
            entities = self._entityDB.getEntities(entityIds.keys())

            for entity in entities:
                entityIds[entity.entity_id] = entity.exportSchema(EntityMini())

        if authUserId:
            # Favorites
            favorites = self._favoriteDB.getFavoriteEntityIds(authUserId)

            # Likes
            likes = self._stampDB.getUserLikes(authUserId)
            
        # Add user objects to stamps
        stamps = []
        for stamp in stampData:
            # Add stamp user
            stamp.user = userIds[stamp.user_id]
            
            # Add entity
            stamp.entity = entityIds[stamp.entity_id]

            # Add credited user(s)
            if stamp.credit != None:
                for i in xrange(len(stamp.credit)):
                    creditedUser = userIds[stamp.credit[i].user_id]
                    stamp.credit[i].color_primary = creditedUser['color_primary']
                    stamp.credit[i].color_secondary = creditedUser['color_secondary']
                    stamp.credit[i].privacy = creditedUser['privacy']

            # Add commenting user(s)
            if stamp.comment_preview != None:
                for i in xrange(len(stamp.comment_preview)):
                    commentingUser = userIds[stamp.comment_preview[i].user_id]
                    stamp.comment_preview[i].user = commentingUser

            if authUserId:
                # Mark as favorited
                if stamp.entity_id in favorites:
                    stamp.is_fav = True

                # Mark as liked
                if stamp.stamp_id in likes:
                    stamp.is_liked = True

            stamps.append(stamp)

        if singleStamp == True:
            return stamps[0]

        return stamps

    
    def addStamp(self, authUserId, entityId, data):
        user        = self._userDB.getUser(authUserId)
        entity      = self._entityDB.getEntity(entityId)

        blurbData   = data.pop('blurb', None)
        creditData  = data.pop('credit', None)
        imageData   = data.pop('image', None)

        # Check to make sure the user has stamps left
        if user.num_stamps_left <= 0:
            msg = "No more stamps remaining"
            logs.warning(msg)
            raise IllegalActionError(msg)

        # Check to make sure the user hasn't already stamped this entity
        if self._stampDB.checkStamp(user.user_id, entity.entity_id):
            msg = "Cannot stamp same entity twice"
            logs.warning(msg)
            raise IllegalActionError(msg)

        # Build stamp
        stamp           = Stamp()
        stamp.user_id   = user.user_id
        stamp.entity_id = entity.entity_id
        stamp.created   = datetime.utcnow()
        stamp.stamp_num = user.num_stamps_total + 1

        # Collect user ids
        userIds = {}
        userIds[user.user_id] = user.exportSchema(UserMini())

        # Extract mentions
        if blurbData != None:
            stamp.blurb = blurbData.strip()
            stamp.mentions = self._extractMentions(blurbData)
                
        # Extract credit
        credit = []
        creditedUserIds = []
        if creditData != None:
            creditedUsers = self._userDB.lookupUsers(None, creditData)

            for creditedUser in creditedUsers:
                userId = creditedUser['user_id']
                if userId == user.user_id or userId in creditedUserIds:
                    continue
                
                result = CreditSchema()
                result.user_id      = creditedUser['user_id']
                result.screen_name  = creditedUser['screen_name']

                # Add to user ids
                userIds[userId] = creditedUser.exportSchema(UserMini())

                # Assign credit
                creditedStamp = self._stampDB.getStampFromUserEntity(userId, entityId)
                if creditedStamp != None:
                    result.stamp_id = creditedStamp.stamp_id

                credit.append(result)

                # Check if block exists between user and credited user
                friendship = Friendship({
                    'user_id':      user.user_id,
                    'friend_id':    userId,
                })
                if self._friendshipDB.blockExists(friendship) == True:
                    logs.debug("Block exists")
                    continue

                ### NOTE:
                # For now, if a block exists then no comment or activity is
                # created. This may change ultimately (i.e. we create the
                # 'comment' and hide it from the recipient until they're
                # unblocked), but for now we're not going to do anything.

                creditedUserIds.append(result.user_id)

            ### TODO: How do we handle credited users that have not yet joined?
            stamp.credit = credit
            
        # Add the stamp data to the database
        stamp = self._stampDB.addStamp(stamp)

        # Add image to stamp
        ### TODO: Unwind stamp if this fails
        if imageData != None:
            
            image = self._imageDB.getImage(imageData)
            self._imageDB.addStampImage(stamp.stamp_id, image)

            # Add image dimensions to stamp object (width,height)
            width, height           = image.size
            stamp.image_dimensions  = "%s,%s" % (width, height)
            stamp                   = self._stampDB.updateStamp(stamp)

        # Add user objects back into stamp
        stamp = self._enrichStampObjects(stamp, authUserId=authUserId, \
            userIds=userIds, entityIds={entity.entity_id: entity.exportSchema(EntityMini())})

        # Add a reference to the stamp in the user's collection
        self._stampDB.addUserStampReference(user.user_id, stamp.stamp_id)
        
        # Add a reference to the stamp in followers' inbox
        followers = self._friendshipDB.getFollowers(user.user_id)
        followers.append(user.user_id)
        self._stampDB.addInboxStampReference(followers, stamp.stamp_id)

        # Update user stats 
        self._userDB.updateUserStats(authUserId, 'num_stamps', \
                    None, increment=1)
        self._userDB.updateUserStats(authUserId, 'num_stamps_left', \
                    None, increment=-1)
        self._userDB.updateUserStats(authUserId, 'num_stamps_total', \
                    None, increment=1)
        
        # If stamped entity is on the to do list, mark as complete
        try:
            self._favoriteDB.completeFavorite(entity.entity_id, user.user_id)
        except:
            pass
        
        # Give credit
        if stamp.credit != None and len(stamp.credit) > 0:
            for item in credit:

                # Only run if user is flagged as credited
                if item.user_id not in creditedUserIds:
                    continue

                # Assign credit
                self._stampDB.giveCredit(item.user_id, stamp)
                
                # Add restamp as comment (if prior stamp exists)
                if 'stamp_id' in item and item['stamp_id'] != None:
                    # Build comment
                    comment                 = Comment()
                    comment.user.user_id    = user.user_id
                    comment.stamp_id        = item.stamp_id
                    comment.restamp_id      = stamp.stamp_id
                    comment.blurb           = stamp.blurb
                    comment.mentions        = stamp.mentions
                    comment.created         = datetime.utcnow()
                    
                    # Add the comment data to the database
                    self._commentDB.addComment(comment)

                # Update credited user stats
                self._userDB.updateUserStats(item.user_id, 'num_credits', \
                    None, increment=1)
                self._userDB.updateUserStats(item.user_id, 'num_stamps_left', \
                    None, increment=EARNED_CREDIT_MULTIPLIER)

        # Note: No activity should be generated for the user creating the stamp

        # Add activity for credited users
        if self._activity == True and len(creditedUserIds) > 0:
            
            activity                = Activity()
            activity.genre          = 'restamp'
            activity.user_id        = user.user_id
            activity.subject        = stamp.entity.title
            activity.link_stamp_id  = stamp.stamp_id
            activity.created        = datetime.utcnow()
            
            self._activityDB.addActivity(creditedUserIds, activity)
        
        # Add activity for mentioned users
        if self._activity == True and stamp.mentions != None and len(stamp.mentions) > 0:
            mentionedUserIds = []
            for mention in stamp.mentions:
                if 'user_id' in mention \
                    and mention['user_id'] not in creditedUserIds \
                    and mention['user_id'] != user.user_id:
                    # Check if block exists between user and mentioned user
                    friendship = Friendship({
                        'user_id':      user.user_id,
                        'friend_id':    mention['user_id'],
                    })
                    if self._friendshipDB.blockExists(friendship) == False:
                        mentionedUserIds.append(mention['user_id'])
            if len(mentionedUserIds) > 0:
                activity                = Activity()
                activity.genre          = 'mention'
                activity.user_id        = user.user_id
                activity.subject        = stamp.entity.title
                activity.blurb          = stamp.blurb
                activity.link_stamp_id  = stamp.stamp_id
                activity.created        = datetime.utcnow()
                
                self._activityDB.addActivity(mentionedUserIds, activity)
        
        return stamp

            
    def updateStamp(self, authUserId, stampId, data):        
        stamp       = self._stampDB.getStamp(stampId)       
        user        = self._userDB.getUser(authUserId)

        blurbData   = data.pop('blurb', stamp.blurb)
        creditData  = data.pop('credit', None)

        # Verify user can modify the stamp
        if authUserId != stamp.user_id:
            msg = "Insufficient privileges to modify stamp"
            logs.warning(msg)
            raise InsufficientPrivilegesError(msg)

        # Collect user ids
        userIds = {}
        userIds[user.user_id] = user.exportSchema(UserMini())

        # Blurb & Mentions
        mentionedUsers = []
        if blurbData == None:
            stamp.blurb = None
        elif blurbData.strip() != stamp.blurb:
            stamp.blurb = blurbData.strip()

            previouslyMentioned = []
            if stamp.mentions != None:
                for mention in stamp.mentions:
                    previouslyMentioned.append(mention.screen_name)
            
            mentions = self._extractMentions(blurbData)
            if mentions != None:
                for mention in mentions:
                    if mention['screen_name'] not in previouslyMentioned:
                        mentionedUsers.append(mention)
            
            stamp.mentions = mentions
                
        # Credit
        credit = []
        creditedUserIds = []
        if creditData == None:
            stamp.credit = None
        else:
            previouslyCredited = []
            for creditedUser in stamp.credit:
                previouslyCredited.append(creditedUser.user_id)

            creditedUsers = self._userDB.lookupUsers(None, creditData)

            for creditedUser in creditedUsers:
                userId = creditedUser['user_id']
                if userId == user.user_id or userId in creditedUserIds:
                    continue
                
                result = CreditSchema()
                result.user_id      = creditedUser['user_id']
                result.screen_name  = creditedUser['screen_name']

                # Add to user ids
                userIds[userId] = creditedUser.exportSchema(UserMini())

                # Assign credit
                creditedStamp = self._stampDB.getStampFromUserEntity(userId, \
                                    stamp.entity.entity_id)
                if creditedStamp != None:
                    result.stamp_id = creditedStamp.stamp_id

                credit.append(result)

                # Check if user was credited previously
                if userId in previouslyCredited:
                    continue

                # Check if block exists between user and credited user
                friendship = Friendship({
                    'user_id':      user.user_id,
                    'friend_id':    userId,
                })
                if self._friendshipDB.blockExists(friendship) == True:
                    logs.debug("Block exists")
                    continue

                ### NOTE:
                # For now, if a block exists then no comment or activity is
                # created. This may change ultimately (i.e. we create the
                # 'comment' and hide it from the recipient until they're
                # unblocked), but for now we're not going to do anything.

                creditedUserIds.append(result.user_id)

            ### TODO: How do we handle credited users that have not yet joined?
            stamp.credit = credit

        stamp.timestamp.modified = datetime.utcnow()
            
        # Update the stamp data in the database
        stamp = self._stampDB.updateStamp(stamp)

        # Add user objects back into stamp
        stamp = self._enrichStampObjects(stamp, authUserId=authUserId, userIds=userIds)

        # Give credit
        if stamp.credit != None and len(stamp.credit) > 0:
            for item in credit:

                # Only run if user is flagged as credited
                if item.user_id not in creditedUserIds:
                    continue

                # Assign credit
                self._stampDB.giveCredit(item.user_id, stamp)
                
                # Add restamp as comment (if prior stamp exists)
                if 'stamp_id' in item and item['stamp_id'] != None:
                    # Build comment
                    comment                 = Comment()
                    comment.user.user_id    = user.user_id
                    comment.stamp_id        = item.stamp_id
                    comment.restamp_id      = stamp.stamp_id
                    comment.blurb           = stamp.blurb
                    comment.mentions        = stamp.mentions
                    comment.created         = datetime.utcnow()
                    
                    # Add the comment data to the database
                    self._commentDB.addComment(comment)

                # Update credited user stats
                self._userDB.updateUserStats(item.user_id, 'num_credits', \
                    None, increment=1)
                self._userDB.updateUserStats(item.user_id, 'num_stamps_left', \
                    None, increment=EARNED_CREDIT_MULTIPLIER)

        # Note: No activity should be generated for the user creating the stamp

        # Add activity for credited users
        if self._activity == True and len(creditedUserIds) > 0:
            activity                = Activity()
            activity.genre          = 'restamp'
            activity.user_id        = user.user_id
            activity.subject        = stamp.entity.title
            activity.link_stamp_id  = stamp.stamp_id
            activity.created        = datetime.utcnow()
            
            self._activityDB.addActivity(creditedUserIds, activity)
        
        # Add activity for mentioned users
        if self._activity == True and stamp.mentions != None \
            and len(stamp.mentions) > 0:
            mentionedUserIds = []
            for mention in stamp.mentions:
                if 'user_id' in mention \
                    and mention['user_id'] not in creditedUserIds \
                    and mention['user_id'] != user.user_id:
                    # Check if block exists between user and mentioned user
                    friendship = Friendship({
                        'user_id':      user.user_id,
                        'friend_id':    mention['user_id'],
                    })
                    if self._friendshipDB.blockExists(friendship) == False:
                        mentionedUserIds.append(mention['user_id'])
            if len(mentionedUserIds) > 0:
                activity                = Activity()
                activity.genre          = 'mention'
                activity.user_id        = user.user_id
                activity.subject        = stamp.entity.title
                activity.blurb          = stamp.blurb
                activity.link_stamp_id  = stamp.stamp_id
                activity.created        = datetime.utcnow()

                self._activityDB.addActivity(mentionedUserIds, activity)

        return stamp
    
    def removeStamp(self, authUserId, stampId):
        stamp       = self._stampDB.getStamp(stampId)
        stamp       = self._enrichStampObjects(stamp, authUserId=authUserId)

        # Verify user has permission to delete
        if stamp.user_id != authUserId:
            msg = "Insufficient privileges to remove stamp"
            logs.warning(msg)
            raise InsufficientPrivilegesError(msg)

        # Remove stamp
        self._stampDB.removeStamp(stamp.stamp_id)

        # Remove from user collection
        self._stampDB.removeUserStampReference(authUserId, stamp.stamp_id)
        
        # Remove from followers' inbox collections
        followers = self._friendshipDB.getFollowers(authUserId)
        followers.append(authUserId)
        self._stampDB.removeInboxStampReference(followers, stamp.stamp_id)

        ### NOTE: 
        # This only removes the stamp from people who follow the user.
        # If we allow for an "opt in" method of users adding individual
        # stamps to their inbox, we'll have to account for that here.

        ### TODO: If restamp, remove from credited stamps' comment list

        ### TODO: Remove from activity? To do? Anything else?

        # Update user stats 
        ### TODO: Do an actual count / update?
        self._userDB.updateUserStats(authUserId, 'num_stamps', \
                    None, increment=-1)
        self._userDB.updateUserStats(authUserId, 'num_stamps_left', \
                    None, increment=1)

        ### TODO: Update credit stats if credit given

        return stamp
        
    def getStamp(self, stampId, authUserId=None):
        stamp       = self._stampDB.getStamp(stampId)
        stamp       = self._enrichStampObjects(stamp, authUserId=authUserId)

        # Check privacy of stamp
        if stamp.user_id != authUserId and stamp.user.privacy == True:
            friendship = Friendship({
                'user_id':      user.user_id,
                'friend_id':    authUserId,
            })

            if not self._friendshipDB.checkFriendship(friendship):
                msg = "Insufficient privileges to view stamp"
                logs.warning(msg)
                raise InsufficientPrivilegesError(msg)
      
        return stamp

    def getStampFromUser(self, screenName, stampNumber):
        user = self._userDB.getUserByScreenName(screenName)
        stamp = self._stampDB.getStampFromUserStampNum(user.user_id, \
                                                        stampNumber)
        stamp = self._enrichStampObjects(stamp)

        if stamp.user.privacy == True:
            msg = "Insufficient privileges to view stamp"
            logs.warning(msg)
            raise InsufficientPrivilegesError(msg)

        return stamp
    
    def updateStampImage(self, authUserId, stampId, data):
        stamp       = self._stampDB.getStamp(stampId)
        stamp       = self._enrichStampObjects(stamp, authUserId=authUserId)

        # Verify user has permission to add image
        if stamp.user_id != authUserId:
            msg = "Insufficient privileges to update stamp image"
            logs.warning(msg)
            raise InsufficientPrivilegesError(msg)
        
        image = self._imageDB.getImage(data)
        self._imageDB.addStampImage(stampId, image)

        # Add image dimensions to stamp object (width,height)
        width, height           = image.size
        stamp.image_dimensions  = "%s,%s" % (width, height)
        stamp                   = self._stampDB.updateStamp(stamp)
        
        return stamp
    

    """
     #####                                                  
    #     #  ####  #    # #    # ###### #    # #####  ####  
    #       #    # ##  ## ##  ## #      ##   #   #   #      
    #       #    # # ## # # ## # #####  # #  #   #    ####  
    #       #    # #    # #    # #      #  # #   #        # 
    #     # #    # #    # #    # #      #   ##   #   #    # 
     #####   ####  #    # #    # ###### #    #   #    ####  
    """

    def addComment(self, authUserId, stampId, blurb):
        user    = self._userDB.getUser(authUserId)
        stamp   = self._stampDB.getStamp(stampId)
        stamp   = self._enrichStampObjects(stamp, authUserId=authUserId)

        # Verify user has the ability to comment on the stamp
        friendship = Friendship({
            'user_id':      stamp.user.user_id,
            'friend_id':    user.user_id,
        })

        # Check if stamp is private; if so, must be a follower
        if stamp.user.privacy == True:
            if not self._friendshipDB.checkFriendship(friendship):
                msg = "Insufficient privileges to add comment"
                logs.warning(msg)
                raise InsufficientPrivilegesError(msg)

        # Check if block exists between user and stamp owner
        if self._friendshipDB.blockExists(friendship) == True:
            logs.info("Block exists")
            raise Exception("Block exists")

        # Extract mentions
        mentions = None
        if blurb != None:
            mentions = self._extractMentions(blurb)

        # Build comment
        comment             = Comment()
        comment.user_id     = user.user_id
        comment.stamp_id    = stamp.stamp_id
        comment.blurb       = blurb
        comment.created     = datetime.utcnow()
        if mentions != None:
            comment.mentions = mentions
            
        # Add the comment data to the database
        comment = self._commentDB.addComment(comment)

        # Add full user object back
        comment.user = user.exportSchema(UserMini())

        # Note: No activity should be generated for the user creating the comment

        # Add activity for mentioned users
        mentionedUserIds = []
        if self._activity == True and mentions != None and len(mentions) > 0:
            for mention in mentions:
                if 'user_id' in mention and mention['user_id'] != user.user_id:
                    # Check if block exists between user and mentioned user
                    friendship = Friendship({
                        'user_id':      user.user_id,
                        'friend_id':    mention['user_id'],
                    })
                    if self._friendshipDB.blockExists(friendship) == False:
                        mentionedUserIds.append(mention['user_id'])
            if len(mentionedUserIds) > 0:
                activity                    = Activity()
                activity.genre              = 'mention'
                activity.user_id            = user.user_id
                activity.subject            = stamp.entity.title
                activity.blurb              = comment.blurb
                activity.link_stamp_id      = stamp.stamp_id
                activity.link_comment_id    = comment.comment_id
                activity.created            = datetime.utcnow()

                self._activityDB.addActivity(mentionedUserIds, activity)
        
        # Add activity for stamp owner
        commentedUserIds = []
        if stamp.user.user_id not in mentionedUserIds \
            and stamp.user.user_id != user.user_id:
            commentedUserIds.append(stamp.user.user_id)
        if len(commentedUserIds) > 0:
            activity                    = Activity()
            activity.genre              = 'comment'
            activity.user_id            = user.user_id
            activity.subject            = stamp.entity.title
            activity.blurb              = comment.blurb
            activity.link_stamp_id      = stamp.stamp_id
            activity.link_comment_id    = comment.comment_id
            activity.created            = datetime.utcnow()
            
            self._activityDB.addActivity(commentedUserIds, activity)
        
        # Add activity for previous commenters
        ### TODO: Limit this to the last 20 comments or so
        repliedUsersDict = {}
        for prevComment in self._commentDB.getComments(stamp.stamp_id):
            repliedUserId = prevComment['user']['user_id']
            if repliedUserId not in commentedUserIds \
                and repliedUserId not in mentionedUserIds \
                and repliedUserId != user.user_id:
                repliedUsersDict[prevComment['user']['user_id']] = 1 
        # repliedUserIds = repliedUsersDict.keys()
        repliedUserIds = []
        for repliedUserId in repliedUsersDict.keys():
            # Check if block exists between user and previous commenter
            friendship = Friendship({
                'user_id':      user.user_id,
                'friend_id':    repliedUserId,
            })
            if self._friendshipDB.blockExists(friendship) == False:
                repliedUserIds.append(repliedUserId)

        if len(repliedUserIds) > 0:
            activity                    = Activity()
            activity.genre              = 'reply'
            activity.user_id            = user.user_id
            activity.subject            = stamp.entity.title
            activity.blurb              = comment.blurb
            activity.link_stamp_id      = stamp.stamp_id
            activity.link_comment_id    = comment.comment_id
            activity.created            = datetime.utcnow()

            self._activityDB.addActivity(repliedUserIds, activity)
        
        # Increment comment count on stamp
        self._stampDB.updateStampStats( \
            stamp.stamp_id, 'num_comments', increment=1)

        return comment
    
    def removeComment(self, authUserId, commentId):
        comment = self._commentDB.getComment(commentId)

        # Only comment owner and stamp owner can delete comment
        if comment.user.user_id != authUserId:
            stamp = self._stampDB.getStamp(comment.stamp_id)
            if stamp.user.user_id != authUserId:
                msg = "Insufficient privileges to remove comment"
                logs.warning(msg)
                raise InsufficientPrivilegesError(msg)

        # Don't allow user to delete comment for restamp notification
        if comment.restamp_id != None:
            msg = "Cannot remove 'restamp' comment"
            logs.warning(msg)
            raise IllegalActionError(msg)

        # Remove comment
        self._commentDB.removeComment(comment.comment_id)

        ### TODO: Remove activity?

        # Increment comment count on stamp
        self._stampDB.updateStampStats( \
            comment.stamp_id, 'num_comments', increment=-1)

        # Add user object
        user = self._userDB.getUser(comment.user_id)
        comment.user = user.exportSchema(UserMini())

        return comment
    
    def getComments(self, stampId, authUserId, **kwargs): 
        stamp = self._stampDB.getStamp(stampId)

        ### TODO: Add slicing (before, since, limit, quality)

        # Check privacy of stamp
        if stamp.user.privacy == True:
            friendship = Friendship({
                'user_id':      stamp.user.user_id,
                'friend_id':    authUserId,
            })

            if not self._friendshipDB.checkFriendship(friendship):
                msg = "Insufficient privileges to view stamp"
                logs.warning(msg)
                raise InsufficientPrivilegesError(msg)
              
        commentData = self._commentDB.getComments(stamp.stamp_id)

        # Get user objects
        userIds = {}
        for comment in commentData:
            userIds[comment.user.user_id] = 1

        users = self._userDB.lookupUsers(userIds.keys(), None)

        for user in users:
            userIds[user.user_id] = user.exportSchema(UserMini())

        comments = []
        for comment in commentData:
            comment.user = userIds[comment.user_id]
            comments.append(comment)

        comments = sorted(comments, key=lambda k: k['timestamp']['created'])
            
        return comments
    
    ### TEMP: Remove after switching to new activity
    def _getComment(self, commentId, **kwargs): 
        comment = self._commentDB.getComment(commentId)

        # Get user objects
        user            = self._userDB.getUser(comment.user.user_id)
        comment.user    = user.exportSchema(UserMini())

        return comment

    
    """
    #                              
    #       # #    # ######  ####  
    #       # #   #  #      #      
    #       # ####   #####   ####  
    #       # #  #   #           # 
    #       # #   #  #      #    # 
    ####### # #    # ######  ####  
    """

    def addLike(self, authUserId, stampId):
        stamp       = self._stampDB.getStamp(stampId)
        stamp       = self._enrichStampObjects(stamp, authUserId=authUserId)

        # Verify user has the ability to 'like' the stamp
        if stamp.user_id != authUserId:
            friendship = Friendship({
                'user_id':      stamp.user_id,
                'friend_id':    authUserId,
            })

            # Check if stamp is private; if so, must be a follower
            if stamp.user.privacy == True:
                if not self._friendshipDB.checkFriendship(friendship):
                    msg = "Insufficient privileges to add comment"
                    logs.warning(msg)
                    raise InsufficientPrivilegesError(msg)

            # Check if block exists between user and stamp owner
            if self._friendshipDB.blockExists(friendship) == True:
                logs.info("Block exists")
                raise Exception("Block exists")

        # Check to verify that user hasn't already liked stamp
        if self._stampDB.checkLike(authUserId, stampId):
            msg = "'Like' exists for user (%s) on stamp (%s)" \
                % (authUserId, stampId)
            logs.warning(msg)
            raise IllegalActionError(msg)

        # Add like
        self._stampDB.addLike(authUserId, stampId)

        # Increment user stats by one
        self._userDB.updateUserStats( \
            stamp.user_id, 'num_likes', increment=1)
        self._userDB.updateUserStats( \
            authUserId, 'num_likes_given', increment=1)

        # Increment stamp stats by one
        self._stampDB.updateStampStats( \
            stamp.stamp_id, 'num_likes', increment=1)
        if stamp.num_likes == None:
            stamp.num_likes = 0
        stamp.num_likes += 1
        stamp.is_liked = True

        # Give credit once at five likes
        if stamp.num_likes >= 5 and not stamp.like_threshold_hit:
            # Update stamp stats
            self._stampDB.giveLikeCredit(stamp.stamp_id)
            stamp.like_threshold_hit = True

            # Update user stats with new credit
            self._userDB.updateUserStats( \
                stamp.user_id, 'num_stamps_left', increment=1)

        # Add activity for stamp owner (if not self)
        if self._activity == True and stamp.user_id != authUserId:
            activity                = Activity()
            activity.genre          = 'like'
            activity.user_id        = authUserId
            activity.subject        = stamp.entity.title
            activity.link_stamp_id  = stamp.stamp_id
            activity.created        = datetime.utcnow()

            self._activityDB.addActivity(stamp.user_id, activity)

        return stamp
    
    def removeLike(self, authUserId, stampId):
        # Remove like (if it exists)
        if not self._stampDB.removeLike(authUserId, stampId):
            msg = "'Like' does not exist for user (%s) on stamp (%s)" \
                % (authUserId, stampId)
            logs.warning(msg)
            raise IllegalActionError(msg)

        # Get stamp object
        stamp       = self._stampDB.getStamp(stampId)
        stamp       = self._enrichStampObjects(stamp, authUserId=authUserId)

        # Increment user stats by one
        self._userDB.updateUserStats( \
            stamp.user_id, 'num_likes', increment=-1)
        self._userDB.updateUserStats( \
            authUserId, 'num_likes_given', increment=-1)

        # Increment stamp stats by one
        self._stampDB.updateStampStats( \
            stamp.stamp_id, 'num_likes', increment=-1)
        if stamp.num_likes == None:
            stamp.num_likes = 0
        stamp.num_likes -= 1

        ### TODO: Remove activity item?

        return stamp
    

    """
     #####                                                                  
    #     #  ####  #      #      ######  ####  ##### #  ####  #    #  ####  
    #       #    # #      #      #      #    #   #   # #    # ##   # #      
    #       #    # #      #      #####  #        #   # #    # # #  #  ####  
    #       #    # #      #      #      #        #   # #    # #  # #      # 
    #     # #    # #      #      #      #    #   #   # #    # #   ## #    # 
     #####   ####  ###### ###### ######  ####    #   #  ####  #    #  ####  
    """

    def _setSliceParams(self, data):
        # Since
        try: 
            since = datetime.utcfromtimestamp(int(data.pop('since', None))-2)
        except:
            since = None
        
        # Before
        try: 
            before = datetime.utcfromtimestamp(int(data.pop('before', None))+2)
        except:
            before = None
        
        return since, before
    
    def _setLimit(self, limit, cap=20):
        try:
            if int(limit) < cap:
                return int(limit)
        except:
            return cap
    
    def _getStampCollection(self, authUserId, stampIds, **kwargs):
        quality         = kwargs.pop('quality', 3)
        limit           = kwargs.pop('limit', None)
        includeComments = kwargs.pop('includeComments', False)
        godMode         = kwargs.pop('godMode', False)
                       
        # Set quality
        if quality == 1:
            stampCap    = 50
            commentCap  = 20
        elif quality == 2:
            stampCap    = 30
            commentCap  = 10
        else:
            stampCap    = 20
            commentCap  = 4

        if godMode == True:
            stampCap    = 10000
            commentCap  = 20
        
        limit = self._setLimit(limit, cap=stampCap)
        
        # Limit slice of data returned
        since, before = self._setSliceParams(kwargs)

        params = {
            'since':    since,
            'before':   before, 
            'limit':    limit,
        }

        stampData = self._stampDB.getStamps(stampIds, **params)

        if includeComments == True:
            commentData = self._commentDB.getCommentsAcrossStamps(stampIds, commentCap)

            # Group previews by stamp_id
            commentPreviews = {}
            for comment in commentData:
                if comment.stamp_id not in commentPreviews:
                    commentPreviews[comment.stamp_id] = []
                commentPreviews[comment.stamp_id].append(comment)

            # Add user object and preview to stamps
            stamps = []
            for stamp in stampData:
                if stamp.stamp_id in commentPreviews:
                    stamp.comment_preview = commentPreviews[stamp.stamp_id]
                stamps.append(stamp)

        stamps = self._enrichStampObjects(stamps, authUserId=authUserId)

        return stamps
    
    def getInboxStamps(self, authUserId, **kwargs):
        stampIds = self._collectionDB.getInboxStampIds(authUserId)

        kwargs['includeComments'] = True

        return self._getStampCollection(authUserId, stampIds, **kwargs)
    
    def getUserStamps(self, userRequest, authUserId, **kwargs):
        user = self._getUserFromIdOrScreenName(userRequest)

        # Check privacy
        if user.privacy == True:
            if authUserId == None:
                msg = "Must be logged in to view account"
                logs.warning(msg)
                raise InsufficientPrivilegesError(msg)

            friendship = Friendship({
                'user_id':      authUserId,
                'friend_id':    user['user_id']
            })

            if not self._friendshipDB.checkFriendship(friendship):
                msg = "Insufficient privileges to view user"
                logs.warning(msg)
                raise InsufficientPrivilegesError(msg)
        
        stampIds = self._collectionDB.getUserStampIds(user.user_id)

        kwargs['includeComments'] = True

        return self._getStampCollection(authUserId, stampIds, **kwargs)
    
    def getCreditedStamps(self, userRequest, authUserId, **kwargs):
        ### TODO: Implement
        raise NotImplementedError
    
    def getUserMentions(self, userID, limit=None):
        ### TODO: Implement
        raise NotImplementedError
        return self._collectionDB.getUserMentions(userID, limit)

    
    """
    #######                             
    #         ##   #    # ######  ####  
    #        #  #  #    # #      #      
    #####   #    # #    # #####   ####  
    #       ###### #    # #           # 
    #       #    #  #  #  #      #    # 
    #       #    #   ##   ######  ####  
    """

    def addFavorite(self, authUserId, entityId, stampId=None):
        entity  = self._entityDB.getEntity(entityId)

        favorite = Favorite({
            'entity': entity.exportSchema(EntityMini()),
            'user_id': authUserId,
        })
        favorite.timestamp.created = datetime.utcnow()

        if stampId != None:
            stamp   = self._stampDB.getStamp(stampId)
            favorite.stamp = stamp

        # Check to verify that user hasn't already favorited entity
        try:
            fav = self._favoriteDB.getFavorite(authUserId, entityId)
            if fav.favorite_id == None:
                raise
            exists = True
        except:
            exists = False

        if exists:
            msg = "Favorite already exists"
            logs.warning(msg)
            raise IllegalActionError(msg)

        # Check if user has already stamped entity, mark as complete if so
        if self._stampDB.checkStamp(authUserId, entityId):
            favorite.complete = True

        favorite = self._favoriteDB.addFavorite(favorite)

        # Enrich stamp
        if stampId != None:
            favorite.stamp = self._enrichStampObjects( \
                                favorite.stamp, authUserId=authUserId)

        # Increment user stats by one
        self._userDB.updateUserStats(authUserId, 'num_faves', \
                    None, increment=1)

        # Add activity for stamp owner (if not self)
        ### TODO: Verify user isn't being blocked
        if self._activity == True and stampId != None \
            and stamp.user_id != authUserId:
            activity                = Activity()
            activity.genre          = 'favorite'
            activity.user_id        = authUserId
            activity.subject        = stamp.entity.title
            activity.link_stamp_id  = stamp.stamp_id
            activity.created        = datetime.utcnow()

            self._activityDB.addActivity(stamp.user_id, activity)

        return favorite
    
    def removeFavorite(self, authUserId, entityId):
        favorite = self._favoriteDB.getFavorite(authUserId, entityId)
        self._favoriteDB.removeFavorite(authUserId, entityId)

        # Decrement user stats by one
        self._userDB.updateUserStats(authUserId, 'num_faves', \
                    None, increment=-1)

        ### TODO: Remove activity item?

        # Enrich stamp
        if favorite.stamp_id != None:
            favorite.stamp = self._enrichStampObjects( \
                                favorite.stamp, authUserId=authUserId)

        return favorite
    
    def getFavorites(self, authUserId, **kwargs):        

        ### TODO: Add slicing (before, since, limit, quality)

        favoriteData = self._favoriteDB.getFavorites(authUserId)

        stamps = []
        for favorite in favoriteData:
            if favorite.stamp_id != None:
                stamps.append(favorite['stamp'])
        stamps = self._enrichStampObjects(stamps, authUserId=authUserId)

        stampIds = {}
        for stamp in stamps:
            stampIds[stamp.stamp_id] = stamp

        favorites = []
        for favorite in favoriteData:
            if favorite.stamp_id != None:
                favorite.stamp = stampIds[favorite.stamp.stamp_id]
            favorites.append(favorite)

        return favorites
    
    """
       #                                        
      # #    ####  ##### # #    # # ##### #   # 
     #   #  #    #   #   # #    # #   #    # #  
    #     # #        #   # #    # #   #     #   
    ####### #        #   # #    # #   #     #   
    #     # #    #   #   #  #  #  #   #     #   
    #     #  ####    #   #   ##   #   #     #   
    """
    
    def getActivity(self, authUserId, **kwargs):
        quality     = kwargs.pop('quality', 3)
        limit       = kwargs.pop('limit', None)
                       
        # Set quality
        if quality == 1:
            stampCap    = 50
            commentCap  = 20
        elif quality == 2:
            stampCap    = 30
            commentCap  = 10
        else:
            stampCap    = 20
            commentCap  = 4
        
        limit = self._setLimit(limit, cap=stampCap)
        
        # Limit slice of data returned
        since, before = self._setSliceParams(kwargs)

        params = {
            'since':    since,
            'before':   before, 
            'limit':    limit,
        }
        
        activityData = self._activityDB.getActivity(authUserId, **params)

        # Append user objects
        userIds = {}
        for item in activityData:
            if item.user.user_id != None:
                userIds[item.user.user_id] = 1

        users = self._userDB.lookupUsers(userIds.keys(), None)

        for user in users:
            userIds[user.user_id] = user.exportSchema(UserMini())

        activity = []
        for item in activityData:
            if item.user.user_id != None:
                item.user = userIds[item.user.user_id]
            activity.append(item)
        
        return activity
    
    
    """
    ######                                      
    #     # #####  # #    #   ##   ##### ###### 
    #     # #    # # #    #  #  #    #   #      
    ######  #    # # #    # #    #   #   #####  
    #       #####  # #    # ######   #   #      
    #       #   #  #  #  #  #    #   #   #      
    #       #    # #   ##   #    #   #   ###### 
    """
    
    def _convertSearchId(self, search_id):
        if search_id.startswith('T_'):
            doc = self._tempEntityDB._collection.find_one({'search_id' : search_id})
            
            if doc is None:
                return None
            
            entity = self._tempEntityDB._convertFromMongo(doc)
            del entity.entity_id
            del entity.search_id
            
            entity = self._entityMatcher.addOne(entity)
            assert entity.entity_id is not None
            return entity.entity_id
        else:
            # already a valid entity id
            return search_id
    
    def _addEntity(self, entity):
        if entity is not None:
            utils.log("[%s] adding 1 entity" % (self, ))
            try:
                #self._entityMatcher.addOne(entity)
                entity2 = self._entityDB.addEntity(entity)
                
                if 'place' in entity:
                    self._placesEntityDB.addEntity(entity2)
                return entity2
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
            entities2 = self._entityDB.addEntities(entities)
            assert len(entities2) == len(entities)
            place_entities = []
            
            for i in xrange(len(entities2)):
                entity = entities2[i]
                if 'place' in entity:
                    place_entities.append(entity)
            
            if len(place_entities) > 0:
                self._placesEntityDB.addEntities(place_entities)
            
            return entities2
        except Exception as e:
            utils.log("[%s] error adding %d entities:" % (self, utils.count(entities)))
            utils.printException()
            # don't let error propagate

