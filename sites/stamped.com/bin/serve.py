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

def checkAuth(request, requireOAuthToken=True):

    if requireOAuthToken == True:
        ### Parse Request for Access Token
        try:
            oauth_token = request.values['oauth_token']
        except:
            msg = "Access token not included"
            logs.warning(msg)
            raise StampedHTTPError("invalid_request", 401, msg)
        
        ### Validate OAuth Access Token
        try:
            authenticated_user_id = stampedAuth.verifyAccessToken(oauth_token)
            if authenticated_user_id == None:
                raise
            return { 'user_id': authenticated_user_id }
        except StampedHTTPError:
            raise
        except Exception:
            msg = "Invalid access token"
            logs.warning(msg)
            raise StampedHTTPError("invalid_token", 401, msg)

    else:
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
                data.client_id, data.client_secret):
                raise
            return True
        except:
            msg = "Invalid client credentials"
            logs.warning(msg)
            raise StampedHTTPError("access_denied", 401, msg)

def parseRequest(schema, request):

    ### Parse Request
    try:
        data, auth = parseRequestForm(schema, request)
    except (InvalidArgument, Fail) as e:
        msg = str(e)
        logs.warning(msg)
        raise StampedHTTPError("invalid_request", 400, e)





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

# ######## #
# Accounts #
# ######## #

@app.route(REST_API_PREFIX + 'account/create.json', methods=['POST'])
def addAccount():
    class RequestSchema(Schema):
        def setSchema(self):
            self.first_name         = SchemaElement(basestring, required=True)
            self.last_name          = SchemaElement(basestring, required=True)
            self.email              = SchemaElement(basestring, required=True)
            self.password           = SchemaElement(basestring, required=True)
            self.screen_name        = SchemaElement(basestring, required=True)
    return handleRequest(RequestSchema(), request, stampedAPI.addAccount, requireOAuthToken=False)

@app.route(REST_API_PREFIX + 'account/settings.json', methods=['POST', 'GET'])
def updateAccount():
    fn = None
    if request.method == 'POST':
        fn = stampedAPI.updateAccount
    elif request.method == 'GET':
        fn = stampedAPI.getAccount

    class RequestSchema(Schema):
        def setSchema(self):
            self.email              = SchemaElement(basestring)
            self.password           = SchemaElement(basestring)
            self.screen_name        = SchemaElement(basestring)
            self.privacy            = SchemaElement(bool)
            self.language           = SchemaElement(basestring)
            self.time_zone          = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, fn)
    
@app.route(REST_API_PREFIX + 'account/update_profile.json', methods=['POST'])
def updateProfile():
    class RequestSchema(Schema):
        def setSchema(self):
            self.first_name         = SchemaElement(basestring)
            self.last_name          = SchemaElement(basestring)
            self.bio                = SchemaElement(basestring)
            self.website            = SchemaElement(basestring)
            self.color              = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, stampedAPI.updateProfile)

@app.route(REST_API_PREFIX + 'account/update_profile_image.json', methods=['POST'])
def updateProfileImage():
    class RequestSchema(Schema):
        def setSchema(self):
            self.profile_image      = SchemaElement(basestring, required=True)
    return handleRequest(RequestSchema(), request, stampedAPI.updateProfileImage)

@app.route(REST_API_PREFIX + 'account/verify_credentials.json', methods=['GET'])
def verifyAccountCredentials():
    ### TODO: Remove this function?
    return "Not Implemented", 404

@app.route(REST_API_PREFIX + 'account/remove.json', methods=['POST'])
def removeAccount():
    ### TODO: Can I pass "None" instead?
    class RequestSchema(Schema):
        def setSchema(self):
            pass
    return handleRequest(RequestSchema(), request, stampedAPI.removeAccount)

@app.route(REST_API_PREFIX + 'account/reset_password.json', methods=['POST'])
def resetPassword():
    ### TODO
    return "Not Implemented", 404

# ##### #
# Users #
# ##### #

@app.route(REST_API_PREFIX + 'users/show.json', methods=['GET'])
def getUser():
    class RequestSchema(Schema):
        def setSchema(self):
            self.user_id            = SchemaElement(basestring)
            self.screen_name        = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, stampedAPI.getUser)

@app.route(REST_API_PREFIX + 'users/lookup.json', methods=['GET'])
def getUsers():
    class RequestSchema(Schema):
        def setSchema(self):
            self.user_ids           = SchemaList(SchemaElement(basestring), delimiter=',')
            self.screen_names       = SchemaList(SchemaElement(basestring), delimiter=',')
    return handleRequest(RequestSchema(), request, stampedAPI.getUsers)

@app.route(REST_API_PREFIX + 'users/search.json', methods=['GET'])
def searchUsers():
    class RequestSchema(Schema):
        def setSchema(self):
            self.q                  = SchemaElement(basestring, required=True)
            self.limit              = SchemaElement(int)
    return handleRequest(RequestSchema(), request, stampedAPI.searchUsers)

@app.route(REST_API_PREFIX + 'users/privacy.json', methods=['GET'])
def getPrivacy():  
    class RequestSchema(Schema):
        def setSchema(self):
            self.user_id            = SchemaElement(basestring)
            self.screen_name        = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, stampedAPI.getPrivacy) 

# ########### #
# Friendships #
# ########### #

@app.route(REST_API_PREFIX + 'friendships/create.json', methods=['POST'])
def addFriendship():
    class RequestSchema(Schema):
        def setSchema(self):
            self.user_id            = SchemaElement(basestring)
            self.screen_name        = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, stampedAPI.addFriendship)

@app.route(REST_API_PREFIX + 'friendships/remove.json', methods=['POST'])
def removeFriendship():
    class RequestSchema(Schema):
        def setSchema(self):
            self.user_id            = SchemaElement(basestring)
            self.screen_name        = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, stampedAPI.removeFriendship)

@app.route(REST_API_PREFIX + 'approveFriendship', methods=['POST'])
def approveFriendship():
    class RequestSchema(Schema):
        def setSchema(self):
            self.user_id            = SchemaElement(basestring)
            self.screen_name        = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, stampedAPI.approveFriendship)

@app.route(REST_API_PREFIX + 'friendships/check.json', methods=['GET'])
def checkFriendship():
    class RequestSchema(Schema):
        def setSchema(self):
            self.user_id            = SchemaElement(basestring)
            self.screen_name        = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, stampedAPI.checkFriendship)

@app.route(REST_API_PREFIX + 'friendships/friends.json', methods=['GET'])
def getFriends():
    class RequestSchema(Schema):
        def setSchema(self):
            self.user_id            = SchemaElement(basestring)
            self.screen_name        = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, stampedAPI.getFriends)

@app.route(REST_API_PREFIX + 'friendships/followers.json', methods=['GET'])
def getFollowers():
    class RequestSchema(Schema):
        def setSchema(self):
            self.user_id            = SchemaElement(basestring)
            self.screen_name        = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, stampedAPI.getFollowers)

@app.route(REST_API_PREFIX + 'friendships/blocks/create.json', methods=['POST'])
def addBlock():
    class RequestSchema(Schema):
        def setSchema(self):
            self.user_id            = SchemaElement(basestring)
            self.screen_name        = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, stampedAPI.addBlock)

@app.route(REST_API_PREFIX + 'friendships/blocks/check.json', methods=['GET'])
def checkBlock():
    class RequestSchema(Schema):
        def setSchema(self):
            self.user_id            = SchemaElement(basestring)
            self.screen_name        = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, stampedAPI.checkBlock)

@app.route(REST_API_PREFIX + 'friendships/blocking.json', methods=['GET'])
def getBlocks():
    class RequestSchema(Schema):
        def setSchema(self):
            pass
    return handleRequest(RequestSchema(), request, stampedAPI.getBlocks)

@app.route(REST_API_PREFIX + 'friendships/blocks/remove.json', methods=['POST'])
def removeBlock():
    class RequestSchema(Schema):
        def setSchema(self):
            self.user_id            = SchemaElement(basestring)
            self.screen_name        = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, stampedAPI.removeBlock)

# ######## #
# Entities #
# ######## #

@app.route(REST_API_PREFIX + 'entities/create.json', methods=['POST'])
def addEntity():
    class RequestSchema(Schema):
        def setSchema(self):
            self.title              = SchemaElement(basestring, required=True)
            self.subtitle           = SchemaElement(basestring, required=True)
            self.category           = SchemaElement(basestring, required=True)
            self.subcategory        = SchemaElement(basestring, required=True)
            self.desc               = SchemaElement(basestring)
            self.address            = SchemaElement(basestring)
            self.coordinates        = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, stampedAPI.addFlatEntity)

@app.route(REST_API_PREFIX + 'entities/show.json', methods=['GET'])
def getEntity():
    class RequestSchema(Schema):
        def setSchema(self):
            self.entity_id          = SchemaElement(basestring, required=True)
    return handleRequest(RequestSchema(), request, stampedAPI.getEntity)

@app.route(REST_API_PREFIX + 'entities/update.json', methods=['POST'])
def updateEntity():
    class RequestSchema(Schema):
        def setSchema(self):
            self.entity_id          = SchemaElement(basestring, required=True)
            self.title              = SchemaElement(basestring)
            self.subtitle           = SchemaElement(basestring)
            self.category           = SchemaElement(basestring)
            self.subcategory        = SchemaElement(basestring)
            self.desc               = SchemaElement(basestring)
            self.address            = SchemaElement(basestring)
            self.coordinates        = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, stampedAPI.updateFlatEntity)

@app.route(REST_API_PREFIX + 'entities/remove.json', methods=['POST'])
def removeEntity():
    class RequestSchema(Schema):
        def setSchema(self):
            self.entity_id          = SchemaElement(basestring, required=True)
    return handleRequest(RequestSchema(), request, stampedAPI.removeEntity)

@app.route(REST_API_PREFIX + 'entities/search.json', methods=['GET'])
def searchEntities():
    class RequestSchema(Schema):
        def setSchema(self):
            self.q                  = SchemaElement(basestring, required=True)
            self.coordinates        = SchemaElement(basestring)
    return handleRequest(RequestSchema(), request, stampedAPI.searchEntities)

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

