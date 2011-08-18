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

from Account import Account
from Entity import *
from User import User
from Stamp import Stamp
from Comment import Comment
from Favorite import Favorite
from Friendship import Friendship
from Activity import Activity

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
        self.output = kwargs.pop('output', False)

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

        ### TODO: Update account settings across denormalized db (e.g. Stamps)

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

        ### TODO: Update profile settings across denormalized db (e.g. Stamps)
        
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

            friendship = Friendship({
                'user_id':      auth['authenticated_user_id'],
                'friend_id':    user['user_id']
            })

            if not self._friendshipDB.checkFriendship(friendship):
                raise Exception("You do not have permission to view this account")
        
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

        reverseFriendship = Friendship({
            'user_id':      user['user_id'],
            'friend_id':    auth['authenticated_user_id'],
        })

        # Check if friendship already exists
        if self._friendshipDB.checkFriendship(friendship) == True:
            logs.info("Friendship exists")
            return self._returnUser(user)

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

    def addFavorite(self, data, auth):
        entity      = self._entityDB.getEntity(data['entity_id'])
        stamp_id    = data.pop('stamp_id', None)

        favorite = Favorite({
            'entity': entity.exportSchema(EntityMini()),
            'user_id': auth['authenticated_user_id'],
        })
        favorite.setTimestampCreated()
        if stamp_id != None:
            stamp   = self._stampDB.getStamp(stamp_id)
            favorite.stamp = stamp.value

        ### TODO: Check to verify that user hasn't already favorited entity

        ### TODO: Check if user has already stamped entity

        favorite = self._favoriteDB.addFavorite(favorite)

        if self.output == 'http':
            return favorite.exportFlat()
        return favorite
    
    def removeFavorite(self, data, auth):
        self._favoriteDB.removeFavorite(data['entity_id'], \
                                        auth['authenticated_user_id'])
        return True
    
    def getFavorites(self, data, auth):        
        favorites = self._favoriteDB.getFavorites(auth['authenticated_user_id'])
        
        if self.output == 'http':
            result = []
            for favorite in favorites:
                result.append(favorite.exportFlat())
            return result

        return favorite
    
    def getFavoritesOld(self, params):        
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

    def addFlatEntity(self, data, auth):
        entity = FlatEntity(data).convertToEntity().exportSparse()
        return self.addEntity(entity, auth)
    
    def addEntity(self, entity):

        entity = self._entityDB.addEntity(entity)

        return entity
    
    def getEntity(self, data, auth):
        entity = self._entityDB.getEntity(data['entity_id'])
        
        ### TODO: Check if user has access to this entity

        if self.output == 'http':
            return entity.exportFlat()
        return entity
    
    def updateFlatEntity(self, data, auth):
        entity = self._entityDB.getEntity(data['entity_id'])

        flatEntity = FlatEntity(entity.exportFlat(), overflow=True)
        for k, v in data.iteritems():
            flatEntity[k] = v
        data = flatEntity.convertToEntity().exportSparse()

        return self.updateEntity(data, auth)

    def updateEntity(self, data, auth):
        entity = self._entityDB.getEntity(data['entity_id'])
        
        # Check if user has access to this entity
        if entity.getUserGenerated() != auth['authenticated_user_id'] \
            or entity.getUserGenerated() == None:
            raise Exception("Insufficient privilages to update entity")

        # Try to import as a full entity
        for k, v in data.iteritems():
            entity[k] = v
        
        entity.setTimestampModified()

        self._entityDB.updateEntity(entity)

        if self.output == 'http':
            return entity.exportFlat()
        return entity
    
    def removeEntity(self, data, auth):
        entity = self._entityDB.getEntity(data['entity_id'])

        # Verify user has permission to delete
        if entity.sources.userGenerated.user_id != auth['authenticated_user_id'] \
            or entity.sources.userGenerated.user_id == None:
            raise Exception("Insufficient privilages to update entity")

        if self._entityDB.removeEntity(data['entity_id']):
            return True
        return False
    
    def searchEntities(self, data, auth):
        ### TODO: Customize query based on authenticated_user_id / coordinates
        
        entities = self._entityDB.searchEntities(data['q'], limit=10)

        result = []        
        for entity in entities:
            result.append(entity.exportAutosuggest())

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

    def _extractMentions(self, text):
        # Define patterns
        user_regex = re.compile(r'([^a-zA-Z0-9_])@([a-zA-Z0-9+_]{1,20})', re.IGNORECASE)
        reply_regex = re.compile(r'@([a-zA-Z0-9+_]{1,20})', re.IGNORECASE)
        
        mentions = [] 
        
        # Check if string match exists at beginning. Should combine with regex 
        # below once I figure out how :)
        reply = reply_regex.match(text)
        if reply:
            data = {}
            data['indices'] = [(reply.start()), reply.end()]
            data['screen_name'] = reply.group(0)[1:]
            try:
                user = self._userDB.getUserByScreenName(data['screen_name'])
                data['user_id'] = user.user_id
                data['display_name'] = user.display_name
            except:
                logs.warning("User not found (%s)" % data['screen_name'])
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
            except:
                logs.warning("User not found (%s)" % data['screen_name'])
            mentions.append(data)
        
        if len(mentions) > 0:
            return mentions
        return None
        # return mentions

    def addStamp(self, data, auth):
        user    = self._userDB.getUser(auth['authenticated_user_id'])
        entity  = self._entityDB.getEntity(data['entity_id'])

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
                ret.append(creditedUser.exportTiny())
            ### TODO: How do we handle credited users that have not yet joined?
            ### TODO: Expand with stamp details (potentially)
            credit = ret

        # Build stamp
        stamp = Stamp({
            'user': user.exportMini(),
            'entity': entity.exportSchema(EntityMini()),
            'blurb': blurb,
            'credit': credit,
            'image': image,
            'mentions': mentions,
        })
        print 'SUCCESS?????'
        stamp.setTimestampCreated()
            
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

                # Assign credit
                creditedStamp = self._stampDB.giveCredit(userId, stamp)
                
                # Add restamp as comment (if prior stamp exists)
                if creditedStamp.stamp_id != None:
                    # Build comment
                    comment = Comment({
                        'user': user.exportMini(),
                        'stamp_id': creditedStamp.stamp_id,
                        'restamp_id': stamp.stamp_id,
                        'blurb': blurb,
                        'mentions': mentions,
                    })
                    comment.setTimestampCreated()
                        
                    # Add the comment data to the database
                    self._commentDB.addComment(comment)

                    # Note: comment is added even if user is being blocked (for
                    # now). We should hide blocked users' comments from 
                    # appearing on view. But we'll come back to this
                    # regardless...

                # Update credited user stats
                self._userDB.updateUserStats(userId, 'num_credit', \
                    None, increment=1)

                ### TODO: Implement this
                # if user.user_id not in self._userDB.creditGivers(userId):
                #     self._userDB.addCreditGiver(userId, user.user_id)
                #     self._userDB.updateUserStats(userId, 'num_credit_givers', \
                #         None, increment=1)

                # Append user_id for activity
                creditedUserIds.append(creditedUser['user_id'])

        # Add activity for credited users
        ### TODO: Verify user isn't being blocked
        if self._activity == True and len(creditedUserIds) > 0:
            activity = Activity({
                'genre': 'restamp',
                'user': user.exportMini(),
                'stamp': stamp.value,
            })
            activity.setTimestampCreated()
            self._activityDB.addActivity(creditedUserIds, activity)
        
        # Add activity for mentioned users
        ### TODO: Verify user isn't being blocked
        if self._activity == True and mentions != None and len(mentions) > 0:
            mentionedUserIds = []
            for mention in mentions:
                if 'user_id' in mention \
                    and mention['user_id'] not in creditedUserIds:
                    mentionedUserIds.append(mention['user_id'])
            if len(mentionedUserIds) > 0:
                activity = Activity({
                    'genre': 'mention',
                    'user': user.exportMini(),
                    'stamp': stamp.value,
                })
                activity.setTimestampCreated()
                self._activityDB.addActivity(mentionedUserIds, activity)
        
        if self.output == 'http':
            return stamp.exportFlat()
        return stamp

            
    def updateStamp(self, data, auth):        
        stamp   = self._stampDB.getStamp(data['stamp_id'])

        blurb   = data.pop('blurb', stamp.blurb)
        credit  = data.pop('credit', None)
        image   = data.pop('image', stamp.image)

        # Extract mentions
        mentions = stamp.mentions
        if blurb != None:
            mentions = self._extractMentions(blurb)
                
        # Extract credit
        if credit != None:
            ret = []
            for creditedUser in self._userDB.lookupUsers(None, credit):
                ret.append(creditedUser.exportTiny())
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

        stamp.setTimestampModified()
            
        # Update the stamp data in the database
        stamp = self._stampDB.updateStamp(stamp)

        # Give credit
        creditedUserIds = []
        if len(creditedUsers) > 0:
            for creditedUser in creditedUsers:
                userId = creditedUser['user_id']

                # Assign credit
                creditedStamp = self._stampDB.giveCredit(userId, stamp)
                
                # Add restamp as comment (if prior stamp exists)
                if creditedStamp.stamp_id != None:
                    # Build comment
                    comment = Comment({
                        'user': user.exportMini(),
                        'stamp_id': creditedStamp.stamp_id,
                        'restamp_id': stamp.stamp_id,
                        'blurb': blurb,
                        'mentions': mentions,
                    })
                    comment.setTimestampCreated()
                        
                    # Add the comment data to the database
                    self._commentDB.addComment(comment)

                # Update credited user stats
                self._userDB.updateUserStats(userId, 'num_credit', \
                    None, increment=1)
                # if auth['authenticated_user_id'] not in self._userDB.creditGivers(userId):
                #     self._userDB.addCreditGiver(userId, user.user_id)
                #     self._userDB.updateUserStats(userId, 'num_credit_givers', \
                #         None, increment=1)

                # Append user_id for activity
                creditedUserIds.append(creditedUser['user_id'])

        # Add activity for credited users
        ### TODO: Verify user isn't being blocked
        if self._activity == True and len(creditedUserIds) > 0:
            activity = Activity({
                'genre': 'restamp',
                'user': user.exportMini(),
                'stamp': stamp.value,
            })
            activity.setTimestampCreated()
            self._activityDB.addActivity(creditedUserIds, activity)
        
        # Add activity for mentioned users
        ### TODO: Verify user isn't being blocked
        if self._activity == True and mentions != None and len(mentions) > 0:
            mentionedUserIds = []
            for mention in mentions:
                if 'user_id' in mention \
                    and mention['user_id'] not in creditedUserIds:
                    mentionedUserIds.append(mention['user_id'])
            if len(mentionedUserIds) > 0:
                activity = Activity({
                    'genre': 'mention',
                    'user': user.exportMini(),
                    'stamp': stamp.value,
                })
                activity.setTimestampCreated()
                self._activityDB.addActivity(mentionedUserIds, activity)

        if self.output == 'http':
            return stamp.exportFlat()
        return stamp
    
    def removeStamp(self, data, auth):
        stamp = self._stampDB.getStamp(data['stamp_id'])

        # Verify user has permission to delete
        if stamp.getOwnerId() != auth['authenticated_user_id']:
            raise Exception("Insufficient privilages to remove Stamp")

        # Remove stamp
        self._stampDB.removeStamp(stamp.stamp_id)

        # Remove from user collection
        self._stampDB.removeUserStampReference(auth['authenticated_user_id'], \
                                                stamp.stamp_id)
        
        # Remove from followers' inbox collections
        followers = self._friendshipDB.getFollowers( \
            auth['authenticated_user_id'])
        followers.append(auth['authenticated_user_id'])
        # Note: this only removes the stamp from people who follow the user.
        # If we allow for an "opt in" method of users adding individual
        # stamps to their inbox, we'll have to account for that here.
        self._stampDB.removeInboxStampReference(followers, stamp.stamp_id)

        ### TODO: If restamp, remove from credited stamps' comment list

        ### TODO: Remove from activity? To do? Anything else?

        return True
        
    def getStamp(self, data, auth):
        stamp = self._stampDB.getStamp(data['stamp_id'])

        # Check privacy of stamp
        if stamp.getStampPrivacy() == True:
            friendship = Friendship({
                'user_id':      stamp.getOwnerId(),
                'friend_id':    auth['authenticated_user_id'],
            })

            if not self._friendshipDB.checkFriendship(friendship):
                raise Exception("Insufficient privilages to view Stamp")
      
        if self.output == 'http':
            return stamp.exportFlat()
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

    def addComment(self, data, auth):
        user    = self._userDB.getUser(auth['authenticated_user_id'])
        stamp   = self._stampDB.getStamp(data['stamp_id'])

        # Verify user has the ability to comment on the stamp
        
        # Check if stamp is private; if so, must be a follower
        if stamp.getStampPrivacy() == True:
            friendship = Friendship({
                'user_id':      stamp.getOwnerId(),
                'friend_id':    user.user_id,
            })

            if not self._friendshipDB.checkFriendship(friendship):
                raise Exception("Insufficient privilages to add Comment")

        # Check if user is blocked by stamp owner
        ### TODO: Unit test this reverse friendship notion
        reverseFriendship= Friendship({
            'user_id':      user.user_id,
            'friend_id':    stamp.getOwnerId(),
        })
        if self._friendshipDB.checkBlock(reverseFriendship) == True:
            logs.info("Block exists")
            raise Exception

        blurb   = data.pop('blurb', None)

        # Extract mentions
        mentions = None
        if blurb != None:
            mentions = self._extractMentions(blurb)

        # Build comment
        comment = Comment({
            'user': user.exportMini(),
            'stamp_id': stamp.stamp_id,
            'blurb': blurb,
            'mentions': mentions,
        })
        comment.setTimestampCreated()
            
        # Add the comment data to the database
        comment = self._commentDB.addComment(comment)

        # Add activity for mentioned users
        ### TODO: Verify user isn't being blocked
        mentionedUserIds = []
        if self._activity == True and mentions != None and len(mentions) > 0:
            for mention in mentions:
                if 'user_id' in mention:
                    mentionedUserIds.append(mention['user_id'])
            if len(mentionedUserIds) > 0:
                activity = Activity({
                    'genre': 'mention',
                    'user': user.exportMini(),
                    'stamp': stamp.value,
                    'comment': comment.value,
                })
                activity.setTimestampCreated()
                self._activityDB.addActivity(mentionedUserIds, activity)
        
        # Add activity for commentor and for stamp owner
        ### TODO: Verify user isn't being blocked
        commentedUserIds = []
        if user.user_id not in mentionedUserIds:
            commentedUserIds.append(user.user_id)
        if stamp.user.user_id not in mentionedUserIds \
            and stamp.user.user_id not in commentedUserIds:
            commentedUserIds.append(stamp.user.user_id)
        if len(commentedUserIds) > 0:
            activity = Activity({
                'genre': 'comment',
                'user': user.exportMini(),
                'stamp': stamp.value,
                'comment': comment.value,
            })
            activity.setTimestampCreated()
            self._activityDB.addActivity(commentedUserIds, activity)
        
        # Add activity for previous commenters
        ### TODO: Verify user isn't being blocked
        ### TODO: Limit this to the last 20 comments or so
        repliedUsersDict = {}
        for prevComment in self._commentDB.getComments(stamp.stamp_id):
            repliedUserId = prevComment['user']['user_id']
            if repliedUserId not in commentedUserIds \
                and repliedUserId not in mentionedUserIds:
                repliedUsersDict[prevComment['user']['user_id']] = 1 
        repliedUserIds = repliedUsersDict.keys()
        if len(repliedUserIds) > 0:
            activity = Activity({
                'genre': 'reply',
                'user': user.exportMini(),
                'stamp': stamp.value,
                'comment': comment.value,
            })
            activity.setTimestampCreated()
            self._activityDB.addActivity(repliedUserIds, activity)
        
        # Increment comment count on stamp
        self._stampDB.incrementStatsForStamp(stamp.stamp_id, 'num_comments', 1)

        if self.output == 'http':
            return comment.exportFlat()
        return comment
    
    def removeComment(self, data, auth):
        comment = self._commentDB.getComment(data['comment_id'])

        # Only comment owner and stamp owner can delete comment
        if comment.user.user_id != auth['authenticated_user_id']:
            stamp = self._stampDB.getStamp(comment.stamp_id)
            if stamp.user.user_id != auth['authenticated_user_id']:
                raise Exception("Insufficient privilages to remove Comment")

        # Don't allow user to delete comment for restamp notification
        if comment.restamp_id != None:
            raise Exception("Cannot remove 'Stamp' comment")

        # Remove comment
        self._commentDB.removeComment(comment.comment_id)

        ### TODO: Remove activity?

        # Increment comment count on stamp
        self._stampDB.incrementStatsForStamp(comment.stamp_id, 'num_comments', -1)

        return True
    
    def getComments(self, data, auth): 
        stamp = self._stampDB.getStamp(data['stamp_id'])

        ### TODO: Add slicing (before, since, limit, quality)

        # Check privacy of stamp
        if stamp.getStampPrivacy() == True:
            friendship = Friendship({
                'user_id':      stamp.getOwnerId(),
                'friend_id':    auth['authenticated_user_id'],
            })

            if not self._friendshipDB.checkFriendship(friendship):
                raise Exception("Insufficient privilages to view Stamp")
              
        comments = self._commentDB.getComments(stamp.stamp_id)
            
        if self.output == 'http':
            result = []
            for comment in comments:
                result.append(comment.exportFlat())
            return result
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
    
    def _getStampCollection(self, stampIds, data, includeComments=False):
        quality     = data.pop('quality', 3)
        limit       = data.pop('limit', None)
                       
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
        since, before = self._setSliceParams(data)

        params = {
            'since':    since,
            'before':   before, 
            'limit':    limit,
        }

        stamps = self._stampDB.getStamps(stampIds, **params)

        result = []

        if includeComments == True:
            comments = self._commentDB.getCommentsAcrossStamps(stampIds, commentCap)

            ### TODO: Find a more efficient way to run this
            for stamp in stamps:
                if self.output == 'http':
                    stamp = stamp.exportFlat()

                stamp['comment_preview'] = []
                for comment in comments:
                    if comment.stamp_id == stamp['stamp_id']:
                        if self.output == 'http':
                            comment = comment.exportFlat()
                        stamp['comment_preview'].append(comment)
                result.append(stamp)
        else:
            for stamp in stamps:
                if self.output == 'http':
                    stamp = stamp.exportFlat()
                result.append(stamp)
        
        return result
    
    def getInboxStamps(self, data, auth):
        
        stampIds = self._collectionDB.getInboxStampIds(auth['authenticated_user_id'])

        return self._getStampCollection(stampIds, data, includeComments=True)
    
    def getUserStamps(self, data, auth):
        user = self._getUserFromIdOrScreenName(data)

        # Check privacy
        if user.privacy == True:
            authenticated_user_id = data.pop('authenticated_user_id', None)
            if authenticated_user_id == None:
                raise Exception("You must be logged in to view this account")

            friendship = Friendship({
                'user_id':      auth['authenticated_user_id'],
                'friend_id':    user['user_id']
            })

            if not self._friendshipDB.checkFriendship(friendship):
                raise Exception("You do not have permission to view this user")
        
        stampIds = self._collectionDB.getUserStampIds(user.user_id)

        return self._getStampCollection(stampIds, data, includeComments=True)
    
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
    
    def getActivity(self, data, auth):
        quality     = data.pop('quality', 3)
        limit       = data.pop('limit', None)
                       
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
        since, before = self._setSliceParams(data)

        params = {
            'since':    since,
            'before':   before, 
            'limit':    limit,
        }
        
        activity = self._activityDB.getActivity(auth['authenticated_user_id'], \
                                                **params)
        
        if self.output == 'http':
            result = []
            for item in activity:
                result.append(item.exportFlat())
            return result
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
    

    """
    #######                                                         
    #        ####  #####  #    #   ##   ##### ##### # #    #  ####  
    #       #    # #    # ##  ##  #  #    #     #   # ##   # #    # 
    #####   #    # #    # # ## # #    #   #     #   # # #  # #      
    #       #    # #####  #    # ######   #     #   # #  # # #  ### 
    #       #    # #   #  #    # #    #   #     #   # #   ## #    # 
    #        ####  #    # #    # #    #   #     #   # #    #  ####  
    
    
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

"""