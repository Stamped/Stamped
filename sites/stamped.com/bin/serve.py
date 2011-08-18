#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import init
import os, flask, json, utils, random, time, hashlib, logs
from flask import request, Response, Flask
from functools import wraps
from Schemas import *
from HTTPSchemas import *

from api.MongoStampedAPI import MongoStampedAPI
from api.MongoStampedAuth import MongoStampedAuth
from utils import AttributeDict
from errors import *
from resource import *

# ################ #
# Global Variables #
# ################ #

REST_API_VERSION = "v1"
REST_API_PREFIX  = "/api/%s/" % REST_API_VERSION
ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
stampedAPI = MongoStampedAPI(output='http')
stampedAuth = MongoStampedAuth()

# ################# #
# Utility Functions #
# ################# #

def encodeType(obj):
    if '_dict' in obj:
        return obj._dict
    else:
        return obj.__dict__

def transformOutput(request, d):
    output_json = json.dumps(d, sort_keys=True, indent=None if request.is_xhr else 2, default=encodeType)
    output = Response(output_json, mimetype='application/json')
    logs.debug("Transform output: \"%s\"" % output_json)
    return output

def parseRequestForm(schema, request, **kwargs):

    ### Parse Request
    if request.method == 'POST':
        unparsedInput = request.form
    elif request.method == 'GET': 
        unparsedInput = request.args
    else:
        logs.warning("End request: Invalid method")
        raise

    data = {}
    auth = {}
    for k, v in unparsedInput.iteritems():
        if k == 'oauth_token':
            auth['oauth_token'] = v
        elif k == 'client_id':
            auth['client_id'] = v
        elif k == 'client_secret':
            auth['client_secret'] = v
        else:
            data[k] = v
        
    logs.debug("Request url: %s" % request.base_url)
    logs.debug("Request data: %s" % data)
    logs.debug("Request auth: %s" % auth)

    try:
        schema.importData(data)
    except (InvalidArgument, Fail) as e:
        utils.log("API function failed to parse input '%s' against schema '%s'" % \
            (str(data), str(schema)))
        utils.printException()
        raise

    # Split color
    ### TODO: Reconsider how to handle this
    if 'color' in schema:
        color = schema.color.split(',')

        schema.color_primary = SchemaElement(basestring)
        schema.color_secondary = SchemaElement(basestring)
        schema.color_primary = color[0]
        schema.color_secondary = color[-1]

        schema.removeElement('color')

    logs.debug("Parsed request data: %s" % schema)

    return schema, auth

def verifyClientCredentials(data):
    if not stampedAuth.verifyClientCredentials( \
        data.client_id, data.client_secret):
        logs.info("Invalid authorization: %s" % request)
        raise StampedHTTPError("Error", 401) 

    return True

def handleAddAccountRequest(data, auth):
    ### Add Account
    try:
        account = stampedAPI.addAccount(data.exportSparse(), auth)
    except:
        logs.warning("Fail")
        raise

    logs.debug("Account added")
    
    ### Generate Refresh Token & Access Token
    token = stampedAuth.addRefreshToken({
        'client_id': auth['client_id'],
        'authenticated_user_id': account['user_id']
    })

    logs.debug("Token created")

    ### Format Output
    result = {
        'user': account,
        'token': token
    }
    
    return result

def checkOAuth(request):
    ### Parse Request for Access Token
    try:
        oauth_token = request.values['oauth_token']
    except:
        msg = "Access token not included"
        logs.warning(msg)
        raise StampedHTTPError("invalid_request", 401, msg)
    
    ### Validate OAuth Access Token
    try:
        authenticated_user_id = stampedAuth.verifyAccessToken({'oauth_token': oauth_token}) #### TEMP! Change stampedAuth
        
        if authenticated_user_id == None:
            raise
        return authenticated_user_id
    except StampedHTTPError:
        raise
    except Exception:
        msg = "Invalid access token"
        logs.warning(msg)
        raise StampedHTTPError("invalid_token", 401, msg)

def checkClient(request):
    ### Parse Request for Client Credentials
    try:
        client_id       = request.values['client_id']
        client_secret   = request.values['client_secret']
    except:
        msg = "Client credentials not included"
        logs.warning(msg)
        raise StampedHTTPError("invalid_request", 401, msg)

    ### Validate Client Credentials
    try:
        if not stampedAuth.verifyClientCredentials( \
        client_id, client_secret):
            raise
        return client_id
    except:
        msg = "Invalid client credentials"
        logs.warning(msg)
        raise StampedHTTPError("access_denied", 401, msg)

def parseRequest(schema, request):
    ### Parse Request
    try:
        logs.debug("Request url: %s" % request.base_url)
        logs.debug("Request data: %s" % request.values)

        data = request.values.to_dict()
        data.pop('oauth_token', None)
        data.pop('client_id', None)
        data.pop('client_secret', None)
    
        if schema == None:
            if len(data) > 0:
                raise
            return
        
        schema.importData(data)

        logs.debug("Parsed request data: %s" % schema)

        return schema

    except (InvalidArgument, Fail) as e:
        msg = str(e)
        logs.warning(msg)
        raise StampedHTTPError("bad_request", 400, e)

def handleHTTPRequest(fn):
    @wraps(fn)
    def handleHTTPRequest():
        try:
            print
            print
            logs.info("Begin: %s" % fn.__name__)
            ret = fn()
            logs.info("End request: Success")
            return ret
        except StampedHTTPError as e:
            logs.warning("%s Error: %s (%s)" % (e.code, e.msg, e.desc))
            return e.msg, e.code
        except Exception as e:
            logs.warning("500 Error: %s" % e)
            return "Internal error", 500
    return handleHTTPRequest






def handleRequest(schema, request, stampedAPIFunc, requireOAuthToken=True):
    try:
        print
        print
        logs.refresh()
        logs.info("Begin request")

        ### Parse Request
        try:
            data, auth = parseRequestForm(schema, request)
        except (InvalidArgument, Fail) as e:
            msg = str(e)
            logs.warning(msg)
            raise StampedHTTPError("invalid_request", 400, e)

        ### EXCEPTION: No OAuth Token
        if requireOAuthToken == False:
            # Check for valid client credentials
            logs.debug("Does not require OAuth Token")
            stampedAuth.verifyClientCredentials(auth)
        else:
            ### Require OAuth token to be included
            if 'oauth_token' not in auth:
                msg = "Access token not included"
                logs.warning(msg)
                raise StampedHTTPError("invalid_request", 401, msg)

            ### Validate OAuth Access Token
            authenticated_user_id = stampedAuth.verifyAccessToken(auth)
            if authenticated_user_id == None:
                msg = "Invalid access token"
                logs.warning(msg)
                raise StampedHTTPError("invalid_token", 401, msg)
            
            auth['authenticated_user_id'] = authenticated_user_id

            logs.debug("Final data set: %s" % (data))

        ### Generate Result
        logs.info("Begin: %s" % stampedAPIFunc.__name__)
        if stampedAPIFunc == stampedAPI.addAccount:
            # Exception -- requires both StampedAuth and StampedAPI. We should
            # try to get rid of this.
            result = handleAddAccountRequest(data, auth)
        else:
            result = stampedAPIFunc(data.exportSparse(), auth)
            
        ### Return to Client
        try:
            ret = transformOutput(request, result)
            logs.info("End request: Success")
            return ret
        except Exception as e:
            msg = "Internal error processing API function '%s' (%s)" % (
                utils.getFuncName(1), str(e))
            utils.log(msg)
            utils.printException()
            return msg, 500
    except StampedHTTPError as e:
        logs.warning("%s Error: %s (%s)" % (e.code, e.msg, e.desc))
        return e.msg, e.code
    except Exception as e:
        logs.warning("500 Error: %s" % e)
        return "Internal error", 500

# ####### #
# OAuth 2 #
# ####### #

@app.route(REST_API_PREFIX + 'oauth2/token.json', methods=['POST'])
def refreshToken():
    class RequestSchema(Schema):
        def setSchema(self):
            self.refresh_token      = SchemaElement(basestring, required=True)
            self.grant_type         = SchemaElement(basestring, required=True)
    return handleRequest(RequestSchema(), request, stampedAuth.verifyRefreshToken, requireOAuthToken=False)

@app.route(REST_API_PREFIX + 'oauth2/login.json', methods=['POST'])
def loginUser():
    class RequestSchema(Schema):
        def setSchema(self):
            self.screen_name        = SchemaElement(basestring, required=True)
            self.password           = SchemaElement(basestring, required=True)
    return handleRequest(RequestSchema(), request, stampedAuth.verifyUserCredentials, requireOAuthToken=False)


"""
   #                                                    
  # #    ####   ####   ####  #    # #    # #####  ####  
 #   #  #    # #    # #    # #    # ##   #   #   #      
#     # #      #      #    # #    # # #  #   #    ####  
####### #      #      #    # #    # #  # #   #        # 
#     # #    # #    # #    # #    # #   ##   #   #    # 
#     #  ####   ####   ####   ####  #    #   #    ####  
"""

@app.route(REST_API_PREFIX + 'account/create.json', methods=['POST'])
@handleHTTPRequest
def addAccount():
    client_id   = checkClient(request)

    schema      = parseRequest(HTTPAccountNew(), request)
    account     = schema.exportSchema(Account())

    account     = stampedAPI.addAccount(account)
    user        = HTTPUser().importSchema(account)

    token       = stampedAuth.addRefreshToken(client_id, user.user_id)

    output      = { 'user': user.exportSparse(), 'token': token }

    return transformOutput(request, output)

@app.route(REST_API_PREFIX + 'account/settings.json', methods=['POST', 'GET'])
@handleHTTPRequest
def updateAccount():
    authUserId  = checkOAuth(request)

    if request.method == 'POST':

        ### TODO: Carve out password changes, require original password sent again?

        ### TEMP: Generate list of changes. Need to do something better eventually...
        schema      = parseRequest(HTTPAccountSettings(), request)
        data        = schema.exportSparse()

        for k, v in data.iteritems():
            if v == '':
                data[k] = None

        ### TODO: Verify email is valid
        account     = stampedAPI.updateAccountSettings(authUserId, data)

    else:
        schema      = parseRequest(None, request)
        account     = stampedAPI.getAccount(authUserId)

    account     = HTTPAccount().importSchema(account)

    return transformOutput(request, account.exportSparse())
    
@app.route(REST_API_PREFIX + 'account/update_profile.json', methods=['POST'])
@handleHTTPRequest
def updateProfile():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPAccountProfile(), request)

    ### TEMP: Generate list of changes. Need to do something better eventually...
    data        = schema.exportSparse()

    for k, v in data.iteritems():
        if v == '':
            data[k] = None

    if 'color' in data:
        color = data['color'].split(',')
        data['color_primary']   = color[0]
        data['color_secondary'] = color[-1]
        del(data['color'])
    
    account     = stampedAPI.updateProfile(authUserId, data)
    user        = HTTPUser().importSchema(account)

    return transformOutput(request, user.exportSparse())

@app.route(REST_API_PREFIX + 'account/update_profile_image.json', methods=['POST'])
@handleHTTPRequest
def updateProfileImage():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPAccountProfileImage(), request)
    
    url         = stampedAPI.updateProfileImage(authUserId, schema.profile_image)

    output      = { 'user_id': authUserId, 'profile_image': url }

    return transformOutput(request, output)

@app.route(REST_API_PREFIX + 'account/remove.json', methods=['POST'])
@handleHTTPRequest
def removeAccount():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(None, request)

    result      = stampedAPI.removeAccount(authUserId)

    return transformOutput(request, result)

@app.route(REST_API_PREFIX + 'account/verify_credentials.json', methods=['GET'])
def verifyAccountCredentials():
    ### TODO: Remove this function?
    return "Not Implemented", 404

@app.route(REST_API_PREFIX + 'account/reset_password.json', methods=['POST'])
def resetPassword():
    ### TODO
    return "Not Implemented", 404

"""
#     #                             
#     #  ####  ###### #####   ####  
#     # #      #      #    # #      
#     #  ####  #####  #    #  ####  
#     #      # #      #####       # 
#     # #    # #      #   #  #    # 
 #####   ####  ###### #    #  ####  
"""

@app.route(REST_API_PREFIX + 'users/show.json', methods=['GET'])
@handleHTTPRequest
def getUser():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    user        = stampedAPI.getUser(schema, authUserId)
    user        = HTTPUser().importSchema(user)

    return transformOutput(request, user.exportSparse())

@app.route(REST_API_PREFIX + 'users/lookup.json', methods=['GET'])
@handleHTTPRequest
def getUsers():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserIds(), request)

    users       = stampedAPI.getUsers(schema.user_ids.value, \
                    schema.screen_names.value, authUserId)

    output = []
    for user in users:
        output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(request, output)

@app.route(REST_API_PREFIX + 'users/search.json', methods=['GET'])
@handleHTTPRequest
def searchUsers():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserSearch(), request)

    users       = stampedAPI.searchUsers(schema.q, schema.limit, authUserId)

    output = []
    for user in users:
        output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(request, output)

@app.route(REST_API_PREFIX + 'users/privacy.json', methods=['GET'])
@handleHTTPRequest
def getPrivacy():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    privacy     = stampedAPI.getPrivacy(schema)

    return transformOutput(request, privacy)

"""
#######                                      
#       #####  # ###### #    # #####   ####  
#       #    # # #      ##   # #    # #      
#####   #    # # #####  # #  # #    #  ####  
#       #####  # #      #  # # #    #      # 
#       #   #  # #      #   ## #    # #    # 
#       #    # # ###### #    # #####   ####  
"""

@app.route(REST_API_PREFIX + 'friendships/create.json', methods=['POST'])
@handleHTTPRequest
def addFriendship():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    user        = stampedAPI.addFriendship(authUserId, schema)
    user        = HTTPUser().importSchema(user)

    return transformOutput(request, user.exportSparse())

@app.route(REST_API_PREFIX + 'friendships/remove.json', methods=['POST'])
@handleHTTPRequest
def removeFriendship():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    user        = stampedAPI.removeFriendship(authUserId, schema)
    user        = HTTPUser().importSchema(user)

    return transformOutput(request, user.exportSparse())

@app.route(REST_API_PREFIX + 'friendships/check.json', methods=['GET'])
@handleHTTPRequest
def checkFriendship():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    result      = stampedAPI.checkFriendship(authUserId, schema)

    return transformOutput(request, result)

@app.route(REST_API_PREFIX + 'friendships/friends.json', methods=['GET'])
@handleHTTPRequest
def getFriends():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    userIds     = stampedAPI.getFriends(schema)
    output      = { 'user_ids': userIds }

    return transformOutput(request, output)

@app.route(REST_API_PREFIX + 'friendships/followers.json', methods=['GET'])
@handleHTTPRequest
def getFollowers():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    userIds     = stampedAPI.getFollowers(schema)
    output      = { 'user_ids': userIds }

    return transformOutput(request, output)

@app.route(REST_API_PREFIX + 'friendships/approve.json', methods=['POST'])
@handleHTTPRequest
def approveFriendship():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    user        = stampedAPI.approveFriendship(authUserId, schema)
    user        = HTTPUser().importSchema(user)

    return transformOutput(request, user.exportSparse())

@app.route(REST_API_PREFIX + 'friendships/blocks/create.json', methods=['POST'])
@handleHTTPRequest
def addBlock():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    user        = stampedAPI.addBlock(authUserId, schema)
    user        = HTTPUser().importSchema(user)

    return transformOutput(request, user.exportSparse())

@app.route(REST_API_PREFIX + 'friendships/blocks/check.json', methods=['GET'])
@handleHTTPRequest
def checkBlock():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    result      = stampedAPI.checkBlock(authUserId, schema)

    return transformOutput(request, result)

@app.route(REST_API_PREFIX + 'friendships/blocking.json', methods=['GET'])
@handleHTTPRequest
def getBlocks():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(None, request)

    userIds     = stampedAPI.getBlocks(authUserId)
    output      = { 'user_ids': userIds }

    return transformOutput(request, output)

@app.route(REST_API_PREFIX + 'friendships/blocks/remove.json', methods=['POST'])
@handleHTTPRequest
def removeBlock():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    user        = stampedAPI.removeBlock(authUserId, schema)
    user        = HTTPUser().importSchema(user)

    return transformOutput(request, user.exportSparse())


"""
#######                                      
#       #    # ##### # ##### # ######  ####  
#       ##   #   #   #   #   # #      #      
#####   # #  #   #   #   #   # #####   ####  
#       #  # #   #   #   #   # #           # 
#       #   ##   #   #   #   # #      #    # 
####### #    #   #   #   #   # ######  ####  
"""

@app.route(REST_API_PREFIX + 'entities/create.json', methods=['POST'])
@handleHTTPRequest
def addEntity():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPNewEntity(), request)
    entity      = schema.exportSchema(Entity())

    entity.sources.userGenerated.user_id = authUserId

    entity      = stampedAPI.addEntity(entity)
    entity      = entity.exportSchema(HTTPEntity())

    return transformOutput(request, entity.exportSparse())

@app.route(REST_API_PREFIX + 'entities/show.json', methods=['GET'])
@handleHTTPRequest
def getEntity():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPEntityId(), request)
    entity      = stampedAPI.getEntity(schema.entity_id, authUserId)
    entity      = entity.exportSchema(HTTPEntity())

    return transformOutput(request, entity.exportSparse())

@app.route(REST_API_PREFIX + 'entities/update.json', methods=['POST'])
@handleHTTPRequest
def updateEntity():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPModifiedEntity(), request)

    ### TEMP: Generate list of changes. Need to do something better eventually...
    data        = schema.exportSparse()
    del(data['entity_id'])

    for k, v in data.iteritems():
        if v == '':
            data[k] = None
    if 'address' in data:
        data['details.place.address'] = data['address']
        del(data['address'])
    if 'coordinates' in data and data['coordinates'] != None:
        data['coordinates'] = {
            'lat': data['coordinates'].split(',')[0],
            'lng': data['coordinates'].split(',')[-1]
        }
    
    entity      = stampedAPI.updateCustomEntity(schema.entity_id, data, authUserId)
    entity      = entity.exportSchema(HTTPEntity())

    return transformOutput(request, entity.exportSparse())

@app.route(REST_API_PREFIX + 'entities/remove.json', methods=['POST'])
@handleHTTPRequest
def removeEntity():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPEntityId(), request)
    result      = stampedAPI.removeCustomEntity(schema.entity_id, authUserId)
    
    return transformOutput(request, result)

@app.route(REST_API_PREFIX + 'entities/search.json', methods=['GET'])
@handleHTTPRequest
def searchEntities():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPEntitySearch(), request)
    query       = schema.exportSchema(EntitySearch())

    result      = stampedAPI.searchEntities(query.q, query.coordinates)
    autosuggest = []
    for item in result:
        item = item.exportSchema(HTTPEntityAutosuggest()).exportSparse()
        autosuggest.append(item)

    return transformOutput(request, autosuggest)

# ###### #
# Stamps #
# ###### #

@app.route(REST_API_PREFIX + 'stamps/create.json', methods=['POST'])
def addStamp():
    class RequestSchema(Schema):
        def setSchema(self):
            self.entity_id          = SchemaElement(basestring, required=True)
            self.blurb              = SchemaElement(basestring)
            self.image              = SchemaElement(basestring)
            self.credit             = SchemaList(SchemaElement(basestring), delimiter=',')
    return handleRequest(RequestSchema(), request, stampedAPI.addStamp)

@app.route(REST_API_PREFIX + 'stamps/update.json', methods=['POST'])
def updateStamp():
    class RequestSchema(Schema):
        def setSchema(self):
            self.stamp_id           = SchemaElement(basestring, required=True)
            self.blurb              = SchemaElement(basestring)
            self.image              = SchemaElement(basestring)
            self.credit             = SchemaList(SchemaElement(basestring), delimiter=',')
    return handleRequest(RequestSchema(), request, stampedAPI.updateStamp)

@app.route(REST_API_PREFIX + 'stamps/show.json', methods=['GET'])
def getStamp():
    class RequestSchema(Schema):
        def setSchema(self):
            self.stamp_id           = SchemaElement(basestring, required=True)
    return handleRequest(RequestSchema(), request, stampedAPI.getStamp)

@app.route(REST_API_PREFIX + 'stamps/remove.json', methods=['POST'])
def removeStamp():
    class RequestSchema(Schema):
        def setSchema(self):
            self.stamp_id           = SchemaElement(basestring, required=True)
    return handleRequest(RequestSchema(), request, stampedAPI.removeStamp)

# ######## #
# Comments #
# ######## #

@app.route(REST_API_PREFIX + 'comments/create.json', methods=['POST'])
def addComment():
    class RequestSchema(Schema):
        def setSchema(self):
            self.stamp_id           = SchemaElement(basestring, required=True)
            self.blurb              = SchemaElement(basestring, required=True)
    return handleRequest(RequestSchema(), request, stampedAPI.addComment)

@app.route(REST_API_PREFIX + 'comments/remove.json', methods=['POST'])
def removeComment():
    class RequestSchema(Schema):
        def setSchema(self):
            self.comment_id         = SchemaElement(basestring, required=True)
    return handleRequest(RequestSchema(), request, stampedAPI.removeComment)

@app.route(REST_API_PREFIX + 'comments/show.json', methods=['GET'])
def getComments():
    class RequestSchema(Schema):
        def setSchema(self):
            self.stamp_id           = SchemaElement(basestring, required=True)
            self.limit              = SchemaElement(int)
            self.since              = SchemaElement(int)
            self.before             = SchemaElement(int)
    return handleRequest(RequestSchema(), request, stampedAPI.getComments)

# ########### #
# Collections #
# ########### #

@app.route(REST_API_PREFIX + 'collections/inbox.json', methods=['GET'])
def getInboxStamps():
    class RequestSchema(Schema):
        def setSchema(self):
            self.limit              = SchemaElement(int)
            self.since              = SchemaElement(int)
            self.before             = SchemaElement(int)
            self.quality            = SchemaElement(int)
    return handleRequest(RequestSchema(), request, stampedAPI.getInboxStamps)

@app.route(REST_API_PREFIX + 'collections/user.json', methods=['GET'])
def getUserStamps():
    class RequestSchema(Schema):
        def setSchema(self):
            self.user_id            = SchemaElement(basestring)
            self.screen_name        = SchemaElement(basestring)
            self.limit              = SchemaElement(int)
            self.since              = SchemaElement(int)
            self.before             = SchemaElement(int)
            self.quality            = SchemaElement(int)
    return handleRequest(RequestSchema(), request, stampedAPI.getUserStamps)

@app.route(REST_API_PREFIX + 'getUserMentions', methods=['GET'])
def getUserMentions():
    return "Not Implemented", 404
    raise NotImplementedError

# ######## #
# Activity #
# ######## #

@app.route(REST_API_PREFIX + 'activity/show.json', methods=['GET'])
def getActivity():
    class RequestSchema(Schema):
        def setSchema(self):
            self.limit              = SchemaElement(int)
            self.since              = SchemaElement(int)
            self.before             = SchemaElement(int)
    return handleRequest(RequestSchema(), request, stampedAPI.getActivity)

# ######### #
# Favorites #
# ######### #

@app.route(REST_API_PREFIX + 'favorites/create.json', methods=['POST'])
def addFavorite():
    class RequestSchema(Schema):
        def setSchema(self):
            self.entity_id          = SchemaElement(basestring, required=True)
            self.stamp_id           = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, stampedAPI.addFavorite)

@app.route(REST_API_PREFIX + 'favorites/remove.json', methods=['POST'])
def removeFavorite():
    class RequestSchema(Schema):
        def setSchema(self):
            self.entity_id          = SchemaElement(basestring, required=True)
    return handleRequest(RequestSchema(), request, stampedAPI.removeFavorite)

@app.route(REST_API_PREFIX + 'favorites/show.json', methods=['GET'])
def getFavorites():
    class RequestSchema(Schema):
        def setSchema(self):
            self.limit              = SchemaElement(int)
            self.since              = SchemaElement(int)
            self.before             = SchemaElement(int)
    return handleRequest(RequestSchema(), request, stampedAPI.getFavorites)

# ############# #
# Miscellaneous #
# ############# #

@app.route('/')
def hello():
    return "This is where stamped.com will go -- huzzah!"
    
@app.route(REST_API_PREFIX)
def indexDoc():
    try:
        f = open(os.path.join(ROOT, 'api/docs/Index.html'))
        ret = f.read()
        f.close()
        return ret
    except Exception as e:
        msg = "Internal error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
        utils.log(msg)
        return msg, 500

@app.route(REST_API_PREFIX + 'stamps')
def stampsDoc():
    try:
        f = open(os.path.join(ROOT, 'api/docs/Stamps.html'))
        ret = f.read()
        f.close()
        return ret
    except Exception as e:
        msg = "Internal error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
        utils.log(msg)
        return msg, 500

@app.route(REST_API_PREFIX + 'accounts')
def accountsDoc():
    try:
        f = open(os.path.join(ROOT, 'api/docs/Accounts.html'))
        ret = f.read()
        f.close()
        return ret
    except Exception as e:
        msg = "Internal error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
        utils.log(msg)
        return msg, 500

@app.route(REST_API_PREFIX + 'users')
def usersDoc():
    try:
        f = open(os.path.join(ROOT, 'api/docs/Users.html'))
        ret = f.read()
        f.close()
        return ret
    except Exception as e:
        msg = "Internal error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
        utils.log(msg)
        return msg, 500

@app.route(REST_API_PREFIX + 'friendships')
def friendshipsDoc():
    try:
        f = open(os.path.join(ROOT, 'api/docs/Friendships.html'))
        ret = f.read()
        f.close()
        return ret
    except Exception as e:
        msg = "Internal error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
        utils.log(msg)
        return msg, 500

@app.route(REST_API_PREFIX + 'collections')
def collectionsDoc():
    try:
        f = open(os.path.join(ROOT, 'api/docs/Collections.html'))
        ret = f.read()
        f.close()
        return ret
    except Exception as e:
        msg = "Internal error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
        utils.log(msg)
        return msg, 500

@app.route(REST_API_PREFIX + 'entities')
def entitiesDoc():
    try:
        f = open(os.path.join(ROOT, 'api/docs/Entities.html'))
        ret = f.read()
        f.close()
        return ret
    except Exception as e:
        msg = "Internal error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
        utils.log(msg)
        return msg, 500

@app.route(REST_API_PREFIX + 'comments')
def commentsDoc():
    try:
        f = open(os.path.join(ROOT, 'api/docs/Comments.html'))
        ret = f.read()
        f.close()
        return ret
    except Exception as e:
        msg = "Internal error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
        utils.log(msg)
        return msg, 500

@app.route(REST_API_PREFIX + 'favorites')
def favoritesDoc():
    try:
        f = open(os.path.join(ROOT, 'api/docs/Favorites.html'))
        ret = f.read()
        f.close()
        return ret
    except Exception as e:
        msg = "Internal error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
        utils.log(msg)
        return msg, 500

@app.route(REST_API_PREFIX + 'activity')
def activityDoc():
    try:
        f = open(os.path.join(ROOT, 'api/docs/Activity.html'))
        ret = f.read()
        f.close()
        return ret
    except Exception as e:
        msg = "Internal error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
        utils.log(msg)
        return msg, 500

# ######## #
# Mainline #
# ######## #

if __name__ == '__main__':    
    app.run(host='0.0.0.0', debug=True, threaded=False)
    #app.run(host='0.0.0.0')

