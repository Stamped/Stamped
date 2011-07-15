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

def transformOutput(d):
    return json.dumps(d, sort_keys=True, indent=2)

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
            #vars()['arg%d' % index]
        except KeyError as e:
            return "Required argument '%s' to API function '%s' not found" % (arg, utils.getFuncName(1)), 400
    
    return transformOutput(stampedAPIFunc(funcArgs))

# ######## #
# Accounts #
# ######## #

@app.route(REST_API_PREFIX + 'addAccount', methods=['POST'])
def addAccount():
    schema = ResourceArgumentSchema([
        ("firstName",         ResourceArgument(required=True, expectedType=basestring)), 
        ("lastName",          ResourceArgument(required=True, expectedType=basestring)), 
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
    return handleGETRequest(request, stampedAPI.getAccount, [ 'userID' ])

@app.route(REST_API_PREFIX + 'updateAccount', methods=['GET'])
def updateAccount():
    schema = ResourceArgumentSchema([
        ("accountID",         ResourceArgument(required=True, expectedType=basestring)), 
        ("firstName",         ResourceArgument(expectedType=basestring)), 
        ("lastName",          ResourceArgument(expectedType=basestring)), 
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

@app.route(REST_API_PREFIX + 'removeAccount', methods=['GET'])
def removeAccount():
    return handleGETRequest(request, stampedAPI.removeAccount, [ 'userID' ])

@app.route(REST_API_PREFIX + 'flagAccount', methods=['GET'])
def flagAccount():
    return handleGETRequest(request, stampedAPI.flagAccount, [ 'userID' ])

@app.route(REST_API_PREFIX + 'unflagAccount', methods=['GET'])
def unflagAccount():
    return handleGETRequest(request, stampedAPI.unflagAccount, [ 'userID' ])

# ##### #
# Users #
# ##### #

@app.route(REST_API_PREFIX + 'addFriendship', methods=['GET'])
def addFriendship():
    return handleGETRequest(request, stampedAPI.addFriendship, [ 'userID', 'friendID' ])

@app.route(REST_API_PREFIX + 'checkFriendship', methods=['GET'])
def checkFriendship():
    return handleGETRequest(request, stampedAPI.checkFriendship, [ 'userID', 'friendID' ])

@app.route(REST_API_PREFIX + 'removeFriendship', methods=['GET'])
def removeFriendship():
    return handleGETRequest(request, stampedAPI.removeFriendship, [ 'userID', 'friendID' ])

@app.route(REST_API_PREFIX + 'getFriends', methods=['GET'])
def getFriends():
    return handleGETRequest(request, stampedAPI.getFriends, [ 'userID' ])

@app.route(REST_API_PREFIX + 'getFollowers', methods=['GET'])
def getFollowers():
    return handleGETRequest(request, stampedAPI.getFollowers, [ 'userID' ])

@app.route(REST_API_PREFIX + 'approveFriendship', methods=['GET'])
def approveFriendship():
    return handleGETRequest(request, stampedAPI.approveFriendship, [ 'userID', 'friendID' ])

@app.route(REST_API_PREFIX + 'addBlock', methods=['GET'])
def addBlock():
    return handleGETRequest(request, stampedAPI.addBlock, [ 'userID', 'friendID' ])

@app.route(REST_API_PREFIX + 'checkBlock', methods=['GET'])
def checkBlock():
    return handleGETRequest(request, stampedAPI.checkBlock, [ 'userID', 'friendID' ])

@app.route(REST_API_PREFIX + 'removeBlock', methods=['GET'])
def removeBlock():
    return handleGETRequest(request, stampedAPI.removeBlock, [ 'userID', 'friendID' ])

@app.route(REST_API_PREFIX + 'getBlocks', methods=['GET'])
def getBlocks():
    return handleGETRequest(request, stampedAPI.getBlocks, [ 'userID' ])

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
        ("category",         ResourceArgumentList(expectedType=basestring)), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.addEntity, schema)

@app.route(REST_API_PREFIX + 'getEntity', methods=['GET'])
def getEntity():
    return handleGETRequest(request, stampedAPI.getEntity, [ 'entityID' ])

@app.route(REST_API_PREFIX + 'updateEntity', methods=['POST'])
def updateEntity():
    schema = ResourceArgumentSchema([
        ("entityID",         ResourceArgument(required=True, expectedType=basestring)), 
        ("title",            ResourceArgument(expectedType=basestring)), 
        ("desc",             ResourceArgument(expectedType=basestring)), 
        ("category",         ResourceArgumentList(expectedType=basestring)), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.updateEntity, schema)

@app.route(REST_API_PREFIX + 'removeEntity', methods=['GET'])
def removeEntity():
    return handleGETRequest(request, stampedAPI.removeEntity, [ 'entityID' ])

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
        ("userID",          ResourceArgument(required=True, expectedType=basestring)), 
        ("entityID",        ResourceArgument(required=True, expectedType=basestring)), 
        ("blurb",           ResourceArgument(required=True, expectedType=basestring)), 
        ("img",             ResourceArgumentList(expectedType=basestring)), 
        ("mentions",        ResourceArgumentList(expectedType=basestring)), 
        ("credit",          ResourceArgumentList(expectedType=basestring)), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.addStamp, schema)

@app.route(REST_API_PREFIX + 'getStamp', methods=['GET'])
def getStamp():
    return handleGETRequest(request, stampedAPI.getStamp, [ 'stampID' ])

@app.route(REST_API_PREFIX + 'getStamps', methods=['GET'])
def getStamps():
    return handleGETRequest(request, stampedAPI.getStamps, [ 'stampIDs' ])

@app.route(REST_API_PREFIX + 'updateStamp', methods=['POST'])
def updateStamp():
    # TODO: the arguments here need work
    schema = ResourceArgumentSchema([
        ("stampID",         ResourceArgument(required=True, expectedType=basestring)), 
        ("userID",          ResourceArgument(expectedType=basestring)), 
        ("entityID",        ResourceArgument(expectedType=basestring)), 
        ("blurb",           ResourceArgument(expectedType=basestring)), 
        ("img",             ResourceArgumentList(expectedType=basestring)), 
        ("mentions",        ResourceArgumentList(expectedType=basestring)), 
        ("credit",          ResourceArgumentList(expectedType=basestring)), 
    ])
    
    return handlePOSTRequest(request, stampedAPI.updateStamp, schema)

@app.route(REST_API_PREFIX + 'removeStamp', methods=['GET'])
def removeStamp():
    return handleGETRequest(request, stampedAPI.removeStamp, [ 'stampID' ])

# ########### #
# Collections #
# ########### #

@app.route(REST_API_PREFIX + 'getInboxStampIDs', methods=['GET'])
def getInboxStampIDs():
    return handleGETRequest(request, stampedAPI.getInboxStampIDs, [ 'userID', 'limit' ])

@app.route(REST_API_PREFIX + 'getInboxStamps', methods=['GET'])
def getInboxStamps():
    return handleGETRequest(request, stampedAPI.getInboxStamps, [ 'userID', 'limit' ])

@app.route(REST_API_PREFIX + 'getUserStampIDs', methods=['GET'])
def getUserStampIDs():
    return handleGETRequest(request, stampedAPI.getUserStampIDs, [ 'userID', 'limit' ])

@app.route(REST_API_PREFIX + 'getUserStamps', methods=['GET'])
def getUserStamps():
    return handleGETRequest(request, stampedAPI.getUserStamps, [ 'userID', 'limit' ])

@app.route(REST_API_PREFIX + 'getUserMentions', methods=['GET'])
def getUserMentions():
    return handleGETRequest(request, stampedAPI.getUserMentions, [ 'userID', 'limit' ])

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

