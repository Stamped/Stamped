
    def verifyAccessToken(self, scope=None, exit_not_present=True, 
            exit_invalid=True, exit_expired=True, exit_scope=True, realm=None):
        pass
        
    def _checkScope(self, required_scope, available_scope):
        pass
    
    def _getAccessTokenParams(self):
        pass
    
    def grantAccessToken(self, inputData=None):
        pass
    
    def _getClientCredentials(self):
        pass
    
    def getAuthorizeParams(self, inputData=None):
        pass
    
    def finishClientAuthorization(self, is_authorized, user_id=None, params={}):
        pass
    
    def _doRedirectUriCallback(self, redirect_uri, params):
        pass
  
    def _buildUri(self, uri, params):
        pass

    def _createAccessToken(self, client_id, user_id, scope=None):
        pass
  
    def _createAuthCode(self, client_id, user_id, redirect_uri, scopeNone):
        pass
  
    def _genAccessToken(self):
        pass
  
    def _genAuthCode(self):
        pass
  
    def _getAuthorizationHeader(self):
        pass
  
    def _sendJsonHeaders(self):
        pass
  
    def _errorDoRedirectUriCallback(self, redirect_uri, error, 
            error_description=None, error_uri=None, state=None):
        pass
  
    def _errorJsonResponse(self, http_status_code, error, 
            error_description=None, error_uri=None):
        pass
  
    def _errorWWWAuthenticateResponseHeader(self, http_status_code, realm, 
            error, error_description=None, error_uri=None, scope=None):
        pass
  
  
    # Storage
    def _getAuthCode(self, code):
        pass
        
    def _checkUserCredentials(self, input_username, stored_username, stored_password):
        pass
        
    def _checkAssertion(self, input_username, assertion_type, assertion):
        pass
        
    def _getRefreshToken(self, refresh_token):
        pass
        
    def _checkNoneAccess(self, input_username):
        pass
        
    def _setAccessToken(self, UNKNOWN):
        pass
        
    def _setRefreshToken(self, UNKNOWN):
        pass
        
    def self._getSupportedGrantTypes(self):
        pass

    def self._unsetRefreshToken(self, old_refresh_token):
        pass

