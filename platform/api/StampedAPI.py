#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from logs import report

try:
    import utils
    import os, logs, re, time, urlparse, math, pylibmc, gevent, traceback, random

    from api import Blacklist
    import libs.ec2_utils
    import libs.Memcache
    import tasks.APITasks
    from api import Entity
    from api import SchemaValidation

    from api.auth                       import convertPasswordForStorage
    from utils                      import lazyProperty, LoggingThreadPool
    from functools                  import wraps
    from errors                     import *
    from libs.ec2_utils             import is_prod_stack
    from pprint                     import pprint, pformat
    from operator                   import itemgetter, attrgetter
    from random                     import seed, random

    from api.AStampedAPI                import AStampedAPI
    from api.AAccountDB                 import AAccountDB
    from api.AEntityDB                  import AEntityDB
    from api.AUserDB                    import AUserDB
    from api.AStampDB                   import AStampDB
    from api.ACommentDB                 import ACommentDB
    from api.ATodoDB                    import ATodoDB
    from api.ACollectionDB              import ACollectionDB
    from api.AFriendshipDB              import AFriendshipDB
    from api.AActivityDB                import AActivityDB
    from api.Schemas                import *
    from api.ActivityCollectionCache    import ActivityCollectionCache
    from libs.Memcache                   import globalMemcache
    from api.HTTPSchemas                import generateStampUrl

    from crawler.RssFeedScraper     import RssFeedScraper

    #resolve classes
    from resolve.EntitySource       import EntitySource
    from resolve.EntityProxySource  import EntityProxySource
    from resolve                    import FullResolveContainer, EntityProxyContainer
    from resolve.AmazonSource               import AmazonSource
    from resolve.FactualSource              import FactualSource
    from resolve.GooglePlacesSource         import GooglePlacesSource
    from resolve.iTunesSource               import iTunesSource
    from resolve.NetflixSource              import NetflixSource
    from resolve.RdioSource                 import RdioSource
    from resolve.SpotifySource              import SpotifySource
    from resolve.TMDBSource                 import TMDBSource
    from resolve.TheTVDBSource              import TheTVDBSource
    from resolve.StampedSource              import StampedSource
    from resolve.EntityProxySource import EntityProxySource

    # TODO (travis): we should NOT be importing * here -- it's okay in limited
    # situations, but in general, this is very bad practice.

    from libs.Netflix               import *
    from libs.Facebook                   import *
    from libs.Twitter                    import *
    from libs.GooglePlaces               import *
    from libs.Rdio                       import *

    from search.AutoCompleteIndex import normalizeTitle, loadIndexFromS3, emptyIndex, pushNewIndexToS3
    
    from datetime                   import datetime, timedelta
except Exception:
    report()
    raise

CREDIT_BENEFIT  = 1 # Per credit
LIKE_BENEFIT    = 1 # Per like

# TODO (travis): refactor API function calling conventions to place optional last
# instead of first.

class StampedAPI(AStampedAPI):
    """
        Database-agnostic implementation of the internal API for accessing
        and manipulating all Stamped backend databases.
    """

    @lazyProperty
    def _netflix(self):
        return globalNetflix()

    @lazyProperty
    def _facebook(self):
        return globalFacebook()

    @lazyProperty
    def _twitter(self):
        return globalTwitter()

    @lazyProperty
    def _googlePlaces(self):
        return globalGooglePlaces()

    @lazyProperty
    def _rdio(self):
        return globalRdio()

    def __init__(self, desc, **kwargs):
        AStampedAPI.__init__(self, desc)
        self.lite_mode = kwargs.pop('lite_mode', False)
        self._cache    = globalMemcache()

        self.ACTIVITY_CACHE_BLOCK_SIZE = 50
        self.ACTIVITY_CACHE_BUFFER_SIZE = 20

        self._activityCache = ActivityCollectionCache(self,
                                                      cacheBlockSize=self.ACTIVITY_CACHE_BLOCK_SIZE,
                                                      cacheBufferSize=self.ACTIVITY_CACHE_BUFFER_SIZE)

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

        if utils.is_ec2():
            self.__autocomplete = loadIndexFromS3()
        else:
            self.__autocomplete = emptyIndex()
        self.__autocomplete_last_loaded = datetime.now()

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
                self._node_name = "%s.%s" % (stack_info.instance.stack, stack_info.instance.name)
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

    def _validateStampColors(self, primary, secondary):
        primary = primary.upper()
        secondary = secondary.upper()

        if not utils.validate_hex_color(primary) or not utils.validate_hex_color(secondary):
            raise StampedInvalidStampColorsError("Invalid format for colors")

        return primary, secondary

    @API_CALL
    @HandleRollback
    def addAccount(self, account, tempImageUrl=None):
        ### TODO: Check if email already exists?
        now = datetime.utcnow()

        timestamp = UserTimestamp()
        timestamp.created = now
        account.timestamp = timestamp
        if account.password is not None:
            account.password = convertPasswordForStorage(account.password)

        # Set initial stamp limit
        account.stats.num_stamps_left = 100
        account.stats.num_stamps_total = 0

        # Set default stamp colors
        if account.color_primary is not None or account.color_secondary is not None:
            primary, secondary = self._validateStampColors(account.color_primary, account.color_secondary)
            account.color_primary = primary
            account.color_secondary = secondary

            # Asynchronously generate stamp file
            tasks.invoke(tasks.APITasks.customizeStamp, args=[primary, secondary])
        else:
            account.color_primary   = '004AB2'
            account.color_secondary = '0057D1'

        # Set default alerts
        alert_settings                          = AccountAlertSettings()
        alert_settings.alerts_credits_apns      = True
        alert_settings.alerts_credits_email     = True
        alert_settings.alerts_likes_apns        = True
        alert_settings.alerts_likes_email       = False
        alert_settings.alerts_todos_apns        = True
        alert_settings.alerts_todos_email       = False
        alert_settings.alerts_mentions_apns     = True
        alert_settings.alerts_mentions_email    = True
        alert_settings.alerts_comments_apns     = True
        alert_settings.alerts_comments_email    = True
        alert_settings.alerts_replies_apns      = True
        alert_settings.alerts_replies_email     = True
        alert_settings.alerts_followers_apns    = True
        alert_settings.alerts_followers_email   = True
        alert_settings.alerts_friends_apns      = True
        alert_settings.alerts_friends_email     = True
        alert_settings.alerts_actions_apns      = True
        alert_settings.alerts_actions_email     = False
        account.alert_settings                  = alert_settings

        # Validate screen name
        account.screen_name = account.screen_name.strip()
        if not utils.validate_screen_name(account.screen_name):
            raise StampedInvalidScreenNameError("Invalid format for screen name: %s" % account.screen_name)

        # Check blacklist
        if account.screen_name.lower() in Blacklist.screen_names:
            raise StampedBlackListedScreenNameError("Blacklisted screen name: %s" % account.screen_name)

        # Validate email address
        if account.email is not None and account.auth_service == 'stamped':
            account.email = str(account.email).lower().strip()
            SchemaValidation.validateEmail(account.email)

        # Add image timestamp if exists
        if tempImageUrl is not None:
            account.timestamp.image_cache = now

        # Create account
        ### TODO: Add intelligent error message
        account = self._accountDB.addAccount(account)
        self._rollback.append((self._accountDB.removeAccount, [account.user_id]))

        # Add stats
        self._statsSink.increment('stamped.api.new_accounts')

        # Add profile image
        if tempImageUrl is not None:
            tasks.invoke(tasks.APITasks.updateProfileImage, args=[account.screen_name, tempImageUrl])

        # Asynchronously send welcome email and add activity items
        tasks.invoke(tasks.APITasks.addAccount, args=[account.user_id])

        return account

    def upgradeAccount(self, authUserId, email, password):
        account = self.getAccount(authUserId)

        if account.auth_service == 'stamped':
            raise StampedAlreadyStampedAuthError("Cannot upgrade an account that is already using stamped auth")

        if account.email != email:
            email = str(email).lower().strip()
            SchemaValidation.validateEmail(email)

            testAccount = None
            try:
                testAccount = self._accountDB.getAccountByEmail(email)
            except StampedAccountNotFoundError:
                pass
            if testAccount is not None:
                raise StampedEmailInUseError("Email is in use by another account")

            account.email = email

        if password is None:
            raise StampedMissingParametersError("A password must be provided")

        account.password = convertPasswordForStorage(password)
        account.auth_service = 'stamped'

        return self._accountDB.updateAccount(account)


    #TODO: Consolidate addFacebookAccount and addTwitterAccount?  After linked accounts get generified

#    def verifyLinkedAccount(self, linkedAccount):
#        if linkedAccount.service_name == 'facebook':
#            try:
#                facebookUser = self._facebook.getUserInfo(linkedAccount.token)
#            except (StampedInputError, StampedUnavailableError) as e:
#                raise StampedThirdPartyError("Unable to get user info from facebook %s" % e)
#            if facebookUser['id'] != linkedAccount.linked_user_id:
#                raise StampedLinkedAccountMismatchError('The facebook id associated with the facebook token is different from the id provided')
##            if facebookUser['name'] != linkedAccount.linked_name:
##                logs.warning("The name associated with the Facebook account is different from the name provided")
##                raise StampedAuthError('Unable to connect to Facebook')
##            if linkedAccount.linked_screen_name is not None and \
##               facebookUser['username'] != linkedAccount.linked_screen_name:
##                logs.warning("The username associated with the Facebook account is different from the screen name provided")
##                raise StampedAuthError('Unable to connect to Facebook')
#            self._verifyFacebookAccount(facebookUser['id'])
#        elif linkedAccount.service_name == 'twitter':
#            try:
#                twitterUser = self._twitter.getUserInfo(linkedAccount.token, linkedAccount.secret)
#            except (StampedInputError, StampedUnavailableError):
#                logs.warning("Unable to get user info from twitter %s" % e)
#                raise StampedInputError('Unable to connect to Twitter')
##            if twitterUser['id'] != linkedAccount.linked_user_id:
##                logs.warning("The twitter id associated with the twitter token/secret is different from the id provided")
##                raise StampedAuthError('Unable to connect to Twitter')
##            if twitterUser['screen_name'] != linkedAccount.linked_screen_name:
##                logs.warning("The twitter id associated with the twitter token/secret is different from the id provided")
##                raise StampedAuthError('Unable to connect to Twitter')
#            self._verifyTwitterAccount(twitterUser['id'])
#        return True

    def _verifyFacebookAccount(self, facebookId, authUserId=None):
        # Check that no Stamped account is linked to the facebookId
        try:
            account = self.getAccountByFacebookId(facebookId)
        except StampedUnavailableError:
            return True
        if account.user_id != authUserId:
            raise StampedLinkedAccountAlreadyExistsError("Account already exists for facebookId: %s" % facebookId)
        return True

    def _verifyTwitterAccount(self, twitterId, authUserId=None):
        # Check that no Stamped account is linked to the twitterId
        try:
            account = self.getAccountByTwitterId(twitterId)
        except StampedUnavailableError:
            return True
        if account.user_id != authUserId:
            raise StampedLinkedAccountAlreadyExistsError("Account already exists for twitterId: %s" % twitterId)
        return True

    @API_CALL
    def addFacebookAccount(self, new_fb_account, tempImageUrl=None):
        """
        For adding a Facebook auth account, first pull the user info from Facebook, verify that the user_id is not already
         linked to another user, populate the linked account information and then chain to the standard addAccount() method
        """

        # first, grab all the information from Facebook using the passed in token
        try:
            facebookUser = self._facebook.getUserInfo(new_fb_account.user_token)
        except (StampedInputError, StampedUnavailableError) as e:
            logs.warning("Unable to get user info from facebook %s" % e)
            raise StampedInputError('Unable to connect to Facebook')
        self._verifyFacebookAccount(facebookUser['id'])
        account = Account().dataImport(new_fb_account.dataExport(), overflow=True)

        # If the facebook account email address is already in our system, then we will use a mock email address
        # to avoid a unique id conflict in our db
        email = 'fb_%s' % facebookUser['id']
        if 'email' in facebookUser:
            try:
                testemail = str(facebookUser['email']).lower().strip()
                self._accountDB.getAccountByEmail(testemail)
            except StampedAccountNotFoundError:
                email = testemail
                SchemaValidation.validateEmail(account.email)

        account.email = email

        account.linked                      = LinkedAccounts()
        fb_acct                             = LinkedAccount()
        fb_acct.service_name                = 'facebook'
        fb_acct.token                       = new_fb_account.user_token
        fb_acct.linked_user_id              = facebookUser['id']
        fb_acct.linked_name                 = facebookUser['name']
        fb_acct.linked_screen_name          = facebookUser.pop('username', None)
        # Enable Open Graph sharing by default
        fb_acct.share_settings = LinkedAccountShareSettings()
        fb_acct.share_settings.share_stamps  = True
        fb_acct.share_settings.share_likes   = True
        fb_acct.share_settings.share_todos   = True
        fb_acct.share_settings.share_follows = True
        account.linked.facebook             = fb_acct
        account.auth_service                = 'facebook'

        # TODO: might want to get rid of this profile_image business, or figure out if it's the default image and ignore it
        #profile_image = 'http://graph.facebook.com/%s/picture?type=large' % user['id']

        account = self.addAccount(account, tempImageUrl=tempImageUrl)
        tasks.invoke(tasks.APITasks.alertFollowersFromFacebook, args=[account.user_id, fb_acct.token])
        return account

    @API_CALL
    def addTwitterAccount(self, new_tw_account, tempImageUrl=None):
        """
        For adding a Twitter auth account, first pull the user info from Twitter, verify that the user_id is not already
         linked to another user, populate the linked account information and then chain to the standard addAccount() method
        """

        # First, get user information from Twitter using the passed in token
        try:
            twitterUser = self._twitter.getUserInfo(new_tw_account.user_token, new_tw_account.user_secret)
        except (StampedInputError, StampedUnavailableError) as e:
            raise StampedThirdPartyError('Unable to get user info from Twitter %s' % e)
        self._verifyTwitterAccount(twitterUser['id'])
        account = Account().dataImport(new_tw_account.dataExport(), overflow=True)

        # If an email address is not provided, create a mock email address.  Necessary because we index on email in Mongo
        #  and require uniqueness
        if account.email is None or accounttest is not None:
            account.email = 'tw_%s' % twitterUser['id']
        else:
            account.email = str(account.email).lower().strip()
            SchemaValidation.validateEmail(account.email)

        account.linked                      = LinkedAccounts()
        tw_acct                             = LinkedAccount()
        tw_acct.service_name                = 'twitter'
        tw_acct.token                       = new_tw_account.user_token
        tw_acct.secret                      = new_tw_account.user_secret
        tw_acct.linked_user_id              = twitterUser['id']
        tw_acct.linked_screen_name          = twitterUser['screen_name']
        tw_acct.linked_name                 = twitterUser.pop('name', None)
        account.linked.twitter              = tw_acct
        account.auth_service                = 'twitter'

        # TODO: might want to get rid of this profile_image business, or figure out if it's the default image and ignore it
        #profile_image = user['profile_background_image_url']

        account = self.addAccount(account, tempImageUrl=tempImageUrl)
        tasks.invoke(tasks.APITasks.alertFollowersFromTwitter,
            args=[account.user_id, new_tw_account.user_token, new_tw_account.user_secret])
        return account

    @API_CALL
    def addAccountAsync(self, userId):
        account = self._accountDB.getAccount(userId)

        self._addWelcomeActivity(userId)

        # Send welcome email
        if account.email is not None and account.auth_service == 'stamped':

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
            friendship              = Friendship()
            friendship.user_id      = followerId
            friendship.friend_id    = account.user_id

            self._friendshipDB.removeFriendship(friendship)

            # Decrement number of friends
            self._userDB.updateUserStats(followerId, 'num_friends', increment=-1)

            # Remove stamps from Inbox
            self._stampDB.removeInboxStampReferencesForUser(followerId, stampIds)

        for friendId in friendIds:
            friendship              = Friendship()
            friendship.user_id      = account.user_id
            friendship.friend_id    = friendId

            self._friendshipDB.removeFriendship(friendship)

            # Decrement number of followers
            self._userDB.updateUserStats(friendId, 'num_followers', increment=-1)

        # Remove todos
        todoEntityIds = self._todoDB.getTodoEntityIds(account.user_id)
        for entityId in todoEntityIds:
            self._todoDB.removeTodo(account.user_id, entityId)
        # Remove todos history
        self._todoDB.removeUserTodosHistory(account.user_id)

        # Remove stamps / collections
        stamps = self._stampDB.getStamps(stampIds)

        for stamp in stamps:
            if stamp.credits is not None and len(stamp.credits) > 0:
                for stampPreview in stamp.credits:
                    self._stampDB.removeCredit(stampPreview.user.user_id, stamp.stamp_id, stamp.user.user_id)

                    # Decrement user stats by one
                    self._userDB.updateUserStats(stampPreview.user.user_id, 'num_credits', increment=-1)

            # Remove activity on stamp
            self._activityDB.removeActivityForStamp(stamp.stamp_id)

        if stampIds is not None and len(stampIds) > 0:
            self._stampDB.removeStamps(stampIds)
            self._stampStatsDB.removeStatsForStamps(stampIds)

        self._stampDB.removeAllUserStampReferences(account.user_id)
        self._stampDB.removeAllInboxStampReferences(account.user_id)
        ### TODO: If restamp, remove from credited stamps' comment list?

        # Remove comments
        comments = self._commentDB.getUserCommentIds(account.user_id)
        for comment in comments:
            # Remove comment
            self._commentDB.removeComment(comment.comment_id)

        # Remove likes
        likedStampIds = self._stampDB.getUserLikes(account.user_id)
        likedStamps = self._stampDB.getStamps(likedStampIds)

        for stamp in likedStamps:
            self._stampDB.removeLike(account.user_id, stamp.stamp_id)

            # Decrement user stats by one
            self._userDB.updateUserStats(stamp.user.user_id, 'num_likes', increment=-1)

        # Remove like history
        self._stampDB.removeUserLikesHistory(account.user_id)

        # Remove activity items
        self._activityDB.removeUserActivity(account.user_id)

        # Remove guide
        ### TODO

        # Remove custom entities
        ### TODO: Do this?

        # Remove profile image
        self._imageDB.removeProfileImage(account.screen_name.lower())

        # Remove account
        self._accountDB.removeAccount(account.user_id)

        # Remove email address from invite list
        if account.email is not None:
            self._inviteDB.remove(account.email)

        return account

    @API_CALL
    def updateAccount(self, authUserId, updateAcctForm):
        account = self._accountDB.getAccount(authUserId)
        fields = updateAcctForm.dataExport()

        if 'screen_name' in fields and account.screen_name != fields['screen_name']:
            if fields['screen_name'] is None:
                raise StampedUnsetRequiredFieldError("Cannot unset screen name")
            old_screen_name = account.screen_name
            account.screen_name = fields['screen_name']

            # Validate screen name
            screen_name = SchemaValidation.validateScreenName(account.screen_name.strip())
            account.screen_name = screen_name

            # Verify screen_name unused
            existingAcct = None
            try:
                existingAcct = self._accountDB.getAccountByScreenName(account.screen_name.lower())
            except StampedUnavailableError:
                pass
            if existingAcct is not None:
                raise StampedScreenNameInUseError("The screen name is already in use")

            # Check Blacklist
            if account.screen_name.lower() in Blacklist.screen_names:
                raise StampedBlackListedScreenNameError("Blacklisted screen name")

            # Asynchronously update profile picture link if screen name has changed
            tasks.invoke(tasks.APITasks.changeProfileImageName, args=[
                old_screen_name.lower(), account.screen_name.lower()])

        if 'name' in fields and account.name != fields['name'] and fields['name'] is not None:
            if fields['name'] is None:
                raise StampedUnsetRequiredFieldError("Cannot unset name")
            account.name = fields['name']
        if 'phone' in fields and account.phone != fields['phone']:
            account.phone = fields['phone']

        if 'bio' in fields and account.bio != fields['bio']:
            account.bio = fields['bio']
        if 'website' in fields and account.website != fields['website']:
            url = SchemaValidation.validateURL(fields['website'])
            account.website = url
        if 'location' in fields and account.location != fields['location']:
            account.location = fields['location']
        if ('color_primary' in fields and account.color_primary != fields['color_primary']) or \
           ('color_secondary' in fields and account.color_secondary != fields['color_secondary']):
            # Asynchronously generate stamp image
            account.color_primary = fields.get('color_primary', account.color_primary)
            account.color_secondary = fields.get('color_secondary', account.color_secondary)
            logs.info('updating stamp color: %s, %s' % (account.color_primary, account.color_secondary))
            tasks.invoke(tasks.APITasks.customizeStamp, args=[account.color_primary, account.color_secondary])
        if 'temp_image_url' in fields:
            image_cache_timestamp = datetime.utcnow()
            account.timestamp.image_cache = image_cache_timestamp
            self._accountDB.updateUserTimestamp(account.user_id, 'image_cache', image_cache_timestamp)
            tasks.invoke(tasks.APITasks.updateProfileImage, args=[account.screen_name, fields['temp_image_url']])

        return self._accountDB.updateAccount(account)

    @API_CALL
    def changeProfileImageNameAsync(self, old_screen_name, new_screen_name):
        self._imageDB.changeProfileImageName(old_screen_name.lower(), new_screen_name.lower())

    @API_CALL
    def getAccount(self, authUserId):
        return self._accountDB.getAccount(authUserId)

    @API_CALL
    def getLinkedAccount(self, authUserId, service_name):
        account = self.getAccount(authUserId)
        if account.linked is None:
            raise StampedLinkedAccountDoesNotExistError("User has no linked accounts")
        linked = getattr(account.linked, service_name)
        if linked is None:
            raise StampedLinkedAccountDoesNotExistError("User has no linked account: %s" % service_name)
        return linked

    @API_CALL
    def getLinkedAccounts(self, authUserId):
        return self.getAccount(authUserId).linked

    #TODO: Consolidate getAccountByFacebookId and getAccountByTwitterId?  After linked account generification is complete

    @API_CALL
    def getAccountByFacebookId(self, facebookId):
        accounts = self._accountDB.getAccountsByFacebookId(facebookId)
        if len(accounts) == 0:
            raise StampedAccountNotFoundError("Unable to find account with facebook_id: %s" % facebookId)
        elif len(accounts) > 1:
            raise StampedLinkedAccountAlreadyExistsError("More than one account exists using facebook_id: %s" % facebookId)
        return accounts[0]

    @API_CALL
    def getAccountByTwitterId(self, twitterId):
        accounts = self._accountDB.getAccountsByTwitterId(twitterId)
        if len(accounts) == 0:
            raise StampedAccountNotFoundError("Unable to find account with twitter_id: %s" % twitterId)
        elif len(accounts) > 1:
            raise StampedLinkedAccountAlreadyExistsError("More than one account exists using twitter_id: %s" % twitterId)
        return accounts[0]

    @API_CALL
    def getAccountByNetflixId(self, netflixId):
        accounts = self._accountDB.getAccountsByNetflixId(netflixId)
        if len(accounts) == 0:
            raise StampedAccountNotFoundError("Unable to find account with netflix_id: %s" % netflixId)
        elif len(accounts) > 1:
            raise StampedLinkedAccountAlreadyExistsError("More than one account exists using netflix_id: %s" % netflixId)
        return accounts[0]

    @API_CALL
    def customizeStamp(self, authUserId, data):
        primary, secondary = self._validateStampColors(data['color_primary'], data['color_secondary'])

        account = self._accountDB.getAccount(authUserId)

        # Import each item
        account.color_primary = primary
        account.color_secondary = secondary

        self._accountDB.updateAccount(account)

        # Asynchronously generate stamp file
        tasks.invoke(tasks.APITasks.customizeStamp, args=[primary, secondary])

        return account

    @API_CALL
    def customizeStampAsync(self, primary, secondary):
        self._imageDB.generateStamp(primary, secondary)

    @API_CALL
    def updateProfileImageAsync(self, screen_name, image_url):
        self._imageDB.addResizedProfileImages(screen_name.lower(), image_url)

    def checkAccount(self, login):
        ### TODO: Clean this up (along with HTTP API function)
        valid = False

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
                raise StampedBlacklistedAccountError('Blacklisted login: %s' % login)
        else:
            raise StampedAccountNotFoundError("Could not find account for email or screen_name")
        return user

    @API_CALL
    def updateAlerts(self, authUserId, on, off):
        account = self._accountDB.getAccount(authUserId)

        accountAlerts = account.alert_settings
        if accountAlerts is None:
            accountAlerts = AccountAlertSettings()

        if on is not None:
            for attr in on:
                if hasattr(accountAlerts, attr):
                    setattr(accountAlerts, attr, True)

        if off is not None:
            for attr in off:
                if hasattr(accountAlerts, attr):
                    setattr(accountAlerts, attr, False)

        account.alert_settings = accountAlerts

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

    def _getTwitterFollowers(self, user_token, user_secret):
        if user_token is None or user_secret is None:
            raise StampedThirdPartyInvalidCredentialsError("Connecting to Twitter requires a valid key / secret")

        twitterIds = self._twitter.getFollowerIds(user_token, user_secret)
        return self._userDB.findUsersByTwitter(twitterIds)

    def _getTwitterFriends(self, user_token, user_secret):
        if user_token is None or user_secret is None:
            raise StampedThirdPartyInvalidCredentialsError("Connecting to Twitter requires a valid key / secret")

        twitterIds = self._twitter.getFriendIds(user_token, user_secret)
        return self._userDB.findUsersByTwitter(twitterIds)

    def _getFacebookFriends(self, user_token):
        if user_token is None:
            raise StampedThirdPartyInvalidCredentialsError("Connecting to Facebook requires a valid token")

        facebookIds = self._facebook.getFriendIds(user_token)
        return self._userDB.findUsersByFacebook(facebookIds)

    @API_CALL
    def addLinkedAccount(self, authUserId, linkedAccount):
        service_name = linkedAccount.service_name

        if service_name == 'facebook':
            if linkedAccount.token is None:
                raise StampedMissingLinkedAccountTokenError("Must provide an access token for facebook account")
            userInfo = self._facebook.getUserInfo(linkedAccount.token)
            self._verifyFacebookAccount(userInfo['id'], authUserId)
            linkedAccount.linked_user_id = userInfo['id']
            linkedAccount.linked_name = userInfo['name']
            if 'username' in userInfo:
                linkedAccount.linked_screen_name = userInfo['username']
            # Enable Open Graph sharing by default
            try:
                self.getLinkedAccount(authUserId, 'facebook')
            except StampedLinkedAccountDoesNotExistError:
                linkedAccount.share_settings = LinkedAccountShareSettings()
                linkedAccount.share_settings.share_stamps  = True
                linkedAccount.share_settings.share_likes   = True
                linkedAccount.share_settings.share_todos   = True
                linkedAccount.share_settings.share_follows = True

        elif service_name == 'twitter':
            if linkedAccount.token is None or linkedAccount.secret is None:
                raise StampedMissingLinkedAccountTokenError("Must provide a token and secret for twitter account")
            userInfo = self._twitter.getUserInfo(linkedAccount.token, linkedAccount.secret)
            self._verifyTwitterAccount(userInfo['id'], authUserId)
            linkedAccount.linked_user_id = userInfo['id']
            linkedAccount.linked_screen_name = userInfo['screen_name']
            
        elif service_name == 'netflix':
            if linkedAccount.token is None or linkedAccount.secret is None:
                raise StampedMissingLinkedAccountTokenError("Must provide a token and secret for netflix account")
            userInfo = self._netflix.getUserInfo(linkedAccount.token, linkedAccount.secret)
            if userInfo['can_instant_watch'] == False:
                raise StampedNetflixNoInstantWatchError("Netflix account must have instant watch access")
            linkedAccount.linked_user_id = userInfo['user_id']
            linkedAccount.linked_name = "%s %s" % (userInfo['first_name'], userInfo['last_name'])

        linkedAccount = self._accountDB.addLinkedAccount(authUserId, linkedAccount)

        # Send out alerts, if applicable
        if linkedAccount.service_name == 'facebook':
            tasks.invoke(tasks.APITasks.alertFollowersFromFacebook, args=[authUserId, linkedAccount.token])
        elif linkedAccount.service_name == 'twitter':
            tasks.invoke(tasks.APITasks.alertFollowersFromTwitter,
                         args=[authUserId, linkedAccount.token, linkedAccount.secret])

        return linkedAccount

#    @API_CALL
#    def updateLinkedAccount(self, authUserId, linkedAccount):
#        # Before we do anything, verify that the account is valid
#        self.verifyLinkedAccount(linkedAccount)
#        self.removeLinkedAccount(authUserId, linkedAccount.service_name)
#        return self.addLinkedAccount(authUserId, linkedAccount)

    @API_CALL
    def updateLinkedAccountShareSettings(self, authUserId, service_name, on, off):
        account = self._accountDB.getAccount(authUserId)

        if account.linked is None or getattr(account.linked, service_name, None) is None:
            raise StampedLinkedAccountDoesNotExistError("Referencing non-existent linked account: %s for user: %s" %
                                                  (service_name, authUserId))
        linkedAccount = getattr(account.linked, service_name)

        shareSettings = linkedAccount.share_settings
        if shareSettings is None:
            shareSettings = LinkedAccountShareSettings()

        if on is not None:
            for attr in on:
                if hasattr(shareSettings, attr):
                    setattr(shareSettings, attr, True)

        if off is not None:
            for attr in off:
                if hasattr(shareSettings, attr):
                    setattr(shareSettings, attr, False)

        linkedAccount.share_settings = shareSettings

        self._accountDB.updateLinkedAccount(authUserId, linkedAccount)
        return linkedAccount

    def _getOpenGraphShareSettings(self, authUserId):
        account = self.getAccount(authUserId)

        # for now, only post to open graph for mike and kevin
        if account.screen_name_lower not in ['ml', 'kevin', 'robby', 'chrisackermann']:
            logs.warning('### Skipping Open Graph post because user not on whitelist')
            return

        if account.linked is None or\
           account.linked.facebook is None or\
           account.linked.facebook.share_settings is None or\
           account.linked.facebook.token is None:
            return None

        return account.linked.facebook.share_settings


    @API_CALL
    def removeLinkedAccount(self, authUserId, service_name):
        if service_name not in ['facebook', 'twitter', 'netflix', 'rdio']:
            raise StampedLinkedAccountDoesNotExistError("Invalid linked account: %s" % service_name)

        account = self.getAccount(authUserId)
        if account.auth_service == service_name:
            raise StampedLinkedAccountIsAuthError('Cannot remove a linked account used for authorization.')

        self._accountDB.removeLinkedAccount(authUserId, service_name)
        return True

    @API_CALL
    def alertFollowersFromTwitterAsync(self, authUserId, twitterKey, twitterSecret):
        account   = self._accountDB.getAccount(authUserId)

        # Only send alert once (when the user initially connects to Twitter)
        if self._accountDB.checkLinkedAccountAlertHistory(authUserId, 'twitter', account.linked.twitter.linked_user_id):
            return False

#        if account.linked.twitter.alerts_sent == True or not account.linked.twitter.user_screen_name:
#            return False

        # Grab friend list from Twitter API
        tw_followers = self._getTwitterFollowers(twitterKey, twitterSecret)

        # Send alert to people not already following the user
        followers = self._friendshipDB.getFollowers(authUserId)
        userIds = []
        for user in tw_followers:
            if user.user_id not in followers:
                userIds.append(user.user_id)

        # Generate activity item
        if len(userIds) > 0:
            self._addLinkedFriendActivity(authUserId, 'twitter', userIds,
                                                 body = 'Your Twitter friend %s joined Stamped.' % account.linked.twitter.linked_screen_name)
            self._accountDB.addLinkedAccountAlertHistory(authUserId, 'twitter', account.linked.twitter.linked_user_id)

        return True

    @API_CALL
    def alertFollowersFromFacebookAsync(self, authUserId, facebookToken):
        account   = self._accountDB.getAccount(authUserId)

        # Only send alert once (when the user initially connects to Facebook)
        if self._accountDB.checkLinkedAccountAlertHistory(authUserId, 'facebook', account.linked.facebook.linked_user_id):
            logs.info("Facebook alerts already sent")
            return False

        # Grab friend list from Facebook API
        fb_friends = self._getFacebookFriends(facebookToken)

        # Send alert to people not already following the user
        followers = self._friendshipDB.getFollowers(authUserId)
        userIds = []
        for user in fb_friends:
            if user.user_id not in followers:
                userIds.append(user.user_id)

        # Generate activity item
        if len(userIds) > 0:
            self._addLinkedFriendActivity(authUserId, 'facebook', userIds,
                                          body = 'Your Facebook friend %s joined Stamped.' % account.linked.facebook.linked_name)
            self._accountDB.addLinkedAccountAlertHistory(authUserId, 'facebook', account.linked.facebook.linked_user_id)

    @API_CALL
    def addToNetflixInstant(self, nf_user_id, nf_token, nf_secret, netflixId):
        if (nf_user_id is None or nf_token is None or nf_secret is None):
            logs.info('Returning because of missing account credentials')
            return None

        netflix = globalNetflix()
        return netflix.addToQueue(nf_user_id, nf_token, nf_secret, netflixId)

    @API_CALL
    def addToNetflixInstantWithUserId(self, authUserId, netflixId):
        account   = self._accountDB.getAccount(authUserId)

        nf_user_id  = None
        nf_token    = None
        nf_secret   = None

        if account.linked is not None and account.linked.netflix is not None:
            nf_user_id  = account.linked.netflix.linked_user_id
            nf_token    = account.linked.netflix.token
            nf_secret   = account.linked.netflix.secret

        return self.addToNetflixInstant(nf_user_id, nf_token, nf_secret, netflixId)


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

    def getUserFromIdOrScreenName(self, userTiny):
        if not isinstance(userTiny, Schema):
            userTiny = UserTiny().dataImport(userTiny)

        if userTiny.user_id is None and userTiny.screen_name is None:
            raise StampedMissingParametersError("Required field missing (user id or screen name)")

        if userTiny.user_id is not None:
            return self._userDB.getUser(userTiny.user_id)

        return self._userDB.getUserByScreenName(userTiny.screen_name)

    def _getUserStampDistribution(self, userId):
        stampIds    = self._collectionDB.getUserStampIds(userId)
        stamps      = self._stampDB.getStamps(stampIds)
        stamps      = self._enrichStampObjects(stamps)

        categories  = {}
        num_stamps  = len(stamps)

        for stamp in stamps:
            category = stamp.entity.category
            categories.setdefault(category, 0)
            categories[category] += 1

        result = []
        for k, v in categories.items():
            distribution = CategoryDistribution()
            distribution.category = k
            distribution.count = v
            result.append(distribution)

        return result

    def _enrichUserObjects(self, users, authUserId=None, **kwargs):

        singleUser = False
        if not isinstance(users, list):
            singleUser  = True
            users       = [users]

        # Only enrich "following" field for now
        if authUserId is not None:
            friends = self._friendshipDB.getFriends(authUserId)
            result = []
            for user in users:
                if user.user_id in friends:
                    user.following = True
                else:
                    user.following = False
                result.append(user)
            users = result

        if singleUser:
            return users[0]

        return users


    ### PUBLIC

    @API_CALL
    def getUser(self, userRequest, authUserId=None):
        user = self.getUserFromIdOrScreenName(userRequest)

        if user.privacy == True:
            if authUserId is None:
                raise StampedViewUserPermissionsError("Insufficient privileges to view user")

            friendship              = Friendship()
            friendship.user_id      = authUserId
            friendship.friend_id    = user.user_id

            if not self._friendshipDB.checkFriendship(friendship):
                raise StampedViewUserPermissionsError("Insufficient privileges to view user")

        if user.stats.num_stamps is not None and user.stats.num_stamps > 0:
            if user.stats.distribution is None or len(user.stats.distribution) == 0:
                distribution = self._getUserStampDistribution(user.user_id)
                user.stats.distribution = distribution
                ### TEMP: This should be async
                self._userDB.updateDistribution(user.user_id, distribution)

        return self._enrichUserObjects(user, authUserId=authUserId)

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

        return self._enrichUserObjects(result, authUserId=authUserId)

    @API_CALL
    def getPrivacy(self, userRequest):
        user = self.getUserFromIdOrScreenName(userRequest)

        return (user.privacy == True)

    @API_CALL
    def findUsersByEmail(self, authUserId, emails):
        ### TODO: Condense with the other "findUsersBy" functions
        ### TODO: Add check for privacy settings?

        users = self._userDB.findUsersByEmail(emails, limit=100)
        return self._enrichUserObjects(users, authUserId=authUserId)

    @API_CALL
    def findUsersByPhone(self, authUserId, phone):
        ### TODO: Add check for privacy settings?

        users = self._userDB.findUsersByPhone(phone, limit=100)
        return self._enrichUserObjects(users, authUserId=authUserId)

    @API_CALL
    def findUsersByTwitter(self, authUserId, user_token, user_secret):
        ### TODO: Add check for privacy settings?
        users = []

        # Grab friend list from Facebook API
        users = self._getTwitterFriends(user_token, user_secret)
        return self._enrichUserObjects(users, authUserId=authUserId)

    @API_CALL
    def findUsersByFacebook(self, authUserId, user_token=None):
        ### TODO: Add check for privacy settings?
        users = []

        # Grab friend list from Facebook API
        users = self._getFacebookFriends(user_token)
        return self._enrichUserObjects(users, authUserId=authUserId)

    @API_CALL
    def getFacebookFriendData(self, user_token=None, offset=0, limit=30):
        ### TODO: Add check for privacy settings?
        if user_token is None:
            raise StampedThirdPartyInvalidCredentialsError("Connecting to Facebook requires a valid token")

        # Grab friend list from Facebook API
        return self._facebook.getFriendData(user_token, offset, limit)

    @API_CALL
    def getTwitterFriendData(self, user_token=None, user_secret=None, offset=0, limit=30):
        ### TODO: Add check for privacy settings?
        if user_token is None or user_secret is None:
            raise StampedThirdPartyInvalidCredentialsError("Connecting to Twitter requires a valid token/secret")

        # Grab friend list from Twitter API
        return self._twitter.getFriendData(user_token, user_secret, offset, limit)

    @API_CALL
    def searchUsers(self, authUserId, query, limit, relationship):
        if limit <= 0 or limit > 20:
            limit = 20

        ### TODO: Add check for privacy settings

        users = self._userDB.searchUsers(authUserId, query, limit, relationship)
        return self._enrichUserObjects(users, authUserId=authUserId)

    @API_CALL
    def getSuggestedUsers(self, authUserId, limit=None, offset=None):
        suggested = [
            'mariobatali',
            'nymag',
            'time',
            'urbandaddy',
            'parislemon',
            'michaelkors',
            'petertravers',
            'rebeccaminkoff',
            'austinchronicle',
        ]
        users = self.getUsers(None, suggested, authUserId)
        users.sort(key=lambda x: suggested.index(x.screen_name.lower()))
        return self._enrichUserObjects(users, authUserId=authUserId)

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
        user = self.getUserFromIdOrScreenName(userRequest)

        # Verify that you're not following yourself :)
        if user.user_id == authUserId:
            raise StampedInvalidFriendshipError("Illegal friendship: you can't follow yourself!")

        friendship              = Friendship()
        friendship.user_id      = authUserId
        friendship.friend_id    = user.user_id

        # Check if friendship already exists
        if self._friendshipDB.checkFriendship(friendship) == True:
            logs.info("Friendship exists")
            return user

        # Check if block exists between authenticating user and user
        if self._friendshipDB.blockExists(friendship) == True:
            raise StampedBlockedUserError("Block exists")

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
            self._addFollowActivity(authUserId, userId)

            # Remove 'friend' activity item
            self._activityDB.removeFriendActivity(authUserId, userId)

        # Add stamps to Inbox
        stampIds = self._collectionDB.getUserStampIds(userId)
        self._stampDB.addInboxStampReferencesForUser(authUserId, stampIds)

        # Increment stats for both users
        self._userDB.updateUserStats(authUserId, 'num_friends',   increment=1)
        self._userDB.updateUserStats(userId,     'num_followers', increment=1)

        # Refresh guide
        tasks.invoke(tasks.APITasks.buildGuide, args=[authUserId])

        # Post to Facebook Open Graph if enabled
        share_settings = self._getOpenGraphShareSettings(authUserId)
        if share_settings is not None and share_settings.share_follows:
            tasks.invoke(tasks.APITasks.postToOpenGraph, kwargs={'authUserId': authUserId,'followUserId':userId})

    @API_CALL
    def removeFriendship(self, authUserId, userRequest):
        user                    = self.getUserFromIdOrScreenName(userRequest)
        friendship              = Friendship()
        friendship.user_id      = authUserId
        friendship.friend_id    = user.user_id

        # Check if friendship doesn't exist
        if self._friendshipDB.checkFriendship(friendship) == False:
            logs.info("Friendship does not exist")
            return user

        self._friendshipDB.removeFriendship(friendship)

        # Asynchronously remove stamps for this friendship
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

    @API_CALL
    def approveFriendship(self, data, auth):
        raise NotImplementedError

    @API_CALL
    def checkFriendship(self, authUserId, userRequest):
        userA = self.getUserFromIdOrScreenName({
                    'user_id': userRequest.user_id_a,
                    'screen_name': userRequest.screen_name_a
                })
        userB = self.getUserFromIdOrScreenName({
                    'user_id': userRequest.user_id_b,
                    'screen_name': userRequest.screen_name_b
                })

        # If either account is private, make sure authUserId is friend
        if userA.privacy == True and authUserId != userA.user_id:
            check                   = Friendship()
            friendship.user_id      = authUserId
            friendship.friend_id    = userA.user_id

            if not self._friendshipDB.checkFriendship(check):
                raise StampedFriendshipCheckPermissionsError("Insufficient privileges to check friendship")

        if userB.privacy == True and authUserId != userB.user_id:
            check                   = Friendship()
            friendship.user_id      = authUserId
            friendship.friend_id    = userB.user_id

            if not self._friendshipDB.checkFriendship(check):
                raise StampedFriendshipCheckPermissionsError("Insufficient privileges to check friendship")

        friendship              = Friendship()
        friendship.user_id      = userA.user_id
        friendship.friend_id    = userB.user_id

        return self._friendshipDB.checkFriendship(friendship)

    @API_CALL
    def getFriends(self, userRequest):
        # TODO (travis): optimization - no need to query DB for user here if userRequest already contains user_id!
        user = self.getUserFromIdOrScreenName(userRequest)

        # Note: This function returns data even if user is private

        friends = self._friendshipDB.getFriends(user.user_id)

        # Return data in reverse-chronological order
        friends.reverse()

        return friends
    
    @API_CALL
    def getEnrichedFriends(self, user_id, limit=100):
        user_ids = self._friendshipDB.getFriends(user_id, limit=limit)
        
        # Return data in reverse-chronological order
        user_ids.reverse()
        
        return self._userDB.lookupUsers(user_ids, None, limit=limit)
    
    @API_CALL
    def getFollowers(self, userRequest):
        # TODO (travis): optimization - no need to query DB for user here if userRequest already contains user_id!
        user = self.getUserFromIdOrScreenName(userRequest)
        
        # Note: This function returns data even if user is private
        
        followers = self._friendshipDB.getFollowers(user.user_id)
        
        # Return data in reverse-chronological order
        followers.reverse()
        
        return followers
    
    @API_CALL
    def getEnrichedFollowers(self, user_id, limit=100):
        user_ids = self._friendshipDB.getFollowers(user_id, limit=limit)
        
        # Return data in reverse-chronological order
        user_ids.reverse()
        
        return self._userDB.lookupUsers(user_ids, None, limit=limit)
    
    @API_CALL
    def addBlock(self, authUserId, userRequest):
        user = self.getUserFromIdOrScreenName(userRequest)

        friendship                      = Friendship()
        friendship.user_id              = authUserId
        friendship.friend_id            = user.user_id

        reverseFriendship               = Friendship()
        reverseFriendship.user_id       = user.user_id
        reverseFriendship.friend_id     = authUserId

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
        user                    = self.getUserFromIdOrScreenName(userRequest)
        friendship              = Friendship()
        friendship.user_id      = authUserId
        friendship.friend_id    = user.user_id

        if self._friendshipDB.checkBlock(friendship):
            return True

        return False

    @API_CALL
    def getBlocks(self, authUserId):
        return self._friendshipDB.getBlocks(authUserId)

    @API_CALL
    def removeBlock(self, authUserId, userRequest):
        user                    = self.getUserFromIdOrScreenName(userRequest)
        friendship              = Friendship()
        friendship.user_id      = authUserId
        friendship.friend_id    = user.user_id

        # Check if block already exists
        if self._friendshipDB.checkBlock(friendship) == False:
            logs.info("Block does not exist")
            return user

        self._friendshipDB.removeBlock(friendship)

        ### TODO: Reenable activity items that were hidden before

        return user

    @API_CALL
    def inviteFriends(self, authUserId, emails):
        for email in emails:
            # Store email address linked to auth user id
            tasks.invoke(tasks.APITasks.inviteFriends, args=[authUserId, email])
        return True

    @API_CALL
    def inviteFriendsAsync(self, authUserId, email):
        # Validate email address
        email = str(email).lower().strip()
        email = SchemaValidation.validateEmail(email)

        if self._inviteDB.checkInviteExists(email, authUserId):
            logs.info("Invite already exists")
            return

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
        if isinstance(entityRequest, Schema):
            entityRequest = entityRequest.dataExport()

        entityId    = entityRequest.pop('entity_id', None)
        searchId    = entityRequest.pop('search_id', None)

        if entityId is None and searchId is None:
            raise StampedMissingParametersError("Required field missing (entity_id or search_id)")

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
        timestamp = BasicTimestamp()
        timestamp.created = datetime.utcnow()
        entity.timestamp = timestamp
        entity = self._entityDB.addEntity(entity)
        return entity

    @API_CALL
    def getEntity(self, entityRequest, authUserId=None):
        entity = self._getEntityFromRequest(entityRequest)

        if entity.isType('artist') and entity.albums is not None:
            albumIds = {}
            for album in entity.albums:
                if album.entity_id is not None:
                    albumIds[album.entity_id] = None
            try:
                albums = self._entityDB.getEntities(albumIds.keys())
            except Exception:
                logs.warning("Unable to get albums for keys: %s" % albumIds.keys())
                albums = []

            for album in albums:
                albumIds[album.entity_id] = album.minimize()

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
            raise StampedEntityUpdatePermissionError("Insufficient privileges to update custom entity")

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
            raise StampedTombstonedEntityError('Cannot update entity %s - old entity has been tombstoned' % entity.entity_id)

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
    def _oldEntitySearch(self):
        from resolve.EntitySearch import EntitySearch
        return EntitySearch()

    @lazyProperty
    def _newEntitySearch(self):
        from search.EntitySearch import EntitySearch
        return EntitySearch()

    @API_CALL
    def searchEntities(self,
                       query,
                       coords=None,
                       authUserId=None,
                       category=None):

        coordsAsTuple = None if coords is None else (coords.lat, coords.lng)
        entities = self._newEntitySearch.searchEntities(category, query, limit=10, coords=coordsAsTuple)

        results = []
        numToStore = 5

        if category != 'place':
            # The 'place' search engines -- especially Google -- return these shitty half-assed results with nowhere
            # near enough detail to be useful for a user, so we definitely want to do a full lookup on those.
            for entity in entities[:numToStore]:
                self._searchEntityDB.writeSearchEntity(entity)

        for entity in entities:
            distance = None
            try:
                if coords is not None and entity.coordinates is not None:
                    a = (coords.lat, coords.lng)
                    b = (entity.coordinates.lat, entity.coordinates.lng)
                    distance = abs(utils.get_spherical_distance(a, b) * 3959)
            except Exception:
                pass

            results.append((entity, distance))

        return results

    def _orderedUnique(self, theList):
        known = set()
        newlist = []

        for d in theList:
            if d in known: continue
            newlist.append(d)
            known.add(d)

        return newlist

    @API_CALL
    def getEntityAutoSuggestions(self, query, category, coordinates=None, authUserId=None):
        if datetime.now() - self.__autocomplete_last_loaded > timedelta(1):
            self.__autocomplete_last_loaded = datetime.now()
            gevent.spawn(loadIndexFromS3).link(self.reloadAutoCompleteIndex)
        if category == 'place':
            if coordinates is None:
                latLng = None
            else:
                latLng = [ coordinates.lat, coordinates.lng ]
            results = self._googlePlaces.getAutocompleteResults(latLng, query, {'radius': 500, 'types' : 'establishment'})
            #make list of names from results, remove duplicate entries, limit to 10
            if results is None:
                return []
            names = self._orderedUnique([place['terms'][0]['value'] for place in results])[:10]
            completions = []
            for name in names:
                completions.append( { 'completion' : name } )
            return completions

        return [{'completion' : name} for name in self.__autocomplete[category][normalizeTitle(unicode(query))]]

    def reloadAutoCompleteIndex(self, greenlet):
        try:
            self.__autocomplete = greenlet.get()
        except Exception as e:
            email = {
                'from' : 'Stamped <noreply@stamped.com>',
                'to' : 'dev@stamped.com',
                'subject' : 'Error while reloading autocomplete index on ' + self.node_name,
                'body' : '<pre>%s</pre>' % str(e),
            }
            utils.sendEmail(email, format='html')

    def updateAutoCompleteIndexAsync(self):
        pushNewIndexToS3()

    @API_CALL
    def getSuggestedEntities(self, authUserId, category, subcategory=None, coordinates=None, limit=10):
        if category == 'place':
            return self._suggestedEntities.getSuggestedEntities(authUserId,
                                                                category=category,
                                                                subcategory=subcategory,
                                                                coords=coordinates,
                                                                limit=limit)

        groups = []

        if category == 'book':
            entityIds = [
                '4edfa29154533e754e00102e', # Steve Jobs
                '4e57aca741ad85147e00153f', # A Game of Thrones
                '4e57ac5841ad85147e000425', # The Hunger Games
                '4fff6529967d717a14000041', # Bared to You
                '4ecaf331fc905f14cc000005', # Fifty Shades of Grey
                '4fe3342e9713961a5e000b5b', # Gone Girl
                '4fff652b967d717a14000047', # Wild
                '4fff652b967d717a1300006c', # Amateur
                '4fff6554967d717a1400013b', # Criminal
                '4fff6555967d717a14000143', # The Next Best Thing 
            ]
            groups.append(('Suggestions', entityIds))

        elif category == 'film':
            entityIds = [
                '4e9cbd8cfe4a1d7bd2000070', # Game of Thrones
                '4ffa194a64c7940d380005f5', # Ted
                '4f835f34d56d835c6e000572', # 21 Jump Street 
                '4e9fb96dfe4a1d1cbe0000f5', # Breaking Bad 
                '4fff6510967d717a13000029', # Magic Mike
                '4fff6507967d717a13000018', # The Amazing Spider Man 
                '4f60dd2cd56d836764000ad6', # Moonrise Kingdom 
                '4fff6519967d717a1300003a', # To Rome With Love
                '4fff650c967d717a13000022', # Brave
                '4eb1c60941ad8531d2000f0b', # Dexter
                '4eb2159b41ad8531d2004a3e', # The Big Bang Theory
            ]
            groups.append(('Suggestions', entityIds))

        elif category == 'music':
            # Songs
            entityIds = [
                '50009a5f64c7945730000556', # wide awake - katy perry
                '4fe47ec964c79459850002ad', # call me maybe - carly rae jepsen
                '50009aac64c794572c0000ac', # whistle - flo rida
                '4f9f0b3c591fa478c30006ac', # Starships - Nikki minaj
            ]
            groups.append(('Songs', entityIds))

            # Albums
            entityIds = [
                '4faa7152591fa4535a0009c2', # Some nights - Fun
                '4fb4fe40591fa462ec0000c5', # Believe - Justin Bieber
                '4eb8716041ad850b9a000009', # Teenage Dream - Katy Perry
                '4fe30253591fa41b4e0008f8', # Overexposed - Maroon 5
                '4ed5418d4820c5450400079a', # Bon Iver - Bon Iver
            ]
            groups.append(('Albums', entityIds))

            # Artists
            entityIds = [
                '4eb3001b41ad855d53000ac8', # Katy Perry
                '4ecb6893fc905f1561000f96', # Bon Iver
                '4eb8700441ad850b6200004f', # Maroon 5
                '4ee0233c54533e75460010e1', # Justin Bieber
                '4eb300e941ad855d53000c36', # Kanye West
                '4f593804d56d835b3e000543', # Fun
            ]
            groups.append(('Artists', entityIds))

        elif category == 'app':
            # Free
            entityIds = [
                '4edac94056f8685d87000bec', # Angry Birds
                '4efa2c666e33431b71000cf2', # Instagram
                '4edac5d1e32a3a08d400000b', # Temple Run
                '4ed44c9482750f30b70002fd', # Pinterest
                '4ed44c3f82750f30b7000196', # Spoitfy
                '4f45e36c591fa43214000195', # Clear
            ]
            groups.append(('Free', entityIds))

            # Paid
            entityIds = [
                '4ed480e456f86859c20023bd', # Words with Friends
                '4fea8b5b64c794370b000222', # Temple Run: Brave
                '4edad3d7e32a3a08d4000048', # The Sims 3
            ]
            groups.append(('Paid', entityIds))

        result = []
        for group in groups:
            name = group[0]
            entityIds = group[1]
            entities = self._entityDB.getEntities(entityIds)
            entities.sort(key=lambda x: entityIds.index(x.entity_id))

            result.append({'name': name, 'entities': entities })
            
        return result

    @API_CALL
    def getMenu(self, entityId):
        menu = self._menuDB.getMenu(entityId)
        if menu is None:
            try:
                self.mergeEntityId(entityId)
                menu = self._menuDB.getMenu(entityId)
            except Exception:
                pass
        if menu is None:
            raise StampedMenuUnavailableError()
        else:
            return menu

    @API_CALL
    def completeAction(self, authUserId, **kwargs):
        tasks.invoke(tasks.APITasks.completeAction, args=[authUserId], kwargs=kwargs)
        return True

    def completeActionAsync(self, authUserId, **kwargs):
        action      = kwargs.pop('action', None)
        source      = kwargs.pop('source', None)
        sourceId    = kwargs.pop('source_id', None)
        entityId    = kwargs.pop('entity_id', None)
        userId      = kwargs.pop('user_id', None)
        stampId     = kwargs.pop('stamp_id', None)

        actions = set([
            'listen',
            'playlist',
            'download',
            'reserve',
            'menu',
            'buy',
            'watch',
            'tickets',
            'queue',
        ])

        # For now, only complete the action if it's associated with an entity and a stamp
        if stampId is not None:
            stamp   = self._stampDB.getStamp(stampId)
            # user    = self._userDB.getUser(stamp.user.user_id)
            entity  = self._entityDB.getEntity(stamp.entity.entity_id)

            if action in actions and authUserId != stamp.user.user_id:
                self._addActionCompleteActivity(authUserId, action, source, stamp.stamp_id, stamp.user.user_id)

        return True

    @API_CALL
    def entityStampedBy(self, entityId, authUserId=None, limit=100):
        try:
            stats = self._entityStatsDB.getEntityStats(entityId)
        except StampedUnavailableError:
            stats = self.updateEntityStatsAsync(entityId)

        userIds = {}

        # Get popular stamp data
        popularUserIds = map(str, stats.popular_users[:limit])
        popularStamps = self._stampDB.getStampsFromUsersForEntity(popularUserIds, entityId)
        popularStamps.sort(key=lambda x: popularUserIds.index(x.user.user_id))

        # Get friend stamp data
        if authUserId is not None:
            friendUserIds = self._friendshipDB.getFriends(authUserId)
            friendStamps = self._stampDB.getStampsFromUsersForEntity(friendUserIds, entityId)

        # Build user list
        for stamp in popularStamps:
            userIds[stamp.user.user_id] = None
        if authUserId is not None:
            for stamp in friendStamps:
                userIds[stamp.user.user_id] = None

        users = self._userDB.lookupUsers(userIds.keys())
        for user in users:
            userIds[user.user_id] = user.minimize()

        # Populate popular stamps
        stampedby = StampedBy()

        stampPreviewList = []
        for stamp in popularStamps:
            preview = StampPreview()
            preview.stamp_id = stamp.stamp_id
            preview.user = userIds[stamp.user.user_id]
            if preview.user is not None:
                stampPreviewList.append(preview)

        allUsers            = StampedByGroup()
        allUsers.stamps     = stampPreviewList
        allUsers.count      = stats.num_stamps
        stampedby.all       = allUsers

        # Populate friend stamps
        if authUserId is not None:
            stampPreviewList = []
            for stamp in friendStamps:
                preview = StampPreview()
                preview.stamp_id = stamp.stamp_id
                preview.user = userIds[stamp.user.user_id]
                stampPreviewList.append(preview)

            friendUsers         = StampedByGroup()
            friendUsers.stamps  = stampPreviewList
            friendUsers.count   = len(friendStamps)
            stampedby.friends   = friendUsers

        return stampedby

    def updateEntityStatsAsync(self, entityId):
        try:
            entity = self._entityDB.getEntity(entityId)
        except StampedDocumentNotFoundError:
            logs.warning("Entity not found: %s" % entityId)
            return 

        if entity.sources.tombstone_id is not None:
            # Call async process to update references
            tasks.invoke(tasks.APITasks.updateTombstonedEntityReferences, args=[entity.entity_id])

        numStamps = self._stampDB.countStampsForEntity(entityId)
        popularStampIds = self._stampStatsDB.getPopularStampIds(entityId=entityId, limit=1000)

        # If for some reason popularStampIds doesn't include all stamps, recalculate them
        if numStamps < 1000 and len(popularStampIds) < numStamps:
            logs.warning("Recalculating stamp stats for entityId=%s" % entityId)
            allStampIds = self._stampDB.getStampIdsForEntity(entityId)
            for stampId in allStampIds:
                if stampId not in popularStampIds:
                    stat = self.updateStampStatsAsync(stampId)
            popularStampIds = self._stampStatsDB.getPopularStampIds(entityId=entityId, limit=1000)

        popularStamps = self._stampDB.getStamps(popularStampIds)
        popularStamps.sort(key=lambda x: popularStampIds.index(x.stamp_id))
        popularStampIds = map(lambda x: x.stamp_id, popularStamps)
        popularUserIds = map(lambda x: x.user.user_id, popularStamps)
        popularStampStats = self._stampStatsDB.getStatsForStamps(popularStampIds)

        if len(popularStampIds) != len(popularUserIds):
            logs.warning("%s: Length of popularStampIds doesn't equal length of popularUserIds" % entityId)
            raise Exception

        numTodos = self._todoDB.countTodosFromEntityId(entityId)
        
        aggStampScore = 0

        for stampStat in popularStampStats:
            if stampStat.score is not None:
                aggStampScore += stampStat.score

        popularity = (1 * numTodos) + (1 * aggStampScore)

        # Entity Quality is a mixture of having an image and having enrichment
        if entity.kind == 'other':
            quality = 0.1
        else:
            quality = 0.6
        
            # Check if entity has an image (places don't matter)
            if entity.kind != 'place':
                if entity.images is None:
                    quality -= 0.3

            # Places
            if entity.kind == 'place':
                if entity.sources.googleplaces_id is None:
                    quality -= 0.3
                if entity.formatted_address is None:
                    quality -= 0.1
                if entity.sources.singleplatform_id is not None:
                    quality += 0.2
                if entity.sources.opentable_id is not None:
                    quality += 0.1


            # Music 
            if entity.isType('track') or entity.isType('album') or entity.isType('artist'):
                
                if entity.sources.itunes_id is None:
                    quality -= 0.3
                if entity.sources.spotify_id is not None: 
                    quality += 0.15
                if entity.sources.rdio_id is not None:
                    quality += 0.15

                if entity.isType('track'):
                    if entity.artists is None:
                        quality -= 0.1
                    if entity.albums is None:
                        quality -= 0.05

                elif entity.isType('artist'):
                    if entity.tracks is None:
                        quality -= 0.1
                    if entity.albums is None:
                        quality -= 0.05

                elif entity.isType('album'):
                    if entity.artists is None:
                        quality -= 0.1
                    if entity.tracks is None:
                        quality -= 0.1

            # Movies and TV
            if entity.isType('movie'):

                if entity.sources.tmdb_id is None:
                    quality -= 0.3
                if entity.sources.itunes_id is not None:
                    quality += 0.2
                if entity.sources.netflix_id is not None:
                    quality += 0.1

            if entity.isType('tv'):
                if entity.sources.thetvdb_id is None:
                    quality -= 0.15
                if entity.sources.netflix_id is not None:
                    quality += 0.2

            # Books
            if entity.isType('book'):

                if entity.sources.amazon_id is None:
                    quality -= 0.2
                if entity.sources.itunes_id is not None:
                    quality += 0.1

            # Apps
            if entity.types[0] == 'app':

                if entity.sources.itunes_url is None:
                    quality -= 0.4
                else:
                    quality += 0.1


        if quality > 1.0:
            logs.warning("Quality score greater than 1 for entity %s" % entityId)
            quality = 1.0

        score = max(quality, quality * popularity)

        stats = EntityStats()
        stats.entity_id = entity.entity_id
        stats.num_stamps = numStamps
        stats.popular_users = popularUserIds
        stats.popular_stamps = popularStampIds
        stats.popularity = popularity
        stats.quality = quality
        stats.score = score
        stats.kind = entity.kind
        stats.types = entity.types
        if entity.kind == 'place' and entity.coordinates is not None:
            stats.lat = entity.coordinates.lat
            stats.lng = entity.coordinates.lng
        self._entityStatsDB.saveEntityStats(stats)

        return stats

    def updateTombstonedEntityReferencesAsync(self, oldEntityId):
        """
        Basic function to update all references to an entity_id that has been tombstoned.
        """
        oldEntity = self._entityDB.getEntity(oldEntityId)
        if oldEntity.sources.tombstone_id is None:
            logs.info("Short circuit: tombstone_id is 'None' for entity %s" % oldEntityId)
            return
        
        newEntity = self._entityDB.getEntity(oldEntity.sources.tombstone_id)
        newEntityId = newEntity.entity_id
        newEntityMini = newEntity.minimize()

        # Stamps
        stampIds = self._stampDB.getStampIdsForEntity(oldEntityId)
        for stampId in stampIds:
            self._stampDB.updateStampEntity(stampId, newEntityMini)
            r = self.updateStampStatsAsync(stampId)

        # Todos
        todoIds = self._todoDB.getTodoIdsFromEntityId(oldEntityId)
        for todoId in todoIds:
            self._todoDB.updateTodoEntity(todoId, newEntityMini)

        self.updateEntityStatsAsync(newEntityId)


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
        if text is None:
            return set()

        screenNames = set()

        # Extract screen names with regex
        for user in self._user_regex.finditer(text):
            screenNames.add(str(user.groups()[0]).lower())

        # Match screen names to users
        users = self._userDB.lookupUsers(screenNames=list(screenNames))
        validScreenNames = set(map(lambda x: str(x.screen_name).lower(), users))

        # Log any invalid screen names
        if len(screenNames) > len(validScreenNames):
            logs.warning("Mentioned screen names not found: %s" % screenNames.difference(validScreenNames))
            logs.debug("Text: %s" % text)

        return validScreenNames

    def _extractCredit(self, creditData, entityId, stampOwner=None):
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
                userId = creditedUser.user_id
                # User cannot give themselves credit!
                if stampOwner is not None and userId == stampOwner:
                    continue
                # User can't give credit to the same person twice
                if userId in creditedUserIds:
                    continue

                result              = StampPreview()
                result.user         = creditedUser.minimize()

                # Assign credit
                creditedStamp = self._stampDB.getStampFromUserEntity(userId, entityId)
                if creditedStamp is not None:
                    result.stamp_id = creditedStamp.stamp_id

                credit.append(result)
                creditedUserIds.add(userId)

        ### TODO: How do we handle credited users that have not yet joined?
        if len(credit) > 0:
            return credit

        return []

    def _enrichStampObjects(self, stampObjects, **kwargs):
        t0 = time.time()
        t1 = t0

        previewLength = kwargs.pop('previews', 10)
        mini        = kwargs.pop('mini', False)

        authUserId  = kwargs.pop('authUserId', None)
        entityIds   = kwargs.pop('entityIds', {})
        userIds     = kwargs.pop('userIds', {})

        singleStamp = False
        if not isinstance(stampObjects, list):
            singleStamp = True
            stampObjects = [stampObjects]

        stampIds = {}
        for stamp in stampObjects:
            stampIds[stamp.stamp_id] = stamp

        stats = self.getStampStats(stampIds.keys())
        # stats = self._stampStatsDB.getStatsForStamps(stampIds.keys())

        logs.debug('Time for getStatsForStamps: %s' % (time.time() - t1))
        t1 = time.time()

        """
        ENTITIES

        Enrich the underlying entity object for all stamps
        """
        allEntityIds = set()

        for stamp in stampObjects:
            allEntityIds.add(stamp.entity.entity_id)

        # Enrich missing entity ids
        missingEntityIds = allEntityIds.difference(set(entityIds.keys()))
        if mini:
            entities = self._entityDB.getEntityMinis(list(missingEntityIds))
        else:
            entities = self._entityDB.getEntities(list(missingEntityIds))

        for entity in entities:
            if entity.sources.tombstone_id is not None:
                # Convert to newer entity
                replacement = self._entityDB.getEntityMini(entity.sources.tombstone_id)
                entityIds[entity.entity_id] = replacement
                # Call async process to update references
                tasks.invoke(tasks.APITasks.updateTombstonedEntityReferences, args=[entity.entity_id])
            else:
                entityIds[entity.entity_id] = entity

        logs.debug('Time for getEntities: %s' % (time.time() - t1))
        t1 = time.time()

        """
        STAMPS

        Enrich the underlying stamp objects for credit received
        """
        underlyingStampIds      = {}
        allUnderlyingStampIds   = set()

        for stat in stats.values():
            if stat.preview_credits is not None:
                for credit in stat.preview_credits[:previewLength]:
                    allUnderlyingStampIds.add(credit)

        # Enrich underlying stamp ids
        underlyingStamps = self._stampDB.getStamps(list(allUnderlyingStampIds))

        for stamp in underlyingStamps:
            underlyingStampIds[stamp.stamp_id] = stamp

        logs.debug('Time for getStamps: %s' % (time.time() - t1))
        t1 = time.time()

        """
        COMMENTS

        Pull in the comment objects for each stamp
        """
        allCommentIds   = set()
        commentIds      = {}

        for stat in stats.values():
            # Comments
            if stat.preview_comments is not None:
                for commentId in stat.preview_comments[:previewLength]:
                    allCommentIds.add(commentId)

        comments = self._commentDB.getComments(list(allCommentIds))

        for comment in comments:
            commentIds[comment.comment_id] = comment

        logs.debug('Time for getComments: %s' % (time.time() - t1))
        t1 = time.time()

        """
        USERS

        Enrich the underlying user objects. This includes:
        - Stamp owner
        - Likes
        - To-Dos
        - Credit received (restamps)
        - Credit given
        - Comments
        """
        allUserIds    = set()

        for stamp in stampObjects:
            # Stamp owner
            allUserIds.add(stamp.user.user_id)

            # Credit given
            if stamp.credits is not None:
                for credit in stamp.credits:
                    allUserIds.add(credit.user.user_id)

        for k, v in commentIds.items():
            allUserIds.add(v.user.user_id)

        for stat in stats.values():
            # Likes
            if stat.preview_likes is not None:
                for like in stat.preview_likes[:previewLength]:
                    allUserIds.add(like)

            # To-Dos
            if stat.preview_todos is not None:
                for todo in stat.preview_todos[:previewLength]:
                    allUserIds.add(todo)

        for stampId, stamp in underlyingStampIds.iteritems():
            # Credit received
            allUserIds.add(stamp.user.user_id)

        # Enrich missing user ids
        missingUserIds = allUserIds.difference(set(userIds.keys()))
        users = self._userDB.lookupUsers(list(missingUserIds))

        for user in users:
            userIds[user.user_id] = user.minimize()

        logs.debug('Time for lookupUsers: %s' % (time.time() - t1))
        t1 = time.time()


        if authUserId:
            ### TODO: Intelligent matching with stampId
            # Todos
            todos = self._todoDB.getTodoEntityIds(authUserId)

            ### TODO: Intelligent matching with stampId
            # Likes
            likes = self._stampDB.getUserLikes(authUserId)

            logs.debug('Time for authUserId queries: %s' % (time.time() - t1))
            t1 = time.time()

        """
        APPLY DATA
        """

        stamps = []

        for stamp in stampObjects:
            try:
                stamp.entity = entityIds[stamp.entity.entity_id]
                stamp.user = userIds[stamp.user.user_id]

                # Credit
                credits = []
                if stamp.credits is not None:
                    for credit in stamp.credits:
                        item                    = StampPreview()
                        item.user               = userIds[str(credit.user.user_id)]
                        item.stamp_id           = credit.stamp_id
                        credits.append(item)
                    stamp.credits = credits

                # Previews
                previews = Previews()
                try:
                    stat = stats[stamp.stamp_id]
                except KeyError:
                    stat = None

                if stat is not None:
                    # Comments
                    commentPreviews = []
                    if stat.preview_comments is not None:
                        for commentId in stat.preview_comments[:previewLength]:
                            try:
                                comment = commentIds[str(commentId)]
                                try:
                                    comment.user = userIds[str(comment.user.user_id)]
                                except KeyError:
                                    logs.warning("Key error for user (user_id = %s)" % userId)
                                    raise
                                commentPreviews.append(comment)
                            except KeyError:
                                logs.warning("Key error for comment (comment_id = %s)" % commentId)
                                logs.debug("Stamp: %s" % stamp)
                                continue
                    previews.comments = commentPreviews

                    # Likes
                    likePreviews = []
                    if stat.preview_likes is not None:
                        for userId in stat.preview_likes[:previewLength]:
                            try:
                                likePreviews.append(userIds[str(userId)])
                            except KeyError:
                                logs.warning("Key error for like (user_id = %s)" % userId)
                                logs.debug("Stamp: %s" % stamp)
                                continue
                    previews.likes = likePreviews

                    # Todos
                    todoPreviews = []
                    if stat.preview_todos is not None:
                        for userId in stat.preview_todos[:previewLength]:
                            try:
                                todoPreviews.append(userIds[str(userId)])
                            except KeyError:
                                logs.warning("Key error for todo (user_id = %s)" % userId)
                                logs.debug("Stamp: %s" % stamp)
                                continue
                    previews.todos = todoPreviews

                    # Credits
                    creditPreviews = []
                    if stat.preview_credits is not None:
                        for i in stat.preview_credits[:previewLength]:
                            try:
                                credit = underlyingStampIds[str(i)]
                                stampPreview = StampPreview()
                                stampPreview.user = userIds[str(credit.user.user_id)]
                                stampPreview.stamp_id = i
                                creditPreviews.append(stampPreview)
                            except KeyError, e:
                                logs.warning("Key error for credit (stamp_id = %s)" % i)
                                logs.warning("Error: %s" % e)
                                continue
                    previews.credits = creditPreviews

                    # Stats
                    stamp.stats.num_comments    = stat.num_comments 
                    stamp.stats.num_todos       = stat.num_todos 
                    stamp.stats.num_credit      = stat.num_credits
                    stamp.stats.num_likes       = stat.num_likes 

                else:
                    tasks.invoke(tasks.APITasks.updateStampStats, args=[str(stamp.stamp_id)])

                stamp.previews = previews

                # User-specific attributes
                if authUserId:
                    if stamp.attributes is None:
                        stamp.attributes = StampAttributesSchema()

                    # Mark as todo
                    stamp.attributes.is_todo = stamp.entity.entity_id in todos

                    # Mark as liked
                    stamp.attributes.is_liked =  stamp.stamp_id in likes

                stamps.append(stamp)

            except KeyError, e:
                logs.warning("Fatal key error: %s" % e)
                logs.debug("Stamp: %s" % stamp)
                continue
            except Exception:
                raise

        logs.debug('Time for stamp iteration: %s' % (time.time() - t1))

        logs.debug('TOTAL TIME: %s' % (time.time() - t0))

        if singleStamp:
            return stamps[0]

        return stamps

    def getStampBadges(self, stamp):
        userId = stamp.user.user_id
        entityId = stamp.entity.entity_id
        badges  = []

        if stamp.stats.stamp_num == 1:
            badge           = Badge()
            badge.user_id   = userId
            badge.genre     = "user_first_stamp"
            badges.append(badge)

        try:
            stats = self._entityStatsDB.getEntityStats(entityId)
        except StampedUnavailableError:
            stats = self.updateEntityStatsAsync(entityId)

        if stats.num_stamps == 0:
            badge           = Badge()
            badge.user_id   = userId
            badge.genre     = "entity_first_stamp"
            badges.append(badge)

        return badges

    @API_CALL
    @HandleRollback
    def addStamp(self, authUserId, entityRequest, data):
        user        = self._userDB.getUser(authUserId)
        entity      = self._getEntityFromRequest(entityRequest)

        entityIds   = { entity.entity_id : entity }

        blurbData   = data.pop('blurb',  None)
        creditData  = data.pop('credits', None)

        imageData   = data.pop('image',  None)
        imageUrl    = data.pop('temp_image_url',    None)
        imageWidth  = data.pop('temp_image_width',  None)
        imageHeight = data.pop('temp_image_height', None)

        now         = datetime.utcnow()

        # Check if the user has already stamped this entity
        stampExists = self._stampDB.checkStamp(user.user_id, entity.entity_id)

        # Check to make sure the user has stamps left
        if not stampExists and user.stats.num_stamps_left <= 0:
            raise StampedOutOfStampsError("No more stamps remaining")

        # Build content
        content = StampContent()
        content.content_id = utils.generateUid()
        timestamp = BasicTimestamp()
        timestamp.created = now  #time.gmtime(utils.timestampFromUid(content.content_id))
        content.timestamp = timestamp
        if blurbData is not None:
            content.blurb = blurbData.strip()

        ### TODO: Verify external image exists via head request?

        # Create the stamp or get the stamp object so we can use its stamp_id for image filenames
        if stampExists:
            stamp = self._stampDB.getStampFromUserEntity(user.user_id, entity.entity_id)
        else:
            stamp = Stamp()

        # Update content if stamp exists
        if stampExists:
            stamp.timestamp.stamped     = now
            stamp.timestamp.modified    = now
            stamp.stats.num_blurbs      = stamp.stats.num_blurbs + 1 if stamp.stats.num_blurbs is not None else 2

            contents                    = list(stamp.contents)
            contents.append(content)
            stamp.contents              = contents

            # Extract credit
            if creditData is not None:
                newCredits = self._extractCredit(creditData, entity.entity_id, stampOwner=authUserId)
                if stamp.credits is None:
                    stamp.credits = newCredits
                else:
                    creditedUserIds = set()
                    credits = list(stamp.credits)
                    for credit in stamp.credits:
                        creditedUserIds.add(credit.user.user_id)
                    for credit in newCredits:
                        if credit.user.user_id not in creditedUserIds:
                            credits.append(credit)
                            creditedUserIds.add(credit.user.user_id)
                    stamp.credits = credits

            stamp = self._stampDB.updateStamp(stamp)

        # Build new stamp
        else:
            stamp.entity                = entity
            stamp.contents              = [ content ]

            userMini                    = UserMini()
            userMini.user_id            = user.user_id
            stamp.user                  = userMini

            stats                       = StampStatsSchema()
            stats.num_blurbs            = 1
            stats.stamp_num             = user.stats.num_stamps_total + 1
            stamp.stats                 = stats

            timestamp                   = StampTimestamp()
            timestamp.created           = now
            timestamp.stamped           = now
            timestamp.modified          = now
            stamp.timestamp             = timestamp

            stamp.badges                = self.getStampBadges(stamp)

            # Extract credit
            if creditData is not None:
                stamp.credits = self._extractCredit(creditData, entity.entity_id, stampOwner=authUserId)

            stamp = self._stampDB.addStamp(stamp)
            self._rollback.append((self._stampDB.removeStamp, {'stampId': stamp.stamp_id}))

        if imageUrl is not None:
            self._statsSink.increment('stamped.api.stamps.images')
            tasks.invoke(tasks.APITasks.addResizedStampImages, args=[imageUrl, stamp.stamp_id, content.content_id])

        # Add stats
        self._statsSink.increment('stamped.api.stamps.category.%s' % entity.category)
        self._statsSink.increment('stamped.api.stamps.subcategory.%s' % entity.subcategory)

        # Enrich linked user, entity, todos, etc. within the stamp
        ### TODO: Pass userIds (need to scrape existing credited users)
        stamp = self._enrichStampObjects(stamp, authUserId=authUserId, entityIds=entityIds)
        logs.debug('Stamp exists: %s' % stampExists)

        if not stampExists:
            # Add a reference to the stamp in the user's collection
            self._rollback.append((self._stampDB.removeUserStampReference, \
                {'stampId': stamp.stamp_id, 'userId': user.user_id}))
            self._stampDB.addUserStampReference(user.user_id, stamp.stamp_id)
            self._stampDB.addInboxStampReference([ user.user_id ], stamp.stamp_id)

            # Update user stats
            self._userDB.updateUserStats(authUserId, 'num_stamps',       increment=1)
            self._userDB.updateUserStats(authUserId, 'num_stamps_left',  increment=-1)
            self._userDB.updateUserStats(authUserId, 'num_stamps_total', increment=1)
            distribution = self._getUserStampDistribution(authUserId)
            self._userDB.updateDistribution(authUserId, distribution)
            
            if utils.is_ec2():
                tasks.invoke(tasks.APITasks.updateUserImageCollage, args=[user.user_id, stamp.entity.category])

        # Generate activity and stamp pointers
        tasks.invoke(tasks.APITasks.addStamp, args=[user.user_id, stamp.stamp_id, imageUrl], 
            kwargs={'stampExists': stampExists})
        
        return stamp
    
    @API_CALL
    def addStampAsync(self, authUserId, stampId, imageUrl, stampExists=False):
        stamp   = self._stampDB.getStamp(stampId)
        entity  = self._entityDB.getEntity(stamp.entity.entity_id)

        if not stampExists:
            # Add references to the stamp in all relevant inboxes
            followers = self._friendshipDB.getFollowers(authUserId)
            self._stampDB.addInboxStampReference(followers, stampId)

            # If stamped entity is on the to do list, mark as complete
            try:
                self._todoDB.completeTodo(entity.entity_id, authUserId)
                if entity.entity_id != stamp.entity.entity_id:
                    self._todoDB.completeTodo(stamp.entity.entity_id, authUserId)
            except Exception:
                pass
        
        creditedUserIds = set()
        
        # Give credit
        if stamp.credits is not None and len(stamp.credits) > 0:
            for item in stamp.credits:
                if item.user.user_id == authUserId:
                    continue

                # Check if the user has been given credit previously
                if self._stampDB.checkCredit(item.user.user_id, stamp):
                    continue

                # Assign credit
                self._stampDB.giveCredit(item.user.user_id, stamp.stamp_id, stamp.user.user_id)
                creditedUserIds.add(item.user.user_id)

                # Add stats
                self._statsSink.increment('stamped.api.stamps.credits')

                # Update credited user stats
                self._userDB.updateUserStats(item.user.user_id, 'num_credits',     increment=1)
                self._userDB.updateUserStats(item.user.user_id, 'num_stamps_left', increment=CREDIT_BENEFIT)

                # Update stamp stats if stamp exists
                creditedStamp = self._stampDB.getStampFromUserEntity(item.user.user_id, entity.entity_id)
                if creditedStamp is not None:
                    tasks.invoke(tasks.APITasks.updateStampStats, args=[creditedStamp.stamp_id])

        # Note: No activity should be generated for the user creating the stamp

        # Add activity for credited users
        if len(creditedUserIds) > 0:
            self._addCreditActivity(authUserId, list(creditedUserIds), stamp.stamp_id, CREDIT_BENEFIT)

        # Add activity for mentioned users
        blurb = stamp.contents[-1].blurb
        if blurb is not None:
            mentionedUserIds = set()
            mentions = self._extractMentions(blurb)
            if len(mentions) > 0:
                mentionedUsers = self._userDB.lookupUsers(screenNames=list(mentions))
                for user in mentionedUsers:
                    if user.user_id != authUserId and user.user_id not in creditedUserIds:
                        mentionedUserIds.add(user.user_id)
            if len(mentionedUserIds) > 0:
                self._addMentionActivity(authUserId, list(mentionedUserIds), stamp.stamp_id)

        # Update entity stats
        tasks.invoke(tasks.APITasks.updateEntityStats, args=[stamp.entity.entity_id])

        # Update stamp stats
        tasks.invoke(tasks.APITasks.updateStampStats, args=[stamp.stamp_id])

        # Post to Facebook Open Graph if enabled
        if not stampExists:
            share_settings = self._getOpenGraphShareSettings(authUserId)
            if share_settings is not None and share_settings.share_stamps:
                tasks.invoke(tasks.APITasks.postToOpenGraph,
                    kwargs={'authUserId': authUserId,'stampId':stamp.stamp_id, 'imageUrl':imageUrl})
    
    @API_CALL
    def updateUserImageCollageAsync(self, userId, category):
        try:
            user = self._userDB.getUser(userId)
        except StampedDocumentNotFoundError as e:
            logs.warning("User not found: %s" % userId)
            return 

        categories  = [ 'default', category ]
        
        self._userImageCollageDB.process_user(user, categories)
    
    @API_CALL
    def addResizedStampImagesAsync(self, imageUrl, stampId, contentId):
        assert imageUrl is not None, "stamp image url unavailable!"

        maxSize = (960, 960)
        supportedSizes   = {
            'ios1x'  : (200, None),
            'ios2x'  : (400, None),
            'web'    : (580, None),
            'mobile' : (572, None),
            }

        # Get stamp using stampId
        stamp = self._stampDB.getStamp(stampId)

        # Find the blurb using the contentId to generate an imageId
        for i, c in enumerate(stamp.contents):
            if c.content_id == contentId:
                imageId = "%s-%s" % (stamp.stamp_id, int(time.mktime(c.timestamp.created.timetuple())))
                contentsKey = i
                break
        else:
            raise StampedInputError('Could not find stamp blurb for image resizing')

        # Generate image
        sizes = self._imageDB.addResizedStampImages(imageUrl, imageId, maxSize, supportedSizes)
        sizes.sort(key=lambda x: x.height, reverse=True)
        image = ImageSchema()
        image.sizes = sizes

        # Update stamp contents with sizes
        contents = list(stamp.contents)
        contents[contentsKey].images = [ image ] # Note: assumes only one image can exist
        stamp.contents = contents
        self._stampDB.updateStamp(stamp)


    @API_CALL
    def shareStamp(self, authUserId, stampId, serviceName, imageUrl):
        stamp = self.getStamp(stampId)
        account = self.getAccount(authUserId)

        if serviceName == 'facebook':
            if account.linked is None or account.linked.facebook is None \
                or account.linked.facebook.token is None or account.linked.facebook.linked_user_id is None:
                raise StampedLinkedAccountError('Cannot share stamp on facebook, missing necessary linked account information.')
            self._facebook.postToNewsFeed(account.linked.facebook.linked_user_id,
                                          account.linked.facebook.token,
                                          stamp.contents[-1].blurb,
                                          imageUrl)
        else:
            raise StampedNoSharingForLinkedAccountError("Sharing is not implemented for service: %s" % serviceName)
        return stamp

    @API_CALL
    def updateStamp(self, authUserId, stampId, data):
        raise NotImplementedError

    @API_CALL
    def removeStamp(self, authUserId, stampId):
        try:
            stamp = self._stampDB.getStamp(stampId)
        except StampedDocumentNotFoundError:
            logs.info("Stamp has already been deleted")
            return True
        
        # Verify user has permission to delete
        if stamp.user.user_id != authUserId:
            raise StampedRemoveStampPermissionsError("Insufficient privileges to remove stamp")

        og_action_id = stamp.og_action_id

        # Remove stamp
        self._stampDB.removeStamp(stamp.stamp_id)
        
        tasks.invoke(tasks.APITasks.removeStamp, args=[authUserId, stampId, stamp.entity.entity_id, stamp.credits, og_action_id])
        
        if utils.is_ec2():
            tasks.invoke(tasks.APITasks.updateUserImageCollage, args=[stamp.user.user_id, stamp.entity.category])
        
        return True
    
    def removeStampAsync(self, authUserId, stampId, entityId, credits=None, og_action_id=None):
        # Remove from user collection
        self._stampDB.removeUserStampReference(authUserId, stampId)

        ### TODO: Remove from inboxes? Or let integrity checker do that?

        # Remove from stats
        self._stampStatsDB.removeStampStats(stampId)

        ### TODO: Remove from activity? To do? Anything else?

        # Remove comments
        ### TODO: Make this more efficient?
        commentIds = self._commentDB.getCommentIds(stampId)
        for commentId in commentIds:
            # Remove comment
            self._commentDB.removeComment(commentId)

        # Remove activity
        self._activityDB.removeActivityForStamp(stampId)

        # Remove as todo if necessary
        try:
            self._todoDB.completeTodo(entityId, authUserId, complete=False)
        except Exception as e:
            logs.warning(e)

        ### TODO: Remove reference in other people's todos

        # Update user stats
        ### TODO: Do an actual count / update?
        self._userDB.updateUserStats(authUserId, 'num_stamps',      increment=-1)
        self._userDB.updateUserStats(authUserId, 'num_stamps_left', increment=1)

        distribution = self._getUserStampDistribution(authUserId)
        self._userDB.updateDistribution(authUserId, distribution)

        # Update credit stats if credit given
        if credits is not None and len(credits) > 0:
            for item in credits:
                # Only run if user is flagged as credited
                if item.user.user_id is None:
                    continue

                # Assign credit
                self._stampDB.removeCredit(item.user.user_id, stampId, authUserId)

                # Update credited user stats
                self._userDB.updateUserStats(item.user.user_id, 'num_credits', increment=-1)

        # Update entity stats
        tasks.invoke(tasks.APITasks.updateEntityStats, args=[entityId])

        # Remove OG activity item, if it was created, and if the user still has a linked FB account
        if og_action_id is not None and self._getOpenGraphShareSettings(authUserId) is not None:
            tasks.invoke(tasks.APITasks.deleteFromOpenGraph, kwargs={'authUserId': authUserId,'og_action_id': og_action_id})

    @API_CALL
    def getStamp(self, stampId, authUserId=None, enrich=True):
        stamp = self._stampDB.getStamp(stampId)
        if enrich:
            stamp = self._enrichStampObjects(stamp, authUserId=authUserId)

        return stamp

    @API_CALL
    def getStampFromUser(self, screenName=None, stampNumber=None, userId=None):
        if userId is None:
            userId = self._userDB.getUserByScreenName(screenName).user_id

        stamp = self._stampDB.getStampFromUserStampNum(userId, stampNumber)
        stamp = self._enrichStampObjects(stamp)

        # TODO: if authUserId == stamp.user.user_id, then the privacy should be disregarded
        if stamp.user.privacy == True:
            raise StampedViewStampPermissionsError("Insufficient privileges to view stamp")

        return stamp

    def getStampStats(self, stampIds):
        if isinstance(stampIds, basestring):
            # One stampId
            try:
                stat = self._stampStatsDB.getStampStats(stampIds)
            except (StampedUnavailableError, KeyError):
                stat = self.updateStampStatsAsync(stampIds)
            return stat

        else:
            # Multiple stampIds
            statsList = self._stampStatsDB.getStatsForStamps(stampIds)
            statsDict = {}
            for stat in statsList:
                statsDict[stat.stamp_id] = stat
            for stampId in stampIds:
                if stampId not in statsDict:
                    try:
                        statsDict[stampId] = self.updateStampStatsAsync(stampId)
                    except Exception as e:
                        logs.warning("Failed to generate stamp stats for %s: %s" % (stampId, e))
            return statsDict

    def updateStampStatsAsync(self, stampId):
        try:
            stamp = self._stampDB.getStamp(stampId)
        except StampedDocumentNotFoundError:
            logs.warning("Stamp not found: %s" % stampId)
            ### TODO: Will returning None cause problems?
            return None

        stats                   = StampStats()
        stats.stamp_id          = stampId

        MAX_PREVIEW             = 10
        stats.last_stamped      = stamp.timestamp.stamped

        likes                   = self._stampDB.getStampLikes(stampId)
        stats.num_likes         = len(likes)
        likes                   = likes[-MAX_PREVIEW:]
        likes.reverse()
        stats.preview_likes     = likes

        """
        Note: To-Do preview objects are composed of two sources: users that have to-do'd the entity from
        the stamp directly ("direct" to-dos) and users that are following you but have also to-do'd the entity
        ("indirect" to-dos). Direct to-dos are guaranteed and will always show up on the stamp. Indirect to-dos
        are recalculated frequently based on your follower list and can change over time.
        """
        todos                   = self._todoDB.getTodosFromStampId(stamp.stamp_id)
        followers               = self._friendshipDB.getFollowers(stamp.user.user_id)
        followerTodos           = self._todoDB.getTodosFromUsersForEntity(followers, stamp.entity.entity_id, limit=100)
        existingTodos           = set(todos)
        for todo in followerTodos:
            if len(todos) >= 100:
                break
            if todo not in existingTodos:
                todos.append(todo)
                existingTodos.add(todo)
        stats.num_todos         = len(todos)
        stats.preview_todos     = todos[:MAX_PREVIEW]

        creditStamps            = self._stampDB.getCreditedStamps(stamp.user.user_id, stamp.entity.entity_id, limit=100)
        stats.num_credits       = len(creditStamps)
        stats.preview_credits   = map(lambda x: x.stamp_id, creditStamps[:MAX_PREVIEW])

        comments                = self._commentDB.getCommentsForStamp(stampId, limit=100)
        stats.num_comments      = len(comments)
        stats.preview_comments  = map(lambda x: x.comment_id, comments[:MAX_PREVIEW])

        entity                  = self._entityDB.getEntity(stamp.entity.entity_id)
        stats.entity_id         = entity.entity_id
        stats.kind              = entity.kind
        stats.types             = entity.types

        if entity.kind == 'place' and entity.coordinates is not None:
            stats.lat           = entity.coordinates.lat
            stats.lng           = entity.coordinates.lng

        if entity.sources.tombstone_id is not None:
            # Call async process to update references
            tasks.invoke(tasks.APITasks.updateTombstonedEntityReferences, args=[entity.entity_id])

        # Stamp popularity - Unbounded score
        popularity = (2 * stats.num_likes) + stats.num_todos + (stats.num_comments / 2.0) + (2 * stats.num_credits)
        #TODO: Add in number of activity_items with the given stamp id 
        
        stats.popularity = float(popularity)

        # Stamp Quality - Score out of 1... 0.5 by default 

        quality = 0.5 

        # -0.2 for no blurb, +0 for <20 chars, +0.1 for 20-50 chars, + 0.16 for 50-100 chars, +0.19 for 100+ chars
        
        blurb = ""
        for content in stamp.contents:
            blurb = "%s%s" % (blurb,content.blurb)
        
        if len(blurb) > 100:
            quality += 0.19
        elif len(blurb) > 50:
            quality += 0.13
        elif len(blurb) > 20:
            quality += 0.1
        elif len(blurb) == 0:
            quality -= 0.2

        # +0.2 for image in the stamp
        for content in stamp.contents:
            if content.images is not None:
                quality += 0.2
                break
        
        # +0.05 if stamp has at least one credit
        if stats.num_credits > 0:
            quality += 0.05


        # +0.02 if blurb has at least one mention in it
        mentions = utils.findMentions(blurb)
        for mention in mentions:
            quality += 0.02
            break
            
        # +0.02 if blurb has at least one url link in it
        urls = utils.findUrls(blurb)
        for url in urls:
            quality += 0.02
            break
        
        # +0.2 if blurb has at least one quote in it 
        if '"' in blurb:
            quality += 0.02

        stats.quality = quality
        
        

        score = max(quality, float(quality * popularity))
        stats.score = score

        self._stampStatsDB.updateStampStats(stats)

        return stats

    # TODO: Move this helper function to a more centralizated location?

    def _kindTypeToOpenGraphType(self, kind, types):
        if kind == 'place':
            if 'bar' in types:
                return 'bar'
            elif 'restaurant' in types:
                return 'restaurant'
            return 'place'

        elif kind == 'person':
            if 'artist' in types:
                return 'artist'
            return 'person'

        elif kind == 'media_collection':
            if 'tv' in types:
                return 'tv_show'
            elif 'album' in types:
                return 'album'

        elif kind == 'media_item':
            if 'track' in types:
                return 'song'
            elif 'movie' in types:
                return 'movie'
            elif 'book' in types:
                return 'book'
            elif 'song' in types:
                return 'song'

        elif kind == 'software':
            if 'app' in types:
                return 'app'
            elif 'video_game' in types:
                return 'video_game'
        return 'other'

    def _getOpenGraphUrl(self, stamp=None, user=None):
        #TODO: fill this with something other than the dummy url
        if stamp is not None:
            url = generateStampUrl(stamp)
            #HACK for testing purposes
            return url.replace('http://www.stamped.com/', 'http://ec2-23-22-98-51.compute-1.amazonaws.com/')
        if user is not None:
            return "http://ec2-23-22-98-51.compute-1.amazonaws.com/%s" % user.screen_name

    def deleteFromOpenGraphAsync(self, authUserId, og_action_id):
        account = self.getAccount(authUserId)
        if account.linked is not None and account.linked.facebook is not None\
           and account.linked.facebook.token is not None:
            token = account.linked.facebook.token
            result = self._facebook.deleteFromOpenGraph(og_action_id, token)


    def postToOpenGraphAsync(self, authUserId, stampId=None, likeStampId=None, todoStampId=None, followUserId=None, imageUrl=None):
        account = self.getAccount(authUserId)

        token = account.linked.facebook.token
        fb_user_id = account.linked.facebook.linked_user_id
        action = None
        ogType = None
        url = None

        kwargs = {}
        stamp = None
        user = None
        if imageUrl is not None:
            kwargs['imageUrl'] = imageUrl
        if stampId is not None:
            action = 'stamp'
            stamp = self.getStamp(stampId)
            kind = stamp.entity.kind
            types = stamp.entity.types
            ogType = self._kindTypeToOpenGraphType(kind, types)
            url = self._getOpenGraphUrl(stamp = stamp)
            kwargs['message'] = stamp.contents[-1].blurb
        elif likeStampId is not None:
            action = 'like'
            stamp = self.getStamp(likeStampId)
            kind = stamp.entity.kind
            types = stamp.entity.types
            ogType = self._kindTypeToOpenGraphType(kind, types)
            url = self._getOpenGraphUrl(stamp = stamp)
        elif todoStampId is not None:
            action = 'todo'
            stamp = self.getStamp(todoStampId)
            kind = stamp.entity.kind
            types = stamp.entity.types
            ogType = self._kindTypeToOpenGraphType(kind, types)
            url = self._getOpenGraphUrl(stamp = stamp)
        elif followUserId is not None:
            action = 'follow'
            user = self.getUser({'user_id' : followUserId})
            ogType = 'user'
            url = self._getOpenGraphUrl(user = user)

        if action is None or ogType is None or url is None:
            return

        logs.info('### calling postToOpenGraph with action: %s  token: %s  ogType: %s  url: %s' % (action, token, ogType, url))
        result = self._facebook.postToOpenGraph(fb_user_id, action, token, ogType, url, **kwargs)
        if stampId is not None and 'id' in result:
            og_action_id = result['id']
            self._stampDB.updateStampOGActionId(stampId, og_action_id)


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
        friendship              = Friendship()
        friendship.user_id      = stamp.user.user_id
        friendship.friend_id    = user.user_id

        # Check if stamp is private; if so, must be a follower
        if stamp.user.privacy == True:
            if not self._friendshipDB.checkFriendship(friendship):
                raise StampedAddCommentPermissionsError("Insufficient privileges to add comment")

        # Check if block exists between user and stamp owner
        if self._friendshipDB.blockExists(friendship) == True:
            raise StampedBlockedUserError("Block exists")

        # Build comment
        comment                     = Comment()
        comment.stamp_id            = stamp.stamp_id
        comment.blurb               = blurb

        userMini                    = UserMini()
        userMini.user_id            = user.user_id
        comment.user                = userMini

        timestamp                   = BasicTimestamp()
        timestamp.created           = datetime.utcnow()
        comment.timestamp           = timestamp

        # Add the comment data to the database
        comment = self._commentDB.addComment(comment)
        self._rollback.append((self._commentDB.removeComment, {'commentId': comment.comment_id}))

        # Add full user object back
        comment.user = user.minimize()

        # self.addCommentAsync(user.user_id, stampId, comment.comment_id)
        tasks.invoke(tasks.APITasks.addComment, args=[user.user_id, stampId, comment.comment_id])

        return comment

    @API_CALL
    def addCommentAsync(self, authUserId, stampId, commentId):
        comment = self._commentDB.getComment(commentId)
        stamp   = self._stampDB.getStamp(stampId)
        stamp   = self._enrichStampObjects(stamp, authUserId=authUserId)

        # Add activity for mentioned users
        mentionedUserIds = set()
        mentions = self._extractMentions(comment.blurb)
        if len(mentions) > 0:
            mentionedUsers = self._userDB.lookupUsers(screenNames=list(mentions))
            for user in mentionedUsers:
                if user.user_id != authUserId:
                    mentionedUserIds.add(user.user_id)
        if len(mentionedUserIds) > 0:
            self._addMentionActivity(authUserId, list(mentionedUserIds), stamp.stamp_id, comment.comment_id)

        # Add activity for stamp owner
        commentedUserIds = set()
        if stamp.user.user_id not in mentionedUserIds and stamp.user.user_id != authUserId:
            commentedUserIds.add(stamp.user.user_id)
        self._addCommentActivity(authUserId, list(commentedUserIds), stamp.stamp_id, comment.comment_id)

        # Increment comment metric
        self._statsSink.increment('stamped.api.stamps.comments', len(commentedUserIds))

        repliedUserIds = set()
        # Add activity for previous commenters
        ### TODO: Limit this to the last 20 comments or so
        for prevComment in self._commentDB.getCommentsForStamp(stamp.stamp_id):
            repliedUserId = prevComment.user.user_id

            if repliedUserId not in commentedUserIds.union(mentionedUserIds).union(repliedUserIds) \
                and repliedUserId != authUserId:

                # Check if block exists between user and previous commenter
                friendship              = Friendship()
                friendship.user_id      = authUserId
                friendship.friend_id    = repliedUserId

                if self._friendshipDB.blockExists(friendship) == False:
                    repliedUserIds.add(repliedUserId)

        if len(repliedUserIds) > 0:
            self._addReplyActivity(authUserId, list(repliedUserIds), stamp.stamp_id, comment.comment_id)

        # Update stamp stats
        tasks.invoke(tasks.APITasks.updateStampStats, args=[stamp.stamp_id])

    @API_CALL
    def removeComment(self, authUserId, commentId):
        comment = self._commentDB.getComment(commentId)

        # Only comment owner and stamp owner can delete comment
        if comment.user.user_id != authUserId:
            stamp = self._stampDB.getStamp(comment.stamp_id)
            if stamp.user.user_id != authUserId:
                raise StampedRemoveCommentPermissionsError("Insufficient privileges to remove comment")

        # Remove comment
        self._commentDB.removeComment(comment.comment_id)

        # Remove activity?
        self._activityDB.removeCommentActivity(authUserId, comment.comment_id)

        # Update stamp stats
        tasks.invoke(tasks.APITasks.updateStampStats, args=[comment.stamp_id])

        return True

    @API_CALL
    def getComments(self, stampId, authUserId, before=None, limit=20, offset=0):
        stamp = self._stampDB.getStamp(stampId)

        # Check privacy of stamp
        if stamp.user.privacy == True:
            friendship              = Friendship()
            friendship.user_id      = stamp.user.user_id
            friendship.friend_id    = authUserId

            if not self._friendshipDB.checkFriendship(friendship):
                raise StampedViewCommentPermissionsError("Insufficient privileges to view comments")

        commentData = self._commentDB.getCommentsForStamp(stamp.stamp_id, before=before, limit=limit, offset=offset)

        # Get user objects
        userIds = {}
        for comment in commentData:
            userIds[comment.user.user_id] = 1

        users = self._userDB.lookupUsers(userIds.keys(), None)

        for user in users:
            userIds[user.user_id] = user.minimize()

        comments = []
        for comment in commentData:
            if userIds[comment.user.user_id] == 1:
                msg = 'Unable to get user_id %s for comment_id %s' % (comment.user.user_id, comment.comment_id)
                logs.warning(msg)
            else:
                comment.user = userIds[comment.user.user_id]
                comments.append(comment)

        # comments = sorted(comments, key=lambda k: k.timestamp.created)

        return comments


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

        # Check to verify that user hasn't already liked stamp
        if self._stampDB.checkLike(authUserId, stampId):
            logs.info("'Like' exists for user (%s) on stamp (%s)" % (authUserId, stampId))
            return stamp

        # Check if user has liked the stamp previously; if so, don't give credit
        previouslyLiked = False
        history = self._stampDB.getUserLikesHistory(authUserId)
        if stampId in history:
            previouslyLiked = True

        # Add like
        self._stampDB.addLike(authUserId, stampId)

        # Increment stats
        self._statsSink.increment('stamped.api.stamps.likes')

        # Force attributes
        if stamp.stats.num_likes is None:
            stamp.stats.num_likes = 0
        stamp.stats.num_likes += 1
        if stamp.attributes is None:
            stamp.attributes = StampAttributesSchema()
        stamp.attributes.is_liked = True

        # Add like async
        tasks.invoke(tasks.APITasks.addLike, args=[authUserId, stampId, previouslyLiked])

        return stamp

    @API_CALL
    def addLikeAsync(self, authUserId, stampId, previouslyLiked=False):
        stamp = self._stampDB.getStamp(stampId)

        # Increment user stats
        self._userDB.updateUserStats(stamp.user.user_id, 'num_likes', increment=1)
        self._userDB.updateUserStats(authUserId, 'num_likes_given', increment=1)

        # Give credit if not previously liked
        if not previouslyLiked and stamp.user.user_id != authUserId:
            # Update user stats with new credit
            self._userDB.updateUserStats(stamp.user.user_id, 'num_stamps_left', increment=LIKE_BENEFIT)

            # Add activity for stamp owner
            self._addLikeActivity(authUserId, stamp.stamp_id, stamp.user.user_id, LIKE_BENEFIT)

        # Update entity stats
        tasks.invoke(tasks.APITasks.updateEntityStats, args=[stamp.entity.entity_id])

        # Update stamp stats
        tasks.invoke(tasks.APITasks.updateStampStats, args=[stamp.stamp_id])

        # Post to Facebook Open Graph if enabled
        share_settings = self._getOpenGraphShareSettings(authUserId)
        if share_settings is not None and share_settings.share_likes:
            tasks.invoke(tasks.APITasks.postToOpenGraph, kwargs={'authUserId': authUserId,'likeStampId':stamp.stamp_id})

    @API_CALL
    def removeLike(self, authUserId, stampId):
        # Remove like (if it exists)
        if not self._stampDB.removeLike(authUserId, stampId):
            logs.warning('Attempted to remove a like that does not exist')
            stamp = self._stampDB.getStamp(stampId)
            return self._enrichStampObjects(stamp, authUserId=authUserId)

        # Get stamp object
        stamp = self._stampDB.getStamp(stampId)
        stamp = self._enrichStampObjects(stamp, authUserId=authUserId)

        # Decrement user stats by one
        self._userDB.updateUserStats(stamp.user.user_id, 'num_likes',    increment=-1)
        self._userDB.updateUserStats(authUserId, 'num_likes_given', increment=-1)

        if stamp.stats.num_likes is None:
            stamp.stats.num_likes = 0

        if stamp.stats.num_likes > 0:
            stamp.stats.num_likes -= 1
        else:
            stamp.stats.num_likes  = 0

        ### NOTE (5/28/12): Removing deletion for now, and only adding new activity items if first time liked
        # Remove activity
        # self._activityDB.removeActivity('like', authUserId, stampId=stampId)

        # Update stamp stats
        tasks.invoke(tasks.APITasks.updateStampStats, args=[stamp.stamp_id])

        return stamp

    @API_CALL
    def getLikes(self, authUserId, stampId):
        ### TODO: Add paging
        stamp = self._stampDB.getStamp(stampId)
        stamp = self._enrichStampObjects(stamp, authUserId=authUserId)

        # Verify user has the ability to view the stamp's likes
        if stamp.user.user_id != authUserId:
            friendship              = Friendship()
            friendship.user_id      = stamp.user.user_id
            friendship.friend_id    = authUserId
            
            # Check if stamp is private; if so, must be a follower
            if stamp.user.privacy == True:
                if not self._friendshipDB.checkFriendship(friendship):
                    raise StampedAddCommentPermissionsError("Insufficient privileges to add comment")
            
            if authUserId is not None:
                # Check if block exists between user and stamp owner
                if self._friendshipDB.blockExists(friendship) == True:
                    raise StampedBlockedUserError("Block exists")
        
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

    def _getStampCollection(self, stampIds, timeSlice, authUserId=None):

        if timeSlice.limit is None or timeSlice.limit <= 0 or timeSlice.limit > 50:
            timeSlice.limit = 50

        # Add one second to timeSlice.before to make the query inclusive of the timestamp passed
        if timeSlice.before is not None:
            timeSlice.before = timeSlice.before + timedelta(seconds=1)

        # Buffer of 10 additional stamps
        limit = timeSlice.limit
        timeSlice.limit = limit + 10

        t0 = time.time()
        stampData = self._stampDB.getStampCollectionSlice(stampIds, timeSlice)
        logs.debug('Time for _getStampCollectionSlice: %s' % (time.time() - t0))

        stamps = self._enrichStampObjects(stampData, authUserId=authUserId, mini=True)
        stamps = stamps[:limit]

        if len(stampData) >= limit and len(stamps) < limit:
            logs.warning("TOO MANY STAMPS FILTERED OUT! %s, %s" % (len(stamps), limit))

        return stamps

    def _searchStampCollection(self, stampIds, searchSlice, authUserId=None):

        if searchSlice.limit is None or searchSlice.limit <= 0 or searchSlice.limit > 50:
            searchSlice.limit = 50

        # Buffer of 10 additional stamps
        limit = searchSlice.limit
        searchSlice.limit = limit + 10

        t0 = time.time()
        stampData = self._stampDB.searchStampCollectionSlice(stampIds, searchSlice)
        logs.debug('Time for _searchStampCollectionSlice: %s' % (time.time() - t0))

        stamps = self._enrichStampObjects(stampData, authUserId=authUserId)
        stamps = stamps[:limit]

        if len(stampData) >= limit and len(stamps) < limit:
            logs.warning("TOO MANY STAMPS FILTERED OUT! %s, %s" % (len(stamps), limit))

        return stamps

    def _getScopeStampIds(self, scope=None, userId=None, authUserId=None):
        """
        If not logged in return "popular" results. Also, allow scope to be set to "popular" if
        not logged in or to user stamps; otherwise, raise exception.
        """

        if scope == 'credit':
            if userId is not None:
                return self._collectionDB.getUserCreditStampIds(userId)
            elif authUserId is not None:
                return self._collectionDB.getUserCreditStampIds(authUserId)
            else:
                raise StampedInputError("User required")

        if scope == 'user':
            if userId is not None:
                return self._collectionDB.getUserStampIds(userId)
            raise StampedInputError("User required")

        if userId is not None and scope is not None:
            raise StampedInputError("Invalid scope combination")

        if userId is not None:
            self._collectionDB.getUserStampIds(userId)

        if scope == 'popular':
            return None

        if authUserId is None:
            raise StampedNotLoggedInError("Must be logged in to view %s" % scope)

        if scope == 'me':
            return self._collectionDB.getUserStampIds(authUserId)

        if scope == 'inbox':
            return self._collectionDB.getInboxStampIds(authUserId)

        if scope == 'friends':
            raise NotImplementedError()

        raise StampedInputError("Unknown scope: %s" % scope)

    @API_CALL
    def getStampCollection(self, timeSlice, authUserId=None):
        # Special-case "tastemakers"
        if timeSlice.scope == 'popular':
            stampIds = []
            limit = timeSlice.limit
            if limit <= 0:
                limit = 20
            start = datetime.utcnow() - timedelta(hours=3)
            if timeSlice.before is not None:
                start = timeSlice.before
            daysOffset = 0
            while len(stampIds) < limit and daysOffset < 7:
                """
                Loop through daily passes to get a full limit's worth of stamps. If a given 24-hour period doesn't
                have enough stamps, it should check the previous day, with a max of one week.
                """
                before = start - timedelta(hours=(24*daysOffset))
                since = before - timedelta(hours=24)
                stampIds += self._stampStatsDB.getPopularStampIds(since=since, before=before, limit=limit, minScore=3)
                daysOffset += 1
            stampIds = stampIds[:limit]

        else:
            t0 = time.time()
            stampIds = self._getScopeStampIds(timeSlice.scope, timeSlice.user_id, authUserId)
            logs.debug('Time for _getScopeStampIds: %s' % (time.time() - t0))

        return self._getStampCollection(stampIds, timeSlice, authUserId=authUserId)

    @API_CALL
    def searchStampCollection(self, searchSlice, authUserId=None):
        t0 = time.time()
        stampIds    = self._getScopeStampIds(searchSlice.scope, searchSlice.user_id, authUserId)
        logs.debug('Time for _getScopeStampIds: %s' % (time.time() - t0))

        return self._searchStampCollection(stampIds, searchSlice, authUserId=authUserId)


    """
     #####
    #     # #    # # #####  ######
    #       #    # # #    # #
    #  #### #    # # #    # #####
    #     # #    # # #    # #
    #     # #    # # #    # #
     #####   ####  # #####  ######
    """

    def _mapGuideSectionToTypes(self, section=None, subsection=None):
        if subsection is not None:
            return [ subsection ]
        elif section is not None:
            if section == 'food':
                return [ 'restaurant', 'bar', 'cafe', 'food' ]
            else:
                return list(Entity.mapCategoryToTypes(section))
        else:
            raise StampedMissingParametersError("No section or subsection specified for guide")

    def getPersonalGuide(self, guideRequest, authUserId):
        assert(authUserId is not None)

        # Todos (via TimeSlice)
        timeSlice = TimeSlice()
        timeSlice.limit = guideRequest.limit
        timeSlice.offset = guideRequest.offset
        timeSlice.viewport = guideRequest.viewport
        timeSlice.types = self._mapGuideSectionToTypes(guideRequest.section, guideRequest.subsection)
        todos = self._todoDB.getTodos(authUserId, timeSlice)

        # User
        user = self._userDB.getUser(authUserId).minimize()

        # Enrich entities
        entityIds = {}
        for todo in todos:
            entityIds[str(todo.entity.entity_id)] = None
        entities = self._entityDB.getEntities(entityIds.keys())
        for entity in entities:
            if entity.sources.tombstone_id is not None:
                # Convert to newer entity
                replacement = self._entityDB.getEntity(entity.sources.tombstone_id)
                entityIds[entity.entity_id] = replacement
                # Call async process to update references
                tasks.invoke(tasks.APITasks.updateTombstonedEntityReferences, args=[entity.entity_id])
            else:
                entityIds[entity.entity_id] = entity

        # Build guide
        result = []
        for item in todos:
            ### TODO: Add friends' stamps / to-dos
            entity = entityIds[item.entity.entity_id]
            previews = Previews()
            previews.todos = [ user ]
            entity.previews = previews
            result.append(entity)

        return result

    def getUserGuide(self, guideRequest, authUserId):
        assert(authUserId is not None)

        forceRefresh = False
        
        try:
            guide = self._guideDB.getGuide(authUserId)
        except (StampedUnavailableError, KeyError):
            # Temporarily build the full guide synchronously. Can't do this in prod (obviously..)
            guide = self._buildUserGuide(authUserId)

        try:
            allItems = getattr(guide, guideRequest.section)
            logs.info("Nothing in guide")
            if allItems is None:
                return []
        except AttributeError:
            raise StampedInputError("Guide request for invalid section: %s" % guideRequest.section)

        limit = 20
        if guideRequest.limit is not None:
            limit = guideRequest.limit
        offset = 0
        if guideRequest.offset is not None:
            offset = guideRequest.offset
            
            
        entityIds = {}
        userIds = {}
        items = []

        if guideRequest.viewport is not None:
            latA = guideRequest.viewport.lower_right.lat
            latB = guideRequest.viewport.upper_left.lat
            lngA = guideRequest.viewport.upper_left.lng
            lngB = guideRequest.viewport.lower_right.lng

        i = 0
        for item in allItems:
            # Filter tags
            if guideRequest.subsection is not None and guideRequest.subsection not in item.tags:
                continue

            # Filter coordinates
            if guideRequest.viewport is not None:
                if item.coordinates is None:
                    continue

                latCheck = False
                lngCheck = False

                if latA < latB:
                    if latA <= item.coordinates.lat and item.coordinates.lat <= latB:
                        latCheck = True
                elif latA > latB:
                    if latA <= item.coordinates.lat or item.coordinates.lat <= latB:
                        latCheck = True

                if lngA < lngB:
                    if lngA <= item.coordinates.lng and item.coordinates.lng <= lngB:
                        lngCheck = True
                elif lngA > lngB:
                    if lngA <= item.coordinates.lng or item.coordinates.lng <= lngB:
                        lngCheck = True

                if not latCheck or not lngCheck:
                    continue

            items.append(item)
            entityIds[item.entity_id] = None
            if item.stamps is not None:
                for stampPreview in item.stamps:
                    userIds[stampPreview.user.user_id] = None
            if item.todo_user_ids is not None:
                for userId in item.todo_user_ids:
                    userIds[userId] = None
            i += 1

            if i >= limit + offset:
                break
        
        items = items[offset:]

        if len(items) == 0:
            return []
        
        # Simulated lottery to shuffle the top 20 (or whatever limit is given when offset == 0)
        if items[0].score is not None: 
            if offset == 0 and guideRequest.section != "food":
                lotterySize = min(limit, len(items))
                lotteryItems = map(lambda x: (x.score,x), items[0:lotterySize])
                items = utils.weightedLottery(lotteryItems)
                
        # Entities
        entities = self._entityDB.getEntities(entityIds.keys())

        for entity in entities:
            if entity.sources.tombstone_id is not None:
                # Convert to newer entity
                replacement = self._entityDB.getEntity(entity.sources.tombstone_id)
                entityIds[entity.entity_id] = replacement
                # Call async process to update references
                tasks.invoke(tasks.APITasks.updateTombstonedEntityReferences, args=[entity.entity_id])
            else:
                entityIds[entity.entity_id] = entity

        # Users
        users = self._userDB.lookupUsers(list(userIds.keys()))

        for user in users:
            userIds[user.user_id] = user.minimize()

        # Build guide
        result = []
        for item in items:
            entity = entityIds[item.entity_id]
            if entity is None:
                logs.warning("Missing entity: %s" % item.entity_id)
                forceRefresh = True
                continue
            previews = Previews()
            if item.stamps is not None:
                stamps = []
                for stampPreview in item.stamps:
                    stampPreviewUser = userIds[stampPreview.user.user_id]
                    if stampPreviewUser is None:
                        logs.warning("Stamp Preview: User (%s) not found in entity (%s)" % \
                            (stampPreview.user.user_id, item.entity_id))
                        # Trigger update to entity stats
                        tasks.invoke(tasks.APITasks.updateEntityStats, args=[item.entity_id])
                        continue
                    stampPreview.user = stampPreviewUser
                    stamps.append(stampPreview)
                previews.stamps = stamps
            if item.todo_user_ids is not None:
                previews.todos = [ userIds[x] for x in item.todo_user_ids ]
            if previews.stamps is not None or previews.todos is not None:
                entity.previews = previews
            result.append(entity)

        # Refresh guide
        if guide.timestamp is not None and datetime.utcnow() > guide.timestamp.generated + timedelta(days=1):
            tasks.invoke(tasks.APITasks.buildGuide, args=[authUserId])

        return result

    ### TODO: Add memcached wrapper
    def getTastemakerGuide(self, guideRequest):
        # Get popular stamps
        types = self._mapGuideSectionToTypes(guideRequest.section, guideRequest.subsection)
        limit = 1000
        viewport = guideRequest.viewport
        if viewport is not None:
            since = None
            limit = 250
        entityStats = self._entityStatsDB.getPopularEntityStats(types=types, viewport=viewport, limit=limit)

        # Rank entities
        limit = 20
        if guideRequest.limit is not None:
            limit = guideRequest.limit
        offset = 0
        if guideRequest.offset is not None:
            offset = guideRequest.offset

        # TODO: Do this in db request
        entityStats = entityStats[offset:offset+limit+5]
        
        userIds = {}

        entityIdsWithScore = {}
        for stat in entityStats:
            if stat.score is None:
                entityIdsWithScore[stat.entity_id] = 0.0
            else:
                entityIdsWithScore[stat.entity_id] = stat.score

            if stat.popular_users is not None:
                for userId in stat.popular_users[:10]:
                    userIds[userId] = None

        scoredEntities = []
        entities = self._entityDB.getEntities(entityIdsWithScore.keys())
        for entity in entities:
            scoredEntities.append((entityIdsWithScore[entity.entity_id], entity))

        scoredEntities.sort(key=lambda x: x[0], reverse=True)

        # Remove the buffer we added earlier (in case any entities no longer exist)
        scoredEntities = scoredEntities[:limit]

        # Apply Lottery
        # if offset == 0 and guideRequest.section != "food":
        #     scoredEntities = utils.weightedLottery(scoredEntities)

        # Users
        users = self._userDB.lookupUsers(list(userIds.keys()))
        for user in users:
            userIds[user.user_id] = user.minimize()

        # Build previews
        entityStampPreviews = {}
        for stat in entityStats:
            if stat.popular_users is not None and stat.popular_stamps is not None:
                if len(stat.popular_users) != len(stat.popular_stamps):
                    logs.warning("Mismatch between popular_users and popular_stamps: entity_id=%s" % stat.entity_id)
                    continue
                stampPreviews = []
                for i in range(min(len(stat.popular_users), 10)):
                    stampPreview = StampPreview()
                    stampPreview.user = userIds[stat.popular_users[i]]
                    stampPreview.stamp_id = stat.popular_stamps[i]
                    if stampPreview.user is None:
                        logs.warning("Stamp Preview: User (%s) not found in entity (%s)" % \
                            (stat.popular_users[i], stat.entity_id))
                        # Trigger update to entity stats
                        tasks.invoke(tasks.APITasks.updateEntityStats, args=[stat.entity_id])
                        continue
                    stampPreviews.append(stampPreview)
                entityStampPreviews[stat.entity_id] = stampPreviews

        # Results
        result = []
        for score, entity in scoredEntities:
            # Update previews
            if entity.entity_id in entityStampPreviews:
                previews = Previews()
                previews.stamps = entityStampPreviews[entity.entity_id]
                entity.previews = previews
            result.append(entity)

        return result

    @API_CALL
    def getGuide(self, guideRequest, authUserId):
        if guideRequest.scope == 'me' and authUserId is not None:
            return self.getPersonalGuide(guideRequest, authUserId)

        if guideRequest.scope == 'inbox' and authUserId is not None:
            return self.getUserGuide(guideRequest, authUserId)

        if guideRequest.scope == 'popular':
            return self.getTastemakerGuide(guideRequest)

        raise StampedInputError("Invalid scope for guide: %s" % guideRequest.scope)

    @API_CALL
    def searchGuide(self, guideSearchRequest, authUserId):
        if guideSearchRequest.scope == 'inbox' and authUserId is not None:
            stampIds = self._getScopeStampIds(scope='inbox', authUserId=authUserId)
        elif guideSearchRequest.scope == 'popular':
            stampIds = None
        elif guideSearchRequest.scope == 'me':
            ### TODO: Return actual search across my todos. For now, just return nothing.
            return []
        else:
            raise StampedInputError("Invalid scope for guide: %s" % guideSearchRequest.scope)

        searchSlice             = SearchSlice()
        searchSlice.limit       = 100
        searchSlice.viewport    = guideSearchRequest.viewport
        searchSlice.query       = guideSearchRequest.query
        searchSlice.types       = self._mapGuideSectionToTypes(guideSearchRequest.section, guideSearchRequest.subsection)

        stamps = self._searchStampCollection(stampIds, searchSlice, authUserId=authUserId)

        entityIds = {}
        userIds = {}

        for stamp in stamps:
            userIds[stamp.user.user_id] = None
            if stamp.entity.entity_id in entityIds:
                continue
            entityIds[stamp.entity.entity_id] = None

        # Entities
        entities = self._entityDB.getEntities(entityIds.keys())

        for entity in entities:
            if entity.sources.tombstone_id is not None:
                # Convert to newer entity
                replacement = self._entityDB.getEntity(entity.sources.tombstone_id)
                entityIds[entity.entity_id] = replacement
                # Call async process to update references
                tasks.invoke(tasks.APITasks.updateTombstonedEntityReferences, args=[entity.entity_id])
            else:
                entityIds[entity.entity_id] = entity

        # Users
        users = self._userDB.lookupUsers(list(userIds.keys()))

        for user in users:
            userIds[user.user_id] = user.minimize()

        # Build previews
        entityStampPreviews = {}
        for stamp in stamps:
            stampPreview = StampPreview()
            stampPreview.user = userIds[stamp.user.user_id]
            stampPreview.stamp_id = stamp.stamp_id

            if stamp.entity.entity_id in entityStampPreviews:
                entityStampPreviews[stamp.entity.entity_id].append(stampPreview)
            else:
                entityStampPreviews[stamp.entity.entity_id] = [ stampPreview ]

        # Results
        result = []
        seenEntities = set()
        for stamp in stamps:
            if stamp.entity.entity_id in seenEntities:
                continue
            entity = entityIds[stamp.entity.entity_id]
            seenEntities.add(stamp.entity.entity_id)

            previews = Previews()
            previews.stamps = entityStampPreviews[stamp.entity.entity_id]
            entity.previews = previews
            result.append(entity)

        return result

    @API_CALL
    def buildGuideAsync(self, authUserId):
        self._buildUserGuide(authUserId)

    def _buildUserGuide(self, authUserId):
        user = self.getUser({'user_id': authUserId})
        now = datetime.utcnow()

        t0 = time.time()

        stampIds = self._collectionDB.getInboxStampIds(user.user_id)
        stamps = self._stampDB.getStamps(stampIds)
        stampStats = self._stampStatsDB.getStatsForStamps(stampIds)
        entityIds = list(set(map(lambda x: x.entity.entity_id, stamps)))
        entities = self._entityDB.getEntities(entityIds)
        todos = set(self._todoDB.getTodoEntityIds(user.user_id))
        friendIds = self._friendshipDB.getFriends(user.user_id)

        stampMap = {} # Map entityId to stamps
        statsMap = {} # Map stampId to stats
        todosMap = {} # Map entityId to userIds

        t1 = time.time()

        sections = {}
        for entity in entities:
            section = entity.category
            if section == 'place':
                if entity.isType('restaurant') or entity.isType('bar') or entity.isType('cafe'):
                    section = 'food'
                else:
                    section = 'other'
            if section not in sections:
                sections[section] = set()
            sections[section].add(entity)

        def entityScore(**kwargs):
            section = kwargs.pop('section', None)
            avgQuality = kwargs.pop('aggQuality', [])
            avgPopularity = kwargs.pop('aggPopularity', [])
            timestamps = kwargs.pop('timestamps', [])
            result = 0
            
            # Remove personal stamp from timestamps if it exists
            try:
                personal_timestamp = (time.mktime(now.timetuple()) - timestamps.pop(authUserId)) / 60 / 60 / 24
            except KeyError:
                personal_timestamp = None
                
            # timestamps is now a list of each friends' most recent stamp time in terms of days since stamped 
            timestamps = map((lambda x: (time.mktime(now.timetuple()) - x) / 60 / 60 / 24), timestamps.values())
            
            #stamp_score
            stamp_score = 0
            personal_stamp_score = 0
            for t in timestamps:
                if t < 10:
                    stamp_score += 1 - (.05 / 10 * t)
                elif t < 90:
                    stamp_score += 1.03125 - (.65 / 80 * t)
                elif t < 290:
                    stamp_score += .435 - (.3 / 200 * t) 
            
            #Personal stamp score - higher is worse
            if personal_timestamp is not None:
                if personal_timestamp < 10:
                    personal_stamp_score = 1 - (.05 / 10 * personal_timestamp)
                elif personal_timestamp < 90:
                    personal_stamp_score = 1.03125 - (.65 / 80 * personal_timestamp)
                elif personal_timestamp < 290:
                    personal_stamp_score = .435 - (.3 / 200 * personal_timestamp)
            
            section_coefs = {
                            'food': 0,
                            'music': 1.0,
                            'film': 0.5,
                            'book': 10,
                            'app': 10
                            }
            
            #Magnify personal stamp score by number of stamps by other friends
            try:
                personal_stamp_score = section_coefs[section] * personal_stamp_score * len(timestamps)
            except KeyError:
                personal_stamp_score = personal_stamp_score * len(timestamps)
                
            ### PERSONAL TODO LIST
            personal_todo_score = 0
            if entity.entity_id in todos:
                personal_todo_score = 1
            
            if len(timestamps) > 0:
                avgQuality = avgQuality / len(timestamps)
                avgPopularity = avgPopularity / len(timestamps)
            
            image_score = 1
            if entity.images is None:
                image_score = 0.01
            
            result = ( (2 * stamp_score) 
                    - (2 * personal_stamp_score) 
                    + (3 * personal_todo_score) 
                    + (1 * avgQuality) 
                    + (1 * max(5, avgPopularity)) ) * (image_score)
            
            return result

        # Build stampMap
        for stamp in stamps:
            if stamp.entity.entity_id not in stampMap:
                stampMap[stamp.entity.entity_id] = set()
            stampMap[stamp.entity.entity_id].add(stamp)
                    
        # Build statsMap and todoMap
        for stat in stampStats:
            statsMap[stat.stamp_id] = stat
            if stat.preview_todos is not None:
                if stat.entity_id not in todosMap:
                    todosMap[stat.entity_id] = set()
                for userId in stat.preview_todos:
                    if userId in friendIds:
                        todosMap[stat.entity_id].add(userId)

        guide = GuideCache()
        guide.user_id = user.user_id
        guide.timestamp = StatTimestamp()
        guide.timestamp.generated = now
        
        for section, entities in sections.items():
            r = []
            for entity in entities:
                aggQuality = 0
                aggPopularity = 0
                timestamps = {}
                for stamp in stampMap[entity.entity_id]:
                    if stamp.stamp_id in statsMap:
                        stat = statsMap[stamp.stamp_id]
                        if stat.quality is not None:
                            aggQuality += stat.quality
                        if stat.popularity is not None:
                            aggPopularity += min(10,stat.popularity)
                    else:
                        # TEMP: Use embedded stats for backwards compatibility
                        if stamp.stats.quality is not None:
                            aggQuality += stamp.stats.quality
                        if stamp.stats.popularity is not None:
                            aggPopularity += min(10,stamp.stats.popularity)
                    if stamp.timestamp.stamped is not None:
                        t = time.mktime(stamp.timestamp.stamped.timetuple())
                        try:
                            if t > timestamps[stamp.user.user_id]:
                                timestamps[stamp.user.user_id] = t
                        except KeyError:
                            timestamps[stamp.user.user_id] = t
                    elif stamp.timestamp.created is not None:
                        t = time.mktime(stamp.timestamp.created.timetuple())
                        try:
                            if t > timestamps[stamp.user.user_id]:
                                timestamps[stamp.user.user_id] = t
                        except KeyError:
                            timestamps[stamp.user.user_id] = t
                
                score = entityScore(section=section,aggQuality=aggQuality,aggPopularity=aggPopularity, timestamps=timestamps)
                coordinates = None
                if hasattr(entity, 'coordinates'):
                    coordinates = entity.coordinates
                r.append((entity.entity_id, score, entity.types, coordinates))
                if entity.entity_id in todos:
                    if entity.entity_id not in todosMap:
                        todosMap[entity.entity_id] = set()
                    todosMap[entity.entity_id].add(user.user_id)

            r.sort(key=itemgetter(1))
            r.reverse()
            cache = []
            for result in r[:1000]:
                item = GuideCacheItem()
                item.entity_id = result[0]
                item.score = result[1]
                item.tags = result[2]
                if result[3] is not None:
                    item.coordinates = result[3]
                if len(stampMap[result[0]]) > 0:
                    preview = []
                    for stamp in stampMap[result[0]]:
                        stampPreview = StampPreview()
                        stampPreview.stamp_id = stamp.stamp_id
                        userPreview = UserMini()
                        userPreview.user_id = stamp.user.user_id
                        stampPreview.user = userPreview
                        preview.append(stampPreview)
                    if len(preview) > 0:
                        item.stamps = preview
                if result[0] in todosMap:
                    userIds = list(todosMap[result[0]])
                    if len(userIds) > 0:
                        item.todo_user_ids = userIds
                cache.append(item)
            setattr(guide, section, cache)
            
        
        logs.info("Time to build guide: %s seconds" % (time.time() - t0))

        self._guideDB.updateGuide(guide)
            
        return guide


    def _testUserGuide(self, authUserId, coeffs):
        user = self.getUser({'user_id': authUserId})
        now = datetime.utcnow()

        t0 = time.time()

        stampIds = self._collectionDB.getInboxStampIds(user.user_id)
        stamps = self._stampDB.getStamps(stampIds)
        stampStats = self._stampStatsDB.getStatsForStamps(stampIds)
        entityIds = list(set(map(lambda x: x.entity.entity_id, stamps)))
        entities = self._entityDB.getEntities(entityIds)
        todos = set(self._todoDB.getTodoEntityIds(user.user_id))
        friendIds = self._friendshipDB.getFriends(user.user_id)

        stampMap = {} # Map entityId to stamps
        statsMap = {} # Map stampId to stats
        todosMap = {} # Map entityId to userIds

        t1 = time.time()

        sections = {}
        for entity in entities:
            section = entity.category
            if section == 'place':
                if entity.isType('restaurant') or entity.isType('bar') or entity.isType('cafe'):
                    section = 'food'
                else:
                    section = 'other'
            if section not in sections:
                sections[section] = set()
            sections[section].add(entity)

        def entityScore(**kwargs):
            section = kwargs.pop('section', None)
            avgQuality = kwargs.pop('aggQuality', [])
            avgPopularity = kwargs.pop('aggPopularity', [])
            timestamps = kwargs.pop('timestamps', [])
            result = 0
            
            #Remove personal stamp from timestamps if it exists
            try:
                personal_timestamp = (time.mktime(now.timetuple()) - timestamps.pop(authUserId)) / 60 / 60 / 24
            except KeyError:
                personal_timestamp = None
                
            #timestamps is now a list of each friends' most recent stamp time in terms of days since stamped 
            timestamps = map((lambda x: (time.mktime(now.timetuple()) - x) / 60 / 60 / 24), timestamps.values())
            
            #stamp_score
            stamp_score = 0
            personal_stamp_score = 0
            for t in timestamps:
                if t < 10:
                    stamp_score += 1 - (.05 / 10 * t)
                elif t < 90:
                    stamp_score += 1.03125 - (.65 / 80 * t)
                elif t < 290:
                    stamp_score += .435 - (.3 / 200 * t)
            
            #Personal stamp score - higher is worse
            if personal_timestamp is not None:
                if personal_timestamp < 10:
                    personal_stamp_score = 1 - (.05 / 10 * personal_timestamp)
                elif personal_timestamp < 90:
                    personal_stamp_score = 1.03125 - (.65 / 80 * personal_timestamp)
                elif personal_timestamp < 290:
                    personal_stamp_score = .435 - (.3 / 200 * personal_timestamp)
            
            section_coefs = {
                            'food': 0,
                            'music': 1.0,
                            'film': 0.5,
                            'book': 10,
                            'app': 10
                            }
            
            #Magnify personal stamp score by number of stamps by other friends
            try:
                personal_stamp_score = coeffs[section] * personal_stamp_score * len(timestamps)
            except KeyError:
                personal_stamp_score = personal_stamp_score * len(timestamps)
                
            ### PERSONAL TODO LIST
            personal_todo_score = 0
            if entity.entity_id in todos:
                personal_todo_score = 1
            
            if len(timestamps) > 0:
                avgQuality = avgQuality / len(timestamps)
                avgPopularity = avgPopularity / len(timestamps)
            
            image_score = 1
            if entity.images is None:
                image_score = 0.01
            
            result = ( (coeffs['stamp'] * stamp_score) 
                        - (coeffs['personal_stamp'] * personal_stamp_score) 
                        + (coeffs['todo'] * personal_todo_score) 
                        + (coeffs['qual'] * avgQuality) 
                        + (coeffs['pop'] * avgPopularity) ) * (image_score)
            
            return result

        # Build stampMap
        for stamp in stamps:
            if stamp.entity.entity_id not in stampMap:
                stampMap[stamp.entity.entity_id] = set()
            stampMap[stamp.entity.entity_id].add(stamp)
                    
        # Build statsMap and todoMap
        for stat in stampStats:
            statsMap[stat.stamp_id] = stat
            if stat.preview_todos is not None:
                if stat.entity_id not in todosMap:
                    todosMap[stat.entity_id] = set()
                for userId in stat.preview_todos:
                    if userId in friendIds:
                        todosMap[stat.entity_id].add(userId)

        guide = GuideCache()
        guide.user_id = user.user_id
        guide.updated = now
        
        for section, entities in sections.items():
            r = []
            for entity in entities:
                aggQuality = 0
                aggPopularity = 0
                timestamps = {}
                for stamp in stampMap[entity.entity_id]:
                    if stamp.stamp_id in statsMap:
                        stat = statsMap[stamp.stamp_id]
                        if stat.quality is not None:
                            aggQuality += stat.quality
                        if stat.popularity is not None:
                            aggPopularity += min(10,stat.popularity)
                    else:
                        # TEMP: Use embedded stats for backwards compatibility
                        if stamp.stats.quality is not None:
                            aggQuality += stamp.stats.quality
                        if stamp.stats.popularity is not None:
                            aggPopularity += min(10,stamp.stats.popularity)
                    if stamp.timestamp.stamped is not None:
                        t = time.mktime(stamp.timestamp.stamped.timetuple())
                        try:
                            if t > timestamps[stamp.user.user_id]:
                                timestamps[stamp.user.user_id] = t
                        except KeyError:
                            timestamps[stamp.user.user_id] = t
                    elif stamp.timestamp.created is not None:
                        t = time.mktime(stamp.timestamp.created.timetuple())
                        try:
                            if t > timestamps[stamp.user.user_id]:
                                timestamps[stamp.user.user_id] = t
                        except KeyError:
                            timestamps[stamp.user.user_id] = t
                
                score = entityScore(section=section,aggQuality=aggQuality,aggPopularity=aggPopularity, timestamps=timestamps)
                coordinates = None
                if hasattr(entity, 'coordinates'):
                    coordinates = entity.coordinates
                r.append((entity.entity_id, score, entity.types, coordinates))
                if entity.entity_id in todos:
                    if entity.entity_id not in todosMap:
                        todosMap[entity.entity_id] = set()
                    todosMap[entity.entity_id].add(user.user_id)

            r.sort(key=itemgetter(1))
            r.reverse()
            cache = []
            for result in r[:1000]:
                item = GuideCacheItem()
                item.entity_id = result[0]
                item.score = result[1]
                item.tags = result[2]
                if result[3] is not None:
                    item.coordinates = result[3]
                if len(stampMap[result[0]]) > 0:
                    preview = []
                    for stamp in stampMap[result[0]]:
                        stampPreview = StampPreview()
                        stampPreview.stamp_id = stamp.stamp_id
                        userPreview = UserMini()
                        userPreview.user_id = stamp.user.user_id
                        stampPreview.user = userPreview
                        preview.append(stampPreview)
                    if len(preview) > 0:
                        item.stamps = preview
                if result[0] in todosMap:
                    userIds = list(todosMap[result[0]])
                    if len(userIds) > 0:
                        item.todo_user_ids = userIds
                cache.append(item)
            setattr(guide, section, cache)
            
        
        logs.info("Time to build guide: %s seconds" % (time.time() - t0))

        self._guideDB.updateGuide(guide)
            
        return guide


    """
     #######
        #     ####  #####   ####   ####
        #    #    # #    # #    # #
        #    #    # #    # #    #  ####
        #    #    # #    # #    #      #
        #    #    # #    # #    # #    #
        #     ####  #####   ####   ####
    """

    def _enrichTodoObjects(self, rawTodos, **kwargs):

        previewLength = kwargs.pop('previews', 10)

        authUserId  = kwargs.pop('authUserId', None)
        entityIds   = kwargs.pop('entityIds', {})
        stampIds    = kwargs.pop('stampIds', {})
        userIds     = kwargs.pop('userIds', {})

        singleTodo = False
        if not isinstance(rawTodos, list):
            singleTodo = True
            rawTodos = [rawTodos]

        """
        ENTITIES

        Enrich the underlying entity object for all todos
        """
        allEntityIds = set()

        for todo in rawTodos:
            allEntityIds.add(todo.entity.entity_id)

        # Enrich missing entity ids
        missingEntityIds = allEntityIds.difference(set(entityIds.keys()))
        entities = self._entityDB.getEntityMinis(list(missingEntityIds))

        for entity in entities:
            if entity.sources.tombstone_id is not None:
                # Convert to newer entity
                replacement = self._entityDB.getEntityMini(entity.sources.tombstone_id)
                entityIds[entity.entity_id] = replacement
                # Call async process to update references
                tasks.invoke(tasks.APITasks.updateTombstonedEntityReferences, args=[entity.entity_id])
            else:
                entityIds[entity.entity_id] = entity

        """
        STAMPS

        Enrich the underlying stamp objects from sourced stamps or if the user has created a stamp
        """
        allStampIds  = set()

        for todo in rawTodos:
            if todo.stamp_id is not None:
                allStampIds.add(todo.stamp_id)
            if todo.source_stamp_ids is not None:
                for stampId in todo.source_stamp_ids:
                    allStampIds.add(stampId)

        # Enrich underlying stamp ids
        stamps = self._stampDB.getStamps(list(allStampIds))

        for stamp in stamps:
            stampIds[stamp.stamp_id] = stamp

        """
        USERS

        Enrich the underlying user objects. This includes:
        - To-do owner
        - Sourced stamps
        - Also to-do'd by
        """
        allUserIds    = set()

        # Add owner
        for todo in rawTodos:
            allUserIds.add(todo.user_id)

        # Add sourced stamps
        for stamp in stamps:
            allUserIds.add(stamp.user.user_id)

        # Add to-dos from friends if logged in
        friendTodos = {}
        if authUserId is not None:
            friendIds = self._friendshipDB.getFriends(authUserId)
            for todo in rawTodos:
                todoUserIds = self._todoDB.getTodosFromUsersForEntity(friendIds, todo.entity.entity_id, limit=10)
                if todoUserIds is not None and len(todoUserIds) > 0:
                    friendTodos[todo.todo_id] = todoUserIds
                    allUserIds = allUserIds.union(set(todoUserIds))

        # Enrich missing user ids
        missingUserIds = allUserIds.difference(set(userIds.keys()))
        users = self._userDB.lookupUsers(list(missingUserIds))

        for user in users:
            userIds[user.user_id] = user.minimize()

        """
        APPLY DATA
        """
        todos = []

        for todo in rawTodos:
            try:
                # User
                user = userIds[todo.user_id]
                if user is None:
                    logs.warning("%s: User not found (%s)" % (todo.todo_id, todo.user_id))
                    continue 

                # Entity
                entity = entityIds[todo.entity.entity_id]
                if entity is None:
                    logs.warning("%s: Entity not found (%s)" % (todo.todo_id, todo.entity.entity_id))

                # Source stamps
                sourceStamps = []
                if todo.source_stamp_ids is not None:
                    for stampId in todo.source_stamp_ids:
                        if stampIds[stampId] is None:
                            logs.warning("%s: Source stamp not found (%s)" % (todo.todo_id, stampId))
                            continue
                        sourceStamps.append(stampIds[stampId])

                # Stamp
                stamp = None 
                if todo.stamp_id is not None:
                    stamp = stampIds[todo.stamp_id]
                    if stamp is None:
                        logs.warning("%s: Stamp not found (%s)" % (todo.todo_id, todo.stamp_id))

                # Also to-do'd by
                previews = None 
                if todo.todo_id in friendTodos and len(friendTodos[todo.todo_id]) > 0:
                    friends = []
                    for friendId in friendTodos[todo.todo_id]:
                        if userIds[friendId] is None:
                            logs.warning("%s: Friend preview not found (%s)" % (todo.todo_id, friendId))
                            continue
                        friends.append(userIds[friendId])
                    if len(friends) > 0:
                        previews = Previews()
                        previews.todos = friends 

                todos.append(todo.enrich(user, entity, previews=previews, sourceStamps=sourceStamps, stamp=stamp))

            except KeyError, e:
                logs.warning("Fatal key error: %s" % e)
                logs.debug("Todo: %s" % todo)
                continue
            except Exception:
                raise

        if singleTodo:
            return todos[0]

        return todos

    def _enrichTodo(self, rawTodo, user=None, entity=None, sourceStamps=None, stamp=None, friendIds=None, authUserId=None):
        if user is None or user.user_id != rawTodo.user_id:
            user = self._userDB.getUser(rawTodo.user_id).minimize()

        if entity is None or entity.entity_id != rawTodo.entity.entity_id:
            entity = self._entityDB.getEntityMini(rawTodo.entity.entity_id)

        if sourceStamps is None and rawTodo.source_stamp_ids is not None:
            # Enrich stamps
            sourceStamps = self._stampDB.getStamps(rawTodo.source_stamp_ids)
            sourceStamps = self._enrichStampObjects(sourceStamps, entityIds={ entity.entity_id : entity }, authUserId=authUserId, mini=True)

        # If Stamp is completed, check if the user has stamped it to populate todo.stamp_id value.
        # this is necessary only for backward compatability.  The new RawTodo schema includes the stamp_id val
        if stamp is None and rawTodo.complete and rawTodo.stamp_id is None and authUserId:
            stamp = self._stampDB.getStampFromUserEntity(authUserId, entity.entity_id)
            if stamp is not None:
                rawTodo.stamp_id = stamp.stamp_id

        previews = None
        if friendIds is not None:
            previews = Previews()

            # TODO: We may want to optimize how we pull in followers' todos by adding a new ref collection as we do
            #  for likes on stamps.
            friendIds = self._todoDB.getTodosFromUsersForEntity(friendIds, entity.entity_id)
            users = self._userDB.lookupUsers(friendIds, limit=10)
            users =  map(lambda x: x.minimize(), users)
            previews.todos = users


        return rawTodo.enrich(user, entity, previews, sourceStamps, stamp)

    @API_CALL
    def addTodo(self, authUserId, entityRequest, stampId=None):
        # Entity
        entity = self._getEntityFromRequest(entityRequest)

        todo                    = RawTodo()
        todo.entity             = entity.minimize()
        todo.user_id            = authUserId
        todo.timestamp          = BasicTimestamp()
        todo.timestamp.created  = datetime.utcnow()

        if stampId is not None:
            # Verify stamp exists
            try:
                source = self._stampDB.getStamp(stampId)
                todo.source_stamp_ids = [source.stamp_id]
            except StampedUnavailableError:
                stampId = None

        # Check to verify that user hasn't already todo'd entity
        try:
            return self._enrichTodoObjects(self._todoDB.getTodo(authUserId, entity.entity_id), authUserId=authUserId)
        except StampedUnavailableError:
            pass

        # Check if user has already stamped the todo entity, mark as complete and provide stamp_id, if so
        stamp = self._stampDB.getStampFromUserEntity(authUserId, entity.entity_id)
        if stamp is not None:
            todo.complete = True
            todo.stamp_id = stamp.stamp_id

        # Check if user has todoed the stamp previously; if so, don't send activity alerts
        previouslyTodoed = False
        history = self._todoDB.getUserTodosHistory(authUserId)
        if todo.todo_id in history:
            previouslyTodoed = True

        todo = self._todoDB.addTodo(todo)

        # Increment stats
        self._statsSink.increment('stamped.api.stamps.todos')

        # Enrich todo
        todo = self._enrichTodoObjects(todo, authUserId=authUserId)

        tasks.invoke(tasks.APITasks.addTodo, 
                        args=[authUserId, entity.entity_id], 
                        kwargs={'stampId': stampId, 'previouslyTodoed': previouslyTodoed})

        return todo

    def addTodoAsync(self, authUserId, entityId, stampId=None, previouslyTodoed=False):
        
        # Friends
        friendIds = self._friendshipDB.getFriends(authUserId)

        # Stamp
        if stampId is not None:
            stamp = self._stampDB.getStamp(stampId)
            stampOwner = stamp.user.user_id

        # Increment user stats by one
        self._userDB.updateUserStats(authUserId, 'num_todos', increment=1)

        # Add activity to all of your friends who stamped the entity
        friendStamps = self._stampDB.getStampsFromUsersForEntity(friendIds, entityId)
        recipientIds = [stamp.user.user_id for stamp in friendStamps]
        if authUserId in recipientIds:
            recipientIds.remove(authUserId)

        if stampId is not None:
            if stampOwner != authUserId:
                recipientIds.append(stampOwner)
        # get rid of duplicate entries
        recipientIds = list(set(recipientIds))

        ### TODO: Verify user isn't being blocked
        if not previouslyTodoed and len(recipientIds) > 0:
            self._addTodoActivity(authUserId, recipientIds, entityId)

        # Update stamp stats
        if stampId is not None:
            tasks.invoke(tasks.APITasks.updateStampStats, args=[stampId])
        for friendStamp in friendStamps:
            tasks.invoke(tasks.APITasks.updateStampStats, args=[friendStamp.stamp_id])

        # Post to Facebook Open Graph if enabled
        # for now, we only post to OpenGraph if the todo was created off of a stamp
        if stampId is not None:
            share_settings = self._getOpenGraphShareSettings(authUserId)
            if share_settings is not None and share_settings.share_todos:
                tasks.invoke(tasks.APITasks.postToOpenGraph, kwargs={'authUserId': authUserId, 'todoStampId':stampId})

    @API_CALL
    def completeTodo(self, authUserId, entityId, complete):
        try:
            RawTodo = self._todoDB.getTodo(authUserId, entityId)
        except StampedUnavailableError:
            raise StampedTodoNotFoundError('Invalid todo: %s' % RawTodo)

        self._todoDB.completeTodo(entityId, authUserId, complete=complete)

        # Enrich todo
        RawTodo.complete = complete
        todo = self._enrichTodoObjects(RawTodo, authUserId=authUserId)

        # TODO: Add activity item

        #if todo.stamp is not None and todo.stamp.stamp_id is not None:
            # Remove activity
            #self._activityDB.removeActivity('todo', authUserId, stampId=todo.stamp.stamp_id)

        # Update stamp stats
#        if todo.sourceStamps is not None:
#            for stamp in todo.sourceStamps:
#                tasks.invoke(tasks.APITasks.updateStampStats, args=[stamp.stamp_id])

        return todo

    @API_CALL
    def removeTodo(self, authUserId, entityId):
        try:
            rawTodo = self._todoDB.getTodo(authUserId, entityId)
        except StampedUnavailableError:
            return True

        self._todoDB.removeTodo(authUserId, entityId)

        # Decrement user stats by one
        self._userDB.updateUserStats(authUserId, 'num_todos', increment=-1)

        if rawTodo.stamp_id is not None:
            tasks.invoke(tasks.APITasks.updateStampStats, args=[rawTodo.stamp_id])

        return True

    @API_CALL
    def getTodos(self, authUserId, timeSlice):

        if timeSlice.limit is None or timeSlice.limit <= 0 or timeSlice.limit > 50:
            timeSlice.limit = 50

        # Add one second to timeSlice.before to make the query inclusive of the timestamp passed
        if timeSlice.before is not None:
            timeSlice.before = timeSlice.before + timedelta(seconds=1)

        todos = self._todoDB.getTodos(authUserId, timeSlice)
        return self._enrichTodoObjects(todos, authUserId=authUserId)

    @API_CALL 
    def getStampTodos(self, authUserId, stamp_id):
        return self._todoDB.getTodosFromStampId(stamp_id)
    

    """
       #
      # #    ####  ##### # #    # # ##### #   #
     #   #  #    #   #   # #    # #   #    # #
    #     # #        #   # #    # #   #     #
    ####### #        #   # #    # #   #     #
    #     # #    #   #   #  #  #  #   #     #
    #     #  ####    #   #   ##   #   #     #
    """

    def _addFollowActivity(self, userId, friendId):
        objects = ActivityObjectIds()
        objects.user_ids = [ friendId ]
        self._addActivity('follow', userId, objects,
                                            group=True,
                                            groupRange=timedelta(days=1),
                                            unique=True)

    def _addCreditActivity(self, userId, recipientIds, stamp_id, benefit):
        objects = ActivityObjectIds()
        objects.user_ids = recipientIds
        objects.stamp_ids = [ stamp_id ]
        self._addActivity('credit', userId, objects,
                                             benefit = benefit)

    def _addLikeActivity(self, userId, stampId, friendId, benefit):
        """
        Note: Ideally, if a user "re-likes" a stamp (e.g. they've liked it before and they
        like it again), it should bump the activity item to the top of your feed. There are a 
        whole bunch of pitfalls with this, though. Do you display that the user earned a stamp?
        How is grouping handled, especially if it's grouped previously? What's the upside 
        (especially if the second like is an accident)? 

        Punting for now, but we can readdress after v2 launch.
        """
        objects = ActivityObjectIds()
        objects.stamp_ids = [ stampId ]
        objects.user_ids = [ friendId ]
        self._addActivity('like', userId, objects,
                                          group = True,
                                          groupRange = timedelta(days=1),
                                          benefit = benefit)

    def _addTodoActivity(self, userId, recipientIds, entityId):
        objects = ActivityObjectIds()
        objects.entity_ids = [ entityId ]
        self._addActivity('todo', userId, objects,
                                          recipientIds = recipientIds,
                                          requireRecipient = True,
                                          group=True,
                                          groupRange=timedelta(days=1))

    def _addCommentActivity(self, userId, recipientIds, stampId, commentId):
        objects = ActivityObjectIds()
        objects.stamp_ids = [ stampId ]
        objects.comment_ids = [ commentId ]
        self._addActivity('comment', userId, objects,
                                             recipientIds = recipientIds)

    def _addReplyActivity(self, userId, recipientIds, stampId, commentId):
        objects = ActivityObjectIds()
        objects.stamp_ids = [ stampId ]
        objects.comment_ids = [ commentId ]
        self._addActivity('reply', userId, objects,
                                           recipientIds = recipientIds,
                                           requireRecipient = True)

    def _addMentionActivity(self, userId, recipientIds, stampId=None, commentId=None):
        objects = ActivityObjectIds()
        if stampId is None and commentId is None:
            raise Exception('Mention activity must include either a stampId or commentId')
        objects = ActivityObjectIds()
        if stampId is not None:
            objects.stamp_ids = [ stampId ]
        if commentId is not None:
            objects.comment_ids = [ commentId ]
        validRecipientIds = []
        for recipientId in recipientIds:
            # Check if block exists between user and mentioned user
            friendship              = Friendship()
            friendship.user_id      = recipientId
            friendship.friend_id    = userId
            if self._friendshipDB.blockExists(friendship) == False:
                validRecipientIds.append(recipientId)
        self._addActivity('mention', userId, objects,
                                             recipientIds = validRecipientIds,
                                             requireRecipient = True)

    def _addInviteActivity(self, userId, friendId, recipientIds):
        objects = ActivityObjectIds()
        objects.user_ids        = [ friendId ]
        self._addActivity('invite', userId, objects,
                                            recipientIds = recipientIds,
                                            requireRecipient = True,
                                            unique = True)

    def _addLinkedFriendActivity(self, userId, service_name, recipientIds, body=None):
        objects = ActivityObjectIds()
        objects.user_ids = [ userId ]
        self._addActivity('friend_%s' % service_name, userId, objects,
                                                              body = body,
                                                              recipientIds = recipientIds,
                                                              requireRecipient = True,
                                                              unique = True)

    def _addActionCompleteActivity(self, userId, action_name, source, stampId, friendId, body=None):
        objects = ActivityObjectIds()
        objects.user_ids        = [ friendId ]
        objects.stamp_ids       = [ stampId ]
        self._addActivity('action_%s' % action_name, userId, objects,
                                                             source = source,
                                                             body = body,
                                                             group = True,
                                                             groupRange = timedelta(days=1),
                                                             unique = True)

    def _addWelcomeActivity(self, recipientId):
        objects = ActivityObjectIds()
        objects.user_ids = [ recipientId ]
        body = "Welcome to Stamped! We've given you 100 stamps to start, so go ahead, try using one now!"
        self._activityDB.addActivity(verb           = 'notification_welcome', 
                                     recipientIds   = [ recipientId ], 
                                     objects        = objects, 
                                     body           = body,
                                     benefit        = 100, 
                                     unique         = True)

    def _addActivity(self, verb,
                           userId,
                           objects,
                           source=None,
                           body=None,
                           recipientIds=[],
                           requireRecipient=False,
                           benefit=None,
                           group=False,
                           groupRange=None,
                           sendAlert=True,
                           unique=False):
        # Verify that activity is enabled
        if not self._activity:
            return

        if len(recipientIds) == 0 and objects.user_ids is not None and len(objects.user_ids) != 0:
            recipientIds = objects.user_ids

        if userId in recipientIds:
            recipientIds.remove(userId)

        if requireRecipient and len(recipientIds) == 0:
            raise StampedActivityMissingRecipientError("Missing recipient")

        # Save activity
        self._activityDB.addActivity(verb           = verb,
                                     subject        = userId,
                                     objects        = objects,
                                     source         = source,
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
    def getActivity(self, authUserId, scope, limit=20, offset=0):

        activityData, final = self._activityCache.getFromCache(limit, offset, scope=scope, authUserId=authUserId)
        logs.debug("ACTIVITY DATA: %s" % activityData)

        # Append user objects
        userIds     = {}
        stampIds    = {}
        entityIds   = {}
        commentIds  = {}
        for item in activityData:
            if item.subjects is not None:
                for userId in item.subjects:
                    userIds[str(userId)] = None

            if item.objects is not None:
                if item.objects.user_ids is not None:
                    for userId in item.objects.user_ids:
                        userIds[str(userId)] = None

                if item.objects.stamp_ids is not None:
                    for stampId in item.objects.stamp_ids:
                        stampIds[str(stampId)] = None

                if item.objects.entity_ids is not None:
                    for entityId in item.objects.entity_ids:
                        entityIds[str(entityId)] = None

                if item.objects.comment_ids is not None:
                    for commentId in item.objects.comment_ids:
                        commentIds[str(commentId)] = None

        personal = (scope == 'me')

        # Enrich users
        users = self._userDB.lookupUsers(userIds.keys(), None)

        for user in users:
            userIds[str(user.user_id)] = user.minimize()

        # Enrich stamps
        stamps = self._stampDB.getStamps(stampIds.keys())

        stamps = self._enrichStampObjects(stamps, authUserId=authUserId, mini=True)
        for stamp in stamps:
            stampIds[str(stamp.stamp_id)] = stamp

        # Enrich entities
        entities = self._entityDB.getEntityMinis(entityIds.keys())
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
            userIds[str(user.user_id)] = user.minimize()
        for comment in comments:
            comment.user = userIds[str(comment.user.user_id)]
            commentIds[str(comment.comment_id)] = comment

        ### TEMP CODE FOR LOCAL COPY THAT DOESN'T ENRICH PROPERLY
        activity = []
        for item in activityData:
            try:
                logs.debug("ACTIVITY ITEM: %s" % item)
                logs.debug("USERS: %s" % userIds)
                logs.debug("STAMPS: %s" % stampIds)
                logs.debug("ENTITIES: %s" % entityIds)
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
        if personal == True:
            self._accountDB.updateUserTimestamp(authUserId, 'activity', datetime.utcnow())
            ### DEPRECATED
            self._userDB.updateUserStats(authUserId, 'num_unread_news', value=0)

        return activity

    @API_CALL
    def getUnreadActivityCount(self, authUserId, **kwargs):
        ### TODO: Cache this in user.num_unread_news
        user = self.getUserFromIdOrScreenName({'user_id': authUserId})
        count = self._activityDB.getUnreadActivityCount(authUserId, user.timestamp.activity)
        if count is None:
            return 0
        return count


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
            if k == 'menu':
                try:
                    self._menuDB.update(v)
                except Exception:
                    logs.warning('Menu enrichment failed')
                    report()

    def _convertSearchId(self, search_id):
        temp_id_prefix = 'T_'
        if not search_id.startswith(temp_id_prefix):
            # already a valid entity id
            return search_id

        # TODO: This code should be moved into a common location with BasicEntity.search_id
        id_components = search_id[len(temp_id_prefix):].split('____')

        sources = {
            'amazon':       AmazonSource,
            'factual':      FactualSource,
            'googleplaces': GooglePlacesSource,
            'itunes':       iTunesSource,
            'rdio':         RdioSource,
            'spotify':      SpotifySource,
            'tmdb':         TMDBSource,
            'thetvdb':      TheTVDBSource,
            'netflix':      NetflixSource,
        }

        sourceAndKeyRe = re.compile('^([A-Z]+)_([\w+-:/]+)$')
        sourcesAndKeys = []
        for component in id_components:
            match = sourceAndKeyRe.match(component)
            if not match:
                logs.warning('Unable to parse search ID component:' + component)
            else:
                sourcesAndKeys.append(match.groups())
        if not sourcesAndKeys:
            logs.warning('Unable to extract and third-party ID from composite search ID: ' + search_id)
            raise StampedUnavailableError("Entity not found")

        stamped = StampedSource(stamped_api=self)
        fast_resolve_results = stamped.resolve_fast_batch(sourcesAndKeys)
        entity_ids = filter(None, fast_resolve_results)
        if len(entity_ids):
            entity_id = entity_ids[0]
        else:
            entity_id = None

        proxies = []
        if not entity_id:
            seenSourceNames = set()
            entity_ids = []
            pool = LoggingThreadPool(len(sources))
            for sourceIdentifier, key in sourcesAndKeys:
                if sourceIdentifier in seenSourceNames:
                    continue
                seenSourceNames.add(sourceIdentifier)

                def loadProxy(sourceIdentifier, key):
                    source = sources[sourceIdentifier.lower()]()
                    try:
                        proxy = source.entityProxyFromKey(key)
                        proxies.append(proxy)
                        if len(proxies) == 1:
                            # This is the first proxy, so we'll try to resolve against Stamped.
                            results = stamped.resolve(proxy)

                            if len(results) > 0 and results[0][0]['resolved']:
                                # We were able to find a match in the Stamped DB.
                                entity_ids.append(results[0][1].key)
                                pool.kill()

                    except KeyError:
                        logs.warning('Failed to load key %s from source %s; exception body:\n%s' %
                                     (key, sourceIdentifier, traceback.format_exc()))

                pool.spawn(loadProxy, sourceIdentifier, key)

            MAX_LOOKUP_TIME=2.5
            pool.join(timeout=MAX_LOOKUP_TIME)
            if entity_ids:
                entity_id = entity_ids[0]

        if not entity_id and not proxies:
            logs.warning('Completely unable to create entity from search ID: ' + search_id)
            raise StampedUnavailableError("Entity not found")

        if entity_id is None:
            entityBuilder = EntityProxyContainer.EntityProxyContainer(proxies[0])
            for proxy in proxies[1:]:
                entityBuilder.addSource(EntityProxySource(proxy))
            entity = entityBuilder.buildEntity()
            entity.third_party_ids = id_components

            entity = self._entityDB.addEntity(entity)
            entity_id = entity.entity_id

        # Enrich and merge entity asynchronously
        self.mergeEntityId(entity_id)

        logs.info('Converted search_id (%s) to entity_id (%s)' % (search_id, entity_id))
        return entity_id

    
    def mergeEntity(self, entity):
        logs.info('Merge Entity: "%s"' % entity.title)
        tasks.invoke(tasks.APITasks.mergeEntity, args=[entity.dataExport()])

    def mergeEntityAsync(self, entityDict):
        self._mergeEntity(Entity.buildEntity(entityDict))

    def mergeEntityId(self, entityId):
        logs.info('Merge EntityId: %s' % entityId)
        tasks.invoke(tasks.APITasks.mergeEntityId, args=[entityId])

    def mergeEntityIdAsync(self, entityId):
        try:
            entity = self._entityDB.getEntity(entityId)
        except StampedDocumentNotFoundError:
            logs.warning("Entity not found: %s" % entityId)
            return
        self._mergeEntity(entity)

    def _mergeEntity(self, entity):
        """Enriches the entity and possibly follow any links it may have.
        """
        persisted = set()
        entity = self._enrichAndPersistEntity(entity, persisted)
        self._followOutLinks(entity, persisted, 0)
        return entity

    def _enrichAndPersistEntity(self, entity, persisted):
        if entity.entity_id in persisted:
            return entity
        logs.info('Merge Entity Async: "%s" (id = %s)' % (entity.title, entity.entity_id))
        entity, modified = self._resolveEntity(entity)
        logs.info('Modified: ' + str(modified))
        modified = self._resolveRelatedEntities(entity) or modified

        if modified:
            if entity.entity_id is None:
                entity = self._entityDB.addEntity(entity)
            else:
                entity = self._entityDB.updateEntity(entity)
        persisted.add(entity.entity_id)
        return entity

    def _resolveEntity(self, entity):
        def _getSuccessor(tombstoneId):
            logs.info("Get successor: %s" % tombstoneId)
            successor_id = tombstoneId
            successor    = self._entityDB.getEntity(successor_id)
            assert successor is not None and successor.entity_id == successor_id

            # TODO: Because we create a new FullResolveContainer() here instead of using self.__full_resolve, we are not
            # reading from or writing to  the joint history about what sources have failed recently and are still
            # cooling down.
            merger = FullResolveContainer.FullResolveContainer()
            merger.addSource(EntitySource(entity, merger.groups))
            successor_decorations = {}
            modified_successor = merger.enrichEntity(successor, successor_decorations)
            self.__handleDecorations(successor, successor_decorations)

            return successor, modified_successor

        try:
            # TEMP: Short circuit if user-generated
            if entity.sources.user_generated_id is not None:
                return entity, False

            # Short circuit if entity is already tombstoned
            if entity.sources.tombstone_id is not None:
                successor, modified_successor = _getSuccessor(entity.sources.tombstone_id)
                logs.info("Entity (%s) already tombstoned (%s)" % (entity.entity_id, successor.entity_id))
                return successor, modified_successor

            # Enrich entity
            decorations = {}
            modified    = self.__full_resolve.enrichEntity(entity, decorations, max_iterations=4)

            # Return successor if entity is tombstoned
            if entity.sources.tombstone_id is not None and entity.sources.tombstone_id != '': # HACK: Why is tombstone_id == ''?
                successor, modified_successor = _getSuccessor(entity.sources.tombstone_id)

                if entity.entity_id is not None:
                    self._entityDB.updateEntity(entity)

                logs.info("Merged entity (%s) with entity %s" % (entity.entity_id, successor.entity_id))
                return successor, modified_successor

            self.__handleDecorations(entity, decorations)

            return entity, modified

        except Exception:
            report()
            raise

    def _resolveRelatedEntities(self, entity):
        def _resolveStubList(entity, attr):
            stubList = getattr(entity, attr)
            if not stubList:
                return False

            resolvedList = []
            stubsModified = False

            for stub in stubList:
                stubId = stub.entity_id
                resolved = self._resolveStub(stub, True)
                if resolved is None:
                    # It's okay to fail resolution here, since we're only resolving against our own
                    # db. We never try to resolve an unknown album, for performance reasons. Also
                    # we don't go from albums to artists, since we will to to the tracks, which lead
                    # to the artists.
                    if attr != 'albums' or entity.isType('album') and attr == 'artists':
                        resolvedList.append(stub)
                    continue
                resolvedList.append(resolved.minimize())
                if stubId != resolved.entity_id:
                    stubsModified = True

            if entity.isType('artist'):
                # Do a quick dedupe of songs in case the same song appears in different albums.
                # TODO(geoff): this should be more robust...
                seenTitles = set()
                dedupedList = []
                for resolved in resolvedList:
                    if resolved.title not in seenTitles:
                        dedupedList.append(resolved)
                        seenTitles.add(resolved.title)
                resolvedList = dedupedList[:20]
            setattr(entity, attr, resolvedList)
            return stubsModified

        return self._iterateOutLinks(entity, _resolveStubList)

    def _shouldFollowLink(self, entity, attribute, depth):
        if attribute == 'albums':
            return False
        if entity.isType('album'):
            return attribute == 'tracks'
        if entity.isType('artist'):
            return True
        return depth == 0

    def _followOutLinks(self, entity, persisted, depth):
        def followStubList(entity, attr):
            if not self._shouldFollowLink(entity, attr, depth):
                return
            stubList = getattr(entity, attr)
            if not stubList:
                return

            mergeEntityTasks = []
            for stub in stubList:
                resolvedFull = self._resolveStub(stub, False)
                if resolvedFull is None:
                    logs.warning('stub resolution failed: %s' % stub)
                    mergeEntityTasks.append(None)
                else:
                    mergeEntityTasks.append(gevent.spawn(self._enrichAndPersistEntity, resolvedFull, persisted))
            
            modified = False
            visitedStubs = []
            mergedEntities = []
            for stub, task in zip(stubList, mergeEntityTasks):
                if task is None:
                    modified = True
                    continue
                mergedEntities.append(task.get())
                visitedStubs.append(mergedEntities[-1].minimize())
                modified = modified or (visitedStubs[-1] != stub)
            setattr(entity, attr, visitedStubs)
            if modified:
                self._entityDB.updateEntity(entity)

            for mergedEntity in mergedEntities:
                self._followOutLinks(mergedEntity, persisted, depth+1)
        self._iterateOutLinks(entity, followStubList)

    def _resolveStub(self, stub, quickResolveOnly):
        """Tries to return either an existing StampedSource entity or a third-party source entity proxy.

        Tries to fast resolve Stamped DB using existing third-party source IDs.
        Failing that (for one source at a time, not for all sources) tries to use standard resolution against
            StampedSource. (TODO: probably worth trying fast_resolve against all sources first, before trying
            falling back?)
        Failing that, just returns an entity proxy using one of the third-party sources for which we found an ID,
            if there were any.
        If none of this works, returns None
        """

        musicSources = {
            'itunes':       iTunesSource,
            'rdio':         RdioSource,
            'spotify':      SpotifySource,
            'amazon':       AmazonSource,
        }

        source          = None
        source_id       = None
        entity_id       = None
        proxy           = None

        stampedSource   = StampedSource(stamped_api=self)

        if stub.entity_id is not None and not stub.entity_id.startswith('T_'):
            entity_id = stub.entity_id
        else:
            # TODO GEOFF FUCK FUCK FUCK: Use third_party_ids here, and resolve_fast_batch!
            for sourceName in musicSources:
                try:
                    if getattr(stub.sources, '%s_id' % sourceName, None) is not None:
                        source = musicSources[sourceName]()
                        source_id = getattr(stub.sources, '%s_id' % sourceName)
                        # Attempt to resolve against the Stamped DB (quick)
                        entity_id = stampedSource.resolve_fast(sourceName, source_id)
                        if entity_id is None and not quickResolveOnly:
                            # Attempt to resolve against the Stamped DB (full)
                            proxy = source.entityProxyFromKey(source_id, entity=stub)
                            results = stampedSource.resolve(proxy)
                            if len(results) > 0 and results[0][0]['resolved']:
                                entity_id = results[0][1].key
                        break
                except Exception as e:
                    logs.info('Threw exception while trying to resolve source %s: %s' % (sourceName, e.message))
                    continue
        if entity_id is not None:
            try:
                entity = self._entityDB.getEntity(entity_id)
            except StampedDocumentNotFoundError:
                logs.warning("Entity id is invalid: %s" % entity_id)
                entity_id = None

        if entity_id is not None:
            pass
        elif source_id is not None and proxy is not None:
            entityProxy = EntityProxyContainer.EntityProxyContainer(proxy)
            entity = entityProxy.buildEntity()
        else:
            return None

        if entity.kind != stub.kind:
            logs.info('Confused and dazed. Stub and result are different kinds: ' + str(stub))
            return None
        return entity

    def _iterateOutLinks(self, entity, func):
        modified = False
        if entity.isType('album'):
            modified = func(entity, 'artists') or modified
            modified = func(entity, 'tracks') or modified
        elif entity.isType('artist'):
            modified = func(entity, 'albums') or modified
            modified = func(entity, 'tracks') or modified
        elif entity.isType('track'):
            modified = func(entity, 'artists') or modified
            modified = func(entity, 'albums') or modified

        return modified


    def crawlExternalSourcesAsync(self):
        stampedSource = StampedSource(stamped_api=self)
        for proxy in RssFeedScraper().fetchSources():
            self.__mergeProxyIntoDb(proxy, stampedSource)

    def __mergeProxyIntoDb(self, proxy, stampedSource):
        entity_id = stampedSource.resolve_fast(proxy.source, proxy.key)

        if entity_id is None:
            results = stampedSource.resolve(proxy)
            if len(results) > 0 and results[0][0]['resolved']:
                entity_id = results[0][1].key

        # The crawled sources are usually readonly sources, such as a scraped website or RSS feed.
        # We therefore can't rely on full enrichment to correctly pick up the data from those
        # sources. That is why we make sure we incorporate the data from the proxy here, either by
        # building a new entity or enriching an existing one.
        entityProxy = EntityProxyContainer.EntityProxyContainer(proxy)
        if entity_id is None:
            entity = entityProxy.buildEntity()
        else:
            entity = self._entityDB.getEntity(entity_id)
            entityProxy.enrichEntity(entity, {})
        self.mergeEntity(entity)

    """
    ######
    #     # #####  # #    #   ##   ##### ######
    #     # #    # # #    #  #  #    #   #
    ######  #    # # #    # #    #   #   #####
    #       #####  # #    # ######   #   #
    #       #   #  #  #  #  #    #   #   #
    #       #    # #   ##   #    #   #   ######
    """

    def addClientLogsEntry(self, authUserId, entry):
        entry.user_id = authUserId
        entry.created = datetime.utcnow()

        return self._clientLogsDB.addEntry(entry)



    def testFunction(self, authUserId, scope, limit, offset):
        activity = self.getActivity(authUserId, scope, limit, offset)
        print ('### activity blah!')
        from pprint import pprint
        for act in activity:
            pprint(act.objects.stamps)

        return


        result = []
        t0 = time.time()
        for item in activity:
            try:
                result.append(HTTPActivity().importEnrichedActivity(item).dataExport())
            except Exception as e:
                logs.warning("Failed to enrich activity: %s" % e)
                logs.debug("Activity: %s" % item)
        logs.debug("### importEnrichedActivity for all HTTPActivity: %s" % (time.time() - t0))
        return result
