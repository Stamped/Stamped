#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils, time, hashlib, random, base64, struct, logs, auth
from datetime import datetime, timedelta

from errors import *
from Schemas import *
from auth import convertPasswordForStorage

from AStampedAuth import AStampedAuth

from AAccountDB import AAccountDB
from AAuthAccessTokenDB import AAuthAccessTokenDB
from AAuthRefreshTokenDB import AAuthRefreshTokenDB


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
    
    # ####### #
    # Clients #
    # ####### #
    
    def addClient(self, params):
        raise NotImplementedError
    
    def verifyClientCredentials(self, clientId, clientSecret):
        ### TODO: remove hardcoded id / secret in plaintext!'
        try:
            if clientId == 'stampedtest' and clientSecret == 'august1ftw':
                logs.info("Client approved")
                return True
            raise
        except:
            raise StampedHTTPError('invalid_client', 401, "Invalid client credentials")
    
    def removeClient(self, params):
        raise NotImplementedError
    
    # ##### #
    # Users #
    # ##### #
    
    def verifyUserCredentials(self, clientId, userIdentifier, password):
        try:
            # Login via email
            if utils.validate_email(userIdentifier):
                user = self._accountDB.getAccountByEmail(userIdentifier)
            # Login via screen name
            elif utils.validate_screen_name(userIdentifier):
                user = self._accountDB.getAccountByScreenName(userIdentifier)
            else:
                raise

            if not auth.comparePasswordToStored(password, user.password):
                raise

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
            token = self.addRefreshToken(clientId, user.user_id)

            logs.info("Token created")

            return user, token
        except:
            msg = "Invalid user credentials"
            logs.warning(msg)
            raise StampedHTTPError("invalid_credentials", 401, msg)
    
    def verifyPassword(self, userId, password):
        try:
            user = self._accountDB.getAccount(userId)

            if not auth.comparePasswordToStored(password, user.password):
                raise

            return True
        except:
            msg = "Invalid password"
            logs.warning(msg)
            raise StampedHTTPError("invalid_credentials", 401, msg)
    
    def forgotPassword(self, email):
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

        # Convert and store new password
        password = convertPasswordForStorage(auth.generateToken(10))
        self._accountDB.updatePassword(account.user_id, password)

        # Remove refresh / access tokens
        self._refreshTokenDB.removeRefreshTokensForUser(account.user_id)
        self._accessTokenDB.removeAccessTokensForUser(account.user_id)

        # Generate reset token




        attempt = 1
        max_attempts = 5
        expire = 600    # 10 minutes
            
        while True:
            try:
                rightNow = datetime.utcnow()

                resetToken = PasswordResetToken()
                resetToken.token_id = auth.generateToken(66)
                resetToken.user_id = account.user_id
                resetToken.expires = rightNow + timedelta(seconds=expire)
                resetToken.timestamp.created = rightNow
                
                self._passwordResetDB.addResetToken(resetToken)
                break
            except:
                if attempt >= max_attempts:
                    ## Add logging
                    raise 
                attempt += 1

        baseurl = 'http://www.stamped.com'
        url = '%s/settings/password/reset/%s' % (baseurl, resetToken.token_id)


        # Email user
        msg = {}
        msg['to'] = email
        msg['from'] = 'Stamped <noreply@stamped.com>'
        msg['subject'] = 'Stamped: Reset Password'
        ### TODO: Update this copy?
        msg['body'] = 'Please visit %s to reset your password' % url

        utils.sendEmail(msg, format='text')

        return True

    def verifyPasswordResetToken(self, resetToken):
        ### Verify Refresh Token
        try:
            token = self._passwordResetDB.getResetToken(resetToken)
            if token.user_id == None:
                raise

            if token['expires'] > datetime.utcnow():
                logs.info("Valid reset token for user id: %s" % token.user_id)
                return token.user_id
            
            logs.warning("Invalid reset token... deleting")
            self._passwordResetDB.removeResetToken(token.token_id)
            raise

        except:
            msg = "Invalid reset token"
            logs.warning(msg)
            raise AuthError("invalid_token", 401, msg)



    # ############## #
    # Refresh Tokens #
    # ############## #
    
    def addRefreshToken(self, clientId, userId):
        attempt = 1
        max_attempts = 5
            
        while True:
            try:
                refreshToken = RefreshToken()
                refreshToken.token_id = auth.generateToken(43)
                refreshToken.client_id = clientId
                refreshToken.user_id = userId
                refreshToken.timestamp.created = datetime.utcnow()

                self._refreshTokenDB.addRefreshToken(refreshToken)
                logs.debug("Refresh Token created")
                break
            except:
                if attempt >= max_attempts:
                    ## Add logging here
                    raise
                attempt += 1

        accessToken = self.addAccessToken(refreshToken.client_id, \
                                            refreshToken.user_id, \
                                            refreshToken.token_id)
        
        ret = {
            'access_token': accessToken['access_token'],
            'expires_in': accessToken['expires_in'],
            'refresh_token': refreshToken['token_id']
        }
        return ret
    
    def verifyRefreshToken(self, clientId, refreshToken):
        ### Verify Refresh Token
        try:
            token = self._refreshTokenDB.getRefreshToken(refreshToken)
            if token.user_id == None:
                raise
        except:
            msg = "Invalid refresh token"
            logs.warning(msg)
            raise AuthError("invalid_token", 401, msg)

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
        attempt = 1
        max_attempts = 5
        expire = 3920   # 1 hour
        expire = 86720  # 24 hours
            
        while True:
            try:
                rightNow = datetime.utcnow()

                accessToken = AccessToken()
                accessToken.token_id = auth.generateToken(22)
                accessToken.client_id = clientId
                accessToken.refresh_token = refreshToken
                accessToken.user_id = authUserId
                accessToken.expires = rightNow + timedelta(seconds=expire)
                accessToken.timestamp.created = rightNow
                
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

            if token['expires'] > datetime.utcnow():
                logs.info("Authenticated user id: %s" % token.user_id)
                return token.user_id
            
            logs.warning("Invalid access token... deleting")
            self._accessTokenDB.removeAccessToken(token.token_id)
            raise
        except:
            msg = "Invalid Access Token"
            logs.warning(msg)
            raise AuthError("invalid_token", 401, msg)
    
    def removeAccessToken(self, tokenId):
        return self._accessTokenDB.removeAccessToken(tokenId)



    
