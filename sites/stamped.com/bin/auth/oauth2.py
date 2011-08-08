#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import time, re, hashlib, random, base64, struct

"""
Adapted from oauth2-php (https:#github.com/geoloqi/oauth2-php/)

 * @mainpage
 * OAuth 2.0 server in PHP, originally written for
 * <a href="http:#www.opendining.net/"> Open Dining</a>. Supports
 * <a href="http:#tools.ietf.org/html/draft-ietf-oauth-v2-10">IETF draft v10</a>.
 *
 * Source repo has sample servers implementations for
 * <a href="http:#php.net/manual/en/book.pdo.php"> PHP Data Objects</a> and
 * <a href="http:#www.mongodb.org/">MongoDB</a>. Easily adaptable to other
 * storage engines.
 *
 * PHP Data Objects supports a variety of databases, including MySQL,
 * Microsoft SQL Server, SQLite, and Oracle, so you can try out the sample
 * to see how it all works.
 *
 * We're expanding the wiki to include more helpful documentation, but for
 * now, your best bet is to view the oauth.php source - it has lots of
 * comments.
 *
 * @author Tim Ridgely <tim.ridgely@gmail.com>
 * @author Aaron Parecki <aaron@parecki.com>
 * @author Edison Wong <hswong3i@pantarei-design.com>
 *
 * @see http:#code.google.com/p/oauth2-php/
"""

# The default duration in seconds of the access token lifetime.
OAUTH2_DEFAULT_ACCESS_TOKEN_LIFETIME = 3600

# The default duration in seconds of the authorization code lifetime.
OAUTH2_DEFAULT_AUTH_CODE_LIFETIME = 30

# The default duration in seconds of the refresh token lifetime.
OAUTH2_DEFAULT_REFRESH_TOKEN_LIFETIME = 1209600


"""
 * @defgroup oauth2_section_2 Client Credentials
 * @{
 *
 * When interacting with the authorization server, the client identifies
 * itself using a client identifier and authenticates using a set of
 * client credentials. This specification provides one mechanism for
 * authenticating the client using password credentials.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-2
"""

"""
 * Regex to filter out the client identifier (described in Section 2 of IETF draft).
 *
 * IETF draft does not prescribe a format for these, however I've arbitrarily
 * chosen alphanumeric strings with hyphens and underscores, 3-32 characters
 * long.
 *
 * Feel free to change.
"""
### TODO: Examine regex expression
OAUTH2_CLIENT_ID_REGEXP = "/^[a-z0-9-_]{3,32}$/i"

"""
 * @}
"""


"""
 * @defgroup oauth2_section_3 Obtaining End-User Authorization
 * @{
 *
 * When the client interacts with an end-user, the end-user MUST first
 * grant the client authorization to access its protected resources.
 * Once obtained, the end-user access grant is expressed as an
 * authorization code which the client uses to obtain an access token.
 * To obtain an end-user authorization, the client sends the end-user to
 * the end-user authorization endpoint.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-3
"""

# Denotes "token" authorization response type.
OAUTH2_AUTH_RESPONSE_TYPE_ACCESS_TOKEN = "token"

# Denotes "code" authorization response type.
OAUTH2_AUTH_RESPONSE_TYPE_AUTH_CODE = "code"

# Denotes "code-and-token" authorization response type.
OAUTH2_AUTH_RESPONSE_TYPE_CODE_AND_TOKEN = "code-and-token"

# Regex to filter out the authorization response type.
OAUTH2_AUTH_RESPONSE_TYPE_REGEXP = "/^(token|code|code-and-token)$/"

# List of valid response types.
OAUTH2_AUTH_RESPONSE_TYPE_LIST = set(['token', 'code', 'code-and-token'])

"""
 * @}
"""


"""
 * @defgroup oauth2_section_4 Obtaining an Access Token
 * @{
 *
 * The client obtains an access token by authenticating with the
 * authorization server and presenting its access grant (in the form of
 * an authorization code, resource owner credentials, an assertion, or a
 * refresh token).
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-4
"""

# Denotes "authorization_code" grant types (for token obtaining).
OAUTH2_GRANT_TYPE_AUTH_CODE = "authorization_code"

# Denotes "password" grant types (for token obtaining).
OAUTH2_GRANT_TYPE_USER_CREDENTIALS = "password"

# Denotes "assertion" grant types (for token obtaining).
OAUTH2_GRANT_TYPE_ASSERTION = "assertion"

# Denotes "refresh_token" grant types (for token obtaining).
OAUTH2_GRANT_TYPE_REFRESH_TOKEN = "refresh_token"

# Denotes "none" grant types (for token obtaining).
OAUTH2_GRANT_TYPE_NONE = "none"

# Regex to filter out the grant type.
OAUTH2_GRANT_TYPE_REGEXP = "/^(authorization_code|password|assertion|refresh_token|none)$/"

# List of valid grant types.
OAUTH2_GRANT_TYPE_LIST = set(['authorization_code', 'password', 'assertion', 'refresh_token', 'none'])

"""
 * @}
"""


"""
 * @defgroup oauth2_section_5 Accessing a Protected Resource
 * @{
 *
 * Clients access protected resources by presenting an access token to
 * the resource server. Access tokens act as bearer tokens, where the
 * token string acts as a shared symmetric secret. This requires
 * treating the access token with the same care as other secrets (e.g.
 * end-user passwords). Access tokens SHOULD NOT be sent in the clear
 * over an insecure channel.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-5
"""

"""
 * Used to define the name of the OAuth access token parameter (POST/GET/etc.).
 *
 * IETF Draft sections 5.1.2 and 5.1.3 specify that it should be called
 * "oauth_token" but other implementations use things like "access_token".
 *
 * I won't be heartbroken if you change it, but it might be better to adhere
 * to the spec.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-5.1.2
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-5.1.3
"""

OAUTH2_TOKEN_PARAM_NAME = "oauth_token"

"""
 * @}
"""


"""
 * @defgroup oauth2_http_status HTTP status code
 * @{
"""

"""
 * "Found" HTTP status code.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-3
"""
OAUTH2_HTTP_FOUND = "302 Found"

"""
 * "Bad Request" HTTP status code.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-4.3
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-5.2.1
"""
OAUTH2_HTTP_BAD_REQUEST = "400 Bad Request"

"""
 * "Unauthorized" HTTP status code.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-4.3
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-5.2.1
"""
OAUTH2_HTTP_UNAUTHORIZED = "401 Unauthorized"

"""
 * "Forbidden" HTTP status code.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-5.2.1
"""
OAUTH2_HTTP_FORBIDDEN = "403 Forbidden"

"""
 * @}
"""


"""
 * @defgroup oauth2_error Error handling
 * @{
 *
 * @todo Extend for i18n.
"""

"""
 * The request is missing a required parameter, includes an unsupported
 * parameter or parameter value, or is otherwise malformed.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-3.2.1
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-4.3.1
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-5.2.1
"""
OAUTH2_ERROR_INVALID_REQUEST = "invalid_request"

"""
 * The client identifier provided is invalid.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-3.2.1
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-4.3.1
"""
OAUTH2_ERROR_INVALID_CLIENT = "invalid_client"

"""
 * The client is not authorized to use the requested response type.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-3.2.1
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-4.3.1
"""
OAUTH2_ERROR_UNAUTHORIZED_CLIENT = "unauthorized_client"

"""
 * The redirection URI provided does not match a pre-registered value.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-3.2.1
"""
OAUTH2_ERROR_REDIRECT_URI_MISMATCH = "redirect_uri_mismatch"

"""
 * The end-user or authorization server denied the request.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-3.2.1
"""
OAUTH2_ERROR_USER_DENIED = "access_denied"

"""
 * The requested response type is not supported by the authorization server.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-3.2.1
"""
OAUTH2_ERROR_UNSUPPORTED_RESPONSE_TYPE = "unsupported_response_type"

"""
 * The requested scope is invalid, unknown, or malformed.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-3.2.1
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-4.3.1
"""
OAUTH2_ERROR_INVALID_SCOPE = "invalid_scope"

"""
 * The provided access grant is invalid, expired, or revoked (e.g. invalid
 * assertion, expired authorization token, bad end-user password credentials,
 * or mismatching authorization code and redirection URI).
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-4.3.1
"""
OAUTH2_ERROR_INVALID_GRANT = "invalid_grant"

"""
 * The access grant included - its type or another attribute - is not
 * supported by the authorization server.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-4.3.1
"""
OAUTH2_ERROR_UNSUPPORTED_GRANT_TYPE = "unsupported_grant_type"

"""
 * The access token provided is invalid. Resource servers SHOULD use this
 * error code when receiving an expired token which cannot be refreshed to
 * indicate to the client that a new authorization is necessary. The resource
 * server MUST respond with the HTTP 401 (Unauthorized) status code.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-5.2.1
"""
OAUTH2_ERROR_INVALID_TOKEN = "invalid_token"

"""
 * The access token provided has expired. Resource servers SHOULD only use
 * this error code when the client is expected to be able to handle the
 * response and request a new access token using the refresh token issued
 * with the expired access token. The resource server MUST respond with the
 * HTTP 401 (Unauthorized) status code.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-5.2.1
"""
OAUTH2_ERROR_EXPIRED_TOKEN = "expired_token"

"""
 * The request requires higher privileges than provided by the access token.
 * The resource server SHOULD respond with the HTTP 403 (Forbidden) status
 * code and MAY include the "scope" attribute with the scope necessary to
 * access the protected resource.
 *
 * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-5.2.1
"""
OAUTH2_ERROR_INSUFFICIENT_SCOPE  "insufficient_scope"

"""
 * @}
"""

"""
 * OAuth2.0 draft v10 server-side implementation.
 *
 * @author Originally written by Tim Ridgely <tim.ridgely@gmail.com>.
 * @author Updated to draft v10 by Aaron Parecki <aaron@parecki.com>.
 * @author Debug, coding style clean up and documented by Edison Wong <hswong3i@pantarei-design.com>.
"""
class OAuth2 (object):
    ### TODO: Is this an object? confirm

    """
    * Return supported authorization response types.
    *
    * You should override this function with your supported response types.
    *
    * @return
    *   A list as below. If you support all authorization response types,
    *   then you'd do:
    * @code
    * return array(
    *   OAUTH2_AUTH_RESPONSE_TYPE_AUTH_CODE,
    *   OAUTH2_AUTH_RESPONSE_TYPE_ACCESS_TOKEN,
    *   OAUTH2_AUTH_RESPONSE_TYPE_CODE_AND_TOKEN,
    * );
    * @endcode
    *
    * @ingroup oauth2_section_3
    """
    def _getSupportedAuthResponseTypes(self):
        return [
            OAUTH2_AUTH_RESPONSE_TYPE_AUTH_CODE,
            OAUTH2_AUTH_RESPONSE_TYPE_ACCESS_TOKEN,
            OAUTH2_AUTH_RESPONSE_TYPE_CODE_AND_TOKEN
        ]

    """
    * Return supported scopes.
    *
    * If you want to support scope use, then have this function return a list
    * of all acceptable scopes (used to throw the invalid-scope error).
    *
    * @return
    *   A list as below, for example:
    * @code
    * return array(
    *   'my-friends',
    *   'photos',
    *   'whatever-else',
    * );
    * @endcode
    *
    * @ingroup oauth2_section_3
    """
    def _getSupportedScopes(self):
        return []

    """
    * Check restricted authorization response types of corresponding Client
    * identifier.
    *
    * If you want to restrict clients to certain authorization response types,
    * override this function.
    *
    * @param $client_id
    *   Client identifier to be check with.
    * @param $response_type
    *   Authorization response type to be check with, would be one of the
    *   values contained in OAUTH2_AUTH_RESPONSE_TYPE_REGEXP.
    *
    * @return
    *   TRUE if the authorization response type is supported by this
    *   client identifier, and FALSE if it isn't.
    *
    * @ingroup oauth2_section_3
    """
    def _checkRestrictedAuthResponseType(self, client_id, response_type):
        return True

    """
    * Check restricted grant types of corresponding client identifier.
    *
    * If you want to restrict clients to certain grant types, override this
    * function.
    *
    * @param $client_id
    *   Client identifier to be check with.
    * @param $grant_type
    *   Grant type to be check with, would be one of the values contained in
    *   OAUTH2_GRANT_TYPE_REGEXP.
    *
    * @return
    *   TRUE if the grant type is supported by this client identifier, and
    *   FALSE if it isn't.
    *
    * @ingroup oauth2_section_4
    """
    def _checkRestrictedGrantType(self, client_id, grant_type):
        return True
        
    """
    * Get default authentication realm for WWW-Authenticate header.
    *
    * Change this to whatever authentication realm you want to send in a
    * WWW-Authenticate header.
    *
    * @return
    *   A string that you want to send in a WWW-Authenticate header.
    *
    * @ingroup oauth2_error
    """
    def _getDefaultAuthenticationRealm(self):
        return "Service"

    # End stuff that should get overridden.

    """
    * Creates an OAuth2.0 server-side instance.
    *
    * @param $config
    *   An associative array as below:
    *   - access_token_lifetime: (optional) The lifetime of access token in
    *     seconds.
    *   - auth_code_lifetime: (optional) The lifetime of authorization code in
    *     seconds.
    *   - refresh_token_lifetime: (optional) The lifetime of refresh token in
    *     seconds.
    *   - display_error: (optional) Whether to show verbose error messages in
    *     the response.
    """
    ### TODO: Reexamine this one...
    def __init__(self, storage, config={}):
    
        # Array of persistent variables stored.
        self._conf = {}
        
        # @var IOAuth2Storage
        self.storage = storage
        
        self.config = config

    """
    * Returns a persistent variable.
    *
    * @param $name
    *   The name of the variable to return.
    * @param $default
    *   The default value to use if this variable has never been set.
    *
    * @return
    *   The value of the variable.
    """
    def getVariable(self, name, default=None):
        name = str(name).lower()
        if name in self._conf:
            return self._conf[name]
        return default

    """
    * Sets a persistent variable.
    *
    * @param $name
    *   The name of the variable to set.
    * @param $value
    *   The value to set.
    """
    def setVariable(self, name, value):
        name = str(name).lower()
        self._conf[name] = value
        
  
    ### Resource protecting (Section 5).

    """
    * Check that a valid access token has been provided.
    *
    * The scope parameter defines any required scope that the token must have.
    * If a scope param is provided and the token does not have the required
    * scope, we bounce the request.
    *
    * Some implementations may choose to return a subset of the protected
    * resource (i.e. "public" data) if the user has not provided an access
    * token or if the access token is invalid or expired.
    *
    * The IETF spec says that we should send a 401 Unauthorized header and
    * bail immediately so that's what the defaults are set to.
    *
    * @param $scope
    *   A space-separated string of required scope(s), if you want to check
    *   for scope.
    * @param $exit_not_present
    *   If TRUE and no access token is provided, send a 401 header and exit,
    *   otherwise return FALSE.
    * @param $exit_invalid
    *   If TRUE and the implementation of getAccessToken() returns NULL, exit,
    *   otherwise return FALSE.
    * @param $exit_expired
    *   If TRUE and the access token has expired, exit, otherwise return FALSE.
    * @param $exit_scope
    *   If TRUE the access token does not have the required scope(s), exit,
    *   otherwise return FALSE.
    * @param $realm
    *   If you want to specify a particular realm for the WWW-Authenticate
    *   header, supply it here.
    *
    * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-5
    *
    * @ingroup oauth2_section_5
    """
    def verifyAccessToken(self, scope=None, exit_not_present=True, 
            exit_invalid=True, exit_expired=True, exit_scope=True, realm=None):
        token_param = self.getAccessTokenParams()
        if token_param == False: # Access token was not provided
            if exit_not_present:
                msg = 'The request is missing a required parameter, includes \
                        an unsupported parameter or parameter value, repeats \
                        the same parameter, uses more than one method for \
                        including an access token, or is otherwise malformed.'
                return self._errorWWWAuthenticateResponseHeader(
                        OAUTH2_HTTP_BAD_REQUEST, 
                        realm, 
                        OAUTH2_ERROR_INVALID_REQUEST, 
                        msg, 
                        None, 
                        scope
                        )
            return False
            
        # Get the stored token data (from the impelementing subclass)
        token = self.getAccessToken(token_params)
        if token == None:
            if exit_expired:
                msg = 'The access token provided is invalid.'
                return self._errorWWWAuthenticateResponseHeader(
                        OAUTH2_HTTP_UNAUTHORIZED, 
                        realm, 
                        OAUTH2_ERROR_INVALID_TOKEN, 
                        msg, 
                        None, 
                        scope
                        )
            return False
        
        # Check token expiration (leaving this check separated for now)
        ### TODO: Check timestamping
        if 'expires' in token and time.time() > token['expires']:
            if exit_expired:
                msg = 'The access token provided has expired.'
                return self._errorWWWAuthenticateResponseHeader(
                        OAUTH2_HTTP_UNAUTHORIZED, 
                        realm, 
                        OAUTH2_ERROR_EXPIRED_TOKEN, 
                        msg, 
                        None, 
                        scope
                        )
            return False
        
        # Check scope, if provided. If token doesn't have a scope, if it's 
        # empty, or if it's insufficient, throw an error
        if (scope != None and 'scope' not in token)
                or (not token['scope'])
                or (not self.checkScope(scope, token['scope'])):
            if exit_scope:
                msg = 'The request requires higher privileges than \
                        provided by the access token.'
                return self._errorWWWAuthenticateResponseHeader(
                        OAUTH2_HTTP_FORBIDDEN, 
                        realm, 
                        OAUTH2_ERROR_INSUFFICIENT_SCOPE, 
                        msg, 
                        None, 
                        scope
                        )
            return False
            
        return True

    """
    * Check if everything in required scope is contained in available scope.
    *
    * @param $required_scope
    *   Required scope to be check with.
    * @param $available_scope
    *   Available scope to be compare with.
    *
    * @return
    *   TRUE if everything in required scope is contained in available scope,
    *   and False if it isn't.
    *
    * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-5
    *
    * @ingroup oauth2_section_5
    """
    def _checkScope(self, required_scope, available_scope):
        if not isinstance(required_scope, list):
            required_scope = required_scope.split(" ")
        if not isinstance(available_scope, list):
            available_scope = available_scope.split(" ")
        return len(required_scope - available_scope) == 0
    

    """
    * Pulls the access token out of the HTTP request.
    *
    * Either from the Authorization header or GET/POST/etc.
    *
    * @return
    *   Access token value if present, and FALSE if it isn't.
    *
    * @todo Support PUT or DELETE.
    *
    * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-5.1
    *
    * @ingroup oauth2_section_5
    """
    def _getAccessTokenParams(self):
        auth_header = self.getAuthorizationHeader()
        
        if auth_header != False:
            ### TODO: How do we get GET/POST params?
            if OAUTH2_TOKEN_PARAM_NAME in request:
                msg = 'Auth token in GET or POST when token present in header'
                self.errorJsonResponse(
                        OAUTH2_HTTP_BAD_REQUEST, 
                        OAUTH2_ERROR_INVALID_REQUEST, 
                        msg
                        )
        
            auth_header = auth_header.strip()
            
            # Make sure it's Token authorization
            if auth_header[:5] != "OAuth ":
                msg = 'Auth header found that doesn\'t start with "OAuth"'
                self.errorJsonResponse(
                        OAUTH2_HTTP_BAD_REQUEST, 
                        OAUTH2_ERROR_INVALID_REQUEST, 
                        msg
                        )
            
            # Parse the rest of the header
            ### TODO: Test regex
            header_regex = re.compile(r'/\s*OAuth\s*="(.+)"/', re.IGNORECASE)
            matches = header_regex.finditer(auth_header[5:])
            if len(matches) < 2:
                msg = 'Malformed auth header'
                self.errorJsonResponse(
                        OAUTH2_HTTP_BAD_REQUEST, 
                        OAUTH2_ERROR_INVALID_REQUEST, 
                        msg
                        )
                
            return matches[1]
            
        ### SKIPPED FOR NOW:
        # if (isset($_GET[OAUTH2_TOKEN_PARAM_NAME])) {
        #   if (isset($_POST[OAUTH2_TOKEN_PARAM_NAME])) # Both GET and POST are not allowed
        #     $this->errorJsonResponse(OAUTH2_HTTP_BAD_REQUEST, OAUTH2_ERROR_INVALID_REQUEST, 
        #            'Only send the token in GET or POST, not both');
        # 
        #   return $_GET[OAUTH2_TOKEN_PARAM_NAME];
        # }
        # 
        # if (isset($_POST[OAUTH2_TOKEN_PARAM_NAME]))
        #   return $_POST[OAUTH2_TOKEN_PARAM_NAME];

        return False

    # Access token granting (Section 4).

    """
    * Grant or deny a requested access token.
    *
    * This would be called from the "/token" endpoint as defined in the spec.
    * Obviously, you can call your endpoint whatever you want.
    * 
    * @param $inputData - The draft specifies that the parameters should be
    * retreived from POST, but you can override to whatever method you like.
    *
    * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-4
    *
    * @ingroup oauth2_section_4
    """
    def grantAccessToken(self, inputData=None):
        ### TODO: Rewrite this section
        data = {}
        try:
            data.grant_type = inputData.grant_type
            data.scope = inputData.scope
            data.code = inputData.code
            data.redirect_uri = inputData.redirect_uri
            data.username = inputData.username
            data.password = inputData.password
            data.assertion_type = inputData.assertion_type
            data.assertion = inputData.assertion
            data.refresh_token = inputData.refresh_token
        except:
            raise Exception("Missing variable")
            
        if data.grant_type not in OAUTH2_GRANT_TYPE_LIST
                or not isinstance(data.scope, basestring)
                or not isinstance(data.code, basestring)
                ### TODO: Add check for valid URL
                or not isinstance(data.username, basestring)
                or not isinstance(data.password, basestring)
                or not isinstance(data.assertion_type, basestring)
                or not isinstance(data.assertion, basestring)
                or not isinstance(data.refresh_token, basestring):
            raise Exception("Invalid input")
        
        ### SKIPPED: Make sure we've implemented the requested grant type
        
        # Authorize the client
        client = self.getClientCredentials()
        
        if self.checkClientCredentials(client[0], client[1]) == False:
            self.errorJsonResponse(OAUTH2_HTTP_BAD_REQUEST, OAUTH2_ERROR_INVALID_CLIENT)
        
        if not self.checkRestrictedGrantType(client[0], data['grant_type']):
            self.errorJsonResponse(OAUTH2_HTTP_BAD_REQUEST, OAUTH2_ERROR_UNAUTHORIZED_CLIENT)
        
        # Do the granting
        if data['grant_type'] == OAUTH2_GRANT_TYPE_AUTH_CODE:
            if not data['code'] or not data['redirect_uri']:
                self.errorJsonResponse(
                        OAUTH2_HTTP_BAD_REQUEST, 
                        OAUTH2_ERROR_INVALID_REQUEST, 
                        'Missing parameters. "code" and "redirect_uri" required'
                        )
            stored = self._getAuthCode(data['code'])
        
            # Ensure that the input uri starts with the stored uri
            if stored == None or client[0] != stored['client_id'] 
                    or data['redirect_uri'] != stored['redirect_uri']:
                self.errorJsonResponse(
                        OAUTH2_HTTP_BAD_REQUEST, 
                        OAUTH2_ERROR_INVALID_GRANT, 
                        "Refresh token doesn't exist or is invalid for the client"
                        )
            if stored['expires'] < time.time():
                self.errorJsonResponse(
                        OAUTH2_HTTP_BAD_REQUEST, 
                        OAUTH2_ERROR_EXPIRED_TOKEN
                        )

        elif data['grant_type'] == OAUTH2_GRANT_TYPE_USER_CREDENTIALS:
            stored = self._checkUserCredentials(client[0], data['username'], data['password'])
            if stored == False:
                self.errorJsonResponse(OAUTH2_HTTP_BAD_REQUEST, OAUTH2_ERROR_INVALID_GRANT)

        elif data['grant_type'] == OAUTH2_GRANT_TYPE_ASSERTION:
            stored = self._checkAssertion(client[0], data['assertion_type'], data['assertion'])
            if stored == False:
                self.errorJsonResponse(OAUTH2_HTTP_BAD_REQUEST, OAUTH2_ERROR_INVALID_GRANT)

        elif data['grant_type'] == OAUTH2_GRANT_TYPE_REFRESH_TOKEN:
            stored = self._getRefreshToken(data['refresh_token'])
            if stored == None or client[0] != stored['client_id']:
                self.errorJsonResponse(
                        OAUTH2_HTTP_BAD_REQUEST, 
                        OAUTH2_ERROR_INVALID_GRANT
                        )
            if stored['expires'] < time.time():
                self.errorJsonResponse(
                        OAUTH2_HTTP_BAD_REQUEST, 
                        OAUTH2_ERROR_EXPIRED_TOKEN
                        )
            self.setVariable('_old_refresh_token', stored['refresh_token'])

        elif data['grant_type'] == OAUTH2_GRANT_TYPE_REFRESH_TOKEN:
            stored = self._checkNoneAccess(client[0])
            if stored == False:
                self.errorJsonResponse(
                        OAUTH2_HTTP_BAD_REQUEST, 
                        OAUTH2_ERROR_INVALID_REQUEST
                        )
            
        # Check scope, if provided
        if data['scope'] and (
                not isinstance(stored, dict)
                or 'scope' not in stored
                or self._checkScope(data['scope'], stored['scope'])
                ):
            self.errorJsonResponse(
                    OAUTH2_HTTP_BAD_REQUEST, 
                    OAUTH2_ERROR_INVALID_SCOPE
                    )
        if 'scope' not in data:
            data['scope'] = None
        
        token = self._createAccessToken(client[0], stored['user_id'], stored['scope'])
        
        self.sendJsonHeaders()
        # print json_encode(token)

    """
    * Internal function used to get the client credentials from HTTP basic
    * auth or POST data.
    *
    * @return
    *   A list containing the client identifier and password, for example
    * @code
    * return array(
    *   $_POST["client_id"],
    *   $_POST["client_secret"],
    * );
    * @endcode
    *
    * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-2
    *
    * @ingroup oauth2_section_2
    """
    def _getClientCredentials(self):
        ### SKIPPED
        # if (isset($_SERVER["PHP_AUTH_USER"]) && $_POST && isset($_POST["client_id"]))
        # $this->errorJsonResponse(OAUTH2_HTTP_BAD_REQUEST, OAUTH2_ERROR_INVALID_CLIENT);
        
        # Try basic auth
        if authorization in request and username in request.authorization:
            return [request.authorization.username, request.authorization.password]
        
        # Try POST
        if request.method == 'POST' and 'client_id' in request.data:
            if 'client_secret' in request.data:
                return [request.data.client_id, request.data.client_secret]
            return [request.data.client_id, None]
        
        # No credentials were specified
        self.errorJsonResponse(OAUTH2_HTTP_BAD_REQUEST, OAUTH2_ERROR_INVALID_CLIENT)

    # End-user/client Authorization (Section 3 of IETF Draft).

    """
    * Pull the authorization request data out of the HTTP request.
    *
    * @param $inputData - The draft specifies that the parameters should be
    * retreived from GET, but you can override to whatever method you like.
    * @return
    *   The authorization parameters so the authorization server can prompt
    *   the user for approval if valid.
    *
    * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-3
    *
    * @ingroup oauth2_section_3
    """
    def getAuthorizeParams(self, inputData=None):
        ### TODO: Rewrite this section
        data = {}
        try:
            data.client_id = inputData.client_id
            data.response_type = inputData.response_type
            data.redirect_uri = inputData.redirect_uri
            data.state = inputData.state
            data.scope = inputData.scope
        except:
            raise Exception("Missing variable")
            
        if data.response_type not in OAUTH2_AUTH_RESPONSE_TYPE_LIST
                ### TODO: Add check for valid client id (regex)
                ### TODO: Add check for valid URL
                or not isinstance(data.scope, basestring)
                or not isinstance(data.state, basestring):
            raise Exception("Invalid input")
        
        # Check if redirect_uri is stored
        stored = self._getClientDetails(data['client_id'])
        
        if stored = None or not stored:
            self.errorJsonResponse(OAUTH2_HTTP_FOUND, OAUTH2_ERROR_INVALID_REQUEST)
        

        # getRedirectUri() should return FALSE if the given client ID is invalid
        # this probably saves us from making a separate db call, and simplifies the method set
        pass
        
        # If there's an existing uri and one from input, verify that they match
        pass

        # Check requested auth response type against the list of supported types
        if data['response_type'] not in self.getSupportedAuthResponseTypes():
            self.errorDoRedirectUriCallback(
                    data['redirect_uri'], 
                    OAUTH2_ERROR_UNSUPPORTED_RESPONSE_TYPE,
                    None,
                    None, 
                    data['state']
                    )
                    
        # Restrict clients to certain authorization response types
        pass
        
        # Validate that the requested scope is supported
        pass

        # Return retreived client details together with input
        return data, stored

    """
    * Redirect the user appropriately after approval.
    *
    * After the user has approved or denied the access request the
    * authorization server should call this function to redirect the user
    * appropriately.
    *
    * @param $is_authorized
    *   TRUE or FALSE depending on whether the user authorized the access.
    * @param $user_id
    *   Identifier of user who authorized the client
    * @param $params
    *   An associative array as below:
    *   - response_type: The requested response: an access token, an
    *     authorization code, or both.
    *   - client_id: The client identifier as described in Section 2.
    *   - redirect_uri: An absolute URI to which the authorization server
    *     will redirect the user-agent to when the end-user authorization
    *     step is completed.
    *   - scope: (optional) The scope of the access request expressed as a
    *     list of space-delimited strings.
    *   - state: (optional) An opaque value used by the client to maintain
    *     state between the request and callback.
    *
    * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-3
    *
    * @ingroup oauth2_section_3
    """
    def finishClientAuthorization(self, is_authorized, user_id=None, params={}):
        result = { 'query': {} }
        if 'state' in params and params['state'] != None:
            result['query']['state'] = params['state']
        if 'is_authorized' == False:
            result['query']['error'] = OAUTH2_ERROR_USER_DENIED
        else:
            if 'response_type' in params and (
                    params['response_type'] == OAUTH2_AUTH_RESPONSE_TYPE_AUTH_CODE
                    or params['response_type'] == OAUTH2_AUTH_RESPONSE_TYPE_CODE_AND_TOKEN):
                result['query']['code'] = self._createAuthCode(
                                            params['client_id'], 
                                            user_id, 
                                            params['redirect_uri'], 
                                            params['scope']
                                            )
            if 'response_type' in params and (
                    params['response_type'] == OAUTH2_AUTH_RESPONSE_TYPE_ACCESS_TOKEN
                    or params['response_type'] == OAUTH2_AUTH_RESPONSE_TYPE_CODE_AND_TOKEN):
                result['fragment'] = self._createAccessToken(params['client_id'], user_id, params['scope'])

        self._doRedirectUriCallback(params['redirect_uri'], result)

    # Other/utility functions.

    """
    * Redirect the user agent.
    *
    * Handle both redirect for success or error response.
    *
    * @param $redirect_uri
    *   An absolute URI to which the authorization server will redirect
    *   the user-agent to when the end-user authorization step is completed.
    * @param $params
    *   Parameters to be pass though buildUri().
    *
    * @ingroup oauth2_section_3
    """
    def _doRedirectUriCallback(self, redirect_uri, params):
        ### SKIPPED
        #header("HTTP/1.1 ". OAUTH2_HTTP_FOUND);
        #header("Location: " . $this->buildUri($redirect_uri, $params));
        #exit;
        pass

    """
    * Build the absolute URI based on supplied URI and parameters.
    *
    * @param $uri
    *   An absolute URI.
    * @param $params
    *   Parameters to be append as GET.
    *
    * @return
    *   An absolute URI with supplied parameters.
    *
    * @ingroup oauth2_section_3
    """
    def _buildUri(self, uri, params):
        ### SKIPPED
        pass

    """
    * Handle the creation of access token, also issue refresh token if support.
    *
    * This belongs in a separate factory, but to keep it simple, I'm just
    * keeping it here.
    *
    * @param $client_id
    *   Client identifier related to the access token.
    * @param $scope
    *   (optional) Scopes to be stored in space-separated string.
    *
    * @ingroup oauth2_section_4
    """
    def _createAccessToken(self, client_id, user_id, scope=None):
        token = {
            'access_token' = self._genAcccessToken(),
            'expires_in' = self.getVariable('access_token_lifetime', OAUTH2_DEFAULT_ACCESS_TOKEN_LIFETIME),
            'scope' = scope
        }
        
        self._setAccessToken(
                token['access_token'],
                client_id,
                user_id,
                time.time() + self.getVariable('access_token_lifetime', OAUTH2_DEFAULT_ACCESS_TOKEN_LIFETIME),
                scope
                )
        
        # Issue a refresh token, if we support them
        if OAUTH2_GRANT_TYPE_REFRESH_TOKEN in self._getSupportedGrantTypes():
            token['refresh_token'] = self.genAccessToken()
            self._setRefreshToken(
                    token['refresh_token'],
                    client_id,
                    user_id,
                    time.time() + self.getVariable('access_token_lifetime', OAUTH2_DEFAULT_REFRESH_TOKEN_LIFETIME),
                    scope
                    )
            # If we've granted a new refresh token, expire the old one
            if self.getVariable('_old_refresh_token'):
                self._unsetRefreshToken(self.getVariable('_old_refresh_token'))
        
        return token

    """
    * Handle the creation of auth code.
    *
    * This belongs in a separate factory, but to keep it simple, I'm just
    * keeping it here.
    *
    * @param $client_id
    *   Client identifier related to the access token.
    * @param $redirect_uri
    *   An absolute URI to which the authorization server will redirect the
    *   user-agent to when the end-user authorization step is completed.
    * @param $scope
    *   (optional) Scopes to be stored in space-separated string.
    *
    * @ingroup oauth2_section_3
    """
    def _createAuthCode(self, client_id, user_id, redirect_uri, scope=None):
        code = self._genAuthCode()
        self._setAuthCode(
                code,
                client_id,
                user_id,
                redirect_uri,
                time.time() + self.getVariable('access_token_lifetime', OAUTH2_DEFAULT_AUTH_CODE_LIFETIME),
                scope
                )
        return code

    """
    * Generate unique access token.
    *
    * Implementing classes may want to override these function to implement
    * other access token or auth code generation schemes.
    *
    * @return
    *   An unique access token.
    *
    * @ingroup oauth2_section_4
    """
    def _genAccessToken(self):
        data = str(random.random()) + str(random.random()) + str(random.random()) + str(time.time())
        token = hashlib.md5(base64.b64encode(struct.pack('L', data)))
        return str(token.hexdigest())
        
    """
    * Generate unique auth code.
    *
    * Implementing classes may want to override these function to implement
    * other access token or auth code generation schemes.
    *
    * @return
    *   An unique auth code.
    *
    * @ingroup oauth2_section_3
    """
    def _genAuthCode(self):
        data = str(random.random()) + str(random.random()) + str(random.random()) + str(time.time())
        token = hashlib.md5(base64.b64encode(struct.pack('L', data)))
        return str(token.hexdigest())

    """
    * Pull out the Authorization HTTP header and return it.
    *
    * Implementing classes may need to override this function for use on
    * non-Apache web servers.
    *
    * @return
    *   The Authorization HTTP header, and FALSE if does not exist.
    *
    * @todo Handle Authorization HTTP header for non-Apache web servers.
    *
    * @ingroup oauth2_section_5
    """
    def _getAuthorizationHeader(self):
        pass

    """
    * Send out HTTP headers for JSON.
    *
    * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-4.2
    * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-4.3
    *
    * @ingroup oauth2_section_4
    """
    def _sendJsonHeaders(self):
        pass

    """
    * Redirect the end-user's user agent with error message.
    *
    * @param $redirect_uri
    *   An absolute URI to which the authorization server will redirect the
    *   user-agent to when the end-user authorization step is completed.
    * @param $error
    *   A single error code as described in Section 3.2.1.
    * @param $error_description
    *   (optional) A human-readable text providing additional information,
    *   used to assist in the understanding and resolution of the error
    *   occurred.
    * @param $error_uri
    *   (optional) A URI identifying a human-readable web page with
    *   information about the error, used to provide the end-user with
    *   additional information about the error.
    * @param $state
    *   (optional) REQUIRED if the "state" parameter was present in the client
    *   authorization request. Set to the exact value received from the client.
    *
    * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-3.2
    *
    * @ingroup oauth2_error
    """
    def _errorDoRedirectUriCallback(self, redirect_uri, error, 
            error_description=None, error_uri=None, state=None):
        pass

    """
    * Send out error message in JSON.
    *
    * @param $http_status_code
    *   HTTP status code message as predefined.
    * @param $error
    *   A single error code.
    * @param $error_description
    *   (optional) A human-readable text providing additional information,
    *   used to assist in the understanding and resolution of the error
    *   occurred.
    * @param $error_uri
    *   (optional) A URI identifying a human-readable web page with
    *   information about the error, used to provide the end-user with
    *   additional information about the error.
    *
    * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-4.3
    *
    * @ingroup oauth2_error
    """
    def _errorJsonResponse(self, http_status_code, error, 
            error_description=None, error_uri=None):
        pass

    """
    * Send a 401 unauthorized header with the given realm and an error, if
    * provided.
    *
    * @param $http_status_code
    *   HTTP status code message as predefined.
    * @param $realm
    *   The "realm" attribute is used to provide the protected resources
    *   partition as defined by [RFC2617].
    * @param $scope
    *   A space-delimited list of scope values indicating the required scope
    *   of the access token for accessing the requested resource.
    * @param $error
    *   The "error" attribute is used to provide the client with the reason
    *   why the access request was declined.
    * @param $error_description
    *   (optional) The "error_description" attribute provides a human-readable text
    *   containing additional information, used to assist in the understanding
    *   and resolution of the error occurred.
    * @param $error_uri
    *   (optional) The "error_uri" attribute provides a URI identifying a human-readable
    *   web page with information about the error, used to offer the end-user
    *   with additional information about the error. If the value is not an
    *   absolute URI, it is relative to the URI of the requested protected
    *   resource.
    *
    * @see http:#tools.ietf.org/html/draft-ietf-oauth-v2-10#section-5.2
    *
    * @ingroup oauth2_error
    """
    def _errorWWWAuthenticateResponseHeader(self, http_status_code, realm, 
            error, error_description=None, error_uri=None, scope=None):
        pass
    
