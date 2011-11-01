#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils
import logs, re, time, Blacklist, auth

from datetime        import datetime
from errors          import *
from auth            import convertPasswordForStorage
from utils           import lazyProperty
from functools       import wraps

from AStampedAPI     import AStampedAPI
from AAccountDB      import AAccountDB
from AEntityDB       import AEntityDB
from APlacesEntityDB import APlacesEntityDB
from AUserDB         import AUserDB
from AStampDB        import AStampDB
from ACommentDB      import ACommentDB
from AFavoriteDB     import AFavoriteDB
from ACollectionDB   import ACollectionDB
from AFriendshipDB   import AFriendshipDB
from AActivityDB     import AActivityDB

from Schemas         import *

# third-party search API wrappers
from GooglePlaces    import GooglePlaces
from libs.apple      import AppleAPI
from libs.AmazonAPI  import AmazonAPI
from libs.TheTVDB    import TheTVDB

CREDIT_BENEFIT  = 2 # Per credit
LIKE_BENEFIT    = 1 # Per 3 stamps

class StampedAPI(AStampedAPI):
    """
        Database-agnostic implementation of the internal API for accessing 
        and manipulating all Stamped backend databases.
    """
    
    def __init__(self, desc, **kwargs):
        AStampedAPI.__init__(self, desc)
        
        # Enable / Disable Functionality
        self._activity = True
        self._rollback = []
        
        if utils.is_ec2():
            try:
                stack_info = self._statsSink.get_stack_info()
                self.node_name = stack_info.instance.name
            except:
                self.node_name = "unknown"
        else:
            self.node_name = "localhost"
    
    def API_CALL(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # time every API call
            t1 = time.time()
            error = False
            
            try:
                ret = f(*args, **kwargs)
            except Exception, e:
                error = True
                raise
            finally:
                t2 = time.time()
                
                stat_prefix = 'stamped.api.methods.%s' % f.func_name
                self = args[0]
                
                duration = (t2 - t1) * 1000.0
                self._statsSink.time('%s.time' % stat_prefix, duration)
                
                stats = [
                    'stamped.api.servers.%s' % self.node_name, 
                    'stamped.api.methods.count', 
                    '%s.count' % stat_prefix, 
                ]
                
                if error:
                    stats.append('%s.errors' % stat_prefix)
                
                self._statsSink.increment(stats)
            
            return ret
        return wrapper
    
    def HandleRollback(f):
        @wraps(f)
        def rollbackWrapper(*args, **kwargs):
            s = args[0]
            s._rollback = []
            try:
                return f(*args, **kwargs)
            except:
                rollback = s._rollback
                rollback.reverse()
                for fn, params in rollback:
                    logs.info('Rollback: %s(%s)' % (fn.__name__, params))
                    if isinstance(params, dict):
                        fn(**params)
                    else:
                        fn(*params)
                raise
        return rollbackWrapper
    
    """
       #                                                    
      # #    ####   ####   ####  #    # #    # #####  ####  
     #   #  #    # #    # #    # #    # ##   #   #   #      
    #     # #      #      #    # #    # # #  #   #    ####  
    ####### #      #      #    # #    # #  # #   #        # 
    #     # #    # #    # #    # #    # #   ##   #   #    # 
    #     #  ####   ####   ####   ####  #    #   #    ####  
    """
    
    @API_CALL
    @HandleRollback
    def addAccount(self, account, imageData=None):
        ### TODO: Check if email already exists?
        
        account.timestamp.created = datetime.utcnow()
        account.password = convertPasswordForStorage(account['password'])
        
        # Set initial stamp limit
        account.stats.num_stamps_left = 100
        account.stats.num_stamps_total = 0
        
        # Set default stamp colors
        account.color_primary   = '004AB2'
        account.color_secondary = '0057D1'

        # Set default alerts
        account.ios_alert_credit       = False
        account.ios_alert_like         = False
        account.ios_alert_fav          = False
        account.ios_alert_mention      = False
        account.ios_alert_comment      = False
        account.ios_alert_reply        = False
        account.ios_alert_follow       = False
        account.email_alert_credit     = True
        account.email_alert_like       = False
        account.email_alert_fav        = False
        account.email_alert_mention    = True
        account.email_alert_comment    = True
        account.email_alert_reply      = True
        account.email_alert_follow     = True
        
        # Validate Screen Name
        account.screen_name = account.screen_name.strip()
        if not utils.validate_screen_name(account.screen_name):
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

        # Add image timestamp if exists
        if imageData:
            account.image_cache = datetime.utcnow()
        
        # Create account
        account = self._accountDB.addAccount(account)
        self._rollback.append((self._accountDB.removeAccount, [account.user_id]))
        
        # Add stats
        self._statsSink.increment('stamped.api.new_accounts')
        
        # Add profile image
        if imageData:
            image   = self._imageDB.getImage(imageData)
            ### TODO: Rollback: Delete image
            self._imageDB.addProfileImage(account.screen_name.lower(), image)
        
        # Add activity if invitations were sent
        invites = self._inviteDB.getInvitations(account.email)
        invitedBy = {}
        for invite in invites:
            invitedBy[invite['user_id']] = 1
            
            activity                = Activity()
            ### TODO: What genre are we picking for this activity item?
            activity.genre              = 'invite_sent'
            activity.user.user_id       = invite['user_id']
            activity.linked_user_id     = invite['user_id']
            activity.timestamp.created  = datetime.utcnow()
            
            self._activityDB.addActivity([account.user_id], activity)
        
        if len(invitedBy) > 0:
            activity                = Activity()
            ### TODO: What genre are we picking for this activity item?
            activity.genre              = 'invite_received'
            activity.user.user_id       = account.user_id
            activity.linked_user_id     = account.user_id
            activity.timestamp.created  = datetime.utcnow()
            
            self._activityDB.addActivity(invitedBy.keys(), activity)
        
        self._inviteDB.join(account.email)

        return account
    
    @API_CALL
    def removeAccount(self, authUserId):
        account = self._accountDB.getAccount(authUserId)
        
        ### TODO: Verify w/ password

        stampIds    = self._collectionDB.getUserStampIds(account.user_id)
        friendIds   = self._friendshipDB.getFriends(account.user_id)
        followerIds = self._friendshipDB.getFollowers(account.user_id)

        # Remove friends / followers
        for followerId in followerIds:
            friendship              = Friendship()
            friendship.user_id      = followerId
            friendship.friend_id    = account.user_id
            
            self._friendshipDB.removeFriendship(friendship)
            
            # Increment stats 
            self._userDB.updateUserStats(followerId, 'num_friends', \
                        None, increment=-1)
            
            # Remove stamps from Inbox
            self._stampDB.removeInboxStampReferencesForUser(followerId, stampIds)

        for friendId in friendIds:
            friendship              = Friendship()
            friendship.user_id      = account.user_id
            friendship.friend_id    = friendId
            
            self._friendshipDB.removeFriendship(friendship)
            
            # Increment stats 
            self._userDB.updateUserStats(friendId, 'num_followers', \
                        None, increment=-1)

        # Remove favorites
        favEntityIds = self._favoriteDB.getFavoriteEntityIds(account.user_id)
        for entityId in favEntityIds:
            self._favoriteDB.removeFavorite(account.user_id, entityId)

        # Remove stamps / collections
        stamps = self._stampDB.getStamps(stampIds, limit=len(stampIds))
        for stamp in stamps:
            if len(stamp.credit) > 0:
                for creditedUser in stamp.credit:
                    self._stampDB.removeCredit(creditedUser['user_id'], stamp)

                    # Decrement user stats by one
                    self._userDB.updateUserStats( \
                        creditedUser['user_id'], 'num_credits', increment=-1)

            # Remove activity on stamp
            self._activityDB.removeActivityForStamp(stamp.stamp_id)

        self._stampDB.removeStamps(stampIds)
        self._stampDB.removeAllUserStampReferences(account.user_id)
        self._stampDB.removeAllInboxStampReferences(account.user_id)
        ### TODO: If restamp, remove from credited stamps' comment list?
        
        # Remove comments
        comments = self._commentDB.getUserCommentIds(account.user_id)
        for comment in comments:
            # Remove comment
            self._commentDB.removeComment(comment.comment_id)

            # Decrement comment count on stamp
            if comment.stamp_id not in stampIds:
                logs.info('STAMP ID: %s' % comment.stamp_id)
                self._stampDB.updateStampStats( \
                    comment.stamp_id, 'num_comments', increment=-1)

        # Remove likes
        likedStampIds = self._stampDB.getUserLikes(account.user_id)
        likedStamps = self._stampDB.getStamps(likedStampIds, \
            limit=len(likedStampIds))
        for stamp in likedStamps:
            self._stampDB.removeLike(account.user_id, stamp.stamp_id)

            # Decrement user stats by one
            self._userDB.updateUserStats( \
                stamp.user_id, 'num_likes', increment=-1)

            # Decrement stamp stats by one
            self._stampDB.updateStampStats( \
                stamp.stamp_id, 'num_likes', increment=-1)

        # Remove activity items
        self._activityDB.removeUserActivity(account.user_id)

        # Remove custom entities
        ### TODO: Do this?

        # Remove profile image
        self._imageDB.removeProfileImage(account.screen_name.lower())
        
        # Remove account
        self._accountDB.removeAccount(account.user_id)
        
        # Remove email address from invite list
        self._inviteDB.remove(account.email)
        
        return account
    
    @API_CALL
    def updateAccountSettings(self, authUserId, data):
        
        ### TODO: Reexamine how updates are done
        ### TODO: Verify that email address is unique, confirm it
        
        account = self._accountDB.getAccount(authUserId)

        old_screen_name = account['screen_name']
        
        # Import each item
        for k, v in data.iteritems():
            if k == 'password':
                v = convertPasswordForStorage(v)
            account[k] = v
        
        # Validate Screen Name
        account.screen_name = account.screen_name.strip()
        if not utils.validate_screen_name(account.screen_name):
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

        # Update profile picture link if screen name has changed
        if account.screen_name.lower() != old_screen_name.lower():
            self._imageDB.changeProfileImageName(old_screen_name.lower(), \
                                                 account.screen_name.lower())

        return account
    
    @API_CALL
    def getAccount(self, authUserId):
        account = self._accountDB.getAccount(authUserId)
        return account
    
    @API_CALL
    def updateProfile(self, authUserId, data):
        
        ### TODO: Reexamine how updates are done

        account = self._accountDB.getAccount(authUserId)

        # Import each item
        for k, v in data.iteritems():
            account[k] = v

        self._accountDB.updateAccount(account)

        return account
    
    @API_CALL
    def customizeStamp(self, authUserId, data):
        ### TODO: Reexamine how updates are done

        primary = data['color_primary'].upper()
        secondary = data['color_secondary'].upper()

        # Validate inputs
        if not utils.validate_hex_color(primary) or \
            not utils.validate_hex_color(secondary):
            msg = "Invalid format for colors"
            logs.warning(msg)
            raise InputError(msg)

        account = self._accountDB.getAccount(authUserId)

        # Import each item
        account.color_primary   = primary
        account.color_secondary = secondary

        self._accountDB.updateAccount(account)

        # Generate file
        self._imageDB.generateStamp(primary, secondary)

        return account
    
    @API_CALL
    def updateProfileImage(self, authUserId, data):
        image   = self._imageDB.getImage(data)
        user    = self._userDB.getUser(authUserId)
        self._imageDB.addProfileImage(user.screen_name.lower(), image)

        image_cache = datetime.utcnow()
        user.image_cache = image_cache
        self._accountDB.updateUserTimestamp(authUserId, 'image_cache', \
            image_cache)
        
        return user
    
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
    
    @API_CALL
    def updateLinkedAccounts(self, authUserId, linkedAccounts):
        self._accountDB.updateLinkedAccounts(authUserId, linkedAccounts)
        
        return True

    @API_CALL
    def updatePassword(self, authUserId, password):
        password = convertPasswordForStorage(password)
        
        self._accountDB.updatePassword(authUserId, password)

        account = self._accountDB.getAccount(authUserId)

        return True

    @API_CALL
    def updateAlerts(self, authUserId, alerts):
        if isinstance(alerts, SchemaElement):
            alerts = alerts.value

        account = self._accountDB.getAccount(authUserId)

        for k, v in alerts.iteritems():
            if v:
                account['alerts'][k] = True
            else:
                account['alerts'][k] = False

        self._accountDB.updateAccount(account)

        return account

    @API_CALL
    def updateAPNSToken(self, authUserId, token):
        self._accountDB.updateAPNSToken(authUserId, token)

        ### TEMP: Update alert settings with first token
        account = self._accountDB.getAccount(authUserId)
        if not account.ios_alert_credit \
            and not account.ios_alert_like \
            and not account.ios_alert_fav \
            and not account.ios_alert_mention \
            and not account.ios_alert_comment \
            and not account.ios_alert_reply \
            and not account.ios_alert_follow:

            account.ios_alert_credit       = True
            account.ios_alert_like         = True
            account.ios_alert_fav          = True
            account.ios_alert_mention      = True
            account.ios_alert_comment      = True
            account.ios_alert_reply        = True
            account.ios_alert_follow       = True

            self._accountDB.updateAccount(account)

        return True

    @API_CALL
    def removeAPNSToken(self, authUserId, token):
        self._accountDB.removeAPNSToken(authUserId, token)
        return True
    
    @API_CALL
    def resetPassword(self, email):
        email = str(email).lower().strip()
        if not utils.validate_email(email):
            msg = "Invalid format for email address"
            logs.warning(msg)
            raise InputError(msg)

        # Verify user exists
        account = self._accountDB.getAccountByEmail(email)
        if not account or not account.user_id:
            msg = "User does not exist"
            logs.warning(msg)
            raise InputError(msg)

        # Generate random password
        new_password = auth.generateToken(10)

        # Convert and store new password
        password = convertPasswordForStorage(new_password)
        self._accountDB.updatePassword(account.user_id, password)

        # Remove refresh / access tokens
        self._refreshTokenDB.removeRefreshTokensForUser(account.user_id)
        self._accessTokenDB.removeAccessTokensForUser(account.user_id)

        # Email user
        msg = {}
        msg['to'] = email
        msg['from'] = 'Stamped <noreply@stamped.com>'
        msg['subject'] = 'Stamped: Reset Password'
        ### TODO: Update this copy?
        msg['body'] = 'Your new password is: %s \n\n'% (new_password) + \
            'To change your password, log in to Stamped and go to ' + \
            'Profile > Settings > Change Password.' 

        utils.sendEmail(msg, format='text')

        return True
    
    
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
    
    @API_CALL
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
    
    @API_CALL
    def getUsers(self, userIds, screenNames, authUserId):

        ### TODO: Add check for privacy settings

        users = self._userDB.lookupUsers(userIds, screenNames, limit=100)

        return users
    
    @API_CALL
    def findUsersByEmail(self, authUserId, emails):
        
        ### TODO: Add check for privacy settings?
        
        users = self._userDB.findUsersByEmail(emails, limit=100)
        
        return users
    
    @API_CALL
    def findUsersByPhone(self, authUserId, phone):
        
        ### TODO: Add check for privacy settings?
        
        users = self._userDB.findUsersByPhone(phone, limit=100)
        
        return users
    
    @API_CALL
    def findUsersByTwitter(self, authUserId, twitterIds):

        ### TODO: Add check for privacy settings?

        users = self._userDB.findUsersByTwitter(twitterIds, limit=100)
        
        return users
    
    @API_CALL
    def findUsersByFacebook(self, authUserId, facebookIds):

        ### TODO: Add check for privacy settings?

        users = self._userDB.findUsersByFacebook(facebookIds, limit=100)
        
        return users
    
    @API_CALL
    def searchUsers(self, query, limit, authUserId):

        limit = self._setLimit(limit, cap=10)

        ### TODO: Add check for privacy settings
        
        users = self._userDB.searchUsers(query, limit)

        return users
    
    @API_CALL
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
    
    @API_CALL
    def addFriendship(self, authUserId, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)
        
        friendship = Friendship({
            'user_id':      authUserId,
            'friend_id':    user.user_id
        })
        
        # Verify that you're not following yourself :)
        if user.user_id == authUserId:
            logs.warning("You can't follow yourself!")
            raise IllegalActionError("Illegal friendship")
        
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
            activity                    = Activity()
            activity.genre              = 'follower'
            activity.user.user_id       = authUserId
            activity.linked_user_id     = authUserId
            # activity.linked_friend_id   = user.user_id
            activity.timestamp.created  = datetime.utcnow()
            
            self._activityDB.addActivity([user.user_id], activity)
        
        # Add stamps to Inbox
        stampIds = self._collectionDB.getUserStampIds(user.user_id)
        self._stampDB.addInboxStampReferencesForUser(authUserId, stampIds)
        
        # Increment stats for both users
        self._userDB.updateUserStats(authUserId, 'num_friends', \
                    None, increment=1)
        self._userDB.updateUserStats(user.user_id, 'num_followers', \
                    None, increment=1)
        
        # Increment stats
        self._statsSink.increment('stamped.api.friendships')
        
        return user
    
    @API_CALL
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

        # Remove activity
        ### TODO: Don't remove this?
        self._activityDB.removeActivity(genre='follower', userId=authUserId, \
                                        recipientId=user['user_id'])
        
        return user
    
    @API_CALL
    def approveFriendship(self, data, auth):
        raise NotImplementedError
    
    @API_CALL
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
        
        return self._friendshipDB.checkFriendship(friendship)
    
    @API_CALL
    def getFriends(self, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)

        # Note: This function returns data even if user is private

        friends = self._friendshipDB.getFriends(user['user_id'])

        return friends
    
    @API_CALL
    def getFollowers(self, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)

        # Note: This function returns data even if user is private

        followers = self._friendshipDB.getFollowers(user['user_id'])

        return followers
    
    @API_CALL
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
    
    @API_CALL
    def checkBlock(self, authUserId, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)
        
        friendship = Friendship({
            'user_id':      authUserId,
            'friend_id':    user['user_id']
        })

        if self._friendshipDB.checkBlock(friendship):
            return True
        return False
    
    @API_CALL
    def getBlocks(self, authUserId):
        blocks = self._friendshipDB.getBlocks(authUserId)

        return blocks
    
    @API_CALL
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
    
    @API_CALL
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

    def _getEntityFromRequest(self, entityRequest):
        if isinstance(entityRequest, SchemaElement):
            entityRequest = entityRequest.value
        entityId    = entityRequest.pop('entity_id', None)
        searchId    = entityRequest.pop('search_id', None)
        
        if entityId is None and searchId is None:
            msg = "Required field missing (entity_id or search_id)"
            logs.warning(msg)
            raise InputError(msg)
        
        if searchId is not None and searchId.startswith('T_'):
            entityId = self._convertSearchId(searchId)
        
        if not entityId:
            entityId = searchId
        
        return self._getEntity(entityId)
    
    def _getEntity(self, entityId):
        if entityId is not None and entityId.startswith('T_'):
            entityId = self._convertSearchId(entityId)
        
        return self._entityDB.getEntity(entityId)
    
    @API_CALL
    def addEntity(self, entity):
        entity.timestamp.created = datetime.utcnow()
        entity = self._entityDB.addEntity(entity)
        return entity
    
    def getEntity(self, entityRequest, authUserId=None):
        entity = self._getEntityFromRequest(entityRequest)
        
        ### TODO: Check if user has access to this entity?
        return entity
    
    @API_CALL
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

    @API_CALL
    def updateEntity(self, data, auth):
        entity = self._entityDB.getEntity(data['entity_id'])
        
        # Try to import as a full entity
        for k, v in data.iteritems():
            entity[k] = v
        
        entity.timestamp.modified = datetime.utcnow()
        self._entityDB.updateEntity(entity)
        
        return entity
    
    @API_CALL
    def removeEntity(self, entityId):
        return self._entityDB.removeEntity(entityId)
    
    @API_CALL
    def removeCustomEntity(self, authUserId, entityId):
        entity = self._entityDB.getEntity(entityId)

        self._entityDB.removeCustomEntity(entityId, authUserId)

        return entity
    
    @API_CALL
    def searchEntities(self, 
                       query, 
                       coords=None, 
                       authUserId=None, 
                       category_filter=None, 
                       subcategory_filter=None, 
                       limit=10, 
                       prefix=False, 
                       local=False, 
                       full=True):
        results = self._entitySearcher.getSearchResults(query=query, 
                                                        coords=coords, 
                                                        limit=limit, 
                                                        category_filter=category_filter, 
                                                        subcategory_filter=subcategory_filter, 
                                                        full=full, 
                                                        prefix=prefix, 
                                                        local=local, 
                                                        user=authUserId)
        return results
    
    @API_CALL
    def searchNearby(self, 
                     coords=None, 
                     authUserId=None, 
                     category_filter=None, 
                     subcategory_filter=None, 
                     limit=10, 
                     prefix=False, 
                     full=True):
        results = self._entitySearcher.getSearchResults(query='', 
                                                        coords=coords, 
                                                        limit=limit, 
                                                        category_filter=category_filter, 
                                                        subcategory_filter=subcategory_filter, 
                                                        full=full, 
                                                        prefix=prefix, 
                                                        local=True, 
                                                        user=authUserId)
        return results
    
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
            ### TODO: Check that userIds != 1 (i.e. user still exists)?
            stamp.user = userIds[stamp.user_id]
            
            # Add entity
            if entityIds[stamp.entity_id] == 1:
                msg = 'Unable to match entity_id %s for stamp_id %s' % \
                    (stamp.entity_id, stamp.stamp_id)
                logs.warning(msg)
                ### TODO: Raise?
            else:
                stamp.entity = entityIds[stamp.entity_id]

            # Add credited user(s)
            if stamp.credit != None:
                for i in xrange(len(stamp.credit)):
                    creditedUser = userIds[stamp.credit[i].user_id]
                    stamp.credit[i].screen_name = creditedUser['screen_name']
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

    @API_CALL
    @HandleRollback
    def addStamp(self, authUserId, entityRequest, data):
        # notes: 
            # 1) checking stamp db
            # 2) call to _enrichStampObjects
            # 3) _stampDB.addStamp itself
        
        t0 = time.time()
        
        user        = self._userDB.getUser(authUserId)
        
        t1 = time.time(); duration = (t1 - t0) * 1000.0; t0 = t1
        self._statsSink.time('stamped.api.methods.addStamp.-2', duration)
        
        entity      = self._getEntityFromRequest(entityRequest)
        
        t1 = time.time(); duration = (t1 - t0) * 1000.0; t0 = t1
        self._statsSink.time('stamped.api.methods.addStamp.-1', duration)
        
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
            msg = "Cannot stamp same entity twice (id = %s)" % entity.entity_id
            logs.warning(msg)
            raise IllegalActionError(msg)
        
        t1 = time.time(); duration = (t1 - t0) * 1000.0; t0 = t1
        self._statsSink.time('stamped.api.methods.addStamp.0', duration)
        
        # Build stamp
        stamp                       = Stamp()
        stamp.user_id               = user.user_id
        stamp.entity_id             = entity.entity_id
        stamp.timestamp.created     = datetime.utcnow()
        stamp.timestamp.modified    = datetime.utcnow()
        stamp.stamp_num             = user.num_stamps_total + 1
        
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
                creditedStamp = self._stampDB.getStampFromUserEntity(userId, \
                    entity.entity_id)
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
        
        # Add stats
        self._statsSink.increment('stamped.api.stamps.category.%s' % entity.category)
        self._statsSink.increment('stamped.api.stamps.subcategory.%s' % entity.subcategory)
        
        # Add the stamp data to the database
        stamp = self._stampDB.addStamp(stamp)
        ### TODO: Rollback adds stamp to "deleted stamps" table. Fix that.
        self._rollback.append((self._stampDB.removeStamp, {'stampId': stamp.stamp_id}))
        
        t1 = time.time(); duration = (t1 - t0) * 1000.0; t0 = t1
        self._statsSink.time('stamped.api.methods.addStamp.1', duration)
        
        # Add image to stamp
        ### TODO: Unwind stamp if this fails
        if imageData != None:
            
            ### TODO: Rollback: Delete Image
            image = self._imageDB.getImage(imageData)
            self._imageDB.addStampImage(stamp.stamp_id, image)
            
            # Add image dimensions to stamp object (width,height)
            width, height           = image.size
            stamp.image_dimensions  = "%s,%s" % (width, height)
            stamp                   = self._stampDB.updateStamp(stamp)
            
            self._statsSink.increment('stamped.api.stamps.images')
        
        t1 = time.time(); duration = (t1 - t0) * 1000.0; t0 = t1
        self._statsSink.time('stamped.api.methods.addStamp.2', duration)
        
        # Add user objects back into stamp
        entityIds = {entity.entity_id: entity.exportSchema(EntityMini())}
        stamp = self._enrichStampObjects(stamp, authUserId=authUserId, \
            userIds=userIds, entityIds=entityIds)
        
        t1 = time.time(); duration = (t1 - t0) * 1000.0; t0 = t1
        self._statsSink.time('stamped.api.methods.addStamp.3', duration)
        
        # Add a reference to the stamp in the user's collection
        self._rollback.append((self._stampDB.removeUserStampReference, \
            {'stampId': stamp.stamp_id, 'userId': user.user_id}))
        self._stampDB.addUserStampReference(user.user_id, stamp.stamp_id)
        
        t2 = time.time(); duration = (t1 - t0) * 1000.0; t0 = t1
        self._statsSink.time('stamped.api.methods.addStamp.4', duration)
        
        # Add a reference to the stamp in followers' inbox
        followers = self._friendshipDB.getFollowers(user.user_id)
        followers.append(user.user_id)
        self._rollback.append((self._stampDB.removeInboxStampReference, \
            {'stampId': stamp.stamp_id, 'userIds': followers}))
        self._stampDB.addInboxStampReference(followers, stamp.stamp_id)
        
        t2 = time.time(); duration = (t1 - t0) * 1000.0; t0 = t1
        self._statsSink.time('stamped.api.methods.addStamp.5', duration)
        
        # Update user stats 
        ### TODO: Should rollback go before or after?
        self._userDB.updateUserStats(authUserId, 'num_stamps', \
                    None, increment=1)
        self._rollback.append((self._userDB.updateUserStats, \
            {'userId': authUserId, 'stat': 'num_stamps', 'increment': -1}))

        self._userDB.updateUserStats(authUserId, 'num_stamps_left', \
                    None, increment=-1)
        self._rollback.append((self._userDB.updateUserStats, \
            {'userId': authUserId, 'stat': 'num_stamps_left', 'increment': 1}))
        
        self._userDB.updateUserStats(authUserId, 'num_stamps_total', \
                    None, increment=1)
        self._rollback.append((self._userDB.updateUserStats, \
            {'userId': authUserId, 'stat': 'num_stamps_total', 'increment': -1}))
        
        t2 = time.time(); duration = (t1 - t0) * 1000.0; t0 = t1
        self._statsSink.time('stamped.api.methods.addStamp.6', duration)
        
        # If stamped entity is on the to do list, mark as complete
        try:
            self._favoriteDB.completeFavorite(entity.entity_id, user.user_id)
            self._rollback.append((self._favoriteDB.completeFavorite, \
                {'entityId': entity.entity_id, 'userId': user.user_id, \
                'complete': False}))
        except:
            pass
        
        # Give credit
        if stamp.credit != None and len(stamp.credit) > 0:
            for item in credit:
                
                # Only run if user is flagged as credited
                if item.user_id not in creditedUserIds:
                    continue
                
                # Assign credit
                self._rollback.append((self._stampDB.removeCredit, \
                    {'creditedUserId': item.user_id, 'stamp': stamp}))
                self._stampDB.giveCredit(item.user_id, stamp)
                
                # # Add restamp as comment (if prior stamp exists)
                # if 'stamp_id' in item and item['stamp_id'] != None:
                #     # Build comment
                #     comment                     = Comment()
                #     comment.user.user_id        = user.user_id
                #     comment.stamp_id            = item.stamp_id
                #     comment.restamp_id          = stamp.stamp_id
                #     comment.blurb               = stamp.blurb
                #     comment.mentions            = stamp.mentions
                #     comment.timestamp.created   = datetime.utcnow()
                    
                #     # Add the comment data to the database
                #     comment = self._commentDB.addComment(comment)
                #     self._rollback.append((self._commentDB.removeComment, \
                #         {'commentId': comment.comment_id}))
                
                # Add stats
                self._statsSink.increment('stamped.api.stamps.credit')
                
                # Update credited user stats
                self._userDB.updateUserStats(item.user_id, 'num_credits', \
                    None, increment=1)
                self._rollback.append((self._userDB.updateUserStats, \
                    {'userId': item.user_id, 'stat': 'num_credits', \
                    'increment': -1}))
                
                self._userDB.updateUserStats(item.user_id, 'num_stamps_left', \
                    None, increment=CREDIT_BENEFIT)
                self._rollback.append((self._userDB.updateUserStats, \
                    {'userId': item.user_id, 'stat': 'num_stamps_left', \
                    'increment': -CREDIT_BENEFIT}))
        
        # Note: No activity should be generated for the user creating the stamp
        
        t2 = time.time(); duration = (t1 - t0) * 1000.0; t0 = t1
        self._statsSink.time('stamped.api.methods.addStamp.7', duration)
        
        # Add activity for credited users
        if self._activity == True and len(creditedUserIds) > 0:
            activity                    = Activity()
            activity.genre              = 'restamp'
            activity.user.user_id       = user.user_id
            activity.subject            = stamp.entity.title
            activity.blurb              = stamp.blurb
            activity.linked_stamp_id    = stamp.stamp_id
            activity.timestamp.created  = datetime.utcnow()
            activity.benefit            = CREDIT_BENEFIT
            
            ### TODO: Rollback: Remove activity
            self._activityDB.addActivity(creditedUserIds, activity)
        
        t2 = time.time(); duration = (t1 - t0) * 1000.0; t0 = t1
        self._statsSink.time('stamped.api.methods.addStamp.8', duration)
        
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
                activity                    = Activity()
                activity.genre              = 'mention'
                activity.user.user_id       = user.user_id
                activity.subject            = stamp.entity.title
                activity.blurb              = stamp.blurb
                activity.linked_stamp_id    = stamp.stamp_id
                activity.timestamp.created  = datetime.utcnow()
                
                ### TODO: Rollback: Remove activity
                self._activityDB.addActivity(mentionedUserIds, activity)
                
                # Increment mentions metric
                self._statsSink.increment('stamped.api.stamps.mentions')
        
        t2 = time.time(); duration = (t1 - t0) * 1000.0; t0 = t1
        self._statsSink.time('stamped.api.methods.addStamp.9', duration)
        
        return stamp
    
    @API_CALL
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
                
                # # Add restamp as comment (if prior stamp exists)
                # if 'stamp_id' in item and item['stamp_id'] != None:
                #     # Build comment
                #     comment                     = Comment()
                #     comment.user.user_id        = user.user_id
                #     comment.stamp_id            = item.stamp_id
                #     comment.removeStamp_id          = stamp.stamp_id
                #     comment.blurb               = stamp.blurb
                #     comment.mentions            = stamp.mentions
                #     comment.timestamp.created   = datetime.utcnow()
                    
                #     # Add the comment data to the database
                #     self._commentDB.addComment(comment)

                # Update credited user stats
                self._userDB.updateUserStats(item.user_id, 'num_credits', \
                    None, increment=1)
                self._userDB.updateUserStats(item.user_id, 'num_stamps_left', \
                    None, increment=CREDIT_BENEFIT)

        # Note: No activity should be generated for the user creating the stamp

        # Add activity for credited users
        if self._activity == True and len(creditedUserIds) > 0:
            activity                    = Activity()
            activity.genre              = 'restamp'
            activity.user.user_id       = user.user_id
            activity.subject            = stamp.entity.title
            activity.blurb              = stamp.blurb
            activity.linked_stamp_id    = stamp.stamp_id
            activity.timestamp.created  = datetime.utcnow()
            activity.benefit            = CREDIT_BENEFIT
            
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
                activity                    = Activity()
                activity.genre              = 'mention'
                activity.user.user_id       = user.user_id
                activity.subject            = stamp.entity.title
                activity.blurb              = stamp.blurb
                activity.linked_stamp_id    = stamp.stamp_id
                activity.timestamp.created  = datetime.utcnow()

                self._activityDB.addActivity(mentionedUserIds, activity)

        return stamp
    
    @API_CALL
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
        # self._stampDB.removeUserStampReference(authUserId, stamp.stamp_id)
        
        # Remove from followers' inbox collections
        # followers = self._friendshipDB.getFollowers(authUserId)
        # followers.append(authUserId)
        # self._stampDB.removeInboxStampReference(followers, stamp.stamp_id)

        ### NOTE: 
        # This only removes the stamp from people who follow the user.
        # If we allow for an "opt in" method of users adding individual
        # stamps to their inbox, we'll have to account for that here.

        ### TODO: If restamp, remove from credited stamps' comment list

        ### TODO: Remove from activity? To do? Anything else?

        # Remove comments
        ### TODO: Make this more efficient?
        comments = self._commentDB.getComments(stampId)
        for comment in comments:
            # Remove comment
            self._commentDB.removeComment(comment.comment_id)

        # Remove activity
        self._activityDB.removeActivityForStamp(stamp.stamp_id)

        # Remove as favorite if necessary
        try:
            self._favoriteDB.completeFavorite(stamp.entity_id, authUserId, complete=False)
        except:
            pass

        # Update user stats 
        ### TODO: Do an actual count / update?
        self._userDB.updateUserStats(authUserId, 'num_stamps', \
                    None, increment=-1)
        self._userDB.updateUserStats(authUserId, 'num_stamps_left', \
                    None, increment=1)

        ### TODO: Update credit stats if credit given

        # Update modified timestamp
        stamp.timestamp.modified = datetime.utcnow()

        return stamp
    
    @API_CALL
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
    
    @API_CALL
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
    
    @API_CALL
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

    @API_CALL
    @HandleRollback
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
        comment                     = Comment()
        comment.user_id             = user.user_id
        comment.stamp_id            = stamp.stamp_id
        comment.blurb               = blurb
        comment.timestamp.created   = datetime.utcnow()
        if mentions != None:
            comment.mentions = mentions
            
        # Add the comment data to the database
        comment = self._commentDB.addComment(comment)
        self._rollback.append((self._commentDB.removeComment, \
            {'commentId': comment.comment_id}))

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
                activity.user.user_id       = user.user_id
                activity.subject            = stamp.entity.title
                activity.blurb              = comment.blurb
                activity.linked_stamp_id    = stamp.stamp_id
                activity.linked_comment_id  = comment.comment_id
                activity.timestamp.created  = datetime.utcnow()

                ### TODO: Rollback: Remove Activity
                self._activityDB.addActivity(mentionedUserIds, activity)
                
                # Increment mentions metric
                self._statsSink.increment('stamped.api.stamps.mentions', len(mentionedUserIds))
        
        # Add activity for stamp owner
        commentedUserIds = []
        if stamp.user.user_id not in mentionedUserIds \
            and stamp.user.user_id != user.user_id:
            commentedUserIds.append(stamp.user.user_id)
        if len(commentedUserIds) > 0:
            activity                    = Activity()
            activity.genre              = 'comment'
            activity.user.user_id       = user.user_id
            activity.subject            = stamp.entity.title
            activity.blurb              = comment.blurb
            activity.linked_stamp_id    = stamp.stamp_id
            activity.linked_comment_id  = comment.comment_id
            activity.timestamp.created  = datetime.utcnow()
            
            ### TODO: Rollback: Remove Activity
            self._activityDB.addActivity(commentedUserIds, activity)
            
            # Increment comment metric
            self._statsSink.increment('stamped.api.stamps.comments', len(commentedUserIds))
        
        # Add activity for previous commenters
        ### TODO: Limit this to the last 20 comments or so
        repliedUsersDict = {}
        for prevComment in self._commentDB.getComments(stamp.stamp_id):
            # Skip if it was generated from a restamp
            if prevComment.restamp_id:
                continue

            repliedUserId = prevComment['user']['user_id']
            if repliedUserId not in commentedUserIds \
                and repliedUserId not in mentionedUserIds \
                and repliedUserId != user.user_id:
                repliedUsersDict[prevComment['user']['user_id']] = 1 
        
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
            activity.user.user_id       = user.user_id
            activity.subject            = stamp.entity.title
            activity.blurb              = comment.blurb
            activity.linked_stamp_id    = stamp.stamp_id
            activity.linked_comment_id  = comment.comment_id
            activity.timestamp.created  = datetime.utcnow()

            ### TODO: Rollback: Remove Activity
            self._activityDB.addActivity(repliedUserIds, activity)
        
        # Increment comment count on stamp
        self._stampDB.updateStampStats( \
            stamp.stamp_id, 'num_comments', increment=1)
        self._rollback.append((self._stampDB.updateStampStats, \
            {'stampId': stamp.stamp_id, 'stat': 'num_comments', 'increment': -1}))

        return comment
    
    @API_CALL
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
    
    @API_CALL
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

    @API_CALL
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
        
        # Increment stats
        self._statsSink.increment('stamped.api.stamps.likes')
        
        # Increment user stats by one
        self._userDB.updateUserStats(stamp.user_id, 'num_likes', increment=1)
        self._userDB.updateUserStats(authUserId, 'num_likes_given', increment=1)
        
        # Increment stamp stats by one
        self._stampDB.updateStampStats(stamp.stamp_id, 'num_likes', increment=1)
        
        if stamp.num_likes == None:
            stamp.num_likes = 0
        
        stamp.num_likes += 1
        stamp.is_liked = True
        
        # Give credit once at five likes
        benefit = False
        if stamp.num_likes >= 3 and not stamp.like_threshold_hit:
            benefit = True
            
            # Update stamp stats
            self._stampDB.giveLikeCredit(stamp.stamp_id)
            stamp.like_threshold_hit = True
            
            # Update user stats with new credit
            self._userDB.updateUserStats( \
                stamp.user_id, 'num_stamps_left', increment=LIKE_BENEFIT)
        
        # Add activity for stamp owner (if not self)
        if self._activity == True and stamp.user_id != authUserId:
            activity                    = Activity()
            activity.genre              = 'like'
            activity.user.user_id       = authUserId
            activity.subject            = stamp.entity.title
            activity.linked_stamp_id    = stamp.stamp_id
            activity.timestamp.created  = datetime.utcnow()
            
            if benefit:
                activity.benefit        = LIKE_BENEFIT
            
            self._activityDB.addActivity([stamp.user_id], activity)
        
        return stamp
    
    @API_CALL
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

        # Remove activity
        self._activityDB.removeActivity('like', authUserId, stampId=stampId)

        return stamp

    @API_CALL
    def getLikes(self, authUserId, stampId):
        stamp       = self._stampDB.getStamp(stampId)
        stamp       = self._enrichStampObjects(stamp, authUserId=authUserId)

        # Verify user has the ability to view the stamp's likes
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
        
        # Get user ids
        userIds = self._stampDB.getStampLikes(stampId)

        # Get users
        ### TODO: Return user ids instead so there's no limit? Or allow paging?
        users = self._userDB.lookupUsers(userIds, None, limit=100)

        return users

    

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
        sort            = kwargs.pop('sort', 'created')
        includeComments = kwargs.pop('comments', False)
                       
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
            'sort':     sort,
        }

        stampData = self._stampDB.getStamps(stampIds, **params)
        
        commentPreviews = {}

        if includeComments == True:
            commentData = self._commentDB.getCommentsAcrossStamps(stampIds, commentCap)

            # Group previews by stamp_id
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

        if kwargs.pop('deleted', False):
            deleted = self._stampDB.getDeletedStamps(stampIds, **params)
            if len(deleted) > 0:
                stamps = stamps + deleted

        stamps.sort(key=lambda k:k.timestamp.modified, reverse=True)

        return stamps[:limit]
    
    @API_CALL
    def getInboxStamps(self, authUserId, **kwargs):
        stampIds = self._collectionDB.getInboxStampIds(authUserId)
        
        kwargs['comments'] = True
        kwargs['deleted'] = True
        kwargs['sort'] = 'modified' ## TEMP
        
        return self._getStampCollection(authUserId, stampIds, **kwargs)
    
    @API_CALL
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

        kwargs['comments'] = True

        return self._getStampCollection(authUserId, stampIds, **kwargs)
    
    @API_CALL
    def getCreditedStamps(self, userRequest, authUserId, **kwargs):
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

        stampIds = self._collectionDB.getUserCreditStampIds(user.user_id)
        logs.info("STAMP IDS: %s" % stampIds)

        return self._getStampCollection(authUserId, stampIds, **kwargs)
    
    @API_CALL
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

    @API_CALL
    def addFavorite(self, authUserId, entityId, stampId=None):
        entity  = self._entityDB.getEntity(entityId)

        favorite = Favorite({
            'entity': entity.exportSchema(EntityMini()),
            'user_id': authUserId,
        })
        favorite.timestamp.created = datetime.utcnow()

        if stampId != None:
            favorite.stamp = self._stampDB.getStamp(stampId)

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
        
        # Increment stats
        self._statsSink.increment('stamped.api.stamps.favorites')
        
        # Enrich stamp
        if stampId != None:
            entityIds = {entity.entity_id: entity.exportSchema(EntityMini())}
            favorite.stamp  = self._enrichStampObjects(favorite.stamp, \
                                authUserId=authUserId, entityIds=entityIds)
        
        # Increment user stats by one
        self._userDB.updateUserStats(authUserId, 'num_faves', \
                    None, increment=1)
        
        # Add activity for stamp owner (if not self)
        ### TODO: Verify user isn't being blocked
        if self._activity == True and stampId != None \
            and favorite.stamp.user_id != authUserId:
            activity                    = Activity()
            activity.genre              = 'favorite'
            activity.user.user_id       = authUserId
            activity.subject            = favorite.stamp.entity.title
            activity.linked_stamp_id    = favorite.stamp.stamp_id
            activity.timestamp.created  = datetime.utcnow()

            self._activityDB.addActivity([favorite.stamp.user_id], activity)
        
        return favorite
    
    @API_CALL
    def removeFavorite(self, authUserId, entityId):
        ### TODO: Fail gracefully if favorite doesn't exist
        favorite = self._favoriteDB.getFavorite(authUserId, entityId)
        logs.debug('FAVORITE: %s' % favorite)
        self._favoriteDB.removeFavorite(authUserId, entityId)

        # Decrement user stats by one
        self._userDB.updateUserStats(authUserId, 'num_faves', \
                    None, increment=-1)

        if not favorite:
            favorite = Favorite()

        # Enrich stamp
        if favorite.stamp_id != None:
            stamp           = self._stampDB.getStamp(favorite.stamp_id)
            favorite.stamp  = self._enrichStampObjects( \
                                stamp, authUserId=authUserId)
            # Just in case...
            favorite.stamp.is_fav = False

            # Remove activity
            self._activityDB.removeActivity('favorite', authUserId, \
                stampId=stamp.stamp_id)

        return favorite
    
    @API_CALL
    def getFavorites(self, authUserId, **kwargs):        

        ### TODO: Add slicing (before, since, limit, quality)

        favoriteData = self._favoriteDB.getFavorites(authUserId)

        # Extract entities & stamps
        entityIds   = {}
        stampIds    = {}
        for favorite in favoriteData:
            entityIds[str(favorite.entity.entity_id)] = 1
            if favorite.stamp_id != None:
                stampIds[str(favorite.stamp_id)] = 1


        # Enrich entities
        entities = self._entityDB.getEntities(entityIds.keys())

        for entity in entities:
            entityIds[str(entity.entity_id)] = entity.exportSchema(EntityMini())

        # Enrich stamps
        stamps = self._stampDB.getStamps(stampIds.keys())
        stamps = self._enrichStampObjects(stamps, authUserId=authUserId, \
                    entityIds=entityIds)

        for stamp in stamps:
            stampIds[str(stamp.stamp_id)] = stamp

        favorites = []
        for favorite in favoriteData:
            # Enrich Entity
            if entityIds[favorite.entity.entity_id] != 1:
                favorite.entity = entityIds[favorite.entity.entity_id]
            else:
                logs.warning('FAV MISSING ENTITY: %s' % favorite.entity)
            # Add Stamp
            if favorite.stamp_id != None:
                if stampIds[favorite.stamp_id] != 1:
                    favorite.stamp = stampIds[favorite.stamp_id]
                else:
                    favorite.stamp_id = None
                    logs.warning('FAV MISSING STAMP: %s' % favorite)
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
    
    @API_CALL
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
        stampIds = {}
        for item in activityData:
            if item.user.user_id != None:
                userIds[item.user.user_id] = 1
            if item.linked_user_id != None:
                userIds[item.linked_user_id] = 1
            if item.linked_stamp_id != None:
                stampIds[item.linked_stamp_id] = 1
        
        # Enrich users
        users = self._userDB.lookupUsers(userIds.keys(), None)
        
        for user in users:
            userIds[str(user.user_id)] = user.exportSchema(UserMini())
        
        # Enrich stamps
        stamps = self._stampDB.getStamps(stampIds.keys())
        stamps = self._enrichStampObjects(stamps, authUserId=authUserId)
        
        for stamp in stamps:
            stampIds[str(stamp.stamp_id)] = stamp
        
        activity = []
        for item in activityData:
            if item.user.user_id != None:
                item.user = userIds[item.user.user_id]
            if item.linked_user_id != None:
                item.linked_user = userIds[item.linked_user_id]
            if item.linked_stamp_id != None:
                item.linked_stamp = stampIds[item.linked_stamp_id]
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
    
    @lazyProperty
    def _googlePlaces(self):
        return GooglePlaces()
    
    @lazyProperty
    def _amazonAPI(self):
        return AmazonAPI()
    
    @lazyProperty
    def _appleAPI(self):
        return AppleAPI()
    
    @lazyProperty
    def _theTVDB(self):
        return TheTVDB()
    
    def _convertSearchId(self, search_id):
        if not search_id.startswith('T_'):
            # already a valid entity id
            return search_id
        
        # temporary entity_id; lookup in tempentities collection and 
        # merge result into primary entities db
        doc = self._tempEntityDB._collection.find_one({'search_id' : search_id})
        entity = None
        
        if doc is not None:
            entity = self._tempEntityDB._convertFromMongo(doc)
        
        if search_id.startswith('T_AMAZON_'):
            asin = search_id[9:]
            results = self._amazonAPI.item_lookup(ItemId=asin, ResponseGroup='Large', transform=True)
            
            for result in results:
                if result.asin == asin:
                    entity = result
                    break
        elif search_id.startswith('T_APPLE_'):
            aid = search_id[8:]
            results = self._appleAPI.lookup(id=aid, transform=True)
            
            for result in results:
                if result.entity.aid == aid:
                    entity = result.entity
                    break
            
            if entity is not None:
                if entity.subcategory == 'album':
                    results = self._appleAPI.lookup(id=entity.aid, media='music', entity='song', transform=True)
                    results = filter(lambda r: r.entity.subcategory == 'song', results)
                    
                    entity.tracks = list(result.entity.title for result in results)
                elif entity.subcategory == 'artist':
                    results = self._appleAPI.lookup(id=entity.aid, 
                                                    media='music', 
                                                    entity='album', 
                                                    limit=200, 
                                                    transform=True)
                    results = filter(lambda r: r.entity.subcategory == 'album', results)
                    
                    if len(results) > 0:
                        albums = []
                        for result in results:
                            schema = ArtistAlbumsSchema()
                            schema.album_name = result.entity.title
                            schema.album_id   = result.entity.aid
                            albums.append(schema)
                        
                        entity.albums = albums
                        images = results[0].entity.images
                        for k in images:
                            entity[k] = images[k]
                    
                    results = self._appleAPI.lookup(id=entity.aid, 
                                                    media='music', 
                                                    entity='song', 
                                                    limit=200, 
                                                    transform=True)
                    results = filter(lambda r: r.entity.subcategory == 'song', results)
                    
                    songs = []
                    for result in results:
                        schema = ArtistSongsSchema()
                        schema.song_id   = result.entity.aid
                        schema.song_name = result.entity.title
                        songs.append(schema)
                    
                    entity.songs = songs
        elif search_id.startswith('T_GOOGLE_'):
            gref = search_id[9:]
            
            details = self._googlePlaces.getPlaceDetails(gref)
            entity2 = self._googlePlaces.parseEntity(details, valid=True)
            
            if entity2 is not None:
                entity = entity2
            
            if entity is not None:
                self._googlePlaces.parseEntityDetail(details, entity)
        elif search_id.startswith('T_TVDB_'):
            thetvdb_id = search_id[7:]
            
            entity = self._theTVDB.lookup(thetvdb_id)
        
        """
        elif search_id.startswith('T_LOCAL_GOOGLE_'):
            info  = search_id[15:]
            split = info.split(',')
            
            if len(split) > 3:
                split = (split[0], split[1], string.joinfields(split[2:], ', '))
            
            lat, lng  = float(split[0]), float(split[1])
            
            latLng  = (lat, lng)
            params  = {
                'name' : split[2], 
            }
            
            results = self._googlePlaces.getEntityResultsByLatLng(latLng, params)
            if len(results) > 0:
                reference = results[0].reference
                details   = self._googlePlaces.getPlaceDetails(result.reference)
                
                if entity is None:
                    entity = self._googlePlaces.parseEntity(details)
                
                self._googlePlaces.parseEntityDetail(details, entity)
        """
        
        if entity is None:
            logs.warning("ERROR: could not match temp entity id %s" % search_id)
            return None
        
        del entity.entity_id
        entity = self._entityMatcher.addOne(entity)
        
        assert entity.entity_id is not None
        logs.debug("converted search_id=%s to entity_id=%s" % \
                   (search_id, entity.entity_id))
        
        return entity.entity_id
    
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

