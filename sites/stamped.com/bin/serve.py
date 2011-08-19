#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import init
import os, flask, json, utils, random, time, hashlib, logs
from flask import request, render_template, Response, Flask
from functools import wraps

from api.MongoStampedAPI import MongoStampedAPI
from api.MongoStampedAuth import MongoStampedAuth
from utils import AttributeDict
from errors import *
from resource_argument import *

# ################ #
# Global Variables #
# ################ #

REST_API_VERSION = "v1"
REST_API_PREFIX  = "/api/%s/" % REST_API_VERSION
ROOT = os.path.dirname(os.path.abspath(__file__))
#utils.init_db_config("localhost:30000")

app = Flask(__name__)

stampedAPI  = MongoStampedAPI()
stampedAuth = MongoStampedAuth()

# ################# #
# Utility Functions #
# ################# #

def _generateLogId():
    m = hashlib.md5(str(time.time()))
    m.update(str(random.random()))
    return str(m.hexdigest())


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

def parseRequestForm(request, schema, requireOAuthToken=True, **kwargs):

    ### Parse Request
    if request.method == 'POST':
        unparsedInput = request.form
    elif request.method == 'GET': 
        unparsedInput = request.args
    else:
        logs.warning("End request: Invalid method")
        raise
        
    logs.debug("Request url: %s" % request.base_url)
    logs.debug("Request data: %s" % unparsedInput)

    if requireOAuthToken:
        schema["oauth_token"] = ResourceArgument(required=True, expectedType=basestring)
        logs.debug("Require OAuth Token")

    try:
        parsedInput = Resource.parse('N/A', schema, unparsedInput)
    except (InvalidArgument, Fail) as e:
        utils.log("API function failed to parse input '%s' against schema '%s'" % \
            (str(unparsedInput), str(schema)))
        utils.printException()
        raise

    logs.debug("Parsed request data: %s" % parsedInput)

    return parsedInput

def verifyClientCredentials(data):
    if not stampedAuth.verifyClientCredentials( \
        data.client_id, data.client_secret):
        logs.info("Invalid authorization: %s" % request)
        raise StampedHTTPError("Error", 401) 

    return True

def verifyBasicAuth(request, **kwargs):
    return True
    ##### REMOVE
    if 'Authorization' not in request.headers or not request.authorization:
        logs.info("Requires authorization")
        return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', 401,
            {'WWW-Authenticate': 'Basic realm="Stamped API"'}
        )
    if request.authorization.username != 'stampedtest' \
        or request.authorization.password != 'august1ftw':
        logs.info("End request: Invalid authorization: %s" % (request))
        return "Error", 401

    return True

def handleAddAccountRequest(data):
    ### Add Account
    try:
        account = stampedAPI.addAccount(data)
    except:
        logs.warning("Fail")
        raise

    logs.debug("Account added")
    
    ### Generate Refresh Token & Access Token
    token = stampedAuth.addRefreshToken({
        'client_id': data['client_id'],
        'authenticated_user_id': account['user_id']
    })

    logs.debug("Token created")

    ### Format Output
    result = {
        'user': account,
        'token': token
    }
    
    return result

def handleRequest(request, stampedAPIFunc, schema):
    try:
        logs.refresh()
        logs.info("Begin request")
        
        ### TEMP: Check Basic Auth
        valid = verifyBasicAuth(request)
        if valid != True:
            logs.info("End request: Fail")
            return valid

        ### Check if OAuth Token Required
        requireOAuthToken = True
        if stampedAPIFunc in [stampedAPI.addAccount, \
            stampedAuth.verifyUserCredentials, stampedAuth.verifyRefreshToken]:
            requireOAuthToken = False

        ### Parse Request
        try:
            parsedInput = parseRequestForm(request, schema, requireOAuthToken=requireOAuthToken)
        except (InvalidArgument, Fail) as e:
            msg = str(e)
            utils.log(msg)
            utils.printException()
            # return msg, 400
            raise StampedHTTPError("invalid_request", 400, e)

        ### EXCEPTION: No OAuth Token
        if requireOAuthToken == False:
            # Check for valid client credentials
            logs.debug("Does not require OAuth Token")
            stampedAuth.verifyClientCredentials(parsedInput)
        else:
            ### Require OAuth token to be included
            if 'oauth_token' not in parsedInput:
                msg = "Access token not included"
                logs.warning(msg)
                raise StampedHTTPError("invalid_request", 401, msg)

            ### Validate OAuth Access Token
            authenticated_user_id = stampedAuth.verifyAccessToken(parsedInput)
            if authenticated_user_id == None:
                msg = "Invalid access token"
                logs.warning(msg)
                raise StampedHTTPError("invalid_token", 401, msg)
            
            ### Convert OAuth Token to User ID
            parsedInput.pop('oauth_token')
            parsedInput['authenticated_user_id'] = authenticated_user_id

            logs.debug("Final data set: %s" % (parsedInput))

        ### Generate Result
        logs.info("Begin: %s" % stampedAPIFunc.__name__)
        if stampedAPIFunc == stampedAPI.addAccount:
            # Exception -- requires both StampedAuth and StampedAPI. We should
            # try to get rid of this.
            result = handleAddAccountRequest(parsedInput)
        else:
            result = stampedAPIFunc(parsedInput)
        
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

def handleRequestOld(request, stampedAPIFunc, schema):
    try:
        ### TEMP: Check Basic Auth
        valid = verifyBasicAuth(request)
        if valid != True:
            logs.info("End request: Fail")
            return valid
        
        requireOAuthToken = False
        
        ### Parse Request
        try:
            parsedInput = parseRequestForm(request, schema, requireOAuthToken=requireOAuthToken)
        except (InvalidArgument, Fail) as e:
            msg = str(e)
            utils.log(msg)
            utils.printException()
            # return msg, 400
            raise StampedHTTPError("invalid_request", 400, e)

        logs.debug("Final data set: %s" % parsedInput)

        ### Generate result
        result = stampedAPIFunc(parsedInput)
        
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

# ####### #
# OAuth 2 #
# ####### #

@app.route(REST_API_PREFIX + 'oauth2/token.json', methods=['POST'])
def refreshToken():
    schema = ResourceArgumentSchema([
        ("client_id",             ResourceArgument(required=True, expectedType=basestring)),
        ("client_secret",         ResourceArgument(required=True, expectedType=basestring)),
        ("refresh_token",         ResourceArgument(required=True, expectedType=basestring)),
        ("grant_type",            ResourceArgument(required=True, expectedType=basestring))
    ])
    return handleRequest(request, stampedAuth.verifyRefreshToken, schema)

@app.route(REST_API_PREFIX + 'oauth2/login.json', methods=['POST'])
def loginUser():
    schema = ResourceArgumentSchema([
        ("client_id",             ResourceArgument(required=True, expectedType=basestring)),
        ("client_secret",         ResourceArgument(required=True, expectedType=basestring)),
        ("screen_name",           ResourceArgument(required=True, expectedType=basestring)),
        ("password",              ResourceArgument(required=True, expectedType=basestring))
    ])
    return handleRequest(request, stampedAuth.verifyUserCredentials, schema)

# ######## #
# Accounts #
# ######## #

@app.route(REST_API_PREFIX + 'account/create.json', methods=['POST'])
def addAccount():
    schema = ResourceArgumentSchema([
        ("client_id",             ResourceArgument(required=True, expectedType=basestring)),
        ("client_secret",         ResourceArgument(required=True, expectedType=basestring)),
        ("first_name",            ResourceArgument(required=True, expectedType=basestring)), 
        ("last_name",             ResourceArgument(required=True, expectedType=basestring)), 
        ("email",                 ResourceArgument(required=True, expectedType=basestring)), 
        ("password",              ResourceArgument(required=True, expectedType=basestring)), 
        ("screen_name",           ResourceArgument(required=True, expectedType=basestring))
    ])
    
    return handleRequest(request, stampedAPI.addAccount, schema)

@app.route(REST_API_PREFIX + 'account/settings.json', methods=['POST', 'GET'])
def updateAccount():
    fn = None
    if request.method == 'POST':
        fn = stampedAPI.updateAccount
    elif request.method == 'GET':
        fn = stampedAPI.getAccount
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("email",                 ResourceArgument(expectedType=basestring)), 
        ("password",              ResourceArgument(expectedType=basestring)), 
        ("screen_name",           ResourceArgument(expectedType=basestring)), 
        ("privacy",               ResourceArgumentBoolean()), 
        ("language",              ResourceArgument(expectedType=basestring)), 
        ("time_zone",             ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, fn, schema)
    
@app.route(REST_API_PREFIX + 'account/update_profile.json', methods=['POST'])
def updateProfile():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("first_name",            ResourceArgument(expectedType=basestring)), 
        ("last_name",             ResourceArgument(expectedType=basestring)), 
        ("bio",                   ResourceArgument(expectedType=basestring)), 
        ("website",               ResourceArgument(expectedType=basestring)), 
        ("color",                 ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.updateProfile, schema)

@app.route(REST_API_PREFIX + 'account/update_profile_image.json', methods=['POST'])
def updateProfileImage():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("profile_image",         ResourceArgument(required=True, expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.updateProfileImage, schema)

@app.route(REST_API_PREFIX + 'account/verify_credentials.json', methods=['GET'])
def verifyAccountCredentials():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.verifyAccountCredentials, schema)

@app.route(REST_API_PREFIX + 'account/remove.json', methods=['POST'])
def removeAccount():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.removeAccount, schema)

@app.route(REST_API_PREFIX + 'account/reset_password.json', methods=['POST'])
def resetPassword():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.resetPassword, schema)

# ##### #
# Users #
# ##### #

@app.route(REST_API_PREFIX + 'users/show.json', methods=['GET'])
def getUser():
    schema = ResourceArgumentSchema([
        ("user_id",               ResourceArgument(expectedType=basestring)), 
        ("screen_name",           ResourceArgument(expectedType=basestring)), 
        #("authenticated_user_id", ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.getUser, schema)

@app.route(REST_API_PREFIX + 'users/lookup.json', methods=['GET'])
def getUsers():
    schema = ResourceArgumentSchema([
        ("user_ids",              ResourceArgument(expectedType=basestring)), 
        ("screen_names",          ResourceArgument(expectedType=basestring)), 
        #("authenticated_user_id", ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.getUsers, schema)

@app.route(REST_API_PREFIX + 'users/search.json', methods=['GET'])
def searchUsers():
    schema = ResourceArgumentSchema([
        ("q",                     ResourceArgument(required=True, expectedType=basestring)), 
        #("authenticated_user_id", ResourceArgument(expectedType=basestring)), 
        ("limit",                 ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.searchUsers, schema)

@app.route(REST_API_PREFIX + 'users/privacy.json', methods=['GET'])
def getPrivacy():
    schema = ResourceArgumentSchema([
        ("user_id",               ResourceArgument(expectedType=basestring)), 
        ("screen_name",           ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.getPrivacy, schema)    

# ########### #
# Friendships #
# ########### #

@app.route(REST_API_PREFIX + 'friendships/create.json', methods=['POST'])
def addFriendship():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("user_id",               ResourceArgument(expectedType=basestring)), 
        ("screen_name",           ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.addFriendship, schema)

@app.route(REST_API_PREFIX + 'friendships/remove.json', methods=['POST'])
def removeFriendship():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("user_id",               ResourceArgument(expectedType=basestring)), 
        ("screen_name",           ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.removeFriendship, schema)

@app.route(REST_API_PREFIX + 'approveFriendship', methods=['POST'])
def approveFriendship():
    schema = ResourceArgumentSchema([
        ("user_id",           ResourceArgument(required=True, expectedType=basestring)), 
        ("friend_id",         ResourceArgument(required=True, expectedType=basestring)), 
    ])
    return handleRequest(request, stampedAPI.approveFriendship, schema)

@app.route(REST_API_PREFIX + 'friendships/check.json', methods=['GET'])
def checkFriendship():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("user_id",               ResourceArgument(required=True, expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.checkFriendship, schema)

@app.route(REST_API_PREFIX + 'friendships/friends.json', methods=['GET'])
def getFriends():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.getFriends, schema)

@app.route(REST_API_PREFIX + 'friendships/followers.json', methods=['GET'])
def getFollowers():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.getFollowers, schema)

@app.route(REST_API_PREFIX + 'friendships/blocks/create.json', methods=['POST'])
def addBlock():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("user_id",               ResourceArgument(expectedType=basestring)), 
        ("screen_name",           ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.addBlock, schema)

@app.route(REST_API_PREFIX + 'friendships/blocks/check.json', methods=['GET'])
def checkBlock():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("user_id",               ResourceArgument(required=True, expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.checkBlock, schema)

@app.route(REST_API_PREFIX + 'friendships/blocking.json', methods=['GET'])
def getBlocks():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.getBlocks, schema)

@app.route(REST_API_PREFIX + 'friendships/blocks/remove.json', methods=['POST'])
def removeBlock():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("user_id",               ResourceArgument(expectedType=basestring)), 
        ("screen_name",           ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.removeBlock, schema)

# ######## #
# Entities #
# ######## #

@app.route(REST_API_PREFIX + 'entities/create.json', methods=['POST'])
def addEntity():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("title",                 ResourceArgument(required=True, expectedType=basestring)), 
        ("desc",                  ResourceArgument(required=True, expectedType=basestring)), 
        ("category",              ResourceArgument(required=True, expectedType=basestring)),
        ("subcategory",           ResourceArgument(required=True, expectedType=basestring)), 
        ("image",                 ResourceArgument(expectedType=basestring)), 
        ("address",               ResourceArgument(expectedType=basestring)), 
        ("coordinates",           ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.addEntity, schema)

@app.route(REST_API_PREFIX + 'entities/show.json', methods=['GET'])
def getEntity():
    schema = ResourceArgumentSchema([
        ("entity_id",             ResourceArgument(required=True, expectedType=basestring)),
        #("authenticated_user_id", ResourceArgument(expectedType=basestring)) 
    ])
    return handleRequest(request, stampedAPI.getEntity, schema)

@app.route(REST_API_PREFIX + 'entities/update.json', methods=['POST'])
def updateEntity():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("entity_id",             ResourceArgument(required=True, expectedType=basestring)), 
        ("title",                 ResourceArgument(expectedType=basestring)), 
        ("desc",                  ResourceArgument(expectedType=basestring)), 
        ("category",              ResourceArgument(expectedType=basestring)), 
        ("image",                 ResourceArgument(expectedType=basestring)), 
        ("address",               ResourceArgument(expectedType=basestring)), 
        ("coordinates",           ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.updateEntity, schema)

@app.route(REST_API_PREFIX + 'entities/remove.json', methods=['POST'])
def removeEntity():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("entity_id",             ResourceArgument(required=True, expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.removeEntity, schema)

@app.route(REST_API_PREFIX + 'entities/search.json', methods=['GET'])
def searchEntities():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)),
        ("q",                     ResourceArgument(required=True, expectedType=basestring)),
        ("coordinates",           ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.searchEntities, schema)

# ###### #
# Stamps #
# ###### #

@app.route(REST_API_PREFIX + 'stamps/create.json', methods=['POST'])
def addStamp():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("entity_id",             ResourceArgument(required=True, expectedType=basestring)), 
        ("blurb",                 ResourceArgument(expectedType=basestring)), 
        ("image",                 ResourceArgument(expectedType=basestring)), 
        ("credit",                ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.addStamp, schema)

@app.route(REST_API_PREFIX + 'stamps/update.json', methods=['POST'])
def updateStamp():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("stamp_id",              ResourceArgument(required=True, expectedType=basestring)), 
        ("blurb",                 ResourceArgument(expectedType=basestring)), 
        ("image",                 ResourceArgument(expectedType=basestring)), 
        ("credit",                ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.updateStamp, schema)

@app.route(REST_API_PREFIX + 'stamps/show.json', methods=['GET'])
def getStamp():
    schema = ResourceArgumentSchema([ 
        ("stamp_id",              ResourceArgument(required=True, expectedType=basestring)),
        #("authenticated_user_id", ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.getStamp, schema)

@app.route(REST_API_PREFIX + 'stamps/remove.json', methods=['POST'])
def removeStamp():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("stamp_id",              ResourceArgument(required=True, expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.removeStamp, schema)

# ######## #
# Comments #
# ######## #

@app.route(REST_API_PREFIX + 'comments/create.json', methods=['POST'])
def addComment():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("stamp_id",              ResourceArgument(required=True, expectedType=basestring)), 
        ("blurb",                 ResourceArgument(required=True, expectedType=basestring)), 
        ("mentions",              ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.addComment, schema)

@app.route(REST_API_PREFIX + 'comments/remove.json', methods=['POST'])
def removeComment():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("comment_id",            ResourceArgument(required=True, expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.removeComment, schema)

@app.route(REST_API_PREFIX + 'comments/show.json', methods=['GET'])
def getComments():
    schema = ResourceArgumentSchema([
        ("stamp_id",              ResourceArgument(required=True, expectedType=basestring)),
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)) 
    ])
    return handleRequest(request, stampedAPI.getComments, schema)

# ########### #
# Collections #
# ########### #

@app.route(REST_API_PREFIX + 'collections/inbox.json', methods=['GET'])
def getInboxStamps():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("limit",                 ResourceArgument(expectedType=basestring)), 
        ("since",                 ResourceArgument(expectedType=basestring)), 
        ("before",                ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.getInboxStamps, schema)

@app.route(REST_API_PREFIX + 'collections/user.json', methods=['GET'])
def getUserStamps():
    schema = ResourceArgumentSchema([
        ("user_id",               ResourceArgument(required=True, expectedType=basestring)), 
        #("authenticated_user_id", ResourceArgument(expectedType=basestring)), 
        ("limit",                 ResourceArgument(expectedType=basestring)), 
        ("since",                 ResourceArgument(expectedType=basestring)), 
        ("before",                ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.getUserStamps, schema)

@app.route(REST_API_PREFIX + 'getUserMentions', methods=['GET'])
def getUserMentions():
    ### TODO: Implement stampedAPI.getUserMentions
    schema = ResourceArgumentSchema([
        ("user_id",               ResourceArgument(required=True, expectedType=basestring)), 
        #("authenticated_user_id", ResourceArgument(expectedType=basestring)), 
        ("limit",                 ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.getUserMentions, schema)

# ######### #
# Favorites #
# ######### #

@app.route(REST_API_PREFIX + 'favorites/create.json', methods=['POST'])
def addFavorite():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("entity_id",             ResourceArgument(required=True, expectedType=basestring)), 
        ("stamp_id",              ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.addFavorite, schema)

@app.route(REST_API_PREFIX + 'favorites/remove.json', methods=['POST'])
def removeFavorite():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("favorite_id",           ResourceArgument(required=True, expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.removeFavorite, schema)

@app.route(REST_API_PREFIX + 'favorites/show.json', methods=['GET'])
def getFavorites():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.getFavorites, schema)

# ######## #
# Activity #
# ######## #

@app.route(REST_API_PREFIX + 'activity/show.json', methods=['GET'])
def getActivity():
    schema = ResourceArgumentSchema([
        #("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("limit",                 ResourceArgument(expectedType=basestring)), 
        ("since",                 ResourceArgument(expectedType=basestring)), 
        ("before",                ResourceArgument(expectedType=basestring))
    ])
    return handleRequest(request, stampedAPI.getActivity, schema)

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

@app.route(REST_API_PREFIX + 'stats')
def statsDoc():
    try:
        return render_template('api/docs/stats.html')
    except Exception as e:
        msg = "Internal error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
        utils.log(msg)
        return msg, 500

# ######## #
# Mainline #
# ######## #

if __name__ == '__main__':    
    app.run(host='0.0.0.0', threaded=False)

