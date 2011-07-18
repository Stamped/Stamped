#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import flask, json, utils
from flask import request, Flask

from api.MongoStampedAPI import MongoStampedAPI
from utils import AttributeDict
from errors import *
from resource import *

# ################ #
# Global Variables #
# ################ #

REST_API_VERSION = "v1"
REST_API_PREFIX  = "/api/%s/" % REST_API_VERSION

app = Flask(__name__)
stampedAPI = MongoStampedAPI() 

# ################# #
# Utility Functions #
# ################# #

def encodeType(obj):
    if '_dict' in obj:
        return obj._dict
    else:
        return obj.__dict__

def transformOutput(d):
    output = json.dumps(d, sort_keys=True, indent=2, default=encodeType)
    print 'Output: ', output
    return output

def parseRequestForm(schema, form):
    apiFuncName = utils.getFuncName(1)
    
    try:
        return Resource.parse(apiFuncName, schema, form)
    except (InvalidArgument, Fail) as e:
        utils.log("API function '%s' failed to parse input '%s' against schema '%s'" % \
            (apiFuncName, str(request.form), str(schema)))
        utils.printException()
        raise

def handlePOSTRequest(request, stampedAPIFunc, schema):
    try:
        parsedInput = parseRequestForm(schema, request.form)
    except (InvalidArgument, Fail) as e:
        return str(e), 400
        
    return transformOutput(stampedAPIFunc(parsedInput))

def handleGETRequest(request, stampedAPIFunc, args):
    funcArgs = [ ]
    
    if not isinstance(args, (tuple, list)):
        args = [ args ]
    
    for arg in args:
        try:
            funcArg = request.args[arg]
            funcArgs.append(funcArg)
            #vars()['arg%d' % index]
        except:
            print 'Mismatched Argument'
    #         except KeyError as e:
    #             return "Required argument '%s' to API function '%s' not found" % (arg, utils.getFuncName(1)), 400

    return transformOutput(stampedAPIFunc(*funcArgs))

# ######## #
# Accounts #
# ######## #

@app.route(REST_API_PREFIX + 'account/create.json', methods=['POST'])
def addAccount():
    schema = ResourceArgumentSchema([
        ("first_name",            ResourceArgument(required=True, expectedType=basestring)), 
        ("last_name",             ResourceArgument(required=True, expectedType=basestring)), 
        ("email",                 ResourceArgument(required=True, expectedType=basestring)), 
        ("password",              ResourceArgument(required=True, expectedType=basestring)), 
        ("screen_name",           ResourceArgument(required=True, expectedType=basestring))
    ])
    return handlePOSTRequest(request, stampedAPI.addAccount, schema)

@app.route(REST_API_PREFIX + 'account/settings.json', methods=['POST', 'GET'])
def updateAccount():
    if request.method == 'POST':
        schema = ResourceArgumentSchema([
            ("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
            ("email",                 ResourceArgument(expectedType=basestring)), 
            ("password",              ResourceArgument(expectedType=basestring)), 
            ("screen_name",           ResourceArgument(expectedType=basestring)), 
            ("privacy",               ResourceArgumentBoolean()), 
            ("language",              ResourceArgument(expectedType=basestring)), 
            ("time_zone",             ResourceArgument(expectedType=basestring))
        ])
        return handlePOSTRequest(request, stampedAPI.updateAccount, schema)
    elif request.method == 'GET':
        return handleGETRequest(request, stampedAPI.getAccount, [ 'authorized_user_id' ])
    else:
        return 'Error', 400

@app.route(REST_API_PREFIX + 'account/update_profile.json', methods=['POST'])
def updateProfile():
    schema = ResourceArgumentSchema([
        ("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("first_name",            ResourceArgument(expectedType=basestring)), 
        ("last_name",             ResourceArgument(expectedType=basestring)), 
        ("bio",                   ResourceArgument(expectedType=basestring)), 
        ("website",               ResourceArgument(expectedType=basestring)), 
        ("color",                 ResourceArgument(expectedType=basestring))
    ])
    return handlePOSTRequest(request, stampedAPI.updateProfile, schema)

@app.route(REST_API_PREFIX + 'account/update_profile_image.json', methods=['POST'])
def updateProfileImage():
    schema = ResourceArgumentSchema([
        ("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("image",                 ResourceArgument(required=True, expectedType=basestring))
    ])
    return handlePOSTRequest(request, stampedAPI.updateProfileImage, schema)

@app.route(REST_API_PREFIX + 'account/verify_credentials.json', methods=['GET'])
def verifyAccountCredentials():
    return handleGETRequest(request, stampedAPI.verifyAccountCredentials, [ 'authenticated_user_id' ])

@app.route(REST_API_PREFIX + 'account/remove.json', methods=['POST'])
def removeAccount():
    schema = ResourceArgumentSchema([
        ("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring))
    ])
    return handlePOSTRequest(request, stampedAPI.removeAccount, schema)

@app.route(REST_API_PREFIX + 'account/reset_password.json', methods=['POST'])
def resetPassword():
    schema = ResourceArgumentSchema([
        ("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring))
    ])
    return handlePOSTRequest(request, stampedAPI.resetPassword, schema)

# ##### #
# Users #
# ##### #

@app.route(REST_API_PREFIX + 'users/show.json', methods=['GET'])
def getUser():
    if request.args.get('user_id'):
        return handleGETRequest(request, stampedAPI.getUser, [ 'user_id' ])
    elif request.args.get('screen_name'):
        return handleGETRequest(request, stampedAPI.getUserByName, [ 'screen_name' ])
    else:
        return 'Error', 400

@app.route(REST_API_PREFIX + 'users/lookup.json', methods=['GET'])
def getUsers():
    if request.args.get('user_ids'):
        return handleGETRequest(request, stampedAPI.getUsers, [ 'user_ids' ])
    elif request.args.get('screen_names'):
        return handleGETRequest(request, stampedAPI.getUsersByName, [ 'screen_names' ])
    else:
        return 'Error', 400

@app.route(REST_API_PREFIX + 'users/search.json', methods=['GET'])
def searchUsers():
    return handleGETRequest(request, stampedAPI.searchUsers, [ 'q', 'limit' ])

@app.route(REST_API_PREFIX + 'users/privacy.json', methods=['GET'])
def getPrivacy():
    if request.args.get('user_id'):
        return handleGETRequest(request, stampedAPI.getPrivacy, [ 'user_id' ])
    elif request.args.get('screen_name'):
        return handleGETRequest(request, stampedAPI.getPrivacyByName, [ 'screen_name' ])
    else:
        return 'Error', 400
    
    

@app.route(REST_API_PREFIX + 'getUserByName', methods=['GET'])
def getUserByName():
    return handleGETRequest(request, stampedAPI.getUserByName, [ 'screen_name' ])

@app.route(REST_API_PREFIX + 'getUsersByName', methods=['GET'])
def getUsersByName():
    return handleGETRequest(request, stampedAPI.getUsersByName, [ 'screen_names' ])     

# ########### ##
# Friendships #
# ########### #

@app.route(REST_API_PREFIX + 'addFriendship', methods=['POST'])
def addFriendship():
    schema = ResourceArgumentSchema([
        ("user_id",           ResourceArgument(required=True, expectedType=basestring)), 
        ("friend_id",         ResourceArgument(required=True, expectedType=basestring)), 
    ])
    return handlePOSTRequest(request, stampedAPI.addFriendship, schema)

@app.route(REST_API_PREFIX + 'removeFriendship', methods=['POST'])
def removeFriendship():
    schema = ResourceArgumentSchema([
        ("user_id",           ResourceArgument(required=True, expectedType=basestring)), 
        ("friend_id",         ResourceArgument(required=True, expectedType=basestring)), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.removeFriendship, schema)

@app.route(REST_API_PREFIX + 'approveFriendship', methods=['POST'])
def approveFriendship():
    schema = ResourceArgumentSchema([
        ("user_id",           ResourceArgument(required=True, expectedType=basestring)), 
        ("friend_id",         ResourceArgument(required=True, expectedType=basestring)), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.approveFriendship, schema)

@app.route(REST_API_PREFIX + 'addBlock', methods=['POST'])
def addBlock():
    schema = ResourceArgumentSchema([
        ("user_id",           ResourceArgument(required=True, expectedType=basestring)), 
        ("friend_id",         ResourceArgument(required=True, expectedType=basestring)), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.addBlock, schema)

@app.route(REST_API_PREFIX + 'removeBlock', methods=['POST'])
def removeBlock():
    schema = ResourceArgumentSchema([
        ("user_id",           ResourceArgument(required=True, expectedType=basestring)), 
        ("friend_id",         ResourceArgument(required=True, expectedType=basestring)), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.removeBlock, schema)

@app.route(REST_API_PREFIX + 'checkFriendship', methods=['GET'])
def checkFriendship():
    return handleGETRequest(request, stampedAPI.checkFriendship, [ 'user_id', 'friend_id' ])

@app.route(REST_API_PREFIX + 'getFriends', methods=['GET'])
def getFriends():
    return handleGETRequest(request, stampedAPI.getFriends, [ 'user_id' ])

@app.route(REST_API_PREFIX + 'getFollowers', methods=['GET'])
def getFollowers():
    return handleGETRequest(request, stampedAPI.getFollowers, [ 'user_id' ])

@app.route(REST_API_PREFIX + 'checkBlock', methods=['GET'])
def checkBlock():
    return handleGETRequest(request, stampedAPI.checkBlock, [ 'user_id', 'friend_id' ])

@app.route(REST_API_PREFIX + 'getBlocks', methods=['GET'])
def getBlocks():
    return handleGETRequest(request, stampedAPI.getBlocks, [ 'user_id' ])

# ######### #
# Favorites #
# ######### #

@app.route(REST_API_PREFIX + 'addFavorite', methods=['POST'])
def addFavorite():
    schema = ResourceArgumentSchema([
        ("userID",            ResourceArgument(required=True, expectedType=basestring)), 
        ("entityID",          ResourceArgument(required=True, expectedType=basestring)), 
        ("stampID",           ResourceArgument(expectedType=basestring)), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.addFavorite, schema)

@app.route(REST_API_PREFIX + 'getFavorite', methods=['GET'])
def getFavorite():
    return handleGETRequest(request, stampedAPI.getFavorite, [ 'userID', 'favoriteID' ])

@app.route(REST_API_PREFIX + 'removeFavorite', methods=['GET'])
def removeFavorite():
    return handleGETRequest(request, stampedAPI.removeFavorite, [ 'userID', 'favoriteID' ])

@app.route(REST_API_PREFIX + 'getFavoriteIDs', methods=['GET'])
def getFavoriteIDs():
    return handleGETRequest(request, stampedAPI.getFavoriteIDs, [ 'userID' ])

@app.route(REST_API_PREFIX + 'getFavorites', methods=['GET'])
def getFavorites():
    return handleGETRequest(request, stampedAPI.getFavorites, [ 'userID' ])

@app.route(REST_API_PREFIX + 'getFavorites', methods=['GET'])
def getFavorites():
    return handleGETRequest(request, stampedAPI.getFavorites, [ 'userID' ])

# ######## #
# Entities #
# ######## #

@app.route(REST_API_PREFIX + 'entities/create.json', methods=['POST'])
def addEntity():
    schema = ResourceArgumentSchema([
        ("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("title",                 ResourceArgument(required=True, expectedType=basestring)), 
        ("desc",                  ResourceArgument(required=True, expectedType=basestring)), 
        ("category",              ResourceArgument(required=True, expectedType=basestring)), 
        ("image",                 ResourceArgument(expectedType=basestring)), 
        ("address",               ResourceArgument(expectedType=basestring)), 
        ("coordinates",           ResourceArgument(expectedType=basestring))
    ])
    
    return handlePOSTRequest(request, stampedAPI.addEntity, schema)

@app.route(REST_API_PREFIX + 'entities/show.json', methods=['GET'])
def getEntity():
    return handleGETRequest(request, stampedAPI.getEntity, [ 'entity_id' ])

@app.route(REST_API_PREFIX + 'entities/update.json', methods=['POST'])
def updateEntity():
    schema = ResourceArgumentSchema([
        ("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("entity_id",             ResourceArgument(required=True, expectedType=basestring)), 
        ("title",                 ResourceArgument(expectedType=basestring)), 
        ("desc",                  ResourceArgument(expectedType=basestring)), 
        ("category",              ResourceArgument(expectedType=basestring)), 
        ("image",                 ResourceArgument(expectedType=basestring)), 
        ("address",               ResourceArgument(expectedType=basestring)), 
        ("coordinates",           ResourceArgument(expectedType=basestring))
    ])
    
    return handlePOSTRequest(request, stampedAPI.updateEntity, schema)

@app.route(REST_API_PREFIX + 'entities/remove.json', methods=['POST'])
def removeEntity():
    schema = ResourceArgumentSchema([
        ("authenticated_user_id", ResourceArgument(required=True, expectedType=basestring)), 
        ("entity_id",             ResourceArgument(required=True, expectedType=basestring))
    ])
    
    return handlePOSTRequest(request, stampedAPI.removeEntity, schema)

@app.route(REST_API_PREFIX + 'entities/search.json', methods=['GET'])
def searchEntities():
    return handleGETRequest(request, stampedAPI.searchEntities, [ 'q', 'limit' ])    

# ###### #
# Stamps #
# ###### #

@app.route(REST_API_PREFIX + 'stamps/add.json', methods=['POST'])
def addStamp():
    # TODO: the arguments here need work
    schema = ResourceArgumentSchema([
        ("user_id",         ResourceArgument(required=True, expectedType=basestring)), 
        ("entity_id",       ResourceArgument(required=True, expectedType=basestring)), 
        ("blurb",           ResourceArgument(required=True, expectedType=basestring)), 
        ("img",             ResourceArgument(expectedType=basestring)), 
        ("mentions",        ResourceArgument(expectedType=basestring)), 
        ("credit",          ResourceArgument(expectedType=basestring)), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.addStamp, schema)

@app.route(REST_API_PREFIX + 'stamps/update.json', methods=['POST'])
def updateStamp():
    # TODO: the arguments here need work
    schema = ResourceArgumentSchema([
        ("stamp_id",        ResourceArgument(required=True, expectedType=basestring)), 
        ("blurb",           ResourceArgument(expectedType=basestring)), 
        ("img",             ResourceArgument(expectedType=basestring)), 
        ("mentions",        ResourceArgument(expectedType=basestring)), 
        ("credit",          ResourceArgument(expectedType=basestring)), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.updateStamp, schema)

@app.route(REST_API_PREFIX + 'stamps/remove.json', methods=['POST'])
def removeStamp():
    # TODO: the arguments here need work
    schema = ResourceArgumentSchema([
        ("stamp_id",        ResourceArgument(required=True, expectedType=basestring)),
        ("user_id",         ResourceArgument(required=True, expectedType=basestring))
    ])
    
    return handlePOSTRequest(request, stampedAPI.removeStamp, schema)

@app.route(REST_API_PREFIX + 'stamps/show/<stamp_id>.json', methods=['GET'])
def getStamp(stamp_id):
    return transformOutput(stampedAPI.getStamp(stamp_id))
#     return handleGETRequest(arguments, stampedAPI.getStamp, [ 'stamp_id' ])

@app.route(REST_API_PREFIX + 'getStamps', methods=['GET'])
def getStamps():
    return handleGETRequest(request, stampedAPI.getStamps, [ 'stamp_ids' ]) 

# ######## #
# Comments #
# ######## #

@app.route(REST_API_PREFIX + 'addComment', methods=['POST'])
def addComment():
    # TODO: the arguments here need work
    schema = ResourceArgumentSchema([
        ("stamp_id",        ResourceArgument(required=True, expectedType=basestring)), 
        ("user_id",         ResourceArgument(required=True, expectedType=basestring)), 
        ("blurb",           ResourceArgument(required=True, expectedType=basestring)), 
        ("mentions",        ResourceArgument(expectedType=basestring))
    ])
    
    return handlePOSTRequest(request, stampedAPI.addComment, schema)

@app.route(REST_API_PREFIX + 'removeComment', methods=['POST'])
def removeComment():
    # TODO: the arguments here need work
    schema = ResourceArgumentSchema([
        ("comment_id",      ResourceArgument(required=True, expectedType=basestring))
    ])
    
    return handlePOSTRequest(request, stampedAPI.removeComment, schema)

@app.route(REST_API_PREFIX + 'getComments', methods=['GET'])
def getComments():
    return handleGETRequest(request, stampedAPI.getComments, [ 'stamp_id' ])

# ########### #
# Collections #
# ########### #

@app.route(REST_API_PREFIX + 'getInboxStampIDs', methods=['GET'])
def getInboxStampIDs():
    return handleGETRequest(request, stampedAPI.getInboxStampIDs, [ 'user_id', 'limit' ])

@app.route(REST_API_PREFIX + 'collections/inbox.json', methods=['GET'])
def getInboxStamps():
    return handleGETRequest(request, stampedAPI.getInboxStamps, [ 'user_id', 'limit' ])

@app.route(REST_API_PREFIX + 'getUserStampIDs', methods=['GET'])
def getUserStampIDs():
    return handleGETRequest(request, stampedAPI.getUserStampIDs, [ 'user_id', 'limit' ])

@app.route(REST_API_PREFIX + 'collections/user.json', methods=['GET'])
def getUserStamps():
    return handleGETRequest(request, stampedAPI.getUserStamps, [ 'user_id', 'limit' ])

@app.route(REST_API_PREFIX + 'getUserMentions', methods=['GET'])
def getUserMentions():
    return handleGETRequest(request, stampedAPI.getUserMentions, [ 'user_id', 'limit' ])

# ############# #
# Miscellaneous #
# ############# #

@app.route('/')
def hello():
    return "This is where stamped.com will go -- huzzah!"

# ######## #
# Mainline #
# ######## #

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0') 

