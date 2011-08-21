#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils, logs, re
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
        account.display_name = "%s %s." % \
                                (account.first_name, account.last_name[0])

        account = self._accountDB.addAccount(account)

        return account


    def updateAccountSettings(self, authUserId, data):
        
        ### TODO: Reexamine how updates are done

        account = self._accountDB.getAccount(authUserId)

        # Import each item
        for k, v in data.iteritems():
            if k == 'password':
                v = convertPasswordForStorage(v)
            account[k] = v

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
    
    def updateProfileImage(self, authUserId, url):

        ### TODO: Grab image and do something with it. Currently just sets as url.
            
        self._accountDB.setProfileImageLink(authUserId, url)
        
        return url
    
    def removeAccount(self, userId):
        return self._accountDB.removeAccount(userId)
    
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

    def _getUserFromIdOrScreenName(self, userRequest):
        if isinstance(userRequest, SchemaElement):
            userRequest = userRequest.value
        user_id         = userRequest.pop('user_id', None)
        screen_name     = userRequest.pop('screen_name', None)

        if user_id == None and screen_name == None:
            raise Exception("Required field missing")

        if user_id != None:
            return self._userDB.getUser(user_id)
        return self._userDB.getUserByScreenName(screen_name)

    ### PUBLIC
    
    def getUser(self, userRequest, authUserId):
        user = self._getUserFromIdOrScreenName(userRequest)
        
        if user.privacy == True:
            if authUserId == None:
                raise Exception("You must be logged in to view this account")

            friendship = Friendship({
                'user_id':      authUserId,
                'friend_id':    user['user_id']
            })

            if not self._friendshipDB.checkFriendship(friendship):
                raise Exception("You do not have permission to view this account")
        
        return user
    
    def getUsers(self, userIds, screenNames, authUserId):

        ### TODO: Add check for privacy settings
        print 'DO IT:', userIds, screenNames

        users = self._userDB.lookupUsers(userIds, screenNames, limit=100)

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
            'friend_id':    user['user_id']
        })

        reverseFriendship = Friendship({
            'user_id':      user['user_id'],
            'friend_id':    authUserId,
        })

        # Check if friendship already exists
        if self._friendshipDB.checkFriendship(friendship) == True:
            logs.info("Friendship exists")
            return user

        # Check if authenticating user is being blocked
        if self._friendshipDB.checkBlock(reverseFriendship) == True:
            logs.info("Block exists")
            raise Exception

        # Check if friend has private account
        if user.privacy == True:
            ### TODO: Create queue for friendship requests
            raise NotImplementedError

        # Create friendship
        self._friendshipDB.addFriendship(friendship)

        ### TODO: Add activity item for receipient?

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

        ### TODO: Remove stamps from Inbox

        # Increment stats for both users
        self._userDB.updateUserStats(authUserId, 'num_friends', \
                    None, increment=-1)
        self._userDB.updateUserStats(user.user_id, 'num_followers', \
                    None, increment=-1)

        return user
    
    def approveFriendship(self, data, auth):
        raise NotImplementedError
    
    def checkFriendship(self, authUserId, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)

        friendship = Friendship({
            'user_id':      authUserId,
            'friend_id':    user['user_id']
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

        return user
    

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
        
        ### TODO: Check if user has access to this entity

        return entity

    def updateCustomEntity(self, authUserId, entityId, data):
        
        ### TODO: Reexamine how updates are done

        entity = self._entityDB.getEntity(entityId)
        
        # Check if user has access to this entity
        if entity.sources.userGenerated.user_id != authUserId \
            or entity.sources.userGenerated.user_id == None:
            raise Exception("Insufficient privilages to update entity")

        # Try to import as a full entity
        for k, v in data.iteritems():
            entity[k] = v
        
        entity.timestamp.modified = datetime.utcnow()

        self._entityDB.updateEntity(entity)

        return entity

    def updateEntity(self, data, auth):
        entity = self._entityDB.getEntity(data['entity_id'])
        
        # Check if user has access to this entity
        if entity.getUserGenerated() != auth['authenticated_user_id'] \
            or entity.getUserGenerated() == None:
            raise Exception("Insufficient privilages to update entity")

        # Try to import as a full entity
        for k, v in data.iteritems():
            entity[k] = v
        
        entity.timestamp.modified = datetime.utcnow()

        self._entityDB.updateEntity(entity)

        return entity
    
    def removeEntity(self, entityId):
        return self._entityDB.removeEntity(entityId)
    
    def removeCustomEntity(self, authUserId, entityId):
        return self._entityDB.removeCustomEntity(entityId, authUserId)
    
    def searchEntities(self, query, coords=None, authUserId=None):

        ### TODO: Customize query based on authenticated_user_id / coordinates
        
        if coords is not None and 'lat' in coords and coords.lat != None:
            try:
                coords = [coords['lat'], coords['lng']]
                if coords[0] == None or coords[1] == None:
                    raise
            except:
                raise InvalidArgument('invalid input coordinates %s' % coords)
        else:
            coords = None
        
        results = self._entitySearcher.getSearchResults(query=query, coords=coords, limit=10)
        output = []

        for result in results:
            output.append(result[0])
        
        return output
    

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
                data['display_name'] = user.display_name
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
                data['display_name'] = user.display_name
                data['screen_name'] = user.screen_name
            except:
                logs.warning("User not found (%s)" % data['screen_name'])
            if data['screen_name'] not in screenNames:
                screenNames.append(data['screen_name'])
                mentions.append(data)
        
        if len(mentions) > 0:
            return mentions
        return None
        # return mentions

    def addStamp(self, authUserId, entityId, data):
        user    = self._userDB.getUser(authUserId)
        entity  = self._entityDB.getEntity(entityId)

        blurb   = data.pop('blurb', None)
        credit  = data.pop('credit', None)
        image   = data.pop('image', None)

        # Check to make sure the user hasn't already stamped this entity
        if self._stampDB.checkStamp(user.user_id, entity.entity_id):
            raise Exception("Cannot stamp same entity twice")

        # Extract mentions
        mentions = None
        if blurb != None:
            mentions = self._extractMentions(blurb)
                
        # Extract credit
        if credit != None:
            ret = []
            for creditedUser in self._userDB.lookupUsers(None, credit):
                ret.append(creditedUser.exportSchema(UserTiny()))
            ### TODO: How do we handle credited users that have not yet joined?
            ### TODO: Expand with stamp details (potentially)
            credit = ret

        # Build stamp
        stamp = Stamp({
            'user': user.exportSchema(UserMini()),
            'entity': entity.exportSchema(EntityMini()),
            'blurb': blurb,
            'credit': credit,
            'image': image,
            'mentions': mentions,
        })
        stamp.timestamp.created = datetime.utcnow()
            
        # Add the stamp data to the database
        stamp = self._stampDB.addStamp(stamp)

        # Add a reference to the stamp in the user's collection
        self._stampDB.addUserStampReference(user.user_id, stamp.stamp_id)
        
        # Add a reference to the stamp in followers' inbox
        followers = self._friendshipDB.getFollowers(user.user_id)
        followers.append(user.user_id)
        self._stampDB.addInboxStampReference(followers, stamp.stamp_id)
        
        # If stamped entity is on the to do list, mark as complete
        try:
            self._favoriteDB.completeFavorite(entity.entity_id, user.user_id)
        except:
            pass
        
        # Give credit
        creditedUserIds = []
        if credit != None and len(credit) > 0:
            for creditedUser in credit:
                userId = creditedUser['user_id']
                if userId == user.user_id or userId in creditedUserIds:
                    break

                # Assign credit
                creditedStamp = self._stampDB.giveCredit(userId, stamp)
                
                # Add restamp as comment (if prior stamp exists)
                if creditedStamp.stamp_id != None:
                    # Build comment
                    comment = Comment({
                        'user': user.exportSchema(UserMini()),
                        'stamp_id': creditedStamp.stamp_id,
                        'restamp_id': stamp.stamp_id,
                        'blurb': blurb,
                        'mentions': mentions,
                    })
                    comment.timestamp.created = datetime.utcnow()
                        
                    # Add the comment data to the database
                    self._commentDB.addComment(comment)

                    # Note: comment is added even if user is being blocked (for
                    # now). We should hide blocked users' comments from 
                    # appearing on view. But we'll come back to this
                    # regardless...

                # Update credited user stats
                self._userDB.updateUserStats(userId, 'num_credits', \
                    None, increment=1)

                ### TODO: Implement this
                # if user.user_id not in self._userDB.creditGivers(userId):
                #     self._userDB.addCreditGiver(userId, user.user_id)
                #     self._userDB.updateUserStats(userId, 'num_credit_givers', \
                #         None, increment=1)

                # Append user_id for activity
                creditedUserIds.append(creditedUser['user_id'])

        # Note: No activity should be generated for the user creating the stamp

        # Add activity for credited users
        ### TODO: Verify user isn't being blocked
        if self._activity == True and len(creditedUserIds) > 0:
            activity = Activity({
                'genre': 'restamp',
                'user': user.exportSchema(UserMini()),
                'stamp': stamp.value,
            })
            activity.timestamp.created = datetime.utcnow()
            self._activityDB.addActivity(creditedUserIds, activity)
        
        # Add activity for mentioned users
        ### TODO: Verify user isn't being blocked
        if self._activity == True and mentions != None and len(mentions) > 0:
            mentionedUserIds = []
            for mention in mentions:
                if 'user_id' in mention \
                    and mention['user_id'] not in creditedUserIds \
                    and mention['user_id'] != user.user_id:
                    mentionedUserIds.append(mention['user_id'])
            if len(mentionedUserIds) > 0:
                activity = Activity({
                    'genre': 'mention',
                    'user': user.exportSchema(UserMini()),
                    'stamp': stamp.value,
                })
                activity.timestamp.created = datetime.utcnow()
                self._activityDB.addActivity(mentionedUserIds, activity)
        
        return stamp

            
    def updateStamp(self, authUserId, stampId, data):        
        stamp   = self._stampDB.getStamp(stampId)       
        user    = self._userDB.getUser(authUserId)

        blurb   = data.pop('blurb', stamp.blurb)
        credit  = data.pop('credit', None)
        image   = data.pop('image', stamp.image)

        # Verify user can modify the stamp
        if authUserId != stamp.user.user_id:
            raise Exception("Insufficient privileges to modify stamp")

        # Extract mentions
        mentions = stamp.mentions
        if blurb != None:
            mentions = self._extractMentions(blurb)
                
        # Extract credit
        if credit != None:
            ret = []
            for creditedUser in self._userDB.lookupUsers(None, credit):
                ret.append(creditedUser.exportSchema(UserTiny()))
            ### TODO: How do we handle credited users that have not yet joined?
            ### TODO: Expand with stamp details (potentially)
            credit = ret
        
        # Compare
        if blurb != stamp.blurb:
            stamp.blurb = blurb

        if image != stamp.image:
            ### TODO: Actually upload the image....
            stamp.image = image

        mentionedUsers = []
        ### TODO: Verify that this works as expected
        if mentions != stamp.mentions:
            if mentions != None:
                previouslyMentioned = []
                for mention in stamp.mentions:
                    previouslyMentioned.append(mention.screen_name)
                for mention in mentions:
                    if mention['screen_name'] not in previouslyMentioned:
                        mentionedUsers.append(mention)
            stamp.mentions = mentions
        
        creditedUsers = []
        ### TODO: Verify that this works as expected
        if credit != stamp.credit:
            if credit == None:
                stamp.credit = []
            else:
                previouslyCredited = []
                for creditedUser in stamp.credit:
                    previouslyCredited.append(creditedUser.user_id)
                for creditedUser in credit:
                    if creditedUser['user_id'] not in previouslyCredited:
                        creditedUsers.append(creditedUser)
                stamp.credit = credit

        stamp.timestamp.modified = datetime.utcnow()
            
        # Update the stamp data in the database
        stamp = self._stampDB.updateStamp(stamp)

        # Give credit
        creditedUserIds = []
        if len(creditedUsers) > 0:
            for creditedUser in creditedUsers:
                userId = creditedUser['user_id']
                if userId == user.user_id or userId in creditedUserIds:
                    break

                # Assign credit
                creditedStamp = self._stampDB.giveCredit(userId, stamp)
                
                # Add restamp as comment (if prior stamp exists)
                if creditedStamp.stamp_id != None:
                    # Build comment
                    comment = Comment({
                        'user': user.exportSchema(UserMini()),
                        'stamp_id': creditedStamp.stamp_id,
                        'restamp_id': stamp.stamp_id,
                        'blurb': blurb,
                        'mentions': mentions,
                    })
                    comment.timestamp.created = datetime.utcnow()
                        
                    # Add the comment data to the database
                    self._commentDB.addComment(comment)

                # Update credited user stats
                self._userDB.updateUserStats(userId, 'num_credits', \
                    None, increment=1)
                # if auth['authenticated_user_id'] not in self._userDB.creditGivers(userId):
                #     self._userDB.addCreditGiver(userId, user.user_id)
                #     self._userDB.updateUserStats(userId, 'num_credit_givers', \
                #         None, increment=1)

                # Append user_id for activity
                creditedUserIds.append(creditedUser['user_id'])

        # Note: No activity should be generated for the user creating the stamp

        # Add activity for credited users
        ### TODO: Verify user isn't being blocked
        if self._activity == True and len(creditedUserIds) > 0:
            activity = Activity({
                'genre': 'restamp',
                'user': user.exportSchema(UserMini()),
                'stamp': stamp.value,
            })
            activity.timestamp.created = datetime.utcnow()
            self._activityDB.addActivity(creditedUserIds, activity)
        
        # Add activity for mentioned users
        ### TODO: Verify user isn't being blocked
        if self._activity == True and mentions != None and len(mentions) > 0:
            mentionedUserIds = []
            for mention in mentions:
                if 'user_id' in mention \
                    and mention['user_id'] not in creditedUserIds \
                    and mention['user_id'] != user.user_id:
                    mentionedUserIds.append(mention['user_id'])
            if len(mentionedUserIds) > 0:
                activity = Activity({
                    'genre': 'mention',
                    'user': user.exportSchema(UserMini()),
                    'stamp': stamp.value,
                })
                activity.timestamp.created = datetime.utcnow()
                self._activityDB.addActivity(mentionedUserIds, activity)

        return stamp
    
    def removeStamp(self, authUserId, stampId):
        stamp = self._stampDB.getStamp(stampId)

        # Verify user has permission to delete
        if stamp.user.user_id != authUserId:
            raise Exception("Insufficient privilages to remove Stamp")

        # Remove stamp
        self._stampDB.removeStamp(stamp.stamp_id)

        # Remove from user collection
        self._stampDB.removeUserStampReference(authUserId, stamp.stamp_id)
        
        # Remove from followers' inbox collections
        followers = self._friendshipDB.getFollowers(authUserId)
        followers.append(authUserId)
        # Note: this only removes the stamp from people who follow the user.
        # If we allow for an "opt in" method of users adding individual
        # stamps to their inbox, we'll have to account for that here.
        self._stampDB.removeInboxStampReference(followers, stamp.stamp_id)

        ### TODO: If restamp, remove from credited stamps' comment list

        ### TODO: Remove from activity? To do? Anything else?

        return stamp
        
    def getStamp(self, stampId, authUserId):
        stamp = self._stampDB.getStamp(stampId)

        # Check privacy of stamp
        if stamp.user.privacy == True:
            friendship = Friendship({
                'user_id':      stamp.user.user_id,
                'friend_id':    authUserId,
            })

            if not self._friendshipDB.checkFriendship(friendship):
                raise Exception("Insufficient privilages to view Stamp")
      
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

        # Verify user has the ability to comment on the stamp
        
        # Check if stamp is private; if so, must be a follower
        if stamp.user.privacy == True:
            friendship = Friendship({
                'user_id':      stamp.user.user_id,
                'friend_id':    user.user_id,
            })

            if not self._friendshipDB.checkFriendship(friendship):
                raise Exception("Insufficient privilages to add Comment")

        # Check if user is blocked by stamp owner
        ### TODO: Unit test this reverse friendship notion
        reverseFriendship= Friendship({
            'user_id':      user.user_id,
            'friend_id':    stamp.user.user_id,
        })
        if self._friendshipDB.checkBlock(reverseFriendship) == True:
            logs.info("Block exists")
            raise Exception

        # Extract mentions
        mentions = None
        if blurb != None:
            mentions = self._extractMentions(blurb)

        # Build comment
        comment = Comment({
            'user': user.exportSchema(UserMini()),
            'stamp_id': stamp.stamp_id,
            'blurb': blurb,
            'mentions': mentions,
        })
        comment.timestamp.created = datetime.utcnow()
            
        # Add the comment data to the database
        comment = self._commentDB.addComment(comment)

        # Note: No activity should be generated for the user creating the comment

        # Add activity for mentioned users
        ### TODO: Verify user isn't being blocked
        mentionedUserIds = []
        if self._activity == True and mentions != None and len(mentions) > 0:
            for mention in mentions:
                if 'user_id' in mention and mention['user_id'] != user.user_id:
                    mentionedUserIds.append(mention['user_id'])
            if len(mentionedUserIds) > 0:
                activity = Activity({
                    'genre': 'mention',
                    'user': user.exportSchema(UserMini()),
                    'stamp': stamp.value,
                    'comment': comment.value,
                })
                activity.timestamp.created = datetime.utcnow()
                self._activityDB.addActivity(mentionedUserIds, activity)
        
        # Add activity for commentor and for stamp owner
        ### TODO: Verify user isn't being blocked
        commentedUserIds = []
        if stamp.user.user_id not in mentionedUserIds \
            and stamp.user.user_id != user.user_id:
            commentedUserIds.append(stamp.user.user_id)
        if len(commentedUserIds) > 0:
            activity = Activity({
                'genre': 'comment',
                'user': user.exportSchema(UserMini()),
                'stamp': stamp.value,
                'comment': comment.value,
            })
            activity.timestamp.created = datetime.utcnow()
            self._activityDB.addActivity(commentedUserIds, activity)
        
        # Add activity for previous commenters
        ### TODO: Verify user isn't being blocked
        ### TODO: Limit this to the last 20 comments or so
        repliedUsersDict = {}
        for prevComment in self._commentDB.getComments(stamp.stamp_id):
            repliedUserId = prevComment['user']['user_id']
            if repliedUserId not in commentedUserIds \
                and repliedUserId not in mentionedUserIds \
                and repliedUserId != user.user_id:
                repliedUsersDict[prevComment['user']['user_id']] = 1 
        repliedUserIds = repliedUsersDict.keys()
        if len(repliedUserIds) > 0:
            activity = Activity({
                'genre': 'reply',
                'user': user.exportSchema(UserMini()),
                'stamp': stamp.value,
                'comment': comment.value,
            })
            activity.timestamp.created = datetime.utcnow()
            self._activityDB.addActivity(repliedUserIds, activity)
        
        # Increment comment count on stamp
        self._stampDB.incrementStatsForStamp(stamp.stamp_id, 'num_comments', 1)

        return comment
    
    def removeComment(self, authUserId, commentId):
        comment = self._commentDB.getComment(commentId)

        # Only comment owner and stamp owner can delete comment
        if comment.user.user_id != authUserId:
            stamp = self._stampDB.getStamp(comment.stamp_id)
            if stamp.user.user_id != authUserId:
                raise Exception("Insufficient privilages to remove Comment")

        # Don't allow user to delete comment for restamp notification
        if comment.restamp_id != None:
            raise Exception("Cannot remove 'Stamp' comment")

        # Remove comment
        self._commentDB.removeComment(comment.comment_id)

        ### TODO: Remove activity?

        # Increment comment count on stamp
        self._stampDB.incrementStatsForStamp(comment.stamp_id, 'num_comments', -1)

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
                raise Exception("Insufficient privilages to view Stamp")
              
        comments = self._commentDB.getComments(stamp.stamp_id)
            
        return comments
    

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
    
    def _getStampCollection(self, stampIds, **kwargs):
        quality         = kwargs.pop('quality', 3)
        limit           = kwargs.pop('limit', None)
        includeComments = kwargs.pop('includeComments', False)
                       
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

        stamps = self._stampDB.getStamps(stampIds, **params)

        if includeComments == True:
            result = []
            comments = self._commentDB.getCommentsAcrossStamps(stampIds, commentCap)

            ### TODO: Find a more efficient way to run this
            for stamp in stamps:
                for comment in comments:
                    if comment.stamp_id == stamp.stamp_id:
                        stamp['comment_preview'].append(comment)
                result.append(stamp)
            return result
        
        return stamps
    
    def getInboxStamps(self, authUserId, **kwargs):
        stampIds = self._collectionDB.getInboxStampIds(authUserId)

        kwargs['includeComments'] = True

        return self._getStampCollection(stampIds, **kwargs)
    
    def getUserStamps(self, userRequest, authUserId, **kwargs):
        user = self._getUserFromIdOrScreenName(userRequest)

        # Check privacy
        if user.privacy == True:
            if authUserId == None:
                raise Exception("You must be logged in to view this account")

            friendship = Friendship({
                'user_id':      authUserId,
                'friend_id':    user['user_id']
            })

            if not self._friendshipDB.checkFriendship(friendship):
                raise Exception("You do not have permission to view this user")
        
        stampIds = self._collectionDB.getUserStampIds(user.user_id)

        kwargs['includeComments'] = True

        return self._getStampCollection(stampIds, **kwargs)
    
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
        entity      = self._entityDB.getEntity(entityId)

        favorite = Favorite({
            'entity': entity.exportSchema(EntityMini()),
            'user_id': authUserId,
        })
        favorite.timestamp.created = datetime.utcnow()
        if stampId != None:
            stamp   = self._stampDB.getStamp(stamp_id)
            favorite.stamp = stamp

        ### TODO: Check to verify that user hasn't already favorited entity

        ### TODO: Check if user has already stamped entity

        favorite = self._favoriteDB.addFavorite(favorite)

        return favorite
    
    def removeFavorite(self, authUserId, entityId):
        favorite = self._favoriteDB.getFavorite(authUserId, entityId)
        self._favoriteDB.removeFavorite(authUserId, entityId)
        return favorite
    
    def getFavorites(self, authUserId, **kwargs):        

        ### TODO: Add slicing (before, since, limit, quality)

        favorites = self._favoriteDB.getFavorites(authUserId)

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
        
        activity = self._activityDB.getActivity(authUserId, **params)
        
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
    
