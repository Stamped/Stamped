#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils
import os, logs, re, time, Blacklist, auth
import libs.ec2_utils
import tasks.APITasks

from pprint          import pprint, pformat
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
            self._node_name = "unknown"
        else:
            self._node_name = "localhost"
        
        utils.log("StampedAPI running on node '%s'" % (self.node_name))
    
    @property
    def node_name(self):
        if self._node_name == 'unknown':
            try:
                stack_info = libs.ec2_utils.get_stack()
                self._node_name = stack_info.instance.name
            except:
                pass
        
        return self._node_name
    
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
        account.ios_alert_credit       = True
        account.ios_alert_like         = True
        account.ios_alert_fav          = True
        account.ios_alert_mention      = True
        account.ios_alert_comment      = True
        account.ios_alert_reply        = True
        account.ios_alert_follow       = True
        account.email_alert_credit     = True
        account.email_alert_like       = False
        account.email_alert_fav        = False
        account.email_alert_mention    = True
        account.email_alert_comment    = True
        account.email_alert_reply      = True
        account.email_alert_follow     = True
        
        # Validate screen name
        account.screen_name = account.screen_name.strip()
        if not utils.validate_screen_name(account.screen_name):
            raise InputError("Invalid format for screen name")
        
        # Check blacklist
        if account.screen_name.lower() in Blacklist.screen_names:
            raise InputError("Blacklisted screen name")
        
        # Validate email address
        account.email = str(account.email).lower().strip()
        if not utils.validate_email(account.email):
            raise InputError("Invalid format for email address")
        
        # Add image timestamp if exists
        if imageData:
            account.image_cache = datetime.utcnow()
        
        # Create account
        ### TODO: Add intelligent error message
        account = self._accountDB.addAccount(account)
        self._rollback.append((self._accountDB.removeAccount, [account.user_id]))
        
        # Add stats
        self._statsSink.increment('stamped.api.new_accounts')
        
        # Add profile image
        if imageData:
            self._addProfileImage(imageData, user_id=None, screen_name=account.screen_name.lower())
        
        # Asynchronously send welcome email and add activity items
        tasks.invoke(tasks.APITasks.addAccount, args=[account.user_id])
        
        return account
    
    @API_CALL
    def addAccountAsync(self, user_id):
        account = self._accountDB.getAccount(user_id)
        
        # Add activity if invitations were sent
        invites = self._inviteDB.getInvitations(account.email)
        invitedBy = {}
        
        for invite in invites:
            invitedBy[invite['user_id']] = 1
            
            ### TODO: What genre are we picking for this activity item?
            self._addActivity(genre='invite_sent', 
                              user_id=invite['user_id'], 
                              recipient_ids=[ account.user_id ])
        
        if len(invitedBy) > 0:
            ### TODO: What genre are we picking for this activity item?
            self._addActivity(genre='invite_received', 
                              user_id=account.user_id, 
                              recipient_ids=invitedBy.keys())
        
        self._inviteDB.join(account.email)
        
        domain = str(account.email).split('@')[1]
        if domain != 'stamped.com':
            msg = {}
            msg['to'] = account.email
            msg['from'] = 'Stamped <noreply@stamped.com>'
            msg['subject'] = 'Welcome to Stamped!'
            
            try:
                base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                path = os.path.join(base, 'alerts', 'templates', 'email_welcome.html.j2')
                template = open(path, 'r')
            except:
                ### TODO: Add error logging?
                raise
            
            params = {'screen_name': account.screen_name, 'email_address': account.email}
            msg['body'] = utils.parseTemplate(template, params)
            
            utils.sendEmail(msg, format='html')
    
    @API_CALL
    def removeAccount(self, authUserId):
        account = self._accountDB.getAccount(authUserId)
        
        ### TODO: Verify w/ password
        
        stampIds    = self._collectionDB.getUserStampIds(account.user_id)
        friendIds   = self._friendshipDB.getFriends(account.user_id)
        followerIds = self._friendshipDB.getFollowers(account.user_id)
        
        # Remove tokens
        self._refreshTokenDB.removeRefreshTokensForUser(account.user_id)
        self._accessTokenDB.removeAccessTokensForUser(account.user_id)
        self._emailAlertDB.removeTokenForUser(account.user_id)
        
        # Remove friends / followers
        for followerId in followerIds:
            friendship = Friendship(user_id=followerId, friend_id=account.user_id)
            
            self._friendshipDB.removeFriendship(friendship)
            
            # Decrement number of friends
            self._userDB.updateUserStats(followerId, 'num_friends', increment=-1)
            
            # Remove stamps from Inbox
            self._stampDB.removeInboxStampReferencesForUser(followerId, stampIds)
        
        for friendId in friendIds:
            friendship = Friendship(user_id=account.user_id, friend_id=friendId)
            
            self._friendshipDB.removeFriendship(friendship)
            
            # Decrement number of followers 
            self._userDB.updateUserStats(friendId, 'num_followers', increment=-1)
        
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
                    self._userDB.updateUserStats(creditedUser['user_id'], 'num_credits', increment=-1)
            
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
                self._stampDB.updateStampStats(comment.stamp_id, 'num_comments', increment=-1)
        
        # Remove likes
        likedStampIds = self._stampDB.getUserLikes(account.user_id)
        likedStamps = self._stampDB.getStamps(likedStampIds, limit=len(likedStampIds))
        
        for stamp in likedStamps:
            self._stampDB.removeLike(account.user_id, stamp.stamp_id)
            
            # Decrement user stats by one
            self._userDB.updateUserStats(stamp.user_id, 'num_likes', increment=-1)
            
            # Decrement stamp stats by one
            self._stampDB.updateStampStats(stamp.stamp_id, 'num_likes', increment=-1)
        
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
        
        ### TODO: Carve out "validate account" function

        # Validate Screen Name
        account.screen_name = account.screen_name.strip()
        if not utils.validate_screen_name(account.screen_name):
            raise InputError("Invalid format for screen name")
        
        # Check blacklist
        if account.screen_name.lower() in Blacklist.screen_names:
            raise InputError("Blacklisted screen name")
        
        # Validate email address
        account.email = str(account.email).lower().strip()
        if not utils.validate_email(account.email):
            raise InputError("Invalid format for email address")
        
        self._accountDB.updateAccount(account)
        
        # Asynchronously update profile picture link if screen name has changed
        if account.screen_name.lower() != old_screen_name.lower():
            tasks.invoke(tasks.APITasks.updateAccountSettings, args=[
                         old_screen_name.lower(), account.screen_name.lower()])
        
        return account
    
    @API_CALL
    def updateAccountSettingsAsync(self, old_screen_name, new_screen_name):
        self._imageDB.changeProfileImageName(old_screen_name, new_screen_name)
    
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
        
        primary   = data['color_primary'].upper()
        secondary = data['color_secondary'].upper()
        
        # Validate inputs
        if not utils.validate_hex_color(primary) or not utils.validate_hex_color(secondary):
            raise InputError("Invalid format for colors")
        
        account = self._accountDB.getAccount(authUserId)
        
        # Import each item
        account.color_primary   = primary
        account.color_secondary = secondary
        
        self._accountDB.updateAccount(account)
        
        # Asynchronously generate stamp file
        tasks.invoke(tasks.APITasks.customizeStamp, args=[primary, secondary])
        
        return account
    
    @API_CALL
    def customizeStampAsync(self, primary, secondary):
        self._imageDB.generateStamp(primary, secondary)
    
    @API_CALL
    def updateProfileImage(self, authUserId, data):
        return self._addProfileImage(data, user_id=authUserId)
    
    @API_CALL
    def updateProfileImageAsync(self, screen_name):
        self._imageDB.addResizedProfileImages(screen_name)
    
    def _addProfileImage(self, data, user_id=None, screen_name=None):
        assert user_id is not None or screen_name is not None
        user = None
        
        if user_id is not None:
            user = self._userDB.getUser(user_id)
            screen_name = user.screen_name
        
        image = self._imageDB.getImage(data)
        self._imageDB.addProfileImage(screen_name.lower(), image)
        
        if user is not None:
            image_cache = datetime.utcnow()
            user.image_cache = image_cache
            self._accountDB.updateUserTimestamp(user.user_id, 'image_cache', image_cache)
        
        tasks.invoke(tasks.APITasks.updateProfileImage, args=[screen_name])
        return user
    
    def checkAccount(self, login):
        ### TODO: Clean this up (along with HTTP API function)
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
                raise InputError("Invalid input")

    def _getFacebookFriends(self, authUserId, token=None):
        if token is None:
            account = self._accountDB.getAccount(authUserId)
            token = account.facebook_token
            
            if token is None:
                raise IllegalActionError("attempting to retrieve facebook friends requires a linked account")
        
        friends    = []
        facbookIds = []
        params     = {}
        
        while True:
            result  = utils.getFacebook(token, '/me/friends', params)
            friends = friends + result['data']
            
            if 'paging' in result and 'next' in result['paging']:
                url = urlparse.urlparse(result['paging']['next'])
                params = dict([part.split('=') for part in url[4].split('&')])
                
                if 'offset' in params and int(params['offset']) == len(friends):
                    continue
            break
        
        for friend in friends:
            facbookIds.append(friend['id'])
        
        return self._userDB.findUsersByFacebook(facebookIds)
    
    @API_CALL
    def updateLinkedAccounts(self, authUserId, **kwargs):
        twitter = kwargs.pop('twitter', None)
        facebook = kwargs.pop('facebook', None)

        # Update Facebook account info
        if facebook.facebook_token:
            token = facebook.facebook_token
            
            # Set user details
            fbUser = utils.getFacebook(token, '/me')
            if 'name' not in fbUser or 'id' not in fbUser:
                raise UnavailableError("problem connecting to facebook account")
            
            facebook.facebook_name = fbUser['name']
            facebook.facebook_id = fbUser['id']
            facebook.facebook_screen_name = fbUser.pop('username', None)
        
        self._accountDB.updateLinkedAccounts(authUserId, twitter=twitter, facebook=facebook)
        
        # Alert Facebook asynchronously
        if facebook.facebook_token:
            ### TODO: Remove second param "facebookIds"
            tasks.invoke(tasks.APITasks.alertFollowersFromFacebook, args=[authUserId, None])
        
        return True
    
    @API_CALL
    def removeLinkedAccount(self, authUserId, linkedAccount):
        if linkedAccount not in ['facebook', 'twitter']:
            raise IllegalActionError("Invalid linked account: %s" % linkedAccount)
        
        self._accountDB.removeLinkedAccount(authUserId, linkedAccount)
        return True
    
    @API_CALL
    def alertFollowersFromTwitter(self, authUserId, twitterIds):
        account = self._accountDB.getAccount(authUserId)
        if account.twitter_alerts_sent == True or not account.twitter_screen_name:
            return False
        
        # Perform the actual alerts asynchronously
        tasks.invoke(tasks.APITasks.alertFollowersFromTwitter, args=[authUserId, twitterIds])
        
        return True
    
    @API_CALL
    def alertFollowersFromTwitterAsync(self, authUserId, twitterIds):
        account   = self._accountDB.getAccount(authUserId)
        if account.twitter_alerts_sent == True or not account.twitter_screen_name:
            return False
        
        users     = self._userDB.findUsersByTwitter(twitterIds)
        followers = self._friendshipDB.getFollowers(authUserId)
        
        userIds = []
        for user in users:
            if user.user_id not in followers:
                userIds.append(user.user_id)
        
        self._addActivity(genre='friend', 
                          user_id=authUserId, 
                          recipient_ids=userIds, 
                          subject='Your Twitter friend %s' % account.twitter_screen_name,
                          checkExists=True)
        
        twitter = TwitterAccountSchema(twitter_alerts_sent=True)
        self._accountDB.updateLinkedAccounts(authUserId, twitter=twitter)
        
        return True
    
    ### DEPRECATED
    @API_CALL
    def alertFollowersFromFacebook(self, authUserId, facebookIds):
        account = self._accountDB.getAccount(authUserId)
        if account.facebook_alerts_sent == True or not account.facebook_name:
            return False
        
        # Perform the actual alerts asynchronously
        tasks.invoke(tasks.APITasks.alertFollowersFromFacebook, args=[authUserId, facebookIds])
        
        return True
    
    @API_CALL
    def alertFollowersFromFacebookAsync(self, authUserId, facebookIds=None):
        
        ### TODO: Deprecate passing parameter "facebookIds"
        
        account   = self._accountDB.getAccount(authUserId)
        
        # Only send alert once (when the user initially connects to Facebook)
        if account.facebook_alerts_sent == True or not account.facebook_name:
            return
        
        # Grab friend list from Facebook API
        if account.facebook_token is not None:
            users = self._getFacebookFriends(authUserId, account.facebook_token)
        else:
            ### DEPRECATED
            users = self._userDB.findUsersByFacebook(facebookIds)
        
        # Send alert to people not already following the user
        followers = self._friendshipDB.getFollowers(authUserId)
        userIds = []
        for user in users:
            if user.user_id not in followers:
                userIds.append(user.user_id)
        
        # Generate activity item
        self._addActivity(genre='friend', 
                          user_id=authUserId, 
                          recipient_ids=userIds, 
                          subject='Your Facebook friend %s' % account.facebook_name, 
                          checkExists=True)
        
        ### TODO: Make this update robust for async request
        facebook = FacebookAccountSchema(facebook_alerts_sent=True)
        self._accountDB.updateLinkedAccounts(authUserId, facebook=facebook)
    
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
        return True
    
    @API_CALL
    def removeAPNSTokenForUser(self, authUserId, token):
        self._accountDB.removeAPNSTokenForUser(authUserId, token)
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
        
        if user_id is None and screen_name is None:
            raise InputError("Required field missing (user id or screen name)")
        
        if user_id is not None:
            return self._userDB.getUser(user_id)
        
        return self._userDB.getUserByScreenName(screen_name)
    
    ### PUBLIC
    
    @API_CALL
    def getUser(self, userRequest, authUserId):
        user = self._getUserFromIdOrScreenName(userRequest)
        
        if user.privacy == True:
            if authUserId is None:
                raise InsufficientPrivilegesError("Insufficient privileges to view user")
            
            friendship = Friendship(user_id=authUserId, friend_id=user.user_id)
            
            if not self._friendshipDB.checkFriendship(friendship):
                raise InsufficientPrivilegesError("Insufficient privileges to view user")
        
        return user
    
    @API_CALL
    def getUsers(self, userIds, screenNames, authUserId):
        ### TODO: Add check for privacy settings
        
        users = self._userDB.lookupUsers(userIds, screenNames, limit=100)
        return users
        
        ### TEMP: Sort result based on user request. This should happen client-side.
        usersByUserIds = {}
        usersByScreenNames = {}
        result = []
        
        for user in users:
            usersByUserIds[user.user_id] = user
            usersByScreenNames[user.screen_name] = user
        
        if isinstance(userIds, list):
            for userId in userIds:
                try:
                    result.append(usersByUserIds[userId])
                except:
                    pass
        
        if isinstance(screenNames, list):
            for screenName in screenNames:
                try:
                    result.append(usersByScreenNames[screenName])
                except:
                    pass
        
        if len(result) != len(users):
            result = users
        
        return result
    
    @API_CALL
    def getPrivacy(self, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)
        
        return (user.privacy == True)
    
    @API_CALL
    def findUsersByEmail(self, authUserId, emails):
        ### TODO: Condense with the other "findUsersBy" functions
        ### TODO: Add check for privacy settings?
        
        return self._userDB.findUsersByEmail(emails, limit=100)
    
    @API_CALL
    def findUsersByPhone(self, authUserId, phone):
        ### TODO: Add check for privacy settings?
        
        return self._userDB.findUsersByPhone(phone, limit=100)
    
    @API_CALL
    def findUsersByTwitter(self, authUserId, twitterIds):
        ### TODO: Add check for privacy settings?
        
        return self._userDB.findUsersByTwitter(twitterIds, limit=100)
    
    @API_CALL
    def findUsersByFacebook(self, authUserId, facebookIds=None):
        ### TODO: Add check for privacy settings?
        
        account   = self._accountDB.getAccount(authUserId)
        
        # Grab friend list from Facebook API
        if account.facebook_token is not None:
            users = self._getFacebookFriends(authUserId, account.facebook_token)
        else:
            ### DEPRECATED
            users = self._userDB.findUsersByFacebook(facebookIds, limit=100)
        
        return users
    
    @API_CALL
    def searchUsers(self, query, limit, authUserId):
        limit = self._setLimit(limit, cap=10)
        
        ### TODO: Add check for privacy settings
        
        return self._userDB.searchUsers(query, limit)
    
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
        
        # Verify that you're not following yourself :)
        if user.user_id == authUserId:
            raise IllegalActionError("Illegal friendship: you can't follow yourself!")
        
        friendship = Friendship(user_id=authUserId, friend_id=user.user_id)
        
        # Check if friendship already exists
        if self._friendshipDB.checkFriendship(friendship) == True:
            logs.info("Friendship exists")
            return user
        
        # Check if block exists between authenticating user and user
        if self._friendshipDB.blockExists(friendship) == True:
            raise IllegalActionError("Block exists")
        
        # Check if friend has private account
        if user.privacy == True:
            ### TODO: Create queue for friendship requests
            raise NotImplementedError
        
        # Create friendship
        self._friendshipDB.addFriendship(friendship)
        
        # Increment stats
        self._statsSink.increment('stamped.api.friendships')
        
        # Asynchronously add stamps and activity for newly created friendship
        tasks.invoke(tasks.APITasks.addFriendship, args=[authUserId, user.user_id])
        
        return user
    
    @API_CALL
    def addFriendshipAsync(self, authUserId, user_id):
        if self._activity:
            # Add activity for followed user
            self._addActivity(genre='follower', 
                              user_id=authUserId, 
                              recipient_ids=[ user_id ])
            
            # Remove 'friend' activity item
            self._activityDB.removeActivity('friend', authUserId, recipientId=user_id)
        
        # Add stamps to Inbox
        stampIds = self._collectionDB.getUserStampIds(user_id)
        self._stampDB.addInboxStampReferencesForUser(authUserId, stampIds)
        
        # Increment stats for both users
        self._userDB.updateUserStats(authUserId, 'num_friends',   increment=1)
        self._userDB.updateUserStats(user_id,    'num_followers', increment=1)
    
    @API_CALL
    def removeFriendship(self, authUserId, userRequest):
        user       = self._getUserFromIdOrScreenName(userRequest)
        friendship = Friendship(user_id=authUserId, friend_id=user.user_id)
        
        # Check if friendship doesn't exist
        if self._friendshipDB.checkFriendship(friendship) == False:
            logs.info("Friendship does not exist")
            return user
        
        self._friendshipDB.removeFriendship(friendship)
        
        # Asynchronously remove stamps and activity for this friendship
        tasks.invoke(tasks.APITasks.removeFriendship, args=[authUserId, user.user_id])
        
        return user
    
    @API_CALL
    def removeFriendshipAsync(self, authUserId, user_id):
        # Decrement stats for both users
        self._userDB.updateUserStats(authUserId, 'num_friends', increment=-1)
        self._userDB.updateUserStats(user_id,  'num_followers', increment=-1)
        
        # Remove stamps from Inbox
        stampIds = self._collectionDB.getUserStampIds(user_id)
        self._stampDB.removeInboxStampReferencesForUser(authUserId, stampIds)
        
        # Remove activity
        self._activityDB.removeActivity(genre='follower', userId=authUserId, recipientId=user_id)
    
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
            check = Friendship(user_id=authUserId, friend_id=userA.user_id)
            
            if not self._friendshipDB.checkFriendship(check):
                raise InsufficientPrivilegesError("Insufficient privileges to check friendship")
        
        if userB.privacy == True and authUserId != userB.user_id:
            check = Friendship(user_id=authUserId, friend_id=userB.user_id)
            
            if not self._friendshipDB.checkFriendship(check):
                raise InsufficientPrivilegesError("Insufficient privileges to check friendship")
        
        friendship = Friendship(user_id=userA.user_id, friend_id=userB.user_id)
        return self._friendshipDB.checkFriendship(friendship)
    
    @API_CALL
    def getFriends(self, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)
        
        # Note: This function returns data even if user is private
        
        friends = self._friendshipDB.getFriends(user['user_id'])
        
        # Return data in reverse-chronological order
        friends.reverse()
        
        return friends
    
    @API_CALL
    def getFollowers(self, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)

        # Note: This function returns data even if user is private

        followers = self._friendshipDB.getFollowers(user['user_id'])

        # Return data in reverse-chronological order
        followers.reverse()

        return followers
    
    @API_CALL
    def addBlock(self, authUserId, userRequest):
        user = self._getUserFromIdOrScreenName(userRequest)
        
        friendship        = Friendship(user_id=authUserId, friend_id=user.user_id)
        reverseFriendship = Friendship(user_id=user.user_id, friend_id=authUserId)
        
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
        user       = self._getUserFromIdOrScreenName(userRequest)
        friendship = Friendship(user_id=authUserId, friend_id=user.user_id)
        
        if self._friendshipDB.checkBlock(friendship):
            return True
        
        return False
    
    @API_CALL
    def getBlocks(self, authUserId):
        return self._friendshipDB.getBlocks(authUserId)
    
    @API_CALL
    def removeBlock(self, authUserId, userRequest):
        user       = self._getUserFromIdOrScreenName(userRequest)
        friendship = Friendship(user_id=authUserId, friend_id=user.user_id)
        
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
            raise InputError("Invalid format for email address")
        
        if self._inviteDB.checkInviteExists(email, authUserId):
            raise InputError("Invite already exists")
        
        # Store email address linked to auth user id
        tasks.invoke(tasks.APITasks.inviteFriend, args=[authUserId, email])
        
        return True
    
    @API_CALL
    def inviteFriendAsync(self, authUserId, email):
        self._inviteDB.inviteUser(email, authUserId)
    
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
            raise InputError("Required field missing (entity_id or search_id)")
        
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
        if entity.generated_by != authUserId or entity.generated_by is None:
            raise InsufficientPrivilegesError("Insufficient privileges to update custom entity")
        
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
                       prefix=False, 
                       local=False, 
                       full=True, 
                       page=0, 
                       limit=10):
        results = self._entitySearcher.getSearchResults(query=query, 
                                                        coords=coords, 
                                                        category_filter=category_filter, 
                                                        subcategory_filter=subcategory_filter, 
                                                        full=full, 
                                                        prefix=prefix, 
                                                        local=local, 
                                                        user=authUserId, 
                                                        limit=((page + 1) * limit))
        offset  = limit * page
        results = results[offset : offset + limit]
        
        return results
    
    @API_CALL
    def searchNearby(self, 
                     coords=None, 
                     authUserId=None, 
                     category_filter=None, 
                     subcategory_filter=None, 
                     prefix=False, 
                     full=True, 
                     page=0, 
                     limit=10):
        results = self._entitySearcher.getSearchResults(query='', 
                                                        coords=coords, 
                                                        category_filter=category_filter, 
                                                        subcategory_filter=subcategory_filter, 
                                                        full=full, 
                                                        prefix=prefix, 
                                                        local=True, 
                                                        user=authUserId, 
                                                        limit=((page + 1) * limit))
        offset  = limit * page
        results = results[offset : offset + limit]
        
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
    
    @lazyProperty
    def _user_regex(self):
        return re.compile(r'(?<![a-zA-Z0-9_])@([a-zA-Z0-9+_]{1,20})(?![a-zA-Z0-9_])', re.IGNORECASE)
    
    def _extractMentions(self, text):
        screenNames = set()
        mentions    = [] 
        
        # Run through and grab mentions
        for user in self._user_regex.finditer(text):
            data = {}
            data['indices'] = [user.start(), user.end()]
            data['screen_name'] = user.groups()[0]
            
            try:
                user = self._userDB.getUserByScreenName(data['screen_name'])
                data['user_id'] = user.user_id
                data['screen_name'] = user.screen_name
            except:
                logs.warning("User not found (%s)" % data['screen_name'])
            
            if data['screen_name'] not in screenNames:
                screenNames.add(data['screen_name'])
                mentions.append(data)
        
        if len(mentions) > 0:
            return mentions
        
        return None
    
    def _extractCredit(self, creditData, user_id, entity_id, userIds):
        creditedUserIds = set()
        credit = []
        
        if creditData is not None and isinstance(creditData, list):
            ### TODO: Filter out non-ASCII data for credit
            creditedScreenNames = []
            for creditedScreenName in creditData:
                if utils.validate_screen_name(creditedScreenName):
                    creditedScreenNames.append(creditedScreenName)
            
            creditedUsers = self._userDB.lookupUsers(None, creditedScreenNames)
            
            for creditedUser in creditedUsers:
                userId = creditedUser['user_id']
                if userId == user_id or userId in creditedUserIds:
                    continue
                
                result = CreditSchema()
                result.user_id      = creditedUser['user_id']
                result.screen_name  = creditedUser['screen_name']
                
                # Add to user ids
                userIds[userId] = creditedUser.exportSchema(UserMini())
                
                # Assign credit
                creditedStamp = self._stampDB.getStampFromUserEntity(userId, entity_id)
                if creditedStamp is not None:
                    result.stamp_id = creditedStamp.stamp_id
                
                credit.append(result)
                creditedUserIds.add(result.user_id)
        
        ### TODO: How do we handle credited users that have not yet joined?
        if len(credit) > 0:
            return credit
        
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
            ### TODO: Intelligent matching with stampId
            # Favorites
            favorites = self._favoriteDB.getFavoriteEntityIds(authUserId)
            
            ### TODO: Intelligent matching with stampId
            # Likes
            likes = self._stampDB.getUserLikes(authUserId)
        
        # Add user objects to stamps
        stamps = []
        for stamp in stampData:
            # Add stamp user
            ### TODO: Check that userIds != 1 (i.e. user still exists)?
            if userIds[stamp.user_id] == 1:
                msg = 'Unable to match user_id %s for stamp id %s' % (stamp.user_id, stamp.stamp_id)
                logs.warning(msg)
                continue
            else:
                stamp.user = userIds[stamp.user_id]
            
            # Add entity
            if entityIds[stamp.entity_id] == 1:
                msg = 'Unable to match entity_id %s for stamp_id %s' % (stamp.entity_id, stamp.stamp_id)
                logs.warning(msg)
                ### TODO: Raise?
            else:
                stamp.entity = entityIds[stamp.entity_id]
            
            # Add credited user(s)
            if stamp.credit is not None:
                credits = []
                for i in xrange(len(stamp.credit)):
                    creditedUser = userIds[stamp.credit[i].user_id]

                    if creditedUser == 1:
                        msg = 'Unable to match user_id %s for credit on stamp id %s' % \
                            (stamp.credit[i].user_id, stamp.stamp_id)
                        logs.warning(msg)
                        continue

                    credit = CreditSchema()
                    credit.user_id          = stamp.credit[i].user_id
                    credit.stamp_id         = stamp.credit[i].stamp_id
                    credit.screen_name      = creditedUser['screen_name']
                    credit.color_primary    = creditedUser['color_primary']
                    credit.color_secondary  = creditedUser['color_secondary']
                    credit.privacy          = creditedUser['privacy']
                    credits.append(credit)
                
                stamp.credit = credits
            
            # Add commenting user(s)
            if stamp.comment_preview is not None:
                comments = []
                
                for i in xrange(len(stamp.comment_preview)):
                    commentingUser = userIds[stamp.comment_preview[i].user_id]
                    
                    if commentingUser != 1:
                        stamp.comment_preview[i].user = commentingUser
                        comments.append(stamp.comment_preview[i])
                
                stamp.comment_preview = comments
            
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
        user        = self._userDB.getUser(authUserId)
        entity      = self._getEntityFromRequest(entityRequest)
        
        blurbData   = data.pop('blurb',  None)
        creditData  = data.pop('credit', None)
        imageData   = data.pop('image',  None)
        
        # Check to make sure the user has stamps left
        if user.num_stamps_left <= 0:
            raise IllegalActionError("No more stamps remaining")
        
        # Check to make sure the user hasn't already stamped this entity
        if self._stampDB.checkStamp(user.user_id, entity.entity_id):
            raise IllegalActionError("Cannot stamp same entity twice (id = %s)" % entity.entity_id)
        
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
        if blurbData is not None:
            stamp.blurb    = blurbData.strip()
            stamp.mentions = self._extractMentions(blurbData)
        
        # Extract credit
        if creditData is not None:
            stamp.credit = self._extractCredit(creditData, user.user_id, entity.entity_id, userIds)
        
        # Add stats
        self._statsSink.increment('stamped.api.stamps.category.%s' % entity.category)
        self._statsSink.increment('stamped.api.stamps.subcategory.%s' % entity.subcategory)
        
        # Add the stamp data to the database
        stamp = self._stampDB.addStamp(stamp)
        ### TODO: Rollback adds stamp to "deleted stamps" table. Fix that.
        self._rollback.append((self._stampDB.removeStamp, {'stampId': stamp.stamp_id}))
        
        # Add image to stamp
        ### TODO: Unwind stamp if this fails
        if imageData is not None:
            ### TODO: Rollback: Delete Image
            image = self._imageDB.getImage(imageData)
            self._imageDB.addStampImage(stamp.stamp_id, image)
            
            # Add image dimensions to stamp object (width,height)
            width, height           = image.size
            stamp.image_dimensions  = "%s,%s" % (width, height)
            stamp                   = self._stampDB.updateStamp(stamp)
            
            self._statsSink.increment('stamped.api.stamps.images')
        
        # Enrich linked user, entity, favorites, etc. within the stamp
        entityIds = {entity.entity_id: entity.exportSchema(EntityMini())}
        stamp = self._enrichStampObjects(stamp, authUserId=authUserId, \
            userIds=userIds, entityIds=entityIds)
        
        # Add a reference to the stamp in the user's collection
        self._rollback.append((self._stampDB.removeUserStampReference, \
            {'stampId': stamp.stamp_id, 'userId': user.user_id}))
        self._stampDB.addUserStampReference(user.user_id, stamp.stamp_id)
        
        # Asynchronously add references to the stamp in follower's inboxes and 
        # add activity for credit and mentions
        tasks.invoke(tasks.APITasks.addStamp, args=[user.user_id, stamp.stamp_id])
        
        return stamp
    
    @API_CALL
    def addStampAsync(self, authUserId, stamp_id):
        stamp = self._stampDB.getStamp(stamp_id)
        
        # Add references to the stamp in all relevant inboxes
        followers = self._friendshipDB.getFollowers(authUserId)
        followers.append(authUserId)
        self._stampDB.addInboxStampReference(followers, stamp_id)
        
        # Update user stats 
        self._userDB.updateUserStats(authUserId, 'num_stamps',       increment=1)
        self._userDB.updateUserStats(authUserId, 'num_stamps_left',  increment=-1)
        self._userDB.updateUserStats(authUserId, 'num_stamps_total', increment=1)
        
        # If stamped entity is on the to do list, mark as complete
        try:
            self._favoriteDB.completeFavorite(entity.entity_id, authUserId)
        except:
            pass
        
        creditedUserIds = []
        
        # Give credit
        if stamp.credit is not None and len(stamp.credit) > 0:
            for item in stamp.credit:
                if item.user_id == authUserId:
                    continue
                
                friendship = Friendship(user_id=authUserId, friend_id=item.user_id)
                
                # Check if block exists between user and credited user
                if self._friendshipDB.blockExists(friendship) == True:
                    logs.debug("Block exists")
                    continue
                
                ### NOTE:
                # For now, if a block exists then no comment or activity is
                # created. This may change ultimately (i.e. we create the
                # 'comment' and hide it from the recipient until they're
                # unblocked), but for now we're not going to do anything.
                
                # Assign credit
                self._stampDB.giveCredit(item.user_id, stamp)
                creditedUserIds.append(item.user_id)
                
                # # Add restamp as comment (if prior stamp exists)
                # if 'stamp_id' in item and item['stamp_id'] is not None:
                #     # Build comment
                #     comment                     = Comment()
                #     comment.user.user_id        = user_id
                #     comment.stamp_id            = item.stamp_id
                #     comment.restamp_id          = stamp.stamp_id
                #     comment.blurb               = stamp.blurb
                #     comment.mentions            = stamp.mentions
                #     comment.timestamp.created   = datetime.utcnow()
                #     
                #     # Add the comment data to the database
                #     comment = self._commentDB.addComment(comment)
                #     self._rollback.append((self._commentDB.removeComment, \
                #         {'commentId': comment.comment_id}))
                
                # Add stats
                self._statsSink.increment('stamped.api.stamps.credit')
                
                # Update credited user stats
                self._userDB.updateUserStats(item.user_id, 'num_credits',     increment=1)
                self._userDB.updateUserStats(item.user_id, 'num_stamps_left', increment=CREDIT_BENEFIT)
        
        # Note: No activity should be generated for the user creating the stamp
        
        # Add activity for credited users
        self._addActivity(genre='restamp', 
                          user_id=authUserId, 
                          recipient_ids=creditedUserIds, 
                          subject=stamp.entity.title, 
                          blurb=stamp.blurb, 
                          linked_stamp_id=stamp.stamp_id, 
                          benefit=CREDIT_BENEFIT)
        
        # Add activity for mentioned users
        self._addMentionActivity(authUserId=authUserId, 
                                 mentions=stamp.mentions, 
                                 ignore=creditedUserIds, 
                                 subject=stamp.entity.title, 
                                 blurb=stamp.blurb, 
                                 linked_stamp_id=stamp.stamp_id)
    
    @API_CALL
    def updateStamp(self, authUserId, stampId, data):        
        stamp       = self._stampDB.getStamp(stampId)       
        user        = self._userDB.getUser(authUserId)
        
        blurbData   = data.pop('blurb', stamp.blurb)
        creditData  = data.pop('credit', None)
        
        # Verify user can modify the stamp
        if authUserId != stamp.user_id:
            raise InsufficientPrivilegesError("Insufficient privileges to modify stamp")
        
        # Collect user ids
        userIds = {}
        userIds[user.user_id] = user.exportSchema(UserMini())
        
        # Blurb & Mentions
        mentionedUsers = []
        
        if blurbData is None:
            stamp.blurb = None
        elif blurbData.strip() != stamp.blurb:
            stamp.blurb = blurbData.strip()
            
            previouslyMentioned = []
            if stamp.mentions is not None:
                for mention in stamp.mentions:
                    previouslyMentioned.append(mention.screen_name)
            
            mentions = self._extractMentions(blurbData)
            if mentions is not None:
                for mention in mentions:
                    if mention['screen_name'] not in previouslyMentioned:
                        mentionedUsers.append(mention)
            
            stamp.mentions = mentions
        
        # Credit
        credit = []
        creditedUserIds = []
        
        if creditData is None or not isinstance(creditData, list):
            stamp.credit = None
        else:
            previouslyCredited = []
            for creditedUser in stamp.credit:
                previouslyCredited.append(creditedUser.user_id)
            
            ### TODO: Filter out non-ASCII data for credit
            creditedScreenNames = []
            for creditedScreenName in creditData:
                if utils.validate_screen_name(creditedScreenName):
                    creditedScreenNames.append(creditedScreenName)
            
            creditedUsers = self._userDB.lookupUsers(None, creditedScreenNames)
            
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
                creditedStamp = self._stampDB.getStampFromUserEntity(userId, stamp.entity.entity_id)
                if creditedStamp is not None:
                    result.stamp_id = creditedStamp.stamp_id

                credit.append(result)

                # Check if user was credited previously
                if userId in previouslyCredited:
                    continue

                # Check if block exists between user and credited user
                friendship = Friendship(user_id=user.user_id, friend_id=userId)
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
        if stamp.credit is not None and len(stamp.credit) > 0:
            for item in credit:
                # Only run if user is flagged as credited
                if item.user_id not in creditedUserIds:
                    continue
                
                # Assign credit
                self._stampDB.giveCredit(item.user_id, stamp)
                
                # # Add restamp as comment (if prior stamp exists)
                # if 'stamp_id' in item and item['stamp_id'] is not None:
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
                self._userDB.updateUserStats(item.user_id, 'num_credits',     increment=1)
                self._userDB.updateUserStats(item.user_id, 'num_stamps_left', increment=CREDIT_BENEFIT)
        
        # Note: No activity should be generated for the user creating the stamp
        
        # Add activity for credited users
        self._addActivity(genre='restamp', 
                          user_id=user.user_id, 
                          recipient_ids=creditedUserIds, 
                          subject=stamp.entity.title, 
                          blurb=stamp.blurb, 
                          linked_stamp_id=stamp.stamp_id, 
                          benefit=CREDIT_BENEFIT)
        
        # Add activity for mentioned users
        if self._activity == True and stamp.mentions is not None and len(stamp.mentions) > 0:
            mentionedUserIds = []
            
            for mention in stamp.mentions:
                if 'user_id' in mention \
                    and mention.user_id not in creditedUserIds \
                    and mention.user_id != user.user_id:
                    # Check if block exists between user and mentioned user
                    
                    friendship = Friendship(user_id=user.user_id, friend_id=mention.user_id)
                    
                    if self._friendshipDB.blockExists(friendship) == False:
                        mentionedUserIds.append(mention['user_id'])
            
            self._addActivity(genre='mention', 
                              user_id=user.user_id, 
                              recipient_ids=mentionedUserIds, 
                              subject=stamp.entity.title, 
                              blurb=stamp.blurb, 
                              linked_stamp_id=stamp.stamp_id)
        
        return stamp
    
    @API_CALL
    def removeStamp(self, authUserId, stampId):
        stamp       = self._stampDB.getStamp(stampId)
        stamp       = self._enrichStampObjects(stamp, authUserId=authUserId)
        
        # Verify user has permission to delete
        if stamp.user_id != authUserId:
            raise InsufficientPrivilegesError("Insufficient privileges to remove stamp")
        
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
        
        ### TODO: Remove reference in other people's favorites

        # Update user stats 
        ### TODO: Do an actual count / update?
        self._userDB.updateUserStats(authUserId, 'num_stamps',      increment=-1)
        self._userDB.updateUserStats(authUserId, 'num_stamps_left', increment=1)
        
        # Update credit stats if credit given
        if stamp.credit is not None and len(stamp.credit) > 0:
            for item in stamp.credit:
                # Only run if user is flagged as credited
                if 'user_id' not in item or item.user_id is None:
                    continue
                
                # Assign credit
                self._stampDB.removeCredit(item.user_id, stamp)
                
                # Update credited user stats
                self._userDB.updateUserStats(item.user_id, 'num_credits', increment=-1)
        
        # Update modified timestamp
        stamp.timestamp.modified = datetime.utcnow()
        
        return stamp
    
    @API_CALL
    def getStamp(self, stampId, authUserId=None):
        stamp       = self._stampDB.getStamp(stampId)
        stamp       = self._enrichStampObjects(stamp, authUserId=authUserId)
        
        # Check privacy of stamp
        if stamp.user_id != authUserId and stamp.user.privacy == True:
            friendship = Friendship(user_id=user.user_id, friend_id=authUserId)
            
            if not self._friendshipDB.checkFriendship(friendship):
                raise InsufficientPrivilegesError("Insufficient privileges to view stamp")
        
        return stamp
    
    @API_CALL
    def getStampFromUser(self, screenName, stampNumber):
        user = self._userDB.getUserByScreenName(screenName)
        stamp = self._stampDB.getStampFromUserStampNum(user.user_id, stampNumber)
        stamp = self._enrichStampObjects(stamp)
        
        # TODO: if authUserId == stamp.user.user_id, then the privacy should be disregarded
        if stamp.user.privacy == True:
            raise InsufficientPrivilegesError("Insufficient privileges to view stamp")
        
        return stamp
    
    @API_CALL
    def updateStampImage(self, authUserId, stampId, data):
        stamp       = self._stampDB.getStamp(stampId)
        stamp       = self._enrichStampObjects(stamp, authUserId=authUserId)
        
        # Verify user has permission to add image
        if stamp.user_id != authUserId:
            raise InsufficientPrivilegesError("Insufficient privileges to update stamp image")
        
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
        friendship = Friendship(user_id=stamp.user.user_id, friend_id=user.user_id)
        
        # Check if stamp is private; if so, must be a follower
        if stamp.user.privacy == True:
            if not self._friendshipDB.checkFriendship(friendship):
                raise InsufficientPrivilegesError("Insufficient privileges to add comment")
        
        # Check if block exists between user and stamp owner
        if self._friendshipDB.blockExists(friendship) == True:
            raise IllegalActionError("Block exists")
        
        # Extract mentions
        mentions = None
        if blurb is not None:
            mentions = self._extractMentions(blurb)
        
        # Build comment
        comment                     = Comment()
        comment.user_id             = user.user_id
        comment.stamp_id            = stamp.stamp_id
        comment.blurb               = blurb
        comment.timestamp.created   = datetime.utcnow()
        if mentions is not None:
            comment.mentions = mentions
        
        # Add the comment data to the database
        comment = self._commentDB.addComment(comment)
        self._rollback.append((self._commentDB.removeComment, {'commentId': comment.comment_id}))
        
        # Add full user object back
        comment.user = user.exportSchema(UserMini())
        
        tasks.invoke(tasks.APITasks.addComment, args=[user.user_id, stampId, comment.comment_id])
        
        return comment
    
    @API_CALL
    def addCommentAsync(self, authUserId, stampId, comment_id):
        comment = self._commentDB.getComment(comment_id)
        stamp   = self._stampDB.getStamp(stampId)
        stamp   = self._enrichStampObjects(stamp, authUserId=authUserId)
        
        # Add activity for mentioned users
        mentionedUserIds = self._addMentionActivity(authUserId=authUserId, 
                                                    mentions=stamp.mentions, 
                                                    subject=stamp.entity.title, 
                                                    blurb=comment.blurb, 
                                                    linked_stamp_id=stamp.stamp_id, 
                                                    linked_comment_id=comment.comment_id)
        
        # Add activity for stamp owner
        commentedUserIds = set()
        if stamp.user.user_id not in mentionedUserIds and stamp.user.user_id != authUserId:
            commentedUserIds.add(stamp.user.user_id)
        
        self._addActivity(genre='comment', 
                          user_id=authUserId, 
                          recipient_ids=commentedUserIds, 
                          subject=stamp.entity.title, 
                          blurb=comment.blurb, 
                          linked_stamp_id=stamp.stamp_id, 
                          linked_comment_id=comment.comment_id)
        
        # Increment comment metric
        self._statsSink.increment('stamped.api.stamps.comments', len(commentedUserIds))
        
        repliedUserIds = []
        
        # Add activity for previous commenters
        ### TODO: Limit this to the last 20 comments or so
        for prevComment in self._commentDB.getComments(stamp.stamp_id):
            # Skip if it was generated from a restamp
            if prevComment.restamp_id:
                continue
            
            repliedUserId = prevComment['user']['user_id']
            if repliedUserId not in commentedUserIds \
                and repliedUserId not in mentionedUserIds \
                and repliedUserId != authUserId:
                
                replied_user_id = prevComment['user']['user_id']
                
                # Check if block exists between user and previous commenter
                friendship = Friendship(user_id=authUserId, friend_id=replied_user_id)
                
                if self._friendshipDB.blockExists(friendship) == False:
                    repliedUserIds.append(replied_user_id)
        
        self._addActivity(genre='reply', 
                          user_id=authUserId, 
                          recipient_ids=repliedUserIds, 
                          subject=stamp.entity.title, 
                          blurb=comment.blurb, 
                          linked_stamp_id=stamp.stamp_id, 
                          linked_comment_id=comment.comment_id)
        
        # Increment comment count on stamp
        self._stampDB.updateStampStats(stamp.stamp_id, 'num_comments', increment=1)
    
    @API_CALL
    def removeComment(self, authUserId, commentId):
        comment = self._commentDB.getComment(commentId)

        # Only comment owner and stamp owner can delete comment
        if comment.user.user_id != authUserId:
            stamp = self._stampDB.getStamp(comment.stamp_id)
            if stamp.user.user_id != authUserId:
                raise InsufficientPrivilegesError("Insufficient privileges to remove comment")

        # Don't allow user to delete comment for restamp notification
        if comment.restamp_id is not None:
            raise IllegalActionError("Cannot remove 'restamp' comment")

        # Remove comment
        self._commentDB.removeComment(comment.comment_id)

        # Remove activity?
        self._activityDB.removeActivity('comment', authUserId, commentId=comment.comment_id)

        # Increment comment count on stamp
        self._stampDB.updateStampStats(comment.stamp_id, 'num_comments', increment=-1)

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
            friendship = Friendship(user_id=stamp.user.user_id, friend_id=authUserId)
            
            if not self._friendshipDB.checkFriendship(friendship):
                raise InsufficientPrivilegesError("Insufficient privileges to view stamp")
              
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
            if userIds[comment.user_id] == 1:
                msg = 'Unable to get user_id %s for comment_id %s' % \
                    (comment.user_id, comment.comment_id)
                logs.warning(msg)
            else:
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
        stamp = self._stampDB.getStamp(stampId)
        stamp = self._enrichStampObjects(stamp, authUserId=authUserId)
        
        # Verify user has the ability to 'like' the stamp
        if stamp.user_id != authUserId:
            friendship = Friendship(user_id=stamp.user_id, friend_id=authUserId)
            
            # Check if stamp is private; if so, must be a follower
            if stamp.user.privacy == True:
                if not self._friendshipDB.checkFriendship(friendship):
                    raise InsufficientPrivilegesError("Insufficient privileges to add comment")
            
            # Check if block exists between user and stamp owner
            if self._friendshipDB.blockExists(friendship) == True:
                raise IllegalActionError("Block exists")
        
        # Check to verify that user hasn't already liked stamp
        if self._stampDB.checkLike(authUserId, stampId):
            raise IllegalActionError("'Like' exists for user (%s) on stamp (%s)" % (authUserId, stampId))
        
        # Add like
        self._stampDB.addLike(authUserId, stampId)
        
        # Increment stats
        self._statsSink.increment('stamped.api.stamps.likes')
        
        # Increment user stats by one
        self._userDB.updateUserStats(stamp.user_id, 'num_likes',    increment=1)
        self._userDB.updateUserStats(authUserId, 'num_likes_given', increment=1)
        
        # Increment stamp stats by one
        self._stampDB.updateStampStats(stamp.stamp_id, 'num_likes', increment=1)
        
        if stamp.num_likes is None:
            stamp.num_likes = 0
        
        stamp.num_likes += 1
        stamp.is_liked = True
        
        # Give credit once a given threshold is hit
        benefit = False
        if stamp.num_likes >= 3 and not stamp.like_threshold_hit:
            benefit = True
            
            # Update stamp stats
            self._stampDB.giveLikeCredit(stamp.stamp_id)
            stamp.like_threshold_hit = True
            
            # Update user stats with new credit
            self._userDB.updateUserStats(stamp.user_id, 'num_stamps_left', increment=LIKE_BENEFIT)
        
        # Add activity for stamp owner (if not self)
        if stamp.user_id != authUserId:
            self._addActivity(genre='like', 
                              user_id=authUserId, 
                              recipient_ids=[ stamp.user_id ], 
                              subject=stamp.entity.title, 
                              linked_stamp_id=stamp.stamp_id)
        
        return stamp
    
    @API_CALL
    def removeLike(self, authUserId, stampId):
        # Remove like (if it exists)
        if not self._stampDB.removeLike(authUserId, stampId):
            raise IllegalActionError("'Like' does not exist for user (%s) on stamp (%s)" % (authUserId, stampId))
        
        # Get stamp object
        stamp = self._stampDB.getStamp(stampId)
        stamp = self._enrichStampObjects(stamp, authUserId=authUserId)
        
        # Decrement user stats by one
        self._userDB.updateUserStats(stamp.user_id, 'num_likes',    increment=-1)
        self._userDB.updateUserStats(authUserId, 'num_likes_given', increment=-1)
        
        # Decrement stamp stats by one
        self._stampDB.updateStampStats(stamp.stamp_id, 'num_likes', increment=-1)
        
        if stamp.num_likes is None:
            stamp.num_likes = 0
        
        if stamp.num_likes > 0:
            stamp.num_likes -= 1
        else:
            stamp.num_likes  = 0
        
        # Remove activity
        self._activityDB.removeActivity('like', authUserId, stampId=stampId)
        
        return stamp
    
    @API_CALL
    def getLikes(self, authUserId, stampId):
        stamp = self._stampDB.getStamp(stampId)
        stamp = self._enrichStampObjects(stamp, authUserId=authUserId)
        
        # Verify user has the ability to view the stamp's likes
        if stamp.user_id != authUserId:
            friendship = Friendship(user_id=stamp.user_id, friend_id=authUserId)
            
            # Check if stamp is private; if so, must be a follower
            if stamp.user.privacy == True:
                if not self._friendshipDB.checkFriendship(friendship):
                    raise InsufficientPrivilegesError("Insufficient privileges to add comment")
            
            # Check if block exists between user and stamp owner
            if self._friendshipDB.blockExists(friendship) == True:
                raise IllegalActionError("Block exists")
        
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
    
    def _setSliceParams(self, data, default_limit=20, default_sort=None):
        # Since
        try: 
            since = datetime.utcfromtimestamp(int(data.pop('since', None)) - 2)
        except:
            since = None
        
        # Before
        try: 
            before = datetime.utcfromtimestamp(int(data.pop('before', None)) + 2)
        except:
            before = None
        
        try:
            limit = int(data.pop('limit', default_limit))
            
            if default_limit is not None and limit > default_limit:
                limit = default_limit
        except:
            limit = default_limit
        
        sort = data.pop('sort', default_sort)
        
        return {
            'since'  : since, 
            'before' : before, 
            'limit'  : limit, 
            'sort'   : sort, 
        }
    
    def _setLimit(self, limit, cap=20):
        try:
            if int(limit) < cap:
                return int(limit)
        except:
            return cap
    
    def _getStampCollection(self, authUserId, stampIds, **kwargs):
        quality         = kwargs.pop('quality', 3)
        includeComments = kwargs.pop('comments', False)
        
        # Set quality
        if quality == 1:        # wifi
            stampCap    = 50
            commentCap  = 20
        elif quality == 2:      # 3G
            stampCap    = 30
            commentCap  = 10
        else:                   # edge
            stampCap    = 20
            commentCap  = 4
        
        # Limit slice of data returned
        params = self._setSliceParams(kwargs, stampCap, 'created')
        
        stampData = self._stampDB.getStamps(stampIds, **params)
        
        commentPreviews = {}
        
        if includeComments == True:
            # Only grab comments for slice
            realizedStampIds = []
            for stamp in stampData:
                realizedStampIds.append(stamp.stamp_id)
            commentData = self._commentDB.getCommentsAcrossStamps(realizedStampIds, commentCap)
            
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
        
        if params['sort'] == 'modified':
            stamps.sort(key=lambda k:k.timestamp.modified, reverse=True)
        else:
            stamps.sort(key=lambda k:k.timestamp.created, reverse=True)
        
        return stamps[:params['limit']]
    
    @API_CALL
    def getInboxStamps(self, authUserId, **kwargs):
        stampIds = self._collectionDB.getInboxStampIds(authUserId)
        
        kwargs['comments']  = True
        kwargs['deleted']   = True
        kwargs['sort']      = 'modified' ## TEMP
        
        return self._getStampCollection(authUserId, stampIds, **kwargs)
    
    @API_CALL
    def getUserStamps(self, userRequest, authUserId, **kwargs):
        user = self._getUserFromIdOrScreenName(userRequest)
        
        # Check privacy
        if user.privacy == True:
            if authUserId is None:
                raise InsufficientPrivilegesError("Must be logged in to view account")
            
            friendship = Friendship(user_id=authUserId, friend_id=user.user_id)
            
            if not self._friendshipDB.checkFriendship(friendship):
                raise InsufficientPrivilegesError("Insufficient privileges to view user")
        
        stampIds = self._collectionDB.getUserStampIds(user.user_id)
        
        kwargs['comments'] = True
        
        ### TEMP
        import copy
        kwargsCopy = copy.deepcopy(kwargs)

        result = self._getStampCollection(authUserId, stampIds, **kwargs)

        ### TEMP
        # Fixes infinite loop where client (1.0.3) mistakenly passes "modified" instead
        # of "created" as 'before' param. This attempts to identify those situations on 
        # the second pass and returns the next segment of stamps.
        if len(result) >= 10 and 'before' in kwargs:
            try:
                before = datetime.utcfromtimestamp(int(kwargsCopy.pop('before', None)))
                from datetime import timedelta
                import calendar
                modified = result[-1].timestamp.modified
                if modified.replace(microsecond=0) + timedelta(seconds=round(modified.microsecond / 1000000.0)) == before \
                    and result[-1].timestamp.created + timedelta(hours=1) < before:
                    kwargsCopy['before'] = int(calendar.timegm(result[-1].timestamp.created.timetuple()))
                    result = self._getStampCollection(authUserId, stampIds, **kwargsCopy)
            except Exception as e:
                logs.warning(e)
                pass

        return result
    
    @API_CALL
    def getCreditedStamps(self, userRequest, authUserId, **kwargs):
        user = self._getUserFromIdOrScreenName(userRequest)
        
        # Check privacy
        if user.privacy == True:
            if authUserId is None:
                raise InsufficientPrivilegesError("Must be logged in to view account")
            
            friendship = Friendship(user_id=authUserId, friend_id=user.user_id)
            
            if not self._friendshipDB.checkFriendship(friendship):
                raise InsufficientPrivilegesError("Insufficient privileges to view user")
        
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
    def addFavorite(self, authUserId, entityRequest, stampId=None):
        entity = self._getEntityFromRequest(entityRequest)
        
        favorite = Favorite(entity=entity.exportSchema(EntityMini()), 
                            user_id=authUserId)
        favorite.timestamp.created = datetime.utcnow()
        
        if stampId is not None:
            favorite.stamp = self._stampDB.getStamp(stampId)
        
        # Check to verify that user hasn't already favorited entity
        try:
            fav = self._favoriteDB.getFavorite(authUserId, entity.entity_id)
            if fav.favorite_id is None:
                raise
            exists = True
        except:
            exists = False
        
        if exists:
            raise IllegalActionError("Favorite already exists")
        
        # Check if user has already stamped entity, mark as complete if so
        if self._stampDB.checkStamp(authUserId, entity.entity_id):
            favorite.complete = True
        
        favorite = self._favoriteDB.addFavorite(favorite)
        
        # Increment stats
        self._statsSink.increment('stamped.api.stamps.favorites')
        
        # Enrich stamp
        if stampId is not None:
            entityIds = {entity.entity_id: entity.exportSchema(EntityMini())}
            favorite.stamp  = self._enrichStampObjects(favorite.stamp, \
                                authUserId=authUserId, entityIds=entityIds)
        
        # Increment user stats by one
        self._userDB.updateUserStats(authUserId, 'num_faves', increment=1)
        
        # Add activity for stamp owner (if not self)
        ### TODO: Verify user isn't being blocked
        if stampId is not None and favorite.stamp.user_id != authUserId:
            self._addActivity(genre='favorite', 
                              user_id=authUserId, 
                              recipient_ids=[ favorite.stamp.user_id ], 
                              subject=favorite.stamp.entity.title, 
                              linked_stamp_id=favorite.stamp.stamp_id)
        
        return favorite
    
    @API_CALL
    def removeFavorite(self, authUserId, entityId):
        ### TODO: Fail gracefully if favorite doesn't exist
        favorite = self._favoriteDB.getFavorite(authUserId, entityId)
        
        if not favorite or not favorite.favorite_id:
            raise UnavailableError('Invalid favorite: %s' % favorite)
        
        self._favoriteDB.removeFavorite(authUserId, entityId)
        
        # Decrement user stats by one
        self._userDB.updateUserStats(authUserId, 'num_faves', increment=-1)
        
        # Enrich stamp
        if favorite.stamp_id is not None:
            stamp           = self._stampDB.getStamp(favorite.stamp_id)
            favorite.stamp  = self._enrichStampObjects(stamp, authUserId=authUserId)
            
            # Just in case...
            favorite.stamp.is_fav = False
            
            # Remove activity
            self._activityDB.removeActivity('favorite', authUserId, stampId=stamp.stamp_id)
        
        return favorite
    
    @API_CALL
    def getFavorites(self, authUserId, **kwargs):
        quality     = kwargs.pop('quality', 3)
        
        # Set quality
        if quality == 1:
            favCap  = 50
        elif quality == 2:
            favCap  = 30
        else:
            favCap  = 20
        
        # Limit slice of data returned
        params = self._setSliceParams(kwargs, favCap, 'created')
        
        favoriteData = self._favoriteDB.getFavorites(authUserId, **params)
        
        # Extract entities & stamps
        entityIds   = {}
        stampIds    = {}
        for favorite in favoriteData:
            entityIds[str(favorite.entity.entity_id)] = 1
            if favorite.stamp_id is not None:
                stampIds[str(favorite.stamp_id)] = 1
        
        # Enrich entities
        entities = self._entityDB.getEntities(entityIds.keys())
        
        for entity in entities:
            entityIds[str(entity.entity_id)] = entity.exportSchema(EntityMini())
        
        # Enrich stamps
        stamps = self._stampDB.getStamps(stampIds.keys(), limit=len(stampIds.keys()))
        stamps = self._enrichStampObjects(stamps, authUserId=authUserId, entityIds=entityIds)
        
        for stamp in stamps:
            stampIds[str(stamp.stamp_id)] = stamp
        
        favorites = []
        for favorite in favoriteData:
            # Enrich Entity
            if entityIds[favorite.entity.entity_id] != 1:
                favorite.entity = entityIds[favorite.entity.entity_id]
            else:
                logs.warning('FAV (%s) MISSING ENTITY (%s)' % \
                    (favorite.favorite_id, favorite.entity.entity_id))
            # Add Stamp
            if favorite.stamp_id is not None:
                if stampIds[favorite.stamp_id] != 1:
                    favorite.stamp = stampIds[favorite.stamp_id]
                else:
                    ### TODO: Clean these up if they're missing
                    logs.warning('FAV (%s) MISSING STAMP (%s)' % \
                        (favorite.favorite_id, favorite.stamp_id))
                    favorite.stamp = Stamp()
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
        quality = kwargs.pop('quality', 3)
        
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
        
        # Limit slice of data returned
        params = self._setSliceParams(kwargs, stampCap)
        
        activityData = self._activityDB.getActivity(authUserId, **params)
        
        # Append user objects
        userIds = {}
        stampIds = {}
        for item in activityData:
            if item.user.user_id is not None:
                userIds[item.user.user_id] = 1
            if item.linked_user_id is not None:
                userIds[item.linked_user_id] = 1
            if item.linked_stamp_id is not None:
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
            try:
                if item.genre in ['invite_received', 'invite_sent']:
                    continue
                
                if item.user.user_id is not None:
                    item.user = userIds[item.user.user_id]
                if item.linked_user_id is not None:
                    item.linked_user = userIds[item.linked_user_id]
                if item.linked_stamp_id is not None:
                    item.linked_stamp = stampIds[item.linked_stamp_id]
            except:
                utils.printException()
                continue
            
            activity.append(item)
        
        # Reset activity count
        self._userDB.updateUserStats(authUserId, 'num_unread_news', value=0)
        
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
    
    def _addActivity(self, genre, user_id, recipient_ids, **kwargs):
        if not self._activity or len(recipient_ids) <= 0:
            return
        
        sendAlert                   = kwargs.pop('sendAlert', True)
        checkExists                 = kwargs.pop('checkExists', False)
        
        activity                    = Activity()
        activity.genre              = genre
        activity.user.user_id       = user_id
        activity.linked_user_id     = user_id # TODO: should this always be set here? 
        activity.timestamp.created  = datetime.utcnow()
        
        for k, v in kwargs.iteritems():
            activity[k] = v
        
        self._activityDB.addActivity(recipient_ids, activity, sendAlert=sendAlert, 
                                     checkExists=checkExists)
        
        # increment unread news for all recipients
        self._userDB.updateUserStats(recipient_ids, 'num_unread_news', increment=1)
    
    def _addMentionActivity(self, authUserId, mentions, ignore=None, **kwargs):
        mentionedUserIds = set()
        
        if self._activity == True and mentions is not None and len(mentions) > 0:
            # Note: No activity should be generated for the user initiating the mention
            for mention in mentions:
                if 'user_id' in mention and mention.user_id != authUserId and \
                    (ignore is None or mention.user_id not in ignore):
                    # Check if block exists between user and mentioned user
                    friendship = Friendship(user_id=authUserId, friend_id=mention.user_id)
                    
                    if self._friendshipDB.blockExists(friendship) == False:
                        mentionedUserIds.add(mention['user_id'])
            
            self._addActivity(genre='mention', 
                              user_id=authUserId, 
                              recipient_ids=mentionedUserIds, 
                              **kwargs)
            
            # Increment mentions metric
            self._statsSink.increment('stamped.api.stamps.mentions', len(mentionedUserIds))
        
        return mentionedUserIds
    
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
            entity2 = None
            
            if details is not None:
                entity2 = self._googlePlaces.parseEntity(details, valid=True)
                
                replace  = (entity is None and entity2 is not None)
                replace |= (entity is not None and entity2 is not None and 
                            entity.title.lower() == entity2.title.lower())
                
                if replace:
                    entity = entity2
                    self._googlePlaces.parseEntityDetail(details, entity)
                elif entity is None:
                    logs.warn("_convertSearchId: unable to find search_id in tempentities (%s) " \
                                "and unable to convert google places reference" % search_id)
                elif entity2 is None:
                    logs.warn("_convertSearchId: unable to convert google places reference (%s)" % search_id)
                else:
                    e1 = pformat(entity.value)
                    e2 = pformat(entity2.value)
                    
                    logs.warn("_convertSearchId: inconsistent google places entities %s vs %s (%s)" % (e1, e2, search_id))
        elif search_id.startswith('T_TVDB_'):
            thetvdb_id = search_id[7:]
            
            entity = self._theTVDB.lookup(thetvdb_id)
        
        if entity is None:
            logs.warning("ERROR: could not match temp entity id %s" % search_id)
            return None
        
        del entity.entity_id
        entity = self._entityMatcher.addOne(entity)
        
        assert entity.entity_id is not None
        logs.debug("converted search_id=%s to entity_id=%s" % (search_id, entity.entity_id))
        
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
    
    def _updateUserStats(self):
        userIds = self._userDB._getAllUserIds()
        
        for userId in userIds:
            user = userDB.getUser(userId)
            userData = user.exportSparse()
            
            if 'stats' not in userData:
                continue
            
            stats = userData['stats']
            
            stats_num_stamps        = stats.pop('num_stamps', 0)
            stats_num_credits       = stats.pop('num_credits', 0)
            stats_num_likes_given   = stats.pop('num_likes_given', 0)
            stats_num_friends       = stats.pop('num_friends', 0)
            stats_num_followers     = stats.pop('num_followers', 0)
            
            num_stamps              = self._stampDB.countStamps(userId)
            num_credits             = self._stampDB.countCredits(userId)
            num_likes_given         = self._stampDB.countUserLikes(userId)
            num_friends             = self._friendshipDB.countFriends(userId)
            num_followers           = self._friendshipDB.countFollowers(userId)
            
            if num_stamps != stats_num_stamps:
                logs.info('user id: %s' % userId)
                logs.info('num_stamps: old (%s) new (%s)' % (stats_num_stamps, num_stamps))
                
                self._userDB.updateUserStats(userId, 'num_stamps', num_stamps)
            
            if num_credits != stats_num_credits:
                logs.info('user id: %s' % userId)
                logs.info('num_credits: old (%s) new (%s)' % (stats_num_credits, num_credits))
                
                self._userDB.updateUserStats(userId, 'num_credits', num_credits)
            
            if num_likes_given != stats_num_likes_given:
                logs.info('user id: %s' % userId)
                logs.info('num_likes_given: old (%s) new (%s)' % (stats_num_likes_given, num_likes_given))
                
                self._userDB.updateUserStats(userId, 'num_likes_given', num_likes_given)
            
            if num_friends != stats_num_friends:
                logs.info('user id: %s' % userId)
                logs.info('num_friends: old (%s) new (%s)' % (stats_num_friends, num_friends))
                
                self._userDB.updateUserStats(userId, 'num_friends', num_friends)
            
            if num_followers != stats_num_followers:
                logs.info('user id: %s' % userId)
                logs.info('num_followers: old (%s) new (%s)' % (stats_num_followers, num_followers))
                
                self._userDB.updateUserStats(userId, 'num_followers', num_followers)

