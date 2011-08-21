#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import init
import os, flask, json, utils, random, time, hashlib, logs
from flask import request, render_template, Response, Flask
from functools import wraps
from Schemas import *
from HTTPSchemas import *

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
            return "Error", 500
    return handleHTTPRequest

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
        authenticated_user_id = stampedAuth.verifyAccessToken(oauth_token)
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

    except:
        msg = "Unable to parse form"
        logs.warning(msg)
        raise StampedHTTPError("bad_request", 400, e)

def encodeType(obj):
    if '_dict' in obj:
        return obj._dict
    else:
        return obj.__dict__

def transformOutput(request, d):
    output_json = json.dumps(d, sort_keys=True, \
        indent=None if request.is_xhr else 2, default=encodeType)
    output = Response(output_json, mimetype='application/json')
    logs.debug("Transform output: \"%s\"" % output_json)
    return output


"""
#######    #                        
#     #   # #   #    # ##### #    # 
#     #  #   #  #    #   #   #    # 
#     # #     # #    #   #   ###### 
#     # ####### #    #   #   #    # 
#     # #     # #    #   #   #    # 
####### #     #  ####    #   #    # 
"""

@app.route(REST_API_PREFIX + 'oauth2/token.json', methods=['POST'])
@handleHTTPRequest
def refreshToken():
    client_id   = checkClient(request)
    schema      = parseRequest(OAuthTokenRequest(), request)

    if str(schema.grant_type).lower() != 'refresh_token':
        msg = "Grant type incorrect"
        logs.warning(msg)
        raise StampedHTTPError("invalid_request", 400, msg)

    token       = stampedAuth.verifyRefreshToken(client_id, schema.refresh_token)
    
    return transformOutput(request, token)

@app.route(REST_API_PREFIX + 'oauth2/login.json', methods=['POST'])
@handleHTTPRequest
def loginUser():
    client_id   = checkClient(request)
    schema      = parseRequest(OAuthLogin(), request)

    token       = stampedAuth.verifyUserCredentials(client_id, \
                                                    schema.screen_name, \
                                                    schema.password)

    return transformOutput(request, token)


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

        ### TEMP: Generate list of changes. Need to do something better eventually..
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
    schema      = parseRequest(HTTPEntityNew(), request)
    entity      = schema.exportSchema(Entity())

    entity.sources.userGenerated.user_id = authUserId
    
    entity      = stampedAPI.addEntity(entity)
    entity      = HTTPEntity().importSchema(entity)

    return transformOutput(request, entity.exportSparse())

@app.route(REST_API_PREFIX + 'entities/show.json', methods=['GET'])
@handleHTTPRequest
def getEntity():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPEntityId(), request)
    entity      = stampedAPI.getEntity(schema.entity_id, authUserId)
    entity      = HTTPEntity().importSchema(entity)

    return transformOutput(request, entity.exportSparse())

@app.route(REST_API_PREFIX + 'entities/update.json', methods=['POST'])
@handleHTTPRequest
def updateEntity():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPEntityEdit(), request)

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
    
    entity      = stampedAPI.updateCustomEntity(authUserId, schema.entity_id, data)
    entity      = HTTPEntity().importSchema(entity)

    return transformOutput(request, entity.exportSparse())

@app.route(REST_API_PREFIX + 'entities/remove.json', methods=['POST'])
@handleHTTPRequest
def removeEntity():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPEntityId(), request)
    result      = stampedAPI.removeCustomEntity(authUserId, schema.entity_id)
    
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
        item = HTTPEntityAutosuggest().importSchema(item).exportSparse()
        autosuggest.append(item)

    return transformOutput(request, autosuggest)


"""
 #####                                    
#     # #####   ##   #    # #####   ####  
#         #    #  #  ##  ## #    # #      
 #####    #   #    # # ## # #    #  ####  
      #   #   ###### #    # #####       # 
#     #   #   #    # #    # #      #    # 
 #####    #   #    # #    # #       ####  
"""

@app.route(REST_API_PREFIX + 'stamps/create.json', methods=['POST'])
@handleHTTPRequest
def addStamp():
    authUserId  = checkOAuth(request)

    schema      = parseRequest(HTTPStampNew(), request)
    entityId    = schema.entity_id
    data        = schema.exportSparse()
    del(data['entity_id'])

    stamp       = stampedAPI.addStamp(authUserId, entityId, data)
    stamp       = HTTPStamp().importSchema(stamp)

    return transformOutput(request, stamp.exportSparse())

@app.route(REST_API_PREFIX + 'stamps/update.json', methods=['POST'])
@handleHTTPRequest
def updateStamp():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPStampEdit(), request)

    ### TEMP: Generate list of changes. Need to do something better eventually...
    data        = schema.exportSparse()
    del(data['stamp_id'])

    for k, v in data.iteritems():
        if v == '':
            data[k] = None
    
    stamp       = stampedAPI.updateStamp(authUserId, schema.stamp_id, data)
    stamp       = HTTPStamp().importSchema(stamp)

    return transformOutput(request, stamp.exportSparse())

@app.route(REST_API_PREFIX + 'stamps/show.json', methods=['GET'])
@handleHTTPRequest
def getStamp():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPStampId(), request)

    stamp       = stampedAPI.getStamp(schema.stamp_id, authUserId)
    stamp       = HTTPStamp().importSchema(stamp)
    
    return transformOutput(request, stamp.exportSparse())

@app.route(REST_API_PREFIX + 'stamps/remove.json', methods=['POST'])
@handleHTTPRequest
def removeStamp():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPStampId(), request)

    stamp       = stampedAPI.removeStamp(authUserId, schema.stamp_id)
    stamp       = HTTPStamp().importSchema(stamp)
    
    return transformOutput(request, stamp.exportSparse())


"""
 #####                                                  
#     #  ####  #    # #    # ###### #    # #####  ####  
#       #    # ##  ## ##  ## #      ##   #   #   #      
#       #    # # ## # # ## # #####  # #  #   #    ####  
#       #    # #    # #    # #      #  # #   #        # 
#     # #    # #    # #    # #      #   ##   #   #    # 
 #####   ####  #    # #    # ###### #    #   #    ####  
"""

@app.route(REST_API_PREFIX + 'comments/create.json', methods=['POST'])
@handleHTTPRequest
def addComment():
    authUserId  = checkOAuth(request)

    schema      = parseRequest(HTTPCommentNew(), request)
    stampId     = schema.stamp_id
    blurb       = schema.blurb

    comment     = stampedAPI.addComment(authUserId, stampId, blurb)
    comment     = HTTPComment().importSchema(comment)

    return transformOutput(request, comment.exportSparse())

@app.route(REST_API_PREFIX + 'comments/remove.json', methods=['POST'])
@handleHTTPRequest
def removeComment():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPCommentId(), request)

    comment     = stampedAPI.removeComment(authUserId, schema.comment_id)
    comment     = HTTPComment().importSchema(comment)
    
    return transformOutput(request, comment.exportSparse())

@app.route(REST_API_PREFIX + 'comments/show.json', methods=['GET'])
@handleHTTPRequest
def getComments():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPCommentSlice(), request)

    data        = schema.exportSparse()
    del(data['stamp_id'])

    comments    = stampedAPI.getComments(schema.stamp_id, authUserId, **data)

    result = []
    for comment in comments:
        result.append(HTTPComment().importSchema(comment).exportSparse())
    
    return transformOutput(request, result)


"""
 #####                                                                  
#     #  ####  #      #      ######  ####  ##### #  ####  #    #  ####  
#       #    # #      #      #      #    #   #   # #    # ##   # #      
#       #    # #      #      #####  #        #   # #    # # #  #  ####  
#       #    # #      #      #      #        #   # #    # #  # #      # 
#     # #    # #      #      #      #    #   #   # #    # #   ## #    # 
 #####   ####  ###### ###### ######  ####    #   #  ####  #    #  ####  
"""

@app.route(REST_API_PREFIX + 'collections/inbox.json', methods=['GET'])
@handleHTTPRequest
def getInboxStamps():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPGenericSlice(), request)

    data        = schema.exportSparse()
    stamps      = stampedAPI.getInboxStamps(authUserId, **data)

    result = []
    for stamp in stamps:
        result.append(HTTPStamp().importSchema(stamp).exportSparse())

    return transformOutput(request, result)

@app.route(REST_API_PREFIX + 'collections/user.json', methods=['GET'])
@handleHTTPRequest
def getUserStamps():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserCollectionSlice(), request)

    data        = schema.exportSparse()
    userRequest = {
                    'user_id':      data.pop('user_id', None),
                    'screen_name':  data.pop('screen_name', None)
                  }
    stamps      = stampedAPI.getUserStamps(userRequest, authUserId, **data)

    result = []
    for stamp in stamps:
        result.append(HTTPStamp().importSchema(stamp).exportSparse())

    return transformOutput(request, result)

@app.route(REST_API_PREFIX + 'getUserMentions', methods=['GET'])
@handleHTTPRequest
def getUserMentions():
    return "Not Implemented", 404
    raise NotImplementedError


"""
#######                             
#         ##   #    # ######  ####  
#        #  #  #    # #      #      
#####   #    # #    # #####   ####  
#       ###### #    # #           # 
#       #    #  #  #  #      #    # 
#       #    #   ##   ######  ####  
"""

@app.route(REST_API_PREFIX + 'favorites/create.json', methods=['POST'])
@handleHTTPRequest
def addFavorite():
    authUserId  = checkOAuth(request)

    schema      = parseRequest(HTTPFavoriteNew(), request)
    entityId    = schema.entity_id
    stampId     = schema.stamp_id

    favorite    = stampedAPI.addFavorite(authUserId, entityId, stampId)
    favorite    = HTTPFavorite().importSchema(favorite)

    return transformOutput(request, favorite.exportSparse())

@app.route(REST_API_PREFIX + 'favorites/remove.json', methods=['POST'])
@handleHTTPRequest
def removeFavorite():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPEntityId(), request)

    favorite    = stampedAPI.removeFavorite(authUserId, schema.entity_id)
    favorite    = HTTPFavorite().importSchema(favorite)

    return transformOutput(request, favorite.exportSparse())

@app.route(REST_API_PREFIX + 'favorites/show.json', methods=['GET'])
@handleHTTPRequest
def getFavorites():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPGenericSlice(), request)

    favorites   = stampedAPI.getFavorites(authUserId, **schema.exportSparse())

    result = []
    for favorite in favorites:
        result.append(HTTPFavorite().importSchema(favorite).exportSparse())
    
    return transformOutput(request, result)


### TODO: Get all favorite ids?


"""
   #                                        
  # #    ####  ##### # #    # # ##### #   # 
 #   #  #    #   #   # #    # #   #    # #  
#     # #        #   # #    # #   #     #   
####### #        #   # #    # #   #     #   
#     # #    #   #   #  #  #  #   #     #   
#     #  ####    #   #   ##   #   #     #   
"""

@app.route(REST_API_PREFIX + 'activity/show.json', methods=['GET'])
@handleHTTPRequest
def getActivity():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPGenericSlice(), request)

    activity    = stampedAPI.getActivity(authUserId, **schema.exportSparse())
    
    result = []
    for item in activity:
        result.append(HTTPActivity().importSchema(item).exportSparse())
    
    return transformOutput(request, result)


"""
#######                      
   #    ###### #    # #####  
   #    #      ##  ## #    # 
   #    #####  # ## # #    # 
   #    #      #    # #####  
   #    #      #    # #      
   #    ###### #    # #      
"""

@app.route(REST_API_PREFIX + 'temp/friends.json', methods=['GET'])
@handleHTTPRequest
def TEMPgetFriends():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    userIds     = stampedAPI.getFriends(schema)
    users       = stampedAPI.getUsers(userIds, None, authUserId)

    output = []
    for user in users:
        output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(request, output)

@app.route(REST_API_PREFIX + 'temp/followers.json', methods=['GET'])
@handleHTTPRequest
def TEMPgetFollowers():
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    userIds     = stampedAPI.getFollowers(schema)
    users       = stampedAPI.getUsers(userIds, None, authUserId)

    output = []
    for user in users:
        output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(request, output)


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
        msg = "Error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
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
        msg = "Error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
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
        msg = "Error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
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
        msg = "Error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
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
        msg = "Error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
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
        msg = "Error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
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
        msg = "Error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
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
        msg = "Error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
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
        msg = "Error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
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
        msg = "Error processing '%s' (%s)" % (utils.getFuncName(0), str(e))
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
    app.run(host='0.0.0.0', threaded=False, debug=True)

