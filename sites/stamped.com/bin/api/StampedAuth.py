#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils, time, hashlib, random, base64, struct, datetime, logs, auth
from errors import *

from AStampedAuth import AStampedAuth

from AAccountDB import AAccountDB
from AAuthAccessTokenDB import AAuthAccessTokenDB
from AAuthRefreshTokenDB import AAuthRefreshTokenDB

from Account import Account
from AuthAccessToken import AuthAccessToken
from AuthRefreshToken import AuthRefreshToken


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
    
    def verifyClientCredentials(self, params):
        ### TODO: remove hardcoded id / secret in plaintext!
        try:
            if params['client_id'] == 'stampedtest' and params['client_secret'] == 'august1ftw':
                logs.info("Client approved")
                return True
            raise StampedHTTPError('invalid_client', 401, "Client credentials are invalid")
        except:
            raise StampedHTTPError('invalid_client', 401, "Client credentials are invalid")
    
    def removeClient(self, params):
        raise NotImplementedError
    
    # ##### #
    # Users #
    # ##### #
    
    def verifyUserCredentials(self, params):

        ### Login
        authenticated_user_id = self._accountDB.verifyAccountCredentials(
            params['screen_name'], 
            params['password'])
        if authenticated_user_id == None:
            msg = "Invalid user credentials"
            logs.warning(msg)
            raise StampedHTTPError("invalid_credentials", 401, msg)

        logs.info("Login successful")
        
        """
        IMPORTANT!!!!!

        Right now we're returning a refresh token upon login. This will have to 
        change ultimately, but it's an okay assumption for now that every login
        will be from the iPhone. Once that changes we'll have to modify this.

        Also, we'll ultimately need a way to deprecate unused refresh tokens. Not
        sure how we'll implement that yet....
        """

        ### Generate Refresh Token & Access Token
        token = self.addRefreshToken({
            'client_id': params.client_id,
            'authenticated_user_id': authenticated_user_id
        })

        logs.info("Token created")

        return token

    # ############## #
    # Refresh Tokens #
    # ############## #
    
    def addRefreshToken(self, params):
        attempt = 1
        max_attempts = 5
            
        while True:
            try:
                refreshToken = AuthRefreshToken()
                refreshToken.token_id = auth.generateToken(43)
                refreshToken.client_id = params['client_id']
                refreshToken.authenticated_user_id = params['authenticated_user_id']
                refreshToken.timestamp = { 'created': datetime.datetime.utcnow() }
                logs.debug("Refresh Token: %s" % refreshToken.getDataAsDict())

                self._refreshTokenDB.addRefreshToken(refreshToken)
                break
            except:
                if attempt >= max_attempts:
                    ## Add logging here
                    raise
                attempt += 1

        logs.info("Refresh token created")

        accessTokenParams = {
            'client_id': refreshToken['client_id'],
            'refresh_token': refreshToken['token_id'],
            'authenticated_user_id': refreshToken['authenticated_user_id']
        }
        accessToken = self.addAccessToken(accessTokenParams)

        ret = {
            'access_token': accessToken['access_token'],
            'expires_in': accessToken['expires_in'],
            'refresh_token': refreshToken['token_id']
        }
        return ret
    
    def verifyRefreshToken(self, params):
        ### Verify Grant Type
        if params['grant_type'] != 'refresh_token':
            msg = "Invalid grant type"
            logs.warn(msg)
            raise StampedHTTPError("invalid_request", 400, msg)

        ### Verify Refresh Token
        try:
            token = self._refreshTokenDB.getRefreshToken(params['refresh_token'])
        except:
            raise

        if token.authenticated_user_id == None:
            msg = "Invalid refresh token"
            logs.warn(msg)
            raise StampedHTTPError("invalid_token", 401, msg)

        ### Generate Access Token
        token = self.addAccessToken({
            'client_id': params.client_id,
            'refresh_token': params.refresh_token,
            'authenticated_user_id': token.authenticated_user_id
        })

        logs.info("Token created")

        return token
    
    def removeRefreshToken(self, params):
        raise NotImplementedError
    
    # ############# #
    # Access Tokens #
    # ############# #
    
    def addAccessToken(self, params):
        attempt = 1
        max_attempts = 5
        expire = 3920
            
        while True:
            try:
                rightNow = datetime.datetime.utcnow()

                accessToken = AuthAccessToken()
                accessToken.token_id = auth.generateToken(22)
                accessToken.client_id = params['client_id']
                accessToken.refresh_token = params['refresh_token']
                accessToken.authenticated_user_id = params['authenticated_user_id']
                accessToken.expires = rightNow + datetime.timedelta(seconds=expire)
                accessToken.timestamp = { 'created': rightNow }
                logs.debug("Access Token: %s" % accessToken.getDataAsDict())
                
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
    
    def verifyAccessToken(self, params):
        logs.debug("Verify access token: %s" % params['oauth_token'])
        try:
            token = self._accessTokenDB.getAccessToken(params['oauth_token'])
            logs.debug("Access token matched")
            logs.debug("Access token data: %s" % token.getDataAsDict())

            if token['expires'] > datetime.datetime.utcnow():
                logs.info("Authenticated user id: %s" % \
                    token.authenticated_user_id)
                return token.authenticated_user_id
            
            logs.warn("Invalid access token... deleting")
            self._accessTokenDB.removeAccessToken(params.oauth_token)
            return None
        except:
            return None
    
    def removeAccessToken(self, params):
        logs.info("Begin")
        return self._accessTokenDB.removeAccessToken(params.token_id)

    # ####### #
    # Private #
    # ####### #

    def _generateToken(self, length, seed='randomString'):
        ### TODO: This needs to be beefed up!
        def _buildToken(seed):
            h = hashlib.md5()
            h.update(seed)
            h.update(str(random.random()))
            h.update('x8c3nls93BAl4s')
            h.update(str(time.time()))
            h.update(str(random.random()))
            return str(h.hexdigest())
        result = _buildToken(seed)
        if len(result) < length:
            result = "%s%s" % (result, _buildToken(result))
        return result[:length]


    