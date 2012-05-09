#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from logs import report

try:
    import utils
    import os, logs, re, time, urlparse
    
    import Blacklist
    import libs.ec2_utils
    import libs.Memcache
    import tasks.APITasks
    
    from datetime               import datetime, timedelta
    from auth                   import convertPasswordForStorage
    from utils                  import lazyProperty
    from functools              import wraps
    from errors                 import *
    from libs.ec2_utils         import is_prod_stack
    from pprint                 import pprint, pformat
    
    from AStampedAPI            import AStampedAPI
    from AAccountDB             import AAccountDB
    from AEntityDB              import AEntityDB
    from APlacesEntityDB        import APlacesEntityDB
    from AUserDB                import AUserDB
    from AStampDB               import AStampDB
    from ACommentDB             import ACommentDB
    from AFavoriteDB            import AFavoriteDB
    from ACollectionDB          import ACollectionDB
    from AFriendshipDB          import AFriendshipDB
    from AActivityDB            import AActivityDB
    from api.Schemas            import *
    from Entity                 import buildEntity, deriveCategoryFromTypes
    
    #resolve classes
    from resolve.EntitySource   import EntitySource
    from resolve                import FullResolveContainer, EntityProxyContainer
    from AmazonSource           import AmazonSource
    from FactualSource          import FactualSource
    from GooglePlacesSource     import GooglePlacesSource
    from iTunesSource           import iTunesSource
    from RdioSource             import RdioSource
    from SpotifySource          import SpotifySource
    from TMDBSource             import TMDBSource
    from TheTVDBSource          import TheTVDBSource
    from StampedSource          import StampedSource

    from Netflix                import *
except Exception:
    report()
    raise

CREDIT_BENEFIT  = 2 # Per credit
LIKE_BENEFIT    = 1 # Per 3 stamps

# TODO (travis): refactor API function calling conventions to place optional last 
# instead of first.

class StampedAPI(AStampedAPI):
    """
        Database-agnostic implementation of the internal API for accessing 
        and manipulating all Stamped backend databases.
    """
    
    def __init__(self, desc, **kwargs):
        AStampedAPI.__init__(self, desc)
        self.lite_mode = kwargs.pop('lite_mode', False)
        self._cache    = libs.Memcache.StampedMemcache()
        
        # Enable / Disable Functionality
        self._activity = True
        self._rollback = []
        
        if utils.is_ec2():
            self._node_name = "unknown"
        else:
            self._node_name = "localhost"
        
        if not self.lite_mode:
            utils.log("StampedAPI running on node '%s'" % (self.node_name))
        
        try:
            self.__is_prod = is_prod_stack()
        except Exception:
            logs.warning('is_prod_stack threw an exception; defaulting to True',exc_info=1)
            self.__is_prod = True
        self.__is_prod = True

        self.__version = 0
        if 'version' in kwargs:
            self.setVersion(kwargs['version'])

    def setVersion(self, version):
        try:
            self.__version = int(version)
        except Exception:
            logs.warning('Invalid API version: %s' % version) 
            raise 

    def getVersion(self):
        return self.__version 
    
    @property
    def node_name(self):
        if self._node_name == 'unknown':
            try:
                stack_info = libs.ec2_utils.get_stack()
                self._node_name = stack_info.instance.name
            except Exception:
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
            except Exception:
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
        now = datetime.utcnow()
        
        account.timestamp.created = now
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
            raise StampedInputError("Invalid format for screen name")
        
        # Check blacklist
        if account.screen_name.lower() in Blacklist.screen_names:
            raise StampedInputError("Blacklisted screen name")
        
        # Validate email address
        account.email = str(account.email).lower().strip()
        if not utils.validate_email(account.email):
            raise StampedInputError("Invalid format for email address")
        
        # Add image timestamp if exists
        if imageData:
            account.image_cache = now
        
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
            
        """
        # Skip this activity item for now 

            ### TODO: What genre are we picking for this activity item?
            self._addActivity(genre='invite_sent', 
                              user_id=invite['user_id'], 
                              recipient_ids=[ account.user_id ])
        
        if len(invitedBy) > 0:
            ### TODO: What genre are we picking for this activity item?
            self._addActivity(genre='invite_received', 
                              user_id=account.user_id, 
                              recipient_ids=invitedBy.keys())
        """
        
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
            except Exception:
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
            raise StampedInputError("Invalid format for screen name")
        
        # Check blacklist
        if account.screen_name.lower() in Blacklist.screen_names:
            raise StampedInputError("Blacklisted screen name")
        
        # Validate email address
        account.email = str(account.email).lower().strip()
        if not utils.validate_email(account.email):
            raise StampedInputError("Invalid format for email address")
        
        self._accountDB.updateAccount(account)
        
        # Asynchronously update profile picture link if screen name has changed
        if account.screen_name.lower() != old_screen_name.lower():
            tasks.invoke(tasks.APITasks.updateAccountSettings, args=[
                         old_screen_name.lower(), account.screen_name.lower()])
        
        return account
    
    @API_CALL
    def updateAccountSettingsAsync(self, old_screen_name, new_screen_name):
        self._imageDB.changeProfileImageName(old_screen_name.lower(), new_screen_name.lower())
    
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
            raise StampedInputError("Invalid format for colors")
        
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
    def updateProfileImage(self, authUserId, schema):
        if schema.profile_image is not None:
            return self._addProfileImage(schema.profile_image, user_id=authUserId)
        
        if schema.temp_image_url is None:
            raise StampedInputError("if no image data is provided, a temp_image_url is required")
        
        user = self._userDB.getUser(authUserId)
        screen_name = user.screen_name
        
        image_cache = datetime.utcnow()
        user.image_cache = image_cache
        self._accountDB.updateUserTimestamp(user.user_id, 'image_cache', image_cache)
        
        tasks.invoke(tasks.APITasks.updateProfileImage, args=[screen_name, schema.temp_image_url])
        
        return user
    
    @API_CALL
    def updateProfileImageAsync(self, screen_name, image_url):
        self._imageDB.addResizedProfileImages(screen_name.lower(), image_url)
    
    def _addProfileImage(self, data, user_id=None, screen_name=None):
        assert user_id is not None or screen_name is not None
        user = None
        
        if user_id is not None:
            user = self._userDB.getUser(user_id)
            screen_name = user.screen_name
        
        image = self._imageDB.getImage(data)
        image_url = self._imageDB.addProfileImage(screen_name.lower(), image)
        
        if user is not None:
            image_cache = datetime.utcnow()
            user.image_cache = image_cache
            self._accountDB.updateUserTimestamp(user.user_id, 'image_cache', image_cache)
        
        tasks.invoke(tasks.APITasks.updateProfileImage, args=[screen_name, image_url])
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
                    logs.info('Blacklisted login: %s' % login)
            else:
                raise
            return user
        except Exception:
            if valid == True:
                msg = "Login info does not exist"
                logs.debug(msg)
                raise KeyError(msg)
            else:
                raise StampedInputError("Invalid input")
    
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


    def _getTwitterFriends(self, key, secret, followers=False):
        if key is None or secret is None:
            raise StampedIllegalActionError("Connecting to Twitter requires a valid key / secret")
        
        baseurl = 'https://api.twitter.com/1/friends/ids.json'
        if followers:
            baseurl = 'https://api.twitter.com/1/followers/ids.json'

        twitterIds = []
        cursor = -1

        while True:
            url = '%s?cursor=%s' % (baseurl, cursor)
            result = utils.getTwitter(url, key, secret)
            if 'ids' in result:
                twitterIds = twitterIds + result['ids']

            # Break if no cursor
            if 'next_cursor' not in result or result['next_cursor'] == 0:
                break
            cursor = result['next_cursor']

        return self._userDB.findUsersByTwitter(twitterIds)

    def _getFacebookFriends(self, token):
        if token is None:
            raise StampedIllegalActionError("Connecting to Facebook requires a valid token")
        
        friends     = []
        facebookIds = []
        params      = {}
        
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
            facebookIds.append(friend['id'])
        
        return self._userDB.findUsersByFacebook(facebookIds)
    
    @API_CALL
    def updateLinkedAccounts(self, authUserId, **kwargs):
        twitter         = kwargs.pop('twitter', None)
        twitterAuth     = kwargs.pop('twitterAuth', None)
        facebook        = kwargs.pop('facebook', None)
        facebookAuth    = kwargs.pop('facebookAuth', None)
        netflixAuth     = kwargs.pop('netflixAuth', None)
        
        self._accountDB.updateLinkedAccounts(authUserId, twitter=twitter, facebook=facebook, netflix=netflixAuth)
        
        # Alert Facebook asynchronously
        if isinstance(facebookAuth, Schema) and facebookAuth.facebook_token is not None:
            kwargs = {'facebookToken': facebookAuth.facebook_token}
            tasks.invoke(tasks.APITasks.alertFollowersFromFacebook, args=[authUserId], kwargs=kwargs)
        
        # Alert Twitter asynchronously
        if isinstance(twitterAuth, Schema) and twitterAuth.twitter_key is not None:
            kwargs = {'twitterKey': twitterAuth.twitter_key, 'twitterSecret': twitterAuth.twitter_secret}
            tasks.invoke(tasks.APITasks.alertFollowersFromTwitter, args=[authUserId], kwargs=kwargs)
        
        return True
    
    @API_CALL
    def removeLinkedAccount(self, authUserId, linkedAccount):
        if linkedAccount not in ['facebook', 'twitter']:
            raise StampedIllegalActionError("Invalid linked account: %s" % linkedAccount)
        
        self._accountDB.removeLinkedAccount(authUserId, linkedAccount)
        return True
    
    ### DEPRECATED
    @API_CALL
    def alertFollowersFromTwitter(self, authUserId, twitterIds):
        account = self._accountDB.getAccount(authUserId)
        if account.twitter_alerts_sent == True or not account.twitter_screen_name:
            return False
        
        # Perform the actual alerts asynchronously
        tasks.invoke(tasks.APITasks.alertFollowersFromTwitter, args=[authUserId, twitterIds])
        
        return True
    
    @API_CALL
    def alertFollowersFromTwitterAsync(self, authUserId, twitterIds=None, twitterKey=None, twitterSecret=None):

        ### TODO: Deprecate passing parameter "twitterIds"
        
        account   = self._accountDB.getAccount(authUserId)

        # Only send alert once (when the user initially connects to Twitter)
        if account.twitter_alerts_sent == True or not account.twitter_screen_name:
            return False
        
        users = []

        # Grab friend list from Twitter API
        if twitterKey is not None and twitterSecret is not None:
            users = self._getTwitterFriends(twitterKey, twitterSecret, followers=True)
        elif twitterIds is not None:
            ### DEPRECATED
            users = self._userDB.findUsersByTwitter(twitterIds)
        
        # Send alert to people not already following the user
        followers = self._friendshipDB.getFollowers(authUserId)
        userIds = []
        for user in users:
            if user.user_id not in followers:
                userIds.append(user.user_id)
        
        # Generate activity item
        self._addActivity(verb          = 'friend_twitter', 
                          userId        = authUserId, 
                          recipientIds  = userIds,
                          body          = 'Your Twitter friend %s joined Stamped.' % account.twitter_screen_name)
        
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
    def alertFollowersFromFacebookAsync(self, authUserId, facebookIds=None, facebookToken=None):
        
        ### TODO: Deprecate passing parameter "facebookIds"
        
        account   = self._accountDB.getAccount(authUserId)
        
        # Only send alert once (when the user initially connects to Facebook)
        if account.facebook_alerts_sent == True or not account.facebook_name:
            return
        
        users = []

        # Grab friend list from Facebook API
        if facebookToken is not None:
            users = self._getFacebookFriends(facebookToken)
        elif facebookIds is not None:
            ### DEPRECATED
            users = self._userDB.findUsersByFacebook(facebookIds)
        
        # Send alert to people not already following the user
        followers = self._friendshipDB.getFollowers(authUserId)
        userIds = []
        for user in users:
            if user.user_id not in followers:
                userIds.append(user.user_id)
        
        # Generate activity item
        self._addActivity(verb          = 'friend_facebook', 
                          userId        = authUserId, 
                          recipientIds  = userIds,
                          body          = 'Your Facebook friend %s joined Stamped.' % account.facebook_name)
        
        facebook = FacebookAccountSchema(facebook_alerts_sent=True)
        self._accountDB.updateLinkedAccounts(authUserId, facebook=facebook)

    @API_CALL
    def addToNetflixInstant(self, authUserId, netflixId):
        """
         Asynchronously add an entity to the user's netflix queue
        """
        account   = self._accountDB.getAccount(authUserId)

        # TODO return HTTPAction to invoke sign in if credentials are unavailable

        logs.info('netflix_user_id: %s    netflix_token: %s   netflix_secret: %s' %
                    (account.netflix_user_id, account.netflix_token, account.netflix_secret))

        if account.netflix_user_id == None or account.netflix_token == None or account.netflix_secret == None:
            logs.info('Returning because of missing account credentials')
            return None

        netflix = globalNetflix()
        logs.info('About to add to Queue')
        result = netflix.addToQueue(account.netflix_user_id, account.netflix_token, account.netflix_secret, netflixId)
        logs.info('successfully added to queue')

        # TODO check results



#        # Only send alert once (when the user initially connects to Twitter)
#        if account.twitter_alerts_sent == True or not account.twitter_screen_name:
#            return False
#
#        users = []
#
#        # Grab friend list from Twitter API
#        if twitterKey is not None and twitterSecret is not None:
#            users = self._getTwitterFriends(twitterKey, twitterSecret, followers=True)
#        elif twitterIds is not None:
#            ### DEPRECATED
#            users = self._userDB.findUsersByTwitter(twitterIds)
#
#        # Send alert to people not already following the user
#        followers = self._friendshipDB.getFollowers(authUserId)
#        userIds = []
#        for user in users:
#            if user.user_id not in followers:
#                userIds.append(user.user_id)
#
#        # Generate activity item
#        self._addActivity(verb          = 'friend_twitter',
#            userId        = authUserId,
#            recipientIds  = userIds,
#            body          = 'Your Twitter friend %s joined Stamped.' % account.twitter_screen_name)
#
#        twitter = TwitterAccountSchema(twitter_alerts_sent=True)
#        self._accountDB.updateLinkedAccounts(authUserId, twitter=twitter)

        return True

    @API_CALL
    def removeFromNetflixInstant(self, authUserId, netflixId=None, netflixKey=None, netflixSecret=None):

        account   = self._accountDB.getAccount(authUserId)

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
    
    def _getUserFromIdOrScreenName(self, userTiny):
        if not isinstance(userTiny, SchemaElement):
            userTiny    = UserTiny(userTiny)
        
        if userTiny.user_id is None and userTiny.screen_name is None:
            raise StampedInputError("Required field missing (user id or screen name)")
        
        if userTiny.user_id is not None:
            return self._userDB.getUser(userTiny.user_id)
        
        return self._userDB.getUserByScreenName(userTiny.screen_name)

    def _getUserStampDistribution(self, userId):

        stampIds    = self._collectionDB.getUserStampIds(userId)
        stamps      = self._stampDB.getStamps(stampIds, limit=len(stampIds))
        
        categories  = {}
        num_stamps  = len(stamps)
        
        for stamp in stamps:
            category = deriveCategoryFromTypes(stamp.entity.types)
            categories.setdefault(category, 0)
            categories[category] += 1

        return [ { 'category': k, 'count': v } for k, v in categories.iteritems() ] 
        
    
    ### PUBLIC
    
    @API_CALL
    def getUser(self, userRequest, authUserId=None):
        user = self._getUserFromIdOrScreenName(userRequest)
        
        if user.privacy == True:
            if authUserId is None:
                raise StampedPermissionsError("Insufficient privileges to view user")
            
            friendship = Friendship(user_id=authUserId, friend_id=user.user_id)
            
            if not self._friendshipDB.checkFriendship(friendship):
                raise StampedPermissionsError("Insufficient privileges to view user")
        
        if self.__version > 0 and len(user.distribution) == 0:
            user.distribution = self._getUserStampDistribution(user.user_id)
        
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
                except Exception:
                    pass
        
        if isinstance(screenNames, list):
            for screenName in screenNames:
                try:
                    result.append(usersByScreenNames[screenName])
                except Exception:
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
    def findUsersByTwitter(self, authUserId, twitterIds=None, twitterKey=None, twitterSecret=None):
        ### TODO: Add check for privacy settings?
        
        users = []

        # Grab friend list from Facebook API
        if twitterKey is not None and twitterSecret is not None:
            users = self._getTwitterFriends(twitterKey, twitterSecret)
        elif twitterIds is not None:
            ### DEPRECATED
            users = self._userDB.findUsersByTwitter(twitterIds, limit=100)
        
        return users
    
    @API_CALL
    def findUsersByFacebook(self, authUserId, facebookIds=None, facebookToken=None):
        ### TODO: Add check for privacy settings?
        
        users = []

        # Grab friend list from Facebook API
        if facebookToken is not None:
            users = self._getFacebookFriends(facebookToken)
        elif facebookIds is not None:
            ### DEPRECATED
            users = self._userDB.findUsersByFacebook(facebookIds, limit=100)
        
        return users
    
    @API_CALL
    def searchUsers(self, authUserId, query, limit, relationship):
        limit = self._setLimit(limit, cap=10)
        
        ### TODO: Add check for privacy settings
        
        return self._userDB.searchUsers(authUserId, query, limit, relationship)
    
    @API_CALL
    def getSuggestedUsers(self, authUserId, request):
        if request.personalized:
            suggestions = self._friendshipDB.getSuggestedUserIds(authUserId, request)
            output      = []
            
            for suggestion in suggestions:
                user_id      = suggestion[0]
                explanations = suggestion[1]
                user         = self._userDB.getUser(user_id)
                
                # TODO: use user's bio if no explanations are available
                output.append([ user, explanations ])
            
            return output
        else:
            suggested = {
                'mariobatali':      1, 
                'nymag':            2,
                'UrbanDaddy':       3,
                'parislemon':       4, 
                'michaelkors':      5, 
                'petertravers':     6,
                'rebeccaminkoff':   7, 
                'austinchronicle':  8,
            }
            
            users = self.getUsers(None, suggested.keys(), authUserId)
            return sorted(users, key=lambda k: suggested[k['screen_name']])
    
    @API_CALL
    def ignoreSuggestedUsers(self, authUserId, user_ids):
        # TODO
        raise NotImplementedError()
    
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
            raise StampedIllegalActionError("Illegal friendship: you can't follow yourself!")
        
        friendship = Friendship(user_id=authUserId, friend_id=user.user_id)
        
        # Check if friendship already exists
        if self._friendshipDB.checkFriendship(friendship) == True:
            logs.info("Friendship exists")
            return user
        
        # Check if block exists between authenticating user and user
        if self._friendshipDB.blockExists(friendship) == True:
            raise StampedIllegalActionError("Block exists")
        
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
    def addFriendshipAsync(self, authUserId, userId):
        if self._activity:
            # Add activity for followed user
            self._addActivity(verb          = 'follow', 
                              userId        = authUserId, 
                              friendId      = userId)
            
            # Remove 'friend' activity item
            self._activityDB.removeActivity('friend', authUserId, friendId=userId)
        
        # Add stamps to Inbox
        stampIds = self._collectionDB.getUserStampIds(userId)
        self._stampDB.addInboxStampReferencesForUser(authUserId, stampIds)
        
        # Increment stats for both users
        self._userDB.updateUserStats(authUserId, 'num_friends',   increment=1)
        self._userDB.updateUserStats(userId,     'num_followers', increment=1)
    
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
    def removeFriendshipAsync(self, authUserId, userId):
        # Decrement stats for both users
        self._userDB.updateUserStats(authUserId, 'num_friends',   increment=-1)
        self._userDB.updateUserStats(userId,     'num_followers', increment=-1)
        
        # Remove stamps from Inbox
        stampIds = self._collectionDB.getUserStampIds(userId)
        self._stampDB.removeInboxStampReferencesForUser(authUserId, stampIds)
        
        # Remove activity
        self._activityDB.removeActivity('follow', authUserId, friendId=userId)
    
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
                raise StampedPermissionsError("Insufficient privileges to check friendship")
        
        if userB.privacy == True and authUserId != userB.user_id:
            check = Friendship(user_id=authUserId, friend_id=userB.user_id)
            
            if not self._friendshipDB.checkFriendship(check):
                raise StampedPermissionsError("Insufficient privileges to check friendship")
        
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
            raise StampedInputError("Invalid format for email address")
        
        if self._inviteDB.checkInviteExists(email, authUserId):
            raise StampedInputError("Invite already exists")
        
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
            raise StampedInputError("Required field missing (entity_id or search_id)")
        
        if entityId is None:
            entityId = searchId
        
        return self._getEntity(entityId)
    
    def _getEntity(self, entityId):
        if entityId is not None and entityId.startswith('T_'):
            entityId = self._convertSearchId(entityId)
        else:
            self.mergeEntityId(entityId)
        
        return self._entityDB.getEntity(entityId)
    
    @API_CALL
    def addEntity(self, entity):
        entity.timestamp.created = datetime.utcnow()
        entity = self._entityDB.addEntity(entity)
        return entity
    
    @API_CALL
    def getEntity(self, entityRequest, authUserId=None):
        entity = self._getEntityFromRequest(entityRequest)
        
        if self.__version > 0 and entity.isType('artist'):
            albumIds = {}
            for album in entity.albums:
                if album.entity_id is not None:
                    albumIds[album.entity_id] = None
            try:
                albums = self._entityDB.getEntities(albumIds.keys())
            except:
                albums = []

            for album in albums:
                albumIds[album.entity_id] = album 

            enrichedAlbums = []
            for album in entity.albums:
                if album.entity_id is not None and album.entity_id in albumIds and albumIds[album.entity_id] is not None:
                    enrichedAlbums.append(albumIds[album.entity_id])
                else:
                    enrichedAlbums.append(album)

            entity.albums = enrichedAlbums

        ### TODO: Check if user has access to this entity?
        return entity
    
    @API_CALL
    def updateCustomEntity(self, authUserId, entityId, data):
        ### TODO: Reexamine how updates are done
        entity = self._entityDB.getEntity(entityId)
        
        # Check if user has access to this entity
        if entity.generated_by != authUserId or entity.generated_by is None:
            raise StampedPermissionsError("Insufficient privileges to update custom entity")
        
        # Try to import as a full entity
        for k, v in data.iteritems():
            entity[k] = v
        
        entity.timestamp.modified = datetime.utcnow()
        self._entityDB.updateEntity(entity)
        
        return entity

    @API_CALL
    def updateEntity(self, data, auth):
        entity = self._entityDB.getEntity(data['entity_id'])

        # Assert that it's the same one (i.e. hasn't been tombstoned)
        if entity.entity_id != data['entity_id']:
            logs.warning('Cannot update entity %s - old entity has been tombstoned' % entity.entity_id)
            raise Exception
        
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
    
    @lazyProperty
    def _entitySearch(self):
        from EntitySearch import EntitySearch
        return EntitySearch()
    
    @API_CALL
    def searchEntities(self, 
                       query, 
                       coords=None, 
                       authUserId=None, 
                       category=None, 
                       subcategory=None):
        entities = self._entitySearch.searchEntities(query, 
                                                     limit=10, 
                                                     coords=coords, 
                                                     category=category, 
                                                     subcategory=subcategory)
        
        results = []
        process = 5
        
        for entity in entities:
            distance = None
            try:
                if coords is not None and entity.coordinates is not None:
                    a = (coords['lat'], coords['lng'])
                    b = (entity.coordinates.lat, entity.coordinates.lng)
                    distance = abs(utils.get_spherical_distance(a, b) * 3959)
            except Exception:
                pass
            
            results.append((entity, distance))
            
            process -= 1
            if process > 0:
                # asynchronously merge & enrich entity
                self.mergeEntity(entity)
        
        return results
    
    @API_CALL
    def searchEntitiesOld(self, 
                          query, 
                          coords=None, 
                          authUserId=None, 
                          category=None, 
                          subcategory=None, 
                          prefix=False, 
                          local=False, 
                          full=True, 
                          page=0, 
                          limit=10):
        results = self._entitySearcher.getSearchResults(query=query, 
                                                        coords=coords, 
                                                        category_filter=category, 
                                                        subcategory_filter=subcategory, 
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
                     category=None, 
                     subcategory=None, 
                     prefix=False, 
                     full=True, 
                     page=0, 
                     limit=10):
        results = self._entitySearcher.getSearchResults(query='', 
                                                        coords=coords, 
                                                        category_filter=category, 
                                                        subcategory_filter=subcategory, 
                                                        full=full, 
                                                        prefix=prefix, 
                                                        local=True, 
                                                        user=authUserId, 
                                                        limit=((page + 1) * limit))
        offset  = limit * page
        results = results[offset : offset + limit]
        
        return results
    
    @API_CALL
    def getSuggestedEntities(self, authUserId, suggested):
        coords = (suggested.coordinates.lat, suggested.coordinates.lng)
        
        return self._suggestedEntities.getSuggestedEntities(authUserId, 
                                                            coords=coords, 
                                                            category=suggested.category, 
                                                            subcategory=suggested.subcategory, 
                                                            limit=suggested.limit)

    @API_CALL
    def completeAction(self, authUserId, **kwargs):
        action      = kwargs.pop('action', None)
        source      = kwargs.pop('source', None)
        sourceId    = kwargs.pop('source_id', None)
        entityId    = kwargs.pop('entity_id', None)
        userId      = kwargs.pop('user_id', None)
        stampId     = kwargs.pop('stamp_id', None)

        actions = set([
            # 'link',
            # 'phone',
            # 'stamped_view_entity',
            # 'stamped_view_stamp',
            # 'stamped_view_user',
            'listen',
            'playlist',
            'download',
            'reserve',
            'menu',
            'buy',
            'watch',
            'tickets',
        ])

        # For now, only complete the action if it's associated with an entity and a stamp
        if stampId is not None:
            stamp   = self._stampDB.getStamp(stampId)
            user    = self._userDB.getUser(stamp.user.user_id)
            entity  = self._entityDB.getEntity(stamp.entity.entity_id)

            if action in actions and authUserId != stamp.user.user_id:
                self._addActivity(verb          = 'action_%s' % action, 
                                  userId        = authUserId, 
                                  friendId      = stamp.user.user_id, 
                                  stampId       = stamp.stamp_id)

        return True

    @API_CALL
    def entityStampedBy(self, entityId, authUserId=None, limit=10):
        try:
            stats = self._entityStatsDB.getEntityStats(entityId)
        except StampedUnavailableError:
            stats = self.updateEntityStatsAsync(entityId)

        popularUserIds = map(str, stats.popular_users[:limit])
        popularStamps = self._stampDB.getStampsFromUsersForEntity(popularUserIds, entityId)
        popularStamps.sort(key=lambda x: popularUserIds.index(x.user.user_id))

        result = {}
        result['all_preview']   = self._enrichStampObjects(popularStamps)
        result['all_count']     = stats.num_stamps

        if authUserId is None:
            return result

        friendUserIds   = self._friendshipDB.getFriends(authUserId)
        friendStamps    = self._stampDB.getStampsFromUsersForEntity(friendUserIds, entityId)

        result['friend_preview']    = self._enrichStampObjects(friendStamps[:limit]) 
        result['friend_count']      = len(friendStamps)

        fofUserIds = self._friendshipDB.getFriendsOfFriends(authUserId, distance=2, inclusive=False)
        fofOverlap = list(set(fofUserIds).intersection(map(str, stats.popular_users)))
        fofStamps = self._stampDB.getStampsFromUsersForEntity(fofOverlap, entityId)

        result['fof_preview']   = self._enrichStampObjects(fofStamps[:limit])
        result['fof_count']     = len(fofStamps)

        return result


    def updateEntityStatsAsync(self, entityId):
        numStamps = self._stampDB.countStampsForEntity(entityId)
        popularUserIds = self._stampDB.getPopularityForEntity(entityId)

        try:
            stats = self._entityStatsDB.getEntityStats(entityId)
            stats.num_stamps = numStamps
            stats.popular_users = popularUserIds
            self._entityStatsDB.updateNumStamps(entityId, numStamps)
            self._entityStatsDB.setPopular(entityId, popularUserIds)
        except StampedUnavailableError:
            stats = EntityStats()
            stats.entity_id = entityId
            stats.num_stamps = numStamps
            stats.popular_users = popularUserIds
            self._entityStatsDB.addEntityStats(stats)
        return stats




    
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
    
    def _extractMentions(self, text, screenNames={}):
        mentions = [] 
        
        # Run through and grab mentions
        for user in self._user_regex.finditer(text):
            data = {}
            data['indices'] = [user.start(), user.end()]
            data['screen_name'] = user.groups()[0]
            
            if data['screen_name'] in screenNames:
                data['user_id'] = screenNames[data['screen_name']]
            else:
                try:
                    user = self._userDB.getUserByScreenName(data['screen_name'])
                    data['user_id'] = user.user_id
                except Exception:
                    logs.warning("User not found (%s)" % data['screen_name'])
            
            if data['screen_name'] not in screenNames.keys() and data['user_id'] is not None:
                screenNames[data['screen_name']] = data['user_id']

            mentions.append(data)
        
        return mentions
    
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

        ### HACK UNTIL PAGING ISSUE IS RESOLVED
        origLen = len(stampData)

        singleStamp = False
        if not isinstance(stampData, list):
            singleStamp = True
            stampData   = [stampData]
        
        # Users
        if len(userIds) == 0:
            for stamp in stampData:
                # Grab user_id from stamp
                userIds[stamp.user_id] = 1
                
                # Grab user_id from credit
                for credit in stamp.credit:
                    userIds[credit.user_id] = 1
                
                # Grab user_id from comments
                for comment in stamp.previews.comments:
                    userIds[comment.user_id] = 1
        
        # Entities
        if len(entityIds) == 0:
            for stamp in stampData:
                # Grab entity_id from stamp
                entityIds[stamp.entity_id] = 1
            
            # TODO: don't fetch entity if it's already filled in
            entities = self._entityDB.getEntities(entityIds.keys())
            
            for entity in entities:
                entityIds[entity.entity_id] = entity

        # Likes
        ### TODO: Rewrite to minimze db calls
        likeUserIds = {}
        for stamp in stampData:
            likeUserIds[stamp.stamp_id] = self._stampDB.getStampLikes(stamp.stamp_id)[:10]
            for likeUserId in likeUserIds[stamp.stamp_id]:
                if likeUserId not in userIds:
                    userIds[likeUserId] = 1

        # Todos
        ### TODO: Rewrite to minimize db calls
        todoUserIds = {}
        for stamp in stampData:
            todoUserIds[stamp.stamp_id] = self._favoriteDB.getFavoritesFromEntityId(stamp.entity.entity_id)[:10]
            for todoUserId in todoUserIds[stamp.stamp_id]:
                if todoUserId not in userIds:
                    userIds[todoUserId] = 1

        # Credit
        creditIds = {}
        for stamp in stampData:
            creditIds[stamp.stamp_id] = self._stampDB.getRestamps(stamp.user.user_id, stamp.entity.entity_id, limit=10)
            for creditItem in creditIds[stamp.stamp_id]:
                if creditItem.user.user_id not in userIds:
                    userIds[creditItem.user.user_id] = 1

        # Users
        if 1 in userIds.values():
            users = self._userDB.lookupUsers(userIds.keys(), None)
            for user in users:
                userIds[user.user_id] = user.exportSchema(UserMini())

        
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
                continue
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
            if len(stamp.previews.comments) > 0:
                comments = []
                
                for i in xrange(len(stamp.previews.comments)):
                    commentingUser = userIds[stamp.previews.comments[i].user_id]
                    
                    if commentingUser != 1:
                        stamp.previews.comments[i].user = commentingUser
                        comments.append(stamp.previews.comments[i])
                
                stamp.previews.comments = comments

            # Add likes
            stamp.previews.likes = []
            for likeUserId in likeUserIds[stamp.stamp_id]:
                assert userIds[likeUserId] != 1
                stamp.previews.likes.append(userIds[likeUserId])

            # Add todos
            stamp.previews.todos = []
            for todoUserId in todoUserIds[stamp.stamp_id]:
                assert userIds[todoUserId] != 1
                stamp.previews.todos.append(userIds[todoUserId])

            # Add restamps
            stamp.previews.credits = []
            for credit in creditIds[stamp.stamp_id]:
                assert userIds[credit.user.user_id] != 1
                assert entityIds[credit.entity.entity_id] != 1
                credit.user = userIds[credit.user.user_id]
                credit.entity = entityIds[credit.entity.entity_id]
                stamp.previews.credits.append(credit)
            
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

        ### HACK UNTIL PAGING ISSUE IS RESOLVED
        while len(stamps) < origLen:
            stamps.append(stamps[len(stamps)-1])

        return stamps
    
    def getStampBadges(self, stamp):
        userId = stamp.user_id
        badges  = []
        
        if stamp.stamp_num == 1:
            badges.append(Badge(dict(
                user_id = userId, 
                genre   = "user_first_stamp", 
            )))
        
        stamps = self._stampDB.getStampsForEntity(stamp.entity.entity_id)
        
        if len(stamps) == 0:
            badges.append(Badge(dict(
                user_id = userId, 
                genre   = "entity_first_stamp", 
            )))
        else:
            friendIds       = set(self._friendshipDB.getFriends(stamp.user.user_id))
            stampUserIds    = set(map(lambda s: s.user.user_id, stamps))
            
            if friendIds.intersection(stampUserIds) == 0:
                badges.append(Badge(dict(
                    user_id = userId, 
                    genre   = "friends_first_stamp", 
                )))
        
        return badges
    
    @API_CALL
    @HandleRollback
    def addStamp(self, authUserId, entityRequest, data):
        user        = self._userDB.getUser(authUserId)
        entity      = self._getEntityFromRequest(entityRequest)

        userIds     = { user.user_id : user.exportSchema(UserMini()) }
        entityIds   = { entity.entity_id : entity }
        
        blurbData   = data.pop('blurb',  None)
        creditData  = data.pop('credit', None)

        imageData   = data.pop('image',  None)
        imageUrl    = data.pop('temp_image_url',    None)
        imageWidth  = data.pop('temp_image_width',  None)
        imageHeight = data.pop('temp_image_height', None)
        imageExists = False

        now         = datetime.utcnow()
        
        # Check if the user has already stamped this entity
        stampExists = self._stampDB.checkStamp(user.user_id, entity.entity_id)
        
        # Check to make sure the user has stamps left
        if not stampExists and user.num_stamps_left <= 0:
            raise StampedIllegalActionError("No more stamps remaining")

        # Build content
        content = StampContent()
        if blurbData is not None:
            content.blurb = blurbData.strip()
            content.mentions = self._extractMentions(blurbData)
            content.timestamp.created = now

        # Add image to stamp
        if imageData is not None:
            raise NotImplementedError()
            """
            if image_url is not None:
                raise StampedInputError("either an image may be uploaded with the stamp itself or an " + 
                                 "external image may be referenced, but not both")
            
            ### TODO: Rollback: Delete Image
            image     = self._imageDB.getImage(imageData)
            image_url = self._imageDB.addStampImage(stamp.stamp_id, image)
            
            image_width, image_height = image.size
            """
        elif imageUrl is not None:
            ### TODO: Ensure external image exists
            """
            # TODO: 
            response = utils.getHeadRequest(image_url)
            
            if response is None:
                raise StampedInputError("unable to access specified stamp image '%s'" % image_url)
            else:
                content_type = response.info().getheader('Content-Type')
                
                if content_type != "image/jpeg":
                    raise StampedInputError("invalid external image format; content-type must be image/jpeg")
            """
            pass
        
        if imageUrl is not None:
            if imageWidth is None or imageHeight is None:
                raise StampedInputError("invalid image dimensions")
            
            # Add image dimensions to stamp object
            image           = ImageSchema()
            size            = ImageSizeSchema()
            size.width      = imageWidth
            size.height     = imageHeight
            image.sizes.append(size)
            content.images  = [ image ]

            imageExists     = True

        # Update content if stamp exists
        if stampExists:
            stamp                       = self._stampDB.getStampFromUserEntity(user.user_id, entity.entity_id)
            stamp.timestamp.stamped     = now
            stamp.timestamp.modified    = now 
            stamp.num_blurbs            = stamp.num_blurbs + 1 if stamp.num_blurbs is not None else 2
            stamp.contents.append(content)

            ### TODO: Extract credit
            if creditData is not None:
                raise NotImplementedError("Add credit for second stamp!")

            stamp = self._stampDB.updateStamp(stamp)

        # Build new stamp
        else:
            stamp                       = Stamp()
            stamp.user_id               = user.user_id
            stamp.entity                = entity
            stamp.timestamp.created     = now
            stamp.timestamp.stamped     = now
            stamp.timestamp.modified    = now 
            stamp.stamp_num             = user.num_stamps_total + 1
            stamp.num_blurbs            = 1
            stamp.badges                = self.getStampBadges(stamp)
            stamp.contents.append(content)

            # Extract credit
            if creditData is not None:
                stamp.credit = self._extractCredit(creditData, user.user_id, entity.entity_id, userIds)

            stamp = self._stampDB.addStamp(stamp)
            self._rollback.append((self._stampDB.removeStamp, {'stampId': stamp.stamp_id}))

        # Resize image
        if imageExists:
            self._statsSink.increment('stamped.api.stamps.images')
            imageId = "%s-%s" % (stamp.stamp_id, int(time.mktime(now.timetuple())))
            tasks.invoke(tasks.APITasks.addResizedStampImages, args=[imageId, imageUrl])

        # Add stats
        self._statsSink.increment('stamped.api.stamps.category.%s' % entity.category)
        self._statsSink.increment('stamped.api.stamps.subcategory.%s' % entity.subcategory)

        # Enrich linked user, entity, favorites, etc. within the stamp
        ### TODO: Pass userIds (need to scrape existing credited users)
        stamp = self._enrichStampObjects(stamp, authUserId=authUserId, entityIds=entityIds)

        if not stampExists:
            # Add a reference to the stamp in the user's collection
            self._rollback.append((self._stampDB.removeUserStampReference, \
                {'stampId': stamp.stamp_id, 'userId': user.user_id}))
            self._stampDB.addUserStampReference(user.user_id, stamp.stamp_id)
            
            # Update user stats 
            self._userDB.updateUserStats(authUserId, 'num_stamps',       increment=1)
            self._userDB.updateUserStats(authUserId, 'num_stamps_left',  increment=-1)
            self._userDB.updateUserStats(authUserId, 'num_stamps_total', increment=1)
            distribution = self._getUserStampDistribution(authUserId)
            self._userDB.updateUserStats(authUserId, 'distribution',     value=distribution)
            
            # Asynchronously add references to the stamp in follower's inboxes and 
            # add activity for credit and mentions
            tasks.invoke(tasks.APITasks.addStamp, args=[user.user_id, stamp.stamp_id])

        return stamp
    
    @API_CALL
    def addStampAsync(self, authUserId, stampId):
        stamp   = self._stampDB.getStamp(stampId)
        entity  = self._entityDB.getEntity(stamp.entity.entity_id)
        
        # Add references to the stamp in all relevant inboxes
        followers = self._friendshipDB.getFollowers(authUserId)
        followers.append(authUserId)
        self._stampDB.addInboxStampReference(followers, stampId)
        
        # If stamped entity is on the to do list, mark as complete
        try:
            self._favoriteDB.completeFavorite(entity.entity_id, authUserId)
            if entity.entity_id != stamp.entity.entity_id:
                self._favoriteDB.completeFavorite(stamp.entity.entity_id, authUserId)
        except Exception:
            pass

        ### TODO: Update stamp with new entity_id if old one is tombstoned
        
        creditedUserIds = set()
        
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
                creditedUserIds.add(item.user_id)
                
                # Add stats
                self._statsSink.increment('stamped.api.stamps.credit')
                
                # Update credited user stats
                self._userDB.updateUserStats(item.user_id, 'num_credits',     increment=1)
                self._userDB.updateUserStats(item.user_id, 'num_stamps_left', increment=CREDIT_BENEFIT)
        
        # Note: No activity should be generated for the user creating the stamp
        
        # Add activity for credited users
        if len(creditedUserIds) > 0:
            self._addActivity(verb          = 'restamp', 
                              userId        = authUserId, 
                              recipientIds  = list(creditedUserIds), 
                              stampId       = stamp.stamp_id, 
                              benefit       = CREDIT_BENEFIT)
        
        # Add activity for mentioned users
        mentionedUserIds = set()
        for item in stamp.contents[-1].mentions:
            if item.user_id is not None and item.user_id != authUserId and item.user_id not in creditedUserIds:
                mentionedUserIds.add(item.user_id)
        if len(mentionedUserIds) > 0:
            self._addActivity(verb          = 'mention', 
                              userId        = authUserId, 
                              recipientIds  = list(mentionedUserIds), 
                              stampId       = stamp.stamp_id)

        # Update entity stats
        tasks.invoke(tasks.APITasks.updateEntityStats, args=[stamp.entity_id])

    
    @API_CALL
    def addResizedStampImagesAsync(self, imageId, imageUrl):
        assert imageUrl is not None, "stamp image url unavailable!"
        
        self._imageDB.addResizedStampImages(imageUrl, imageId)
    
    @API_CALL
    def updateStamp(self, authUserId, stampId, data):
        raise NotImplementedError
        """
        stamp       = self._stampDB.getStamp(stampId)
        user        = self._userDB.getUser(authUserId)
        
        blurbData   = data.pop('blurb', stamp.blurb)
        creditData  = data.pop('credit', None)
        
        # Verify user can modify the stamp
        if authUserId != stamp.user_id:
            raise StampedPermissionsError("Insufficient privileges to modify stamp")
        
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
                          stamp_id=stamp.stamp_id, 
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
                              stamp_id=stamp.stamp_id)
        
        return stamp
        """
    
    @API_CALL
    def removeStamp(self, authUserId, stampId):
        stamp       = self._stampDB.getStamp(stampId)
        stamp       = self._enrichStampObjects(stamp, authUserId=authUserId)
        
        # Verify user has permission to delete
        if stamp.user_id != authUserId:
            raise StampedPermissionsError("Insufficient privileges to remove stamp")
        
        # Remove stamp
        self._stampDB.removeStamp(stamp.stamp_id)
        
        ### NOTE: we rely on deleted stamps remaining in user's inboxes to 
        # signal to clients that the stamp should be removed. this is not 
        # necessary for the user stamps collection
        
        # Remove from user collection
        self._stampDB.removeUserStampReference(authUserId, stamp.stamp_id)
        
        ### TODO: Remove from activity? To do? Anything else?
        
        # Remove comments
        ### TODO: Make this more efficient?
        comments = self._commentDB.getCommentsForStamp(stampId)
        for comment in comments:
            # Remove comment
            self._commentDB.removeComment(comment.comment_id)
        
        # Remove activity
        self._activityDB.removeActivityForStamp(stamp.stamp_id)
        
        # Remove as favorite if necessary
        try:
            self._favoriteDB.completeFavorite(stamp.entity_id, authUserId, complete=False)
        except Exception:
            pass
        
        ### TODO: Remove reference in other people's favorites

        # Update user stats 
        ### TODO: Do an actual count / update?
        self._userDB.updateUserStats(authUserId, 'num_stamps',      increment=-1)
        self._userDB.updateUserStats(authUserId, 'num_stamps_left', increment=1)
        distribution = self._getUserStampDistribution(authUserId)
        self._userDB.updateUserStats(authUserId, 'distribution', value=distribution)
        
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

        # Update entity stats
        tasks.invoke(tasks.APITasks.updateEntityStats, args=[stamp.entity_id])
        
        return stamp
    
    @API_CALL
    def getStamp(self, stampId, authUserId=None):
        stamp       = self._stampDB.getStamp(stampId)
        stamp       = self._enrichStampObjects(stamp, authUserId=authUserId)
        
        # Check privacy of stamp
        if stamp.user_id != authUserId and stamp.user.privacy == True:
            friendship = Friendship(user_id=user.user_id, friend_id=authUserId)
            
            if not self._friendshipDB.checkFriendship(friendship):
                raise StampedPermissionsError("Insufficient privileges to view stamp")
        
        return stamp
    
    @API_CALL
    def getStampFromUser(self, screenName, stampNumber):
        user = self._userDB.getUserByScreenName(screenName)
        stamp = self._stampDB.getStampFromUserStampNum(user.user_id, stampNumber)
        stamp = self._enrichStampObjects(stamp)
        
        # TODO: if authUserId == stamp.user.user_id, then the privacy should be disregarded
        if stamp.user.privacy == True:
            raise StampedPermissionsError("Insufficient privileges to view stamp")
        
        return stamp
    
    @API_CALL
    def updateStampImage(self, authUserId, stampId, data):
        stamp       = self._stampDB.getStamp(stampId)
        stamp       = self._enrichStampObjects(stamp, authUserId=authUserId)
        
        # Verify user has permission to add image
        if stamp.user_id != authUserId:
            raise StampedPermissionsError("Insufficient privileges to update stamp image")
        
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
                raise StampedPermissionsError("Insufficient privileges to add comment")
        
        # Check if block exists between user and stamp owner
        if self._friendshipDB.blockExists(friendship) == True:
            raise StampedIllegalActionError("Block exists")
        
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
        mentionedUserIds = set()
        for item in comment.mentions:
            if item.user_id is not None and item.user_id != authUserId:
                mentionedUserIds.add(item.user_id)
        if len(mentionedUserIds) > 0:
            self._addActivity(verb          = 'mention', 
                              userId        = authUserId, 
                              recipientIds  = list(mentionedUserIds), 
                              stampId       = stamp.stamp_id,
                              commentId     = comment.comment_id)
        
        # Add activity for stamp owner
        commentedUserIds = set()
        if stamp.user.user_id not in mentionedUserIds and stamp.user.user_id != authUserId:
            commentedUserIds.add(stamp.user.user_id)
        
        self._addActivity(verb          = 'comment', 
                          userId        = authUserId, 
                          recipientIds  = list(commentedUserIds), 
                          stampId       = stamp.stamp_id,
                          commentId     = comment.comment_id)
        
        # Increment comment metric
        self._statsSink.increment('stamped.api.stamps.comments', len(commentedUserIds))
        
        repliedUserIds = set()
        
        # Add activity for previous commenters
        ### TODO: Limit this to the last 20 comments or so
        for prevComment in self._commentDB.getCommentsForStamp(stamp.stamp_id):
            # Skip if it was generated from a restamp
            if prevComment.restamp_id:
                continue
            
            repliedUserId = prevComment['user']['user_id']
            if repliedUserId not in commentedUserIds \
                and repliedUserId not in mentionedUserIds \
                and repliedUserId not in repliedUserIds \
                and repliedUserId != authUserId:
                
                replied_user_id = prevComment['user']['user_id']
                
                # Check if block exists between user and previous commenter
                friendship = Friendship(user_id=authUserId, friend_id=replied_user_id)
                
                if self._friendshipDB.blockExists(friendship) == False:
                    repliedUserIds.add(replied_user_id)
        
        if len(repliedUserIds) > 0:
            self._addActivity(verb          = 'reply', 
                              userId        = authUserId, 
                              recipientIds  = list(repliedUserIds), 
                              stampId       = stamp.stamp_id,
                              commentId     = comment.comment_id)
        
        # Increment comment count on stamp
        self._stampDB.updateStampStats(stamp.stamp_id, 'num_comments', increment=1)
    
    @API_CALL
    def removeComment(self, authUserId, commentId):
        comment = self._commentDB.getComment(commentId)

        # Only comment owner and stamp owner can delete comment
        if comment.user.user_id != authUserId:
            stamp = self._stampDB.getStamp(comment.stamp_id)
            if stamp.user.user_id != authUserId:
                raise StampedPermissionsError("Insufficient privileges to remove comment")

        # Don't allow user to delete comment for restamp notification
        if comment.restamp_id is not None:
            raise StampedIllegalActionError("Cannot remove 'restamp' comment")

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
                raise StampedPermissionsError("Insufficient privileges to view stamp")
              
        commentData = self._commentDB.getCommentsForStamp(stamp.stamp_id)
        
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
        
        tasks.invoke(tasks.APITasks.getComments, args=[authUserId, stampId])
        
        return comments
    
    @API_CALL
    def getCommentsAsync(self, authUserId, stampId):
        self._stampDB.addView(authUserId, stampId)
    
    
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
                    raise StampedPermissionsError("Insufficient privileges to add comment")
            
            # Check if block exists between user and stamp owner
            if self._friendshipDB.blockExists(friendship) == True:
                raise StampedIllegalActionError("Block exists")
        
        # Check to verify that user hasn't already liked stamp
        if self._stampDB.checkLike(authUserId, stampId):
            raise StampedIllegalActionError("'Like' exists for user (%s) on stamp (%s)" % (authUserId, stampId))
        
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
        benefit = None
        if stamp.num_likes >= 3 and not stamp.like_threshold_hit:
            benefit = LIKE_BENEFIT
            
            # Update stamp stats
            self._stampDB.giveLikeCredit(stamp.stamp_id)
            stamp.like_threshold_hit = True
            
            # Update user stats with new credit
            self._userDB.updateUserStats(stamp.user_id, 'num_stamps_left', increment=LIKE_BENEFIT)
        
        # Add activity for stamp owner (if not self)
        if stamp.user_id != authUserId:
            self._addActivity(verb          = 'like', 
                              userId        = authUserId, 
                              stampId       = stamp.stamp_id,
                              friendId      = stamp.user_id,
                              benefit       = benefit)

        # Update entity stats
        tasks.invoke(tasks.APITasks.updateEntityStats, args=[stamp.entity_id])
        
        return stamp
    
    @API_CALL
    def removeLike(self, authUserId, stampId):
        # Remove like (if it exists)
        if not self._stampDB.removeLike(authUserId, stampId):
            raise StampedIllegalActionError("'Like' does not exist for user (%s) on stamp (%s)" % (authUserId, stampId))
        
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
                    raise StampedPermissionsError("Insufficient privileges to add comment")
            
            # Check if block exists between user and stamp owner
            if self._friendshipDB.blockExists(friendship) == True:
                raise StampedIllegalActionError("Block exists")
        
        # Get user ids
        userIds = self._stampDB.getStampLikes(stampId)
        
        return userIds
    
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
        except Exception:
            since = None
        
        # Before
        try: 
            before = datetime.utcfromtimestamp(int(data.pop('before', None)) + 2)
        except Exception:
            before = None
        
        try:
            limit = int(data.pop('limit', default_limit))
            
            if default_limit is not None and limit > default_limit:
                limit = default_limit
        except Exception:
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
        except Exception:
            return cap
    
    def _getStampCollection(self, authUserId, stampIds, genericCollectionSlice, enrich=True):
        if stampIds is not None and genericCollectionSlice.offset >= len(stampIds):
            return []
        
        quality         = genericCollectionSlice.quality
        
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
        
        if genericCollectionSlice.limit is None:
            genericCollectionSlice.limit = stampCap

        # Adjustment for multiple blurbs to use "stamped" timestamp instead of "created"
        if genericCollectionSlice.sort == 'created':
            genericCollectionSlice.sort = 'stamped'
        
        stampData = self._stampDB.getStampsSlice(stampIds, genericCollectionSlice)
        
        stamps = self._enrichStampCollection(stampData, genericCollectionSlice, authUserId, enrich, commentCap)
        
        if self.__version == 0:
            if genericCollectionSlice.deleted and (genericCollectionSlice.sort in ['modified', 'created', 'stamped']):
                if len(stamps) >= genericCollectionSlice.limit:
                    genericCollectionSlice.since = stamps[-1]['timestamp'][genericCollectionSlice.sort] 
                
                deleted = self._stampDB.getDeletedStamps(stampIds, genericCollectionSlice)
                
                if len(deleted) > 0:
                    stamps = stamps + deleted
                    ### TODO: Fails if sort == 'stamped' since it doesn't exist in deletedStamp objects
                    stamps.sort(key=lambda k: k['timestamp'][genericCollectionSlice.sort], reverse=not genericCollectionSlice.reverse)
        
        return stamps

    def _enrichStampCollection(self, stampData, genericCollectionSlice, authUserId=None, enrich=True, commentCap=4):
        commentPreviews = {}
        
        if genericCollectionSlice.comments:
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
                stamp.previews.comments = commentPreviews[stamp.stamp_id]
            
            stamps.append(stamp)
        
        if enrich:
            stamps = self._enrichStampObjects(stamps, authUserId=authUserId, nofilter=True)

        return stamps
    
    @API_CALL
    def getInboxStamps(self, authUserId, genericCollectionSlice):
        stampIds = self._collectionDB.getInboxStampIds(authUserId)

        # TODO: deprecate with new clients going forward
        genericCollectionSlice.deleted = True
        
        return self._getStampCollection(authUserId, stampIds, genericCollectionSlice)
    
    @API_CALL
    def getUserStamps(self, authUserId, userSlice):
        user = self._getUserFromIdOrScreenName(userSlice)
        
        # Check privacy
        if user.privacy == True:
            if authUserId is None:
                raise StampedPermissionsError("Must be logged in to view account")
            
            friendship = Friendship(user_id=authUserId, friend_id=user.user_id)
            
            if not self._friendshipDB.checkFriendship(friendship):
                raise StampedPermissionsError("Insufficient privileges to view user")
        
        stampIds = self._collectionDB.getUserStampIds(user.user_id)
        result   = self._getStampCollection(authUserId, stampIds, userSlice)
        
        ### TEMP
        # Fixes infinite loop where client (1.0.3) mistakenly passes "modified" instead
        # of "created" as 'before' param. This attempts to identify those situations on 
        # the second pass and returns the next segment of stamps.
        if len(result) >= 10 and userSlice.before is not None:
            try:
                before = datetime.utcfromtimestamp(int(userSlice.before))
                import calendar
                modified = result[-1].timestamp.modified
                if modified.replace(microsecond=0) + timedelta(seconds=round(modified.microsecond / 1000000.0)) == before \
                    and result[-1].timestamp.created + timedelta(hours=1) < before:
                    userSlice.before = int(calendar.timegm(result[-1].timestamp.created.timetuple()))
                    result = self._getStampCollection(authUserId, stampIds, userSlice)
            except Exception as e:
                logs.warning(e)
                pass
        
        return result
    
    @API_CALL
    def getCreditedStamps(self, authUserId, userSlice):
        user = self._getUserFromIdOrScreenName(userSlice)
        
        # Check privacy
        if user.privacy == True:
            if authUserId is None:
                raise StampedPermissionsError("Must be logged in to view account")
            
            friendship = Friendship(user_id=authUserId, friend_id=user.user_id)
            
            if not self._friendshipDB.checkFriendship(friendship):
                raise StampedPermissionsError("Insufficient privileges to view user")
        
        stampIds = self._collectionDB.getUserCreditStampIds(user.user_id)
        
        return self._getStampCollection(authUserId, stampIds, userSlice)
    
    @API_CALL
    def getFriendsStamps(self, authUserId, friendsSlice):
        if friendsSlice.distance > 3 or friendsSlice.distance < 0:
            raise StampedInputError("Unsupported value for distance")
        
        friend_stamps = self._collectionDB.getFriendsStamps(authUserId, friendsSlice)
        stamp_ids = friend_stamps.keys()
        stamps    = self._getStampCollection(authUserId, stamp_ids, friendsSlice)
        
        for stamp in stamps:
            try:
                friends     = friend_stamps[stamp.stamp_id]
                screen_name = "@%s" % stamp.user.screen_name.lower()
                stamp.via   = screen_name
                
                if friends is not None:
                    if len(friends) == 0:
                        stamp.via = screen_name
                    elif len(friends) > 2:
                        stamp.via = "%s via %d friends" % (screen_name, len(friends))
                    else:
                        names = map(lambda user_id: "@%s" % self._userDB.getUser(user_id)['screen_name'].lower(), friends)
                        stamp.via = "%s via %s" % (screen_name, ' and '.join(names))
            except Exception:
                utils.printException()
        
        return stamps
    
    @API_CALL
    def getSuggestedStamps(self, authUserId, genericCollectionSlice):
        return self._getStampCollection(authUserId, None, genericCollectionSlice)
    
    @API_CALL
    def getEntityStamps(self, entityId, authUserId, genericCollectionSlice, showCount=False):
        count = None

        # Use relationships
        if authUserId is not None and genericCollectionSlice.__class__.__name__ == 'FriendsSlice':
            distance = genericCollectionSlice.distance
            userIds = self._friendshipDB.getFriendsOfFriends(authUserId, distance=distance, inclusive=False)
            if showCount == True:
                count = self._stampDB.countStampsForEntity(entityId, userIds=userIds) 
                if count == 0:
                    return [], 0
            stampData = self._stampDB.getStampsSliceForEntity(entityId, genericCollectionSlice, userIds=userIds)

        # Use popular
        else:
            if showCount == True:
                count = self._stampDB.countStampsForEntity(entityId)
                if count <= 0:
                    return [], 0
            stampData = self._stampDB.getStampsSliceForEntity(entityId, genericCollectionSlice)
            
        stamps = self._enrichStampCollection(stampData, genericCollectionSlice, authUserId=authUserId)

        return stamps, count
    
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
        
        favorite                    = Favorite()
        favorite.entity             = entity
        favorite.user_id            = authUserId
        favorite.timestamp.created  = datetime.utcnow()
        
        if stampId is not None:
            favorite.stamp = self._stampDB.getStamp(stampId)
        
        # Check to verify that user hasn't already favorited entity
        try:
            fav = self._favoriteDB.getFavorite(authUserId, entity.entity_id)
            if fav.favorite_id is None:
                raise
            exists = True
        except Exception:
            exists = False
        
        if exists:
            raise StampedDuplicationError("Favorite already exists")
        
        # Check if user has already stamped entity, mark as complete if so
        if self._stampDB.checkStamp(authUserId, entity.entity_id):
            favorite.complete = True
        
        favorite = self._favoriteDB.addFavorite(favorite)
        
        # Increment stats
        self._statsSink.increment('stamped.api.stamps.favorites')
        
        # Enrich stamp
        if stampId is not None:
            entityIds = {entity.entity_id: entity}
            favorite.stamp = self._enrichStampObjects(favorite.stamp, \
                                authUserId=authUserId, entityIds=entityIds)
        
        # Increment user stats by one
        self._userDB.updateUserStats(authUserId, 'num_faves', increment=1)
        
        # Add activity for stamp owner (if not self)
        ### TODO: Verify user isn't being blocked
        ### TODO: Make async
        if stampId is not None and favorite.stamp.user_id != authUserId:

            self._addActivity(verb          = 'todo', 
                              userId        = authUserId, 
                              entityId      = entity.entity_id,
                              friendId      = favorite.stamp.user_id, 
                              stampId       = stampId)
        
        return favorite
    
    @API_CALL
    def removeFavorite(self, authUserId, entityId):
        ### TODO: Fail gracefully if favorite doesn't exist
        favorite = self._favoriteDB.getFavorite(authUserId, entityId)
        
        if not favorite or not favorite.favorite_id:
            raise StampedUnavailableError('Invalid favorite: %s' % favorite)
        
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
            self._activityDB.removeActivity('todo', authUserId, stampId=stamp.stamp_id)
        
        return favorite
    
    @API_CALL
    def getFavorites(self, authUserId, genericCollectionSlice):
        quality     = genericCollectionSlice.quality
        
        # Set quality
        if quality == 1:
            favCap  = 50
        elif quality == 2:
            favCap  = 30
        else:
            favCap  = 20
        
        if genericCollectionSlice.limit is None:
            genericCollectionSlice.limit = favCap
        
        # TODO: remove this temporary restriction since all client builds before 
        # v1.1 assume an implicit sort on created date
        if genericCollectionSlice.sort == 'modified':
            genericCollectionSlice.sort = 'created'
        
        favoriteData = self._favoriteDB.getFavorites(authUserId, genericCollectionSlice)
        
        # Extract entities & stamps
        entityIds   = {}
        stampIds    = {}
        favorites   = []
        
        for favorite in favoriteData:
            entityIds[str(favorite.entity.entity_id)] = 1
            
            if favorite.stamp_id is not None:
                stampIds[str(favorite.stamp_id)] = 1
        
        # Enrich entities
        entities = self._entityDB.getEntities(entityIds.keys())
        
        for entity in entities:
            entityIds[str(entity.entity_id)] = entity
        
        # Enrich stamps
        stamps = self._stampDB.getStamps(stampIds.keys(), limit=len(stampIds.keys()))
        stamps = self._enrichStampObjects(stamps, authUserId=authUserId, entityIds=entityIds)
        
        for stamp in stamps:
            stampIds[str(stamp.stamp_id)] = stamp
        
        for favorite in favoriteData:
            # Enrich Entity
            if entityIds[favorite.entity.entity_id] != 1:
                favorite.entity = entityIds[favorite.entity.entity_id]
            else:
                logs.warning('FAV (%s) MISSING ENTITY (%s)' % (favorite.favorite_id, favorite.entity.entity_id))
            
            # Add Stamp
            if favorite.stamp_id is not None:
                if stampIds[favorite.stamp_id] != 1:
                    favorite.stamp = stampIds[favorite.stamp_id]
                else:
                    ### TODO: Clean these up if they're missing
                    logs.warning('FAV (%s) MISSING STAMP (%s)' % (favorite.favorite_id, favorite.stamp_id))
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
    
    def _addActivity(self, verb, userId, **kwargs):
        # Verify that activity is enabled
        if not self._activity:
            return

        body                    = None
        group                   = False
        groupRange              = None
        requireRecipient       = False
        unique                  = False

        objects = ActivityObjectIds()

        logs.info('\n### ADDING ACTIVITY verb: %s   userId: %s' % (verb, userId))

        if verb == 'follow':
            objects.user_ids        = [ kwargs['friendId'] ] 
            group                   = True
            groupRange              = timedelta(days=1)

        elif verb == 'restamp':
            objects.user_ids        = kwargs['recipientIds']
            objects.stamp_ids       = [ kwargs['stampId'] ] 

        elif verb == 'like':
            objects.stamp_ids       = [ kwargs['stampId'] ] 
            group                   = True

        elif verb == 'todo':
            objects.user_ids        = [ kwargs['friendId'] ]
            objects.stamp_ids       = [ kwargs['stampId'] ]
            objects.entity_ids      = [ kwargs['entityId'] ] # Is this necessary? Do we require stamps?
            group                   = True

        elif verb == 'comment':
            objects.stamp_ids       = [ kwargs['stampId'] ]
            objects.comment_ids     = [ kwargs['commentId'] ]

        elif verb == 'reply':
            objects.stamp_ids       = [ kwargs['stampId'] ]
            objects.comment_ids     = [ kwargs['commentId'] ]
            requireRecipient       = True

        elif verb == 'mention':
            recipientIds = kwargs.pop('recipientIds', [])
            validRecipientIds = []
            for recipientId in recipientIds:
                # Check if block exists between user and mentioned user
                friendship = Friendship(user_id=recipientId, friend_id=userId)
                if self._friendshipDB.blockExists(friendship) == False:
                    validRecipientIds.append(recipientId)
            kwargs['recipientIds']  = validRecipientIds

            objects.stamp_ids       = [ kwargs['stampId'] ]
            if 'commentId' in kwargs and kwargs['commentId'] is not None:
                objects.comment_ids     = [ kwargs['commentId'] ]
            requireRecipient       = True

        elif verb == 'invite':
            objects.user_ids        = [ kwargs['friendId'] ]
            requireRecipient       = True
            unique                  = True

        elif verb.startswith('friend_'):
            body                    = kwargs.pop('body', None)
            requireRecipient       = True
            unique                  = True

        elif verb.startswith('action_'):
            objects.stamp_ids       = [ kwargs['stampId'] ]
            requireRecipient        = True
            unique                  = True

        else:
            raise Exception("Unrecognized activity verb: %s" % verb)


        sendAlert       = kwargs.pop('sendAlert', True)
        benefit         = kwargs.pop('benefit', None)

        recipientIds    = kwargs.pop('recipientIds', []) 
        friendId        = kwargs.pop('friendId', None)

        if len(recipientIds) == 0 and friendId is not None:
            recipientIds = [ friendId ]

        if userId in recipientIds:
            recipientIds.remove(userId)

        if requireRecipient and len(recipientIds) == 0:
            raise Exception("Missing recipient")

        # Save activity
        self._activityDB.addActivity(verb           = verb, 
                                     subject        = userId, 
                                     objects        = objects, 
                                     body           = body,
                                     recipientIds   = recipientIds, 
                                     benefit        = benefit,
                                     group          = group,
                                     groupRange     = groupRange,
                                     sendAlert      = sendAlert,
                                     unique         = unique)

        # Increment unread news for all recipients
        if len(recipientIds) > 0:
            self._userDB.updateUserStats(recipientIds, 'num_unread_news', increment=1)
    
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

        kwargs['sort'] = 'created'
        
        # Limit slice of data returned
        params = self._setSliceParams(kwargs, stampCap)
        
        distance = kwargs.pop('distance', 0)
        if distance > 0:
            personal = False
            friends = self._friendshipDB.getFriends(authUserId)
            activityData = []
            params['verbs'] = ['comment', 'like', 'todo', 'restamp', 'follow']
            dirtyActivityData = self._activityDB.getActivityForUsers(friends, **params)
            for item in dirtyActivityData:
                item.subjects = list(set(item.subjects.value).intersection(set(friends)))
                activityData.append(item)
        else:
            personal = True
            activityData = self._activityDB.getActivity(authUserId, **params)
        
        # Append user objects
        userIds     = {}
        stampIds    = {}
        entityIds   = {}
        commentIds  = {}
        for item in activityData:
            for userId in item.subjects:
                userIds[str(userId)] = None 
            for userId in item.objects.user_ids:
                userIds[str(userId)] = None 
            for stampId in item.objects.stamp_ids:
                stampIds[str(stampId)] = None 
            for entityId in item.objects.entity_ids:
                entityIds[str(entityId)] = None 
            for commentId in item.objects.comment_ids:
                commentIds[str(commentId)] = None 
        
        # Enrich users
        users = self._userDB.lookupUsers(userIds.keys(), None)
        
        for user in users:
            userIds[str(user.user_id)] = user.exportSchema(UserMini())
        
        # Enrich stamps
        stamps = self._stampDB.getStamps(stampIds.keys())
        stamps = self._enrichStampObjects(stamps, authUserId=authUserId)
        
        for stamp in stamps:
            stampIds[str(stamp.stamp_id)] = stamp

        # Enrich entities
        entities = self._entityDB.getEntities(entityIds.keys())
        for entity in entities:
            entityIds[str(entity.entity_id)] = entity 

        # Enrich comments
        comments = self._commentDB.getComments(commentIds.keys())
        commentUserIds = {}
        for comment in comments:
            if comment.user.user_id not in userIds:
                commentUserIds[comment.user.user_id] = None
        users = self._userDB.lookupUsers(commentUserIds.keys(), None)
        for user in users:
            userIds[str(user.user_id)] = user.exportSchema(UserMini())
        for comment in comments:
            comment.user = userIds[str(comment.user.user_id)]
            commentIds[str(comment.comment_id)] = comment

        activity = []
        for item in activityData:
            try:
                if item.verb in ['invite_received', 'invite_sent']:
                    continue

                activity.append(item.enrich(authUserId  = authUserId,
                                            users       = userIds, 
                                            stamps      = stampIds, 
                                            entities    = entityIds, 
                                            comments    = commentIds,
                                            personal    = personal))

            except Exception as e:
                logs.warning('Activity enrichment failed: %s' % e)
                logs.info('Activity item: \n%s\n' % item)
                utils.printException()
                continue
            
        
        # Reset activity count
        if personal:
            self._accountDB.updateUserTimestamp(authUserId, 'activity', datetime.utcnow())
            ### DEPRECATED
            self._userDB.updateUserStats(authUserId, 'num_unread_news', value=0)
        
        return activity

    @API_CALL
    def getUnreadActivityCount(self, authUserId, **kwargs):
        ### TODO: Cache this in user.num_unread_news
        user = self._getUserFromIdOrScreenName({'user_id': authUserId})
        count = self._activityDB.getUnreadActivityCount(authUserId, user.timestamp.activity)
        if count is None:
            return 0
        return count

    
    """
    #     # ###### #     # #     #
    ##   ## #      ##    # #     #
    # # # # #      # #   # #     #
    #  #  # ###### #  #  # #     #
    #     # #      #   # # #     #
    #     # #      #    ## #     #
    #     # ###### #     #  #####
    """
    
    def getMenu(self, entityId):
        menu = self._menuDB.getMenu(entityId)
        if menu is None:
            try:
                self.mergeEntityId(entityId)
                menu = self._menuDB.getMenu(entityId)
            except Exception:
                pass
        if menu is None:
            raise StampedUnavailableError()
        else:
            return menu

    """
    ######                                            
    #     # ######  ####   ####  #      #    # ###### 
    #     # #      #      #    # #      #    # #      
    ######  #####   ####  #    # #      #    # #####  
    #   #   #           # #    # #      #    # #      
    #    #  #      #    # #    # #       #  #  #      
    #     # ######  ####   ####  ######   ##   ###### 
                                                   
    """
    
    @lazyProperty
    def __full_resolve(self):
        return FullResolveContainer.FullResolveContainer()
    
    def __handleDecorations(self, entity, decorations):
        for k,v in decorations.items():
            ### TODO: decorations returned as dict, not schema. Fix?
            if k == 'menu': # and v.__class__.__name__ == 'MenuSchema': 
                try:
                    menu = MenuSchema()
                    menu.importData(v)
                    self._menuDB.update(menu)
                except Exception:
                    logs.warning('Menu enrichment failed')
                    report()
    
    def _convertSearchId(self, search_id):
        if not search_id.startswith('T_'):
            # already a valid entity id
            return search_id
        
        source_name, source_id = re.match(r'^T_([A-Z]*)_([\w+-:]*)', search_id).groups()
        
        sources = {
            'amazon':       AmazonSource,
            'factual':      FactualSource,
            'googleplaces': GooglePlacesSource,
            'itunes':       iTunesSource,
            'rdio':         RdioSource,
            'spotify':      SpotifySource,
            'tmdb':         TMDBSource,
            'thetvdb':      TheTVDBSource,
        }
        
        if source_name.lower() not in sources:
            logs.warning('Source not found: %s (%s)' % (source_name, search_id))
            raise StampedUnavailableError
        
        # Attempt to resolve against the Stamped DB
        source    = sources[source_name.lower()]()
        stamped   = StampedSource(stamped_api=self)
        entity_id = stamped.resolve_fast(source, source_id)
        
        if entity_id is None:
            proxy = source.entityProxyFromKey(source_id)
            results = stamped.resolve(proxy)
            
            if len(results) > 0 and results[0][0]['resolved']:
                # Source key found in the Stamped DB
                entity_id = results[0][1].key
        
        if entity_id is None:
            entityProxy = EntityProxyContainer.EntityProxyContainer(proxy)
            entity = entityProxy.buildEntity()
            
            entity = self._entityDB.addEntity(entity)
            entity_id = entity.entity_id
            
        # Enrich and merge entity asynchronously
        self.mergeEntityId(entity_id)
        
        logs.info('Converted search_id (%s) to entity_id (%s)' % (search_id, entity_id))
        return entity_id
    

    def mergeEntity(self, entity, link=True):
        logs.info('Merge Entity: "%s"' % entity.title)
        tasks.invoke(tasks.APITasks.mergeEntity, args=[entity.value, link])
    
    def mergeEntityAsync(self, entityDict, link=True):
        self._mergeEntity(buildEntity(entityDict), link)

    def mergeEntityId(self, entityId, link=True):
        logs.info('Merge EntityId: %s' % entityId)
        tasks.invoke(tasks.APITasks.mergeEntityId, args=[entityId, link])
    
    def mergeEntityIdAsync(self, entityId, link=True):
        self._mergeEntity(self._entityDB.getEntity(entityId), link)
    
    def _mergeEntity(self, entity, link=True):
        logs.info('Merge Entity Async: "%s" (id = %s)' % (entity.title, entity.entity_id))
        modified = self._resolveEntity(entity)

        if link:
            modified = self._resolveEntityLinks(entity) | modified

        if modified:
            if entity.entity_id is None:
                self._entityDB.addEntity(entity)
            else:
                self._entityDB.updateEntity(entity)


    def _resolveEntity(self, entity):

        def _getSuccessor(tombstoneId):
            successor_id = tombstoneId
            successor    = self._entityDB.getEntity(successor_id)
            assert successor is not None and successor.entity_id == successor_id
            
            merger = FullResolveContainer.FullResolveContainer()
            merger.addSource(EntitySource(entity, merger.groups))
            successor_decorations = {}
            modified_successor = merger.enrichEntity(successor, successor_decorations)
            self.__handleDecorations(successor, successor_decorations)

            return successor, modified_successor

        try:
            # TEMP: Short circuit if user-generated
            if entity.sources.user_generated_id is not None:
                return False 

            # Short circuit if entity is already tombstoned
            if entity.sources.tombstone_id is not None:
                successor, modified_successor = _getSuccessor(entity.sources.tombstone_id)
                logs.info("Entity (%s) already tombstoned (%s)" % (entity.entity_id, successor.entity_id))
                entity = successor
                return modified_successor

            # Enrich entity
            decorations = {}
            modified    = self.__full_resolve.enrichEntity(entity, decorations, max_iterations=4)
            
            # Return successor if entity is tombstoned
            if entity.sources.tombstone_id is not None:
                successor, modified_successor = _getSuccessor(entity.sources.tombstone_id)

                if entity.entity_id is not None:
                    self._entityDB.updateEntity(entity)
                
                logs.info("Merged entity (%s) with entity %s" % (entity.entity_id, successor.entity_id))
                entity = successor
                return modified_successor

            self.__handleDecorations(entity, decorations)

            return modified 

        except Exception:
            report()
            raise


    def _resolveEntityLinks(self, entity):
        
        def _resolveStub(stub, sources):
            source          = None
            source_id       = None
            entity_id       = None
            proxy           = None

            stubModified    = False

            if stub.entity_id is not None and not stub.entity_id.startswith('T_'):
                entity_id = stub.entity_id
            else:
                for sourceName in sources:
                    try:
                        if stub.sources['%s_id' % sourceName] is not None:
                            source = sources[sourceName]()
                            source_id = stub.sources['%s_id' % sourceName]
                            # Attempt to resolve against the Stamped DB (quick)
                            entity_id = stampedSource.resolve_fast(source, source_id)
                            if entity_id is None:
                                # Attempt to resolve against the Stamped DB (full)
                                proxy = source.entityProxyFromKey(source_id, entity=stub)
                                results = stampedSource.resolve(proxy)
                                if len(results) > 0 and results[0][0]['resolved']:
                                    entity_id = results[0][1].key
                            break
                    except Exception:
                        pass
            if entity_id is not None:
                entity = self._entityDB.getEntity(entity_id)
            elif source_id is not None and proxy is not None:
                entityProxy = EntityProxyContainer.EntityProxyContainer(proxy)
                entity = entityProxy.buildEntity()
                stubModified = True 
            else:
                logs.warning('Unable to resolve stub: %s' % stub)
                raise KeyError('Unable to resolve stub')

            return entity, stubModified


        ### TRACKS
        def _resolveTrack(stub):
            try:
                track, trackModified = _resolveStub(stub, musicSources)
            except KeyError as e:
                logs.warning('Track resolution failed: %s' % e)
                return stub

            # Merge track if it wasn't resolved
            if track.entity_id is None:
                self.mergeEntity(track, link=False)

            return track

        def _resolveTracks(entity):
            trackList = []
            tracksModified = False
            for stub in entity.tracks:
                trackId = stub.entity_id
                track = _resolveTrack(stub)
                trackList.append(track.minimize())

                # Compare entity id before and after
                if trackId != track.entity_id:
                    tracksModified = True

            entity.tracks = trackList
            return tracksModified


        ### ALBUMS
        def _resolveAlbum(stub):
            try:
                album, albumModified = _resolveStub(stub, musicSources)
            except KeyError:
                logs.warning('Album resolution failed')
                return stub

            # Merge album if it wasn't resolved
            if album.entity_id is None:
                self.mergeEntity(album)

            return album

        def _resolveAlbums(entity):
            albumList = []
            albumsModified = False
            for stub in entity.albums:
                albumId = stub.entity_id
                album = _resolveAlbum(stub)
                albumList.append(album.minimize())

                # Compare entity id before and after
                if albumId != album.entity_id:
                    albumsModified = True

            entity.albums = albumList
            return albumsModified


        ### ARTISTS
        def _resolveArtist(stub):
            try:
                artist, artistModified = _resolveStub(stub, musicSources)
            except KeyError:
                logs.warning('Artist resolution failed')
                return stub

            # Merge artist if it wasn't resolved
            # if artist.entity_id is None:
            #     self.mergeEntity(artist)

            return artist

        def _resolveArtists(entity):
            artistList = []
            artistsModified = False
            for stub in entity.artists:
                artistId = stub.entity_id
                artist = _resolveArtist(stub)
                artistList.append(artist.minimize())

                # Compare entity id before and after
                if artistId != artist.entity_id:
                    artistsModified = True

            entity.artists = artistList
            return artistsModified

        stampedSource   = StampedSource(stamped_api = self)
        musicSources    = {
            'itunes':       iTunesSource,
            'rdio':         RdioSource,
            'spotify':      SpotifySource,
            'amazon':       AmazonSource,
        }

        modified = False

        if entity.isType('album'):
            modified = _resolveArtists(entity) | modified
            modified = _resolveTracks(entity) | modified

        if entity.isType('artist'):
            modified = _resolveAlbums(entity) | modified
            modified = _resolveTracks(entity) | modified

        if entity.isType('artist') or entity.isType('track'):
            # Enrich albums instead
            for albumItem in entity.albums:
                try:
                    albumItem, albumModified = _resolveStub(albumItem, musicSources)
                    if albumItem.entity_id is not None:
                        if albumItem.isType('album'):
                            self.mergeEntityId(albumItem.entity_id)
                    else:
                        self.mergeEntity(albumItem)
                except Exception as e:
                    logs.warning('Failed to enrich album: %s' % e)

        return modified

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
    
    def addClientLogsEntry(self, authUserId, entry):
        entry.user_id = authUserId
        entry.created = datetime.utcnow()
        
        return self._clientLogsDB.addEntry(entry)

