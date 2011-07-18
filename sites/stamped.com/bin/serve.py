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
    print str(d)
    print repr(d)
    return json.dumps(d, sort_keys=True, indent=2, default=encodeType)

def parseRequestForm(schema, form):
    apiFuncName = utils.getFuncName(2)
    
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
            print 'False'
    #         except KeyError as e:
    #             return "Required argument '%s' to API function '%s' not found" % (arg, utils.getFuncName(1)), 400

    return transformOutput(stampedAPIFunc(*funcArgs))

# ######## #
# Accounts #
# ######## #

@app.route(REST_API_PREFIX + 'addAccount', methods=['POST'])
def addAccount():
    schema = ResourceArgumentSchema([
        ("first_name",        ResourceArgument(required=True, expectedType=basestring)), 
        ("last_name",         ResourceArgument(required=True, expectedType=basestring)), 
        ("username",          ResourceArgument(required=True, expectedType=basestring)), 
        ("email",             ResourceArgument(required=True, expectedType=basestring)), 
        ("password",          ResourceArgument(required=True, expectedType=basestring)), 
        ("locale",            ResourceArgument(required=True, expectedType=basestring)), 
        ("primary_color",     ResourceArgument(required=True, expectedType=basestring)), 
        ("secondary_color",   ResourceArgument(expectedType=basestring)), 
        ("img",               ResourceArgument(expectedType=basestring)), 
        ("website",           ResourceArgument(expectedType=basestring)), 
        ("bio",               ResourceArgument(expectedType=basestring)), 
        ("privacy",           ResourceArgumentBoolean(default=False)), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.addAccount, schema)

@app.route(REST_API_PREFIX + 'getAccount', methods=['GET'])
def getAccount():
    return handleGETRequest(request, stampedAPI.getAccount, [ 'account_id' ])

@app.route(REST_API_PREFIX + 'updateAccount', methods=['POST'])
def updateAccount():
    schema = ResourceArgumentSchema([
        ("account_id",        ResourceArgument(required=True, expectedType=basestring)), 
        ("first_name",        ResourceArgument(expectedType=basestring)), 
        ("last_name",         ResourceArgument(expectedType=basestring)), 
        ("username",          ResourceArgument(expectedType=basestring)), 
        ("email",             ResourceArgument(expectedType=basestring)), 
        ("password",          ResourceArgument(expectedType=basestring)), 
        ("locale",            ResourceArgument(expectedType=basestring)), 
        ("primary_color",     ResourceArgument(expectedType=basestring)), 
        ("secondary_color",   ResourceArgument(expectedType=basestring)), 
        ("img",               ResourceArgument(expectedType=basestring)), 
        ("website",           ResourceArgument(expectedType=basestring)), 
        ("bio",               ResourceArgument(expectedType=basestring)), 
        ("privacy",           ResourceArgumentBoolean()), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.updateAccount, schema)

@app.route(REST_API_PREFIX + 'removeAccount', methods=['POST'])
def removeAccount():
    schema = ResourceArgumentSchema([
        ("account_id",        ResourceArgument(required=True, expectedType=basestring)), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.removeAccount, schema)

@app.route(REST_API_PREFIX + 'flagAccount', methods=['GET'])
def flagAccount():
    return handleGETRequest(request, stampedAPI.flagAccount, [ 'account_id' ])

@app.route(REST_API_PREFIX + 'unflagAccount', methods=['GET'])
def unflagAccount():
    return handleGETRequest(request, stampedAPI.unflagAccount, [ 'account_id' ])

# ##### #
# Users #
# ##### #

@app.route(REST_API_PREFIX + 'getUser', methods=['GET'])
def getUser():
    return handleGETRequest(request, stampedAPI.getUser, [ 'user_id' ])

@app.route(REST_API_PREFIX + 'getUsers', methods=['GET'])
def getUsers():
    return handleGETRequest(request, stampedAPI.getUsers, [ 'user_ids' ])

@app.route(REST_API_PREFIX + 'getUserByName', methods=['GET'])
def getUserByName():
    return handleGETRequest(request, stampedAPI.getUserByName, [ 'username' ])

@app.route(REST_API_PREFIX + 'getUsersByName', methods=['GET'])
def getUsersByName():
    return handleGETRequest(request, stampedAPI.getUsersByName, [ 'usernames' ])

@app.route(REST_API_PREFIX + 'searchUsers', methods=['GET'])
def searchUsers():
    return handleGETRequest(request, stampedAPI.searchUsers, [ 'query', 'limit' ])

@app.route(REST_API_PREFIX + 'getPrivacy', methods=['GET'])
def getPrivacy():
    return handleGETRequest(request, stampedAPI.getPrivacy, [ 'user_id' ])        

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

@app.route(REST_API_PREFIX + 'addEntity', methods=['POST'])
def addEntity():
    schema = ResourceArgumentSchema([
        ("title",            ResourceArgument(required=True, expectedType=basestring)), 
        ("desc",             ResourceArgument(required=True, expectedType=basestring)), 
        ("category",         ResourceArgument(required=True, expectedType=basestring)), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.addEntity, schema)

@app.route(REST_API_PREFIX + 'getEntity', methods=['GET'])
def getEntity():
    return handleGETRequest(request, stampedAPI.getEntity, [ 'entity_id' ])

@app.route(REST_API_PREFIX + 'updateEntity', methods=['POST'])
def updateEntity():
    schema = ResourceArgumentSchema([
        ("entity_id",        ResourceArgument(required=True, expectedType=basestring)), 
        ("title",            ResourceArgument(expectedType=basestring)), 
        ("desc",             ResourceArgument(expectedType=basestring)), 
        ("category",         ResourceArgument(expectedType=basestring)), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.updateEntity, schema)

@app.route(REST_API_PREFIX + 'removeEntity', methods=['POST'])
def removeEntity():
    schema = ResourceArgumentSchema([
        ("entity_id",        ResourceArgument(required=True, expectedType=basestring)), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.removeEntity, schema)

@app.route(REST_API_PREFIX + 'searchEntities', methods=['GET'])
def searchEntities():
    return handleGETRequest(request, stampedAPI.searchEntities, [ 'query', 'limit' ])    

# ###### #
# Stamps #
# ###### #

@app.route(REST_API_PREFIX + 'addStamp', methods=['POST'])
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

@app.route(REST_API_PREFIX + 'updateStamp', methods=['POST'])
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

@app.route(REST_API_PREFIX + 'removeStamp', methods=['POST'])
def removeStamp():
    # TODO: the arguments here need work
    schema = ResourceArgumentSchema([
        ("stamp_id",        ResourceArgument(required=True, expectedType=basestring)),
        ("user_id",         ResourceArgument(required=True, expectedType=basestring))
    ])
    
    return handlePOSTRequest(request, stampedAPI.removeStamp, schema)

@app.route(REST_API_PREFIX + 'getStamp', methods=['GET'])
def getStamp():
    return handleGETRequest(request, stampedAPI.getStamp, [ 'stamp_id' ])

@app.route(REST_API_PREFIX + 'getStamps', methods=['GET'])
def getStamps():
    return handleGETRequest(request, stampedAPI.getStamps, [ 'stamp_ids' ])

# ########### #
# Collections #
# ########### #

@app.route(REST_API_PREFIX + 'getInboxStampIDs', methods=['GET'])
def getInboxStampIDs():
    return handleGETRequest(request, stampedAPI.getInboxStampIDs, [ 'user_id', 'limit' ])

@app.route(REST_API_PREFIX + 'getInboxStamps', methods=['GET'])
def getInboxStamps():
    return handleGETRequest(request, stampedAPI.getInboxStamps, [ 'user_id', 'limit' ])

@app.route(REST_API_PREFIX + 'getUserStampIDs', methods=['GET'])
def getUserStampIDs():
    return handleGETRequest(request, stampedAPI.getUserStampIDs, [ 'user_id', 'limit' ])

@app.route(REST_API_PREFIX + 'getUserStamps', methods=['GET'])
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
    #app.run(debug=True)
    app.run(host='0.0.0.0') 

