#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils, time, hashlib, random, base64, struct, datetime
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
    
    def verifyClientCredentials(self, client_id, client_secret):
        ### TODO: remove hardcoded id / secret in plaintext!
        try:
            if client_id == 'stampedtest' and client_secret == 'august1ftw':
                return True
            return False
        except:
            return False
    
    def removeClient(self, params):
        raise NotImplementedError
    
    # ##### #
    # Users #
    # ##### #
    
    def verifyUserCredentials(self, params, **kwargs):
        logPath = "verifyUserCredentials"
        if 'logPath' in kwargs:
            logPath = "%s | %s" % (kwargs['logPath'], logPath)

        utils.logs.info("%s | Verify username/password: %s" % (logPath, params['screen_name']))
        return self._accountDB.verifyAccountCredentials(params['screen_name'], params['password'])

    # ############## #
    # Refresh Tokens #
    # ############## #
    
    def addRefreshToken(self, params, **kwargs):
        logPath = "verifyRefreshToken"
        if 'logPath' in kwargs:
            logPath = "%s | %s" % (kwargs['logPath'], logPath)

        attempt = 1
        max_attempts = 5
            
        utils.logs.info("%s | Add refresh token" % (logPath))
        while True:
            try:
                refreshToken = AuthRefreshToken()
                refreshToken.token_id = self._generateToken(43)
                refreshToken.client_id = params['client_id']
                refreshToken.authenticated_user_id = params['authenticated_user_id']
                refreshToken.timestamp = { 'created': datetime.datetime.utcnow() }
                utils.logs.debug("%s | Refresh Token: %s" % (logPath, refreshToken.getDataAsDict()))

                self._refreshTokenDB.addRefreshToken(refreshToken)
                break
            except:
                if attempt >= max_attempts:
                    raise Fail("Unable to add token")
                attempt += 1

        utils.logs.info("%s | Refresh token created" % (logPath))

        accessTokenParams = {
            'client_id': refreshToken['client_id'],
            'refresh_token': refreshToken['token_id'],
            'authenticated_user_id': refreshToken['authenticated_user_id']
        }
        accessToken = self.addAccessToken(accessTokenParams, logPath=logPath)

        ret = {
            'access_token': accessToken['access_token'],
            'expires_in': accessToken['expires_in'],
            'refresh_token': refreshToken['token_id']
        }
        return ret
    
    def verifyRefreshToken(self, params, **kwargs):
        logPath = "verifyRefreshToken"
        if 'logPath' in kwargs:
            logPath = "%s | %s" % (kwargs['logPath'], logPath)

        utils.logs.info("%s | Verify refresh token: %s" % (logPath, params['refresh_token']))
        try:
            token = self._refreshTokenDB.getRefreshToken(params['refresh_token'])
            utils.logs.info("Token received")
            return token.authenticated_user_id
        except:
            return None
    
    def removeRefreshToken(self, params):
        raise NotImplementedError
    
    # ############# #
    # Access Tokens #
    # ############# #
    
    def addAccessToken(self, params, **kwargs):
        logPath = "verifyRefreshToken"
        if 'logPath' in kwargs:
            logPath = "%s | %s" % (kwargs['logPath'], logPath)

        attempt = 1
        max_attempts = 5
        expire = 3920
            
        utils.logs.info("%s | Add access token" % (logPath))
        while True:
            try:
                rightNow = datetime.datetime.utcnow()

                accessToken = AuthAccessToken()
                accessToken.token_id = self._generateToken(22)
                accessToken.client_id = params['client_id']
                accessToken.refresh_token = params['refresh_token']
                accessToken.authenticated_user_id = params['authenticated_user_id']
                accessToken.expires = rightNow + datetime.timedelta(seconds=expire)
                accessToken.timestamp = { 'created': rightNow }
                utils.logs.debug("%s | Access Token: %s" % (logPath, accessToken.getDataAsDict()))
                
                self._accessTokenDB.addAccessToken(accessToken)
                break
            except:
                if attempt >= max_attempts:
                    raise Fail("Unable to add token")
                attempt += 1

        ret = {
            'access_token': accessToken.token_id,
            'expires_in': expire
        }
        return ret
    
    def verifyAccessToken(self, params, **kwargs):
        logPath = "verifyRefreshToken"
        if 'logPath' in kwargs:
            logPath = "%s | %s" % (kwargs['logPath'], logPath)

        utils.logs.info("%s | Verify access token: %s" % (logPath, params['oauth_token']))
        try:
            token = self._accessTokenDB.getAccessToken(params['oauth_token'])
            utils.logs.info("%s | Access token matched" % logPath)
            utils.logs.debug("%s | Access token data: %s" % (logPath, token.getDataAsDict()))

            if token['expires'] > datetime.datetime.utcnow():
                utils.logs.info("%s | Valid access token; returning user_id" % logPath)
                return token.authenticated_user_id
            
            utils.logs.info("%s | Invalid access token... deleting" % logPath)
            self._accessTokenDB.removeAccessToken(params.oauth_token)
            return None
        except:
            return None
    
    def removeAccessToken(self, params):
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


    