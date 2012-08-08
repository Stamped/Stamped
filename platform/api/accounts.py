#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from api_old import Blacklist
from api_old.Schemas                    import *
from api_old.auth                       import convertPasswordForStorage
from api_old                            import SchemaValidation
from api_old.S3ImageDB                  import S3ImageDB

import utils
import datetime
import logs
import libs.ec2_utils
import libs.Facebook
import libs.Twitter

from api.module import APIObject
from api.activity import Activity

from db.mongodb.MongoAccountCollection import MongoAccountCollection

from db.mongodb.MongoUserCollection             import MongoUserCollection
from db.mongodb.MongoStampCollection            import MongoStampCollection, MongoStampStatsCollection
from db.mongodb.MongoCommentCollection          import MongoCommentCollection
from db.mongodb.MongoTodoCollection             import MongoTodoCollection
from db.mongodb.MongoCollectionCollection       import MongoCollectionCollection
from db.mongodb.MongoFriendshipCollection       import MongoFriendshipCollection
from db.mongodb.MongoActivityCollection         import MongoActivityCollection
from db.mongodb.MongoInvitationCollection       import MongoInvitationCollection
from db.mongodb.MongoAuthAccessTokenCollection  import MongoAuthAccessTokenCollection
from db.mongodb.MongoAuthRefreshTokenCollection import MongoAuthRefreshTokenCollection
from db.mongodb.MongoAuthEmailAlertsCollection  import MongoAuthEmailAlertsCollection



from utils import lazyProperty, LoggingThreadPool

class Accounts(APIObject):

    def __init__(self):
        APIObject.__init__(self)

    @lazyProperty
    def _accountDB(self):
        return MongoAccountCollection()


    
    @lazyProperty
    def _todoDB(self):
        return MongoTodoCollection()
    
    @lazyProperty
    def _userDB(self):
        return MongoUserCollection()
    
    @lazyProperty
    def _imageDB(self):
        return S3ImageDB()
    
    @lazyProperty
    def _stampDB(self):
        return MongoStampCollection()
    
    @lazyProperty
    def _inviteDB(self):
        return MongoInvitationCollection()
    
    @lazyProperty
    def _commentDB(self):
        return MongoCommentCollection()
    
    @lazyProperty
    def _activityDB(self):
        return MongoActivityCollection()
    
    @lazyProperty
    def _collectionDB(self):
        return MongoCollectionCollection()
    
    @lazyProperty
    def _emailAlertDB(self):
        return MongoAuthEmailAlertsCollection()
    
    @lazyProperty
    def _friendshipDB(self):
        return MongoFriendshipCollection()
    
    @lazyProperty
    def _stampStatsDB(self):
        return MongoStampStatsCollection()
    
    @lazyProperty
    def _accessTokenDB(self):
        return MongoAuthAccessTokenCollection()
    
    @lazyProperty
    def _refreshTokenDB(self):
        return MongoAuthRefreshTokenCollection()


    @lazyProperty
    def _facebook(self):
        return libs.Facebook.Facebook()
    
    @lazyProperty
    def _twitter(self):
        return libs.Twitter.Twitter()

    @lazyProperty
    def _activity(self):
        return Activity()


    def _validateStampColors(self, primary, secondary):
        primary = primary.upper()
        secondary = secondary.upper()

        if not utils.validate_hex_color(primary) or not utils.validate_hex_color(secondary):
            raise StampedInvalidStampColorsError("Invalid format for colors")

        return primary, secondary

    def addAccount(self, account, tempImageUrl=None):
        ### TODO: Check if email already exists?
        now = datetime.datetime.utcnow()

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
            self.call_task(self.customizeStampAsync, {'primary': primary, 'secondary': secondary})

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

        # Add profile image
        if tempImageUrl is not None:
            self.call_task(self.updateProfileImageAsync, {'screen_name': account.screen_name, 'image_url': tempImageUrl})

        # Asynchronously send welcome email and add activity items
        self.call_task(self.addAccountAsync, {'userId': account.user_id})

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

        # Call async task
        payload = {
            'authUserId': account.user_id, 
            'facebookToken': fb_acct.token
        }
        # Kick off an async task to query FB and determine if user granted us sharing permissions
        self.call_task(self.updateFBPermissionsAsync, payload)
        self.call_task(self.alertFollowersFromFacebookAsync, payload)

        return account

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
        if account.email is None or account.test is not None:
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
        
        # Call async task
        payload = {
            'authUserId': account.user_id, 
            'twitterKey': new_tw_account.user_token, 
            'twitterSecret': new_tw_account.user_secret
        }
        self.call_task(self.alertFollowersFromTwitterAsync, payload)
        
        return account

    def addAccountAsync(self, userId):
        delay = 1
        while True:
            try:
                account = self._accountDB.getAccount(userId)
                break
            except StampedDocumentNotFoundError:
                if delay > 60:
                    raise
                time.sleep(delay)
                delay *= 2

        self._activity.addWelcomeActivity(userId)

        # Send welcome email
        if libs.ec2_utils.is_prod_stack() and account.email is not None and account.auth_service == 'stamped':

            self._inviteDB.join(account.email)

            domain = str(account.email).split('@')[1]
            if domain != 'stamped.com':
                msg = {}
                msg['to'] = account.email
                msg['from'] = 'Stamped <noreply@stamped.com>'
                msg['subject'] = 'Welcome to Stamped!'

                try:
                    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    path = os.path.join(base, 'alerts', 'new-templates', 'email_welcome.html')
                    template = open(path, 'r')
                except Exception:
                    ### TODO: Add error logging?
                    raise

                params = {'screen_name': account.screen_name, 'email_address': account.email}
                msg['body'] = utils.parseTemplate(template, params)

                utils.sendEmail(msg, format='html')

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
            payload = {
                'old_screen_name': old_screen_name.lower(),
                'new_screen_name': account.screen_name.lower(),
            }
            self.call_task(self.changeProfileImageNameAsync, payload)

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
            payload = {
                'primary': account.color_primary,
                'secondary': account.color_secondary,
            }
            self.call_task(self.customizeStampAsync, payload)

        if 'temp_image_url' in fields:
            image_cache_timestamp = datetime.datetime.utcnow()
            account.timestamp.image_cache = image_cache_timestamp
            self._accountDB.updateUserTimestamp(account.user_id, 'image_cache', image_cache_timestamp)
            payload = {
                'screen_name': account.screen_name,
                'image_url': fields['temp_image_url'],
            }
            self.call_task(self.updateProfileImageAsync, payload)

        return self._accountDB.updateAccount(account)

    def changeProfileImageNameAsync(self, old_screen_name, new_screen_name):
        self._imageDB.changeProfileImageName(old_screen_name.lower(), new_screen_name.lower())

    def get(self, authUserId):
        return self._accountDB.getAccount(authUserId)

    def getAccount(self, authUserId):
        logs.warning("DEPRECATED FUNCTION (getAccount()): Use 'get()' instead")
        return self.get(authUserId)
    
    def getAccountByScreenName(self, screen_name):
        return self._accountDB.getAccountByScreenName(screen_name)
    
    def getLinkedAccount(self, authUserId, service_name):
        account = self.getAccount(authUserId)
        if account.linked is None:
            raise StampedLinkedAccountDoesNotExistError("User has no linked accounts")
        linked = getattr(account.linked, service_name)
        if linked is None:
            raise StampedLinkedAccountDoesNotExistError("User has no linked account: %s" % service_name)
        return linked

    def getLinkedAccounts(self, authUserId):
        return self.getAccount(authUserId).linked

    #TODO: Consolidate getAccountByFacebookId and getAccountByTwitterId?  After linked account generification is complete

    def getAccountByFacebookId(self, facebookId):
        accounts = self._accountDB.getAccountsByFacebookId(facebookId)
        if len(accounts) == 0:
            raise StampedAccountNotFoundError("Unable to find account with facebook_id: %s" % facebookId)
        elif len(accounts) > 1:
            raise StampedLinkedAccountAlreadyExistsError("More than one account exists using facebook_id: %s" % facebookId)
        return accounts[0]

    def getAccountByTwitterId(self, twitterId):
        accounts = self._accountDB.getAccountsByTwitterId(twitterId)
        if len(accounts) == 0:
            raise StampedAccountNotFoundError("Unable to find account with twitter_id: %s" % twitterId)
        elif len(accounts) > 1:
            raise StampedLinkedAccountAlreadyExistsError("More than one account exists using twitter_id: %s" % twitterId)
        return accounts[0]

    def getAccountByNetflixId(self, netflixId):
        accounts = self._accountDB.getAccountsByNetflixId(netflixId)
        if len(accounts) == 0:
            raise StampedAccountNotFoundError("Unable to find account with netflix_id: %s" % netflixId)
        elif len(accounts) > 1:
            raise StampedLinkedAccountAlreadyExistsError("More than one account exists using netflix_id: %s" % netflixId)
        return accounts[0]

    def customizeStamp(self, authUserId, data):
        primary, secondary = self._validateStampColors(data['color_primary'], data['color_secondary'])

        account = self._accountDB.getAccount(authUserId)

        # Import each item
        account.color_primary = primary
        account.color_secondary = secondary

        self._accountDB.updateAccount(account)

        # Asynchronously generate stamp file
        payload = {
            'primary': primary,
            'secondary': secondary,
        }
        self.call_task(self.customizeStampAsync, payload)

        return account

    def customizeStampAsync(self, primary, secondary):
        self._imageDB.generateStamp(primary, secondary)

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

    def updateAPNSToken(self, authUserId, token):
        self._accountDB.updateAPNSToken(authUserId, token)
        return True

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

    def addLinkedAccount(self, authUserId, linkedAccount):
        service_name = linkedAccount.service_name

        if service_name == 'facebook':
            if linkedAccount.token is None:
                raise StampedMissingLinkedAccountTokenError("Must provide an access token for facebook account")
            userInfo = self._facebook.getUserInfo(linkedAccount.token)
            self._verifyFacebookAccount(userInfo['id'], authUserId)
            linkedAccount.linked_user_id = userInfo['id']
            linkedAccount.third_party_id = userInfo['third_party_id']
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
            payload = {
                'authUserId': authUserId, 
                'facebookToken': linkedAccount.token
            }
            # Kick off an async task to query FB and determine if user granted us sharing permissions
            self.call_task(self.updateFBPermissionsAsync, payload)
            # Send out alert
            self.call_task(self.alertFollowersFromFacebookAsync, payload)

        elif linkedAccount.service_name == 'twitter':
            payload = {
                'authUserId': authUserId, 
                'twitterKey': linkedAccount.token, 
                'twitterSecret': linkedAccount.secret,
            }
            self.call_task(self.alertFollowersFromTwitterAsync, payload)

        return linkedAccount

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

    def getOpenGraphShareSettings(self, authUserId):
        account = self.getAccount(authUserId)

        if account.linked is None or\
           account.linked.facebook is None or\
           account.linked.facebook.share_settings is None or\
           account.linked.facebook.token is None or \
           account.linked.facebook.have_share_permissions == False:
            return None

        return account.linked.facebook.share_settings

    def updateFBPermissionsAsync(self, authUserId, facebookToken):
        acct = self.getAccount(authUserId)
        if acct.linked is None or acct.linked.facebook is None:
            return False
        linked = acct.linked.facebook
        permissions = self._facebook.getUserPermissions(facebookToken)
        linked.have_share_permissions = \
            ('publish_actions' in permissions) and (permissions['publish_actions'] == 1)

        facebookToken, expires = self._facebook.extendAccessToken(facebookToken)
        linked.token = facebookToken

        if expires is not None:
            expires = datetime.datetime.fromtimestamp(time.time() + expires)
            linked.token_expiration = expires
        else:
            logs.warning("NO EXPIRATION FOR USER %s: %s" % (authUserId, facebookToken))

        linked.extended_timestamp = datetime.datetime.utcnow()
        self._accountDB.updateLinkedAccount(authUserId, linked)
        return True


    def removeLinkedAccount(self, authUserId, service_name):
        if service_name not in ['facebook', 'twitter', 'netflix', 'rdio']:
            raise StampedLinkedAccountDoesNotExistError("Invalid linked account: %s" % service_name)

        account = self.getAccount(authUserId)
        if account.auth_service == service_name:
            raise StampedLinkedAccountIsAuthError('Cannot remove a linked account used for authorization.')

        self._accountDB.removeLinkedAccount(authUserId, service_name)
        return True

    def alertFollowersFromTwitterAsync(self, authUserId, twitterKey, twitterSecret):
        delay = 1
        while True:
            try:
                account   = self._accountDB.getAccount(authUserId)
                # Only send alert once (when the user initially connects to Twitter)
                if self._accountDB.checkLinkedAccountAlertHistory(authUserId, 'twitter', account.linked.twitter.linked_user_id):
                    return False
                break
            except StampedDocumentNotFoundError:
                if delay > 60:
                    raise
                time.sleep(delay)
                delay *= 2


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

    def alertFollowersFromFacebookAsync(self, authUserId, facebookToken):
        delay = 1
        while True:
            try:
                account   = self._accountDB.getAccount(authUserId)
                # Only send alert once (when the user initially connects to Facebook)
                if self._accountDB.checkLinkedAccountAlertHistory(authUserId, 'facebook', account.linked.facebook.linked_user_id):
                    logs.info("Facebook alerts already sent")
                    return False
                break
            except StampedDocumentNotFoundError:
                if delay > 60:
                    raise
                time.sleep(delay)
                delay *= 2

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

    def addToNetflixInstant(self, nf_user_id, nf_token, nf_secret, netflixId):
        if (nf_user_id is None or nf_token is None or nf_secret is None):
            logs.info('Returning because of missing account credentials')
            return None

        netflix = globalNetflix()
        return netflix.addToQueue(nf_user_id, nf_token, nf_secret, netflixId)

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

