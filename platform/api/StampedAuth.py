#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from api import auth
import time, hashlib, random, base64, struct, os

from datetime               import datetime, timedelta
from errors                 import *
from api.Schemas            import *

from api.AStampedAuth           import AStampedAuth
from api.AAccountDB             import AAccountDB
from api.AAuthAccessTokenDB     import AAuthAccessTokenDB
from api.AAuthRefreshTokenDB    import AAuthRefreshTokenDB
from api.AAuthEmailAlertsDB     import AAuthEmailAlertsDB

from libs.Facebook              import globalFacebook
from libs.Twitter               import globalTwitter

class StampedAuth(AStampedAuth):
    """
        Database-agnostic implementation of the internal API for authentication 
        into Stamped.
    """
    
    def __init__(self, desc):
        AStampedAuth.__init__(self, desc)
        self._validated = False
    
    def _validate(self):
        self._validated = True
        
    @property
    def isValid(self):
        return self._validated

    @lazyProperty
    def _facebook(self):
        return globalFacebook()

    @lazyProperty
    def _twitter(self):
        return globalTwitter()
    
    # ####### #
    # Clients #
    # ####### #
    
    def addClient(self, params):
        raise NotImplementedError

    def getClientDetails(self, clientId):
        client = Client()
        client.client_id = clientId 

        if clientId == 'iphone8':
            client.client_class = 'iphone'
            client.api_version  = 1
            client.is_mobile    = True
            client.resolution   = 1

        elif clientId == 'iphone8@2x':
            client.client_class = 'iphone'
            client.api_version  = 1
            client.is_mobile    = True
            client.resolution   = 2

        else:
            client.api_version  = 0

        return client

    
    def verifyClientCredentials(self, clientId, clientSecret):
        ### TODO: remove hardcoded id / secret in plaintext!'
        clientIds = {
            'stampedtest'       : 'august1ftw',
            'iphone8'           : 'LnIFbmL0a75G8iQeHCV8VOT4fWFAWhzu', # 2.0
            'iphone8@2x'        : 'LnIFbmL0a75G8iQeHCV8VOT4fWFAWhzu',
            'iphone-2.0.1'      : '9ll4520o4m3706m3nmpn10871nl81340', # 2.0.1
            'web-1.0.0'         : '9lm4520o4m3718m3nmpn10h71nlbmui5', 
        }

        if clientId not in clientIds:
            raise StampedInvalidClientError("Invalid client id: %s" % clientId)

        if clientSecret != clientIds[clientId]:
            raise StampedInvalidClientError("Invalid client secret: %s" % clientId)

        logs.info("Client approved: %s" % clientId)
        return True
    
    def removeClient(self, params):
        raise NotImplementedError
    
    # ##### #
    # Users #
    # ##### #
    
    def verifyUserCredentials(self, clientId, userIdentifier, password):
        # Login via email
        if utils.validate_email(userIdentifier):
            account = self._accountDB.getAccountByEmail(userIdentifier)
        # Login via screen name
        elif utils.validate_screen_name(userIdentifier):
            account = self._accountDB.getAccountByScreenName(userIdentifier)
        else:
            raise StampedInvalidCredentialsError("Account not found: %s" % userIdentifier)

        if account.auth_service != 'stamped':
            raise StampedWrongAuthServiceError("Attempting a stamped login for an account that doesn't use stamped for auth")

        if not auth.comparePasswordToStored(password, account.password):
            raise StampedInvalidCredentialsError("Invalid password for user: %s" % userIdentifier)

        logs.info("Login successful")

        """
        IMPORTANT!!!!!

        Right now we're returning a refresh token upon login. This will
        have to change ultimately, but it's an okay assumption for now
        that every login will be from the iPhone. Once that changes we may
        have to modify this.

        Also, we'll ultimately need a way to deprecate unused refresh
        tokens. Not sure how we'll implement that yet....
        """

        ### Generate Refresh Token & Access Token
        token = self.addRefreshToken(clientId, account.user_id)

        logs.info("Token created")

        return account, token

# TODO: Consolidate facebook credentials verifications with twitter?

    def verifyFacebookUserCredentials(self, clientId, fb_token):
        try:
            fb_user = self._facebook.getUserInfo(fb_token)
        except StampedInputError as e:
            logs.warning("Facebook login failed: %s" % e)
            raise

        # TODO: remove repetitious code here (same as api.getAccountByFacebookId()
        accounts = self._accountDB.getAccountsByFacebookId(fb_user['id'])
        if len(accounts) == 0:
            raise StampedAccountNotFoundError("Unable to find account with facebook_id: %s" % fb_user['id'])
        elif len(accounts) > 1:
            raise StampedLinkedAccountAlreadyExistsError("More than one account exists for facebook_id: %s" % fb_user['id'])
        account = accounts[0]

        logs.info("Login successful")

        """
        IMPORTANT!!!!!

        Right now we're returning a refresh token upon login. This will
        have to change ultimately, but it's an okay assumption for now
        that every login will be from the iPhone. Once that changes we may
        have to modify this.

        Also, we'll ultimately need a way to deprecate unused refresh
        tokens. Not sure how we'll implement that yet....
        """

        ### Generate Refresh Token & Access Token
        token = self.addRefreshToken(clientId, account.user_id)

        logs.info("Token created")

        ### Update linked account with latest user token
        facebookToken, expires = self._facebook.extendAccessToken(fb_token)
        account.linked.facebook.token = facebookToken
        if expires is not None:
            expires = datetime.fromtimestamp(time.time() + expires)
            account.linked.facebook.token_expiration = expires
        account.linked.facebook.extended_timestamp = datetime.utcnow()
        self._accountDB.updateLinkedAccount(account.user_id, account.linked.facebook)

        return account, token

    def verifyTwitterUserCredentials(self, clientId, user_token, user_secret):
        try:
            tw_user = self._twitter.getUserInfo(user_token, user_secret)
        except StampedInputError as e:
            logs.warning("Twitter login failed: %s" % e)
            raise

        # TODO: remove repetitious code here (same as api.getAccountByTwitterId()
        accounts = self._accountDB.getAccountsByTwitterId(tw_user['id'])
        logs.info('### verifyTwitterUserCredentials')
        if len(accounts) == 0:
            raise StampedAccountNotFoundError("Unable to find account with twitter_id: %s" % tw_user['id'])
        elif len(accounts) > 1:
            raise StampedLinkedAccountAlreadyExistsError("More than one account exists using twitter_id: %s" % tw_user['id'])
        account = accounts[0]

        logs.info("Login successful")

        """
        IMPORTANT!!!!!

        Right now we're returning a refresh token upon login. This will
        have to change ultimately, but it's an okay assumption for now
        that every login will be from the iPhone. Once that changes we may
        have to modify this.

        Also, we'll ultimately need a way to deprecate unused refresh
        tokens. Not sure how we'll implement that yet....
        """

        ### Generate Refresh Token & Access Token
        token = self.addRefreshToken(clientId, account.user_id)

        logs.info("Token created")

        ### Update linked account
        logs.info('account: %s' % account)
        self._accountDB.updateLinkedAccount(account.user_id, account.linked.twitter)

        return account, token

    
    def verifyPassword(self, userId, password):
        user = self._accountDB.getAccount(userId)
        if not auth.comparePasswordToStored(password, user.password):
            raise StampedInvalidPasswordError("Invalid password")

        return True

    def forgotPassword(self, email):
        email = str(email).lower().strip()
        if not utils.validate_email(email):
            msg = "Invalid format for email address"
            logs.warning(msg)
            raise StampedInputError(msg)
        
        # Verify user exists
        account = self._accountDB.getAccountByEmail(email)
        if not account or not account.user_id:
            msg = "User does not exist"
            logs.warning(msg)
            raise StampedInputError(msg)
        
        attempt = 1
        max_attempts = 5
        expire = 1800    # 30 minutes
        
        while True:
            try:
                rightNow = datetime.utcnow()

                resetToken = PasswordResetToken()
                resetToken.token_id = auth.generateToken(36)
                resetToken.user_id = account.user_id
                resetToken.expires = rightNow + timedelta(seconds=expire)
                
                timestamp = BasicTimestamp()
                timestamp.created = rightNow
                resetToken.timestamp = timestamp
                
                self._passwordResetDB.addResetToken(resetToken)
                break
            except Exception:
                if attempt >= max_attempts:
                    ## Add logging
                    raise 
                attempt += 1

        # TODO: switch this back to https after resolving the issue where assets 
        # aren't loaded over SSL
        url = 'http://www.stamped.com/pw/%s' % resetToken.token_id
        prettyurl = 'http://stamped.com/pw/%s' % resetToken.token_id
        
        # Email user
        msg = {}
        msg['to'] = email
        msg['from'] = 'Stamped <noreply@stamped.com>'
        msg['subject'] = 'Stamped: Forgot Password'
        
        try:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(base, 'alerts', 'templates', 'email_password_forgot.html.j2')
            template = open(path, 'r')
        except Exception:
            ### TODO: Add error logging?
            raise
        
        params = {'url': url, 'prettyurl': prettyurl}
        msg['body'] = utils.parseTemplate(template, params)
        
        utils.sendEmail(msg, format='html')
        
        return True

    def verifyPasswordResetToken(self, resetToken):
        ### Verify Refresh Token
        try:
            token = self._passwordResetDB.getResetToken(resetToken)
            if token.user_id is None:
                raise

            if token.expires > datetime.utcnow():
                logs.info("Valid reset token for user id: %s" % token.user_id)
                return token.user_id
            
            logs.warning("Invalid reset token... deleting")
            self._passwordResetDB.removeResetToken(token.token_id)
            raise

        except Exception:
            msg = "Invalid reset token"
            logs.warning(msg)
            raise StampedAuthError("invalid_token", msg)

    def updatePassword(self, authUserId, password):
        
        account = self._accountDB.getAccount(authUserId)

        # Convert and store new password
        password = auth.convertPasswordForStorage(password)
        self._accountDB.updatePassword(authUserId, password)

        # Remove refresh / access tokens
        self._refreshTokenDB.removeRefreshTokensForUser(authUserId)
        self._accessTokenDB.removeAccessTokensForUser(authUserId)

        # If there is no email address associated with the account, we're done
        if account.email is None:
            return True

        # Send confirmation email
        msg = {}
        msg['to'] = account.email
        msg['from'] = 'Stamped <noreply@stamped.com>'
        msg['subject'] = 'Stamped: Your Password Has Been Reset'

        try:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(base, 'alerts', 'templates', 'email_password_reset.html.j2')
            template = open(path, 'r')
        except Exception:
            ### TODO: Add error logging?
            raise
        
        params = {
            'screen_name': account.screen_name, 
            'email_address': account.email,
        }
        msg['body'] = utils.parseTemplate(template, params)

        utils.sendEmail(msg, format='html')

        return True



    # ############## #
    # Refresh Tokens #
    # ############## #
    
    def addRefreshToken(self, clientId, userId):
        attempt = 1
        max_attempts = 5
            
        while True:
            try:
                timestamp = BasicTimestamp()
                timestamp.created = datetime.utcnow()

                refreshToken = RefreshToken()
                refreshToken.token_id = auth.generateToken(43)
                refreshToken.client_id = clientId
                refreshToken.user_id = userId
                refreshToken.timestamp = timestamp

                self._refreshTokenDB.addRefreshToken(refreshToken)
                logs.debug("Refresh Token created")
                break
            except:
                if attempt >= max_attempts:
                    ## Add logging here
                    raise
                attempt += 1

        accessTokenData = self.addAccessToken(refreshToken.client_id, \
                                                refreshToken.user_id, \
                                                refreshToken.token_id)
        
        ret = {
            'access_token': accessTokenData['access_token'],
            'expires_in': accessTokenData['expires_in'],
            'refresh_token': refreshToken.token_id,
        }
        return ret
    
    def verifyRefreshToken(self, clientId, refreshToken):
        ### Verify Refresh Token
        try:
            token = self._refreshTokenDB.getRefreshToken(refreshToken)
            if token.user_id is None:
                raise
        except:
            raise StampedInvalidRefreshTokenError("Invalid refresh token")

        ### Generate Access Token
        token = self.addAccessToken(clientId, token.user_id, refreshToken)

        logs.info("Token created")

        return token
    
    def removeRefreshToken(self, params):
        raise NotImplementedError
    
    # ############# #
    # Access Tokens #
    # ############# #
    
    def addAccessToken(self, clientId, authUserId, refreshToken):
        max_attempts = 5
        attempt = 1
        expire  = 3920   # 1 hour
        expire  = 86720  # 24 hours
        expire  = 607040  # 1 week
        
        while True:
            try:
                rightNow = datetime.utcnow()

                timestamp = BasicTimestamp()
                timestamp.created = rightNow

                accessToken = AccessToken()
                accessToken.token_id = auth.generateToken(22)
                accessToken.client_id = clientId
                accessToken.refresh_token = refreshToken
                accessToken.user_id = authUserId
                accessToken.expires = rightNow + timedelta(seconds=expire)
                accessToken.timestamp = timestamp
                
                self._accessTokenDB.addAccessToken(accessToken)
                break
            except:
                if attempt >= max_attempts:
                    ## Add logging
                    raise 
                attempt += 1

        ret = {
            'access_token': accessToken.token_id,
            'expires_in': expire
        }

        logs.info("Access token created")
        return ret
    
    def verifyAccessToken(self, token):
        logs.debug("Verify access token: %s" % token)
        try:
            token = self._accessTokenDB.getAccessToken(token)
            logs.debug("Access token matched")

            if token.expires > datetime.utcnow():
                logs.info("Authenticated user id: %s" % token.user_id)
                return token.user_id, token.client_id
            
            logs.warning("Invalid access token... deleting")
            self._accessTokenDB.removeAccessToken(token.token_id)
            raise StampedInvalidAuthTokenError("Invalid access token")
        except StampedInvalidAuthTokenError:
            raise
        except Exception as e:
            logs.warning("Exception raised: %s" % e)
            raise StampedInvalidAuthTokenError("Invalid Access Token")
    
    def removeAccessToken(self, tokenId):
        return self._accessTokenDB.removeAccessToken(tokenId)
    
    # ################### #
    # Email Access Tokens #
    # ################### #

    def addEmailAlertToken(self, userId):
        attempt = 1
        max_attempts = 15
            
        while True:
            try:
                timestamp = BasicTimestamp()
                timestamp.created = datetime.utcnow()

                token = SettingsEmailAlertToken()
                token.token_id = auth.generateToken(43)
                token.user_id = userId
                token.timestamp = timestamp

                self._emailAlertDB.addToken(token)
                logs.debug("Email Alert Token Created")
                break
            except:
                if attempt >= max_attempts:
                    ## Add logging here
                    raise
                attempt += 1

        return token.token_id

    def verifyEmailAlertToken(self, tokenId):
        try:
            token = self._emailAlertDB.getToken(tokenId)
            if token.user_id is None:
                raise
            return token.user_id
        except:
            raise StampedInvalidAuthTokenError("Invalid Email Alert Auth Token")

    def ensureEmailAlertTokenForUser(self, userId):
        token = self._emailAlertDB.getTokensForUser(userId)

        if token.user_id != userId:
            try:
                token = self.addEmailAlertToken(userId)
            except Exception as e:
                logs.warning('UNABLE TO ADD TOKEN FOR USER "%s": %s' % (userId, e))
                return None
        return token

    def ensureEmailAlertTokensForUsers(self, userIds):
        tokens = self._emailAlertDB.getTokensForUsers(userIds)

        result = {}
        for token in tokens:
            result[token.user_id] = token.token_id

        for userId in userIds:
            if userId not in result.keys():
                try:
                    token = self.addEmailAlertToken(userId)
                    result[userId] = token
                except Exception as e:
                    logs.warning('UNABLE TO ADD TOKEN FOR USER "%s": %s' % (userId, e))
                    pass
        
        return result

