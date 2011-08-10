#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import sys, thread, urllib, json

# import StampedAPI from StampedAPI

class apiOpener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('stampedtest', 'august1ftw')

def testGET(baseurl, path, data):
    params = urllib.urlencode(data)
#     print params
    result = json.load(apiOpener().open("%s/%s?%s" % (baseurl, path, params)))
    return result
    
def testPOST(baseurl, path, data):
    params = urllib.urlencode(data)
#     print params
    try:
        result = apiOpener().open("%s/%s" % (baseurl, path), params)
    except IOError as e:
        return e
    try:
        jsonResult = json.load(result)
        return jsonResult
    except:
        return "Unable to parse data into JSON"


def main():

    print    
    print '      BEGIN'
    
    baseurl = "http://0.0.0.0:5000/api/v1"
#     baseurl = "http://50.19.163.247:5000/api/v1"
#     
#     accountTest(baseurl)
#     
#     userTest(baseurl)
#     
#     entityTest(baseurl)
# 
    # stampTest(baseurl)

    # friendshipTest(baseurl)
 
    collectionTest(baseurl)

#     commentTest(baseurl)
# 
#     favoriteTest(baseurl)
# 
#     activityTest(baseurl)
 
    print '      COMPLETE'
    print 


# ######## #
# Accounts #
# ######## #

def accountTest(baseurl):

    print    
    print '      ACCOUNT'
    
    path = "account/create.json"
    data = {
        "first_name": "Kevin",
        "last_name": "Palms", 
        "email": "kevin@stamped.com", 
        "password": "******",
        "screen_name": "kpalms"
    }
    userID = testPOST(baseurl, path, data)['user_id']
    if len(userID) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print userID
        raise Exception
        
        
    path = "account/settings.json"
    data = {
        "authenticated_user_id": userID,
        "screen_name": "kevin",
        "privacy": False,
    }
    result = testPOST(baseurl, path, data)
    if result['privacy'] == False:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/settings.json"
    data = {
        "authenticated_user_id": userID
    }
    result = testGET(baseurl, path, data)
    if result['privacy'] == False:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/update_profile.json"
    data = {
        "authenticated_user_id": userID,
        "bio": "My long biography goes here.",
        "color": "333333,999999"
    }
    result = testPOST(baseurl, path, data)
    if result['color_primary'] == '333333':
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/update_profile_image.json"
    data = {
        "authenticated_user_id": userID,
        "profile_image": "https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg" ### TEMP!!!
    }
    result = testPOST(baseurl, path, data)
    if result['profile_image'] == 'https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg':
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/verify_credentials.json"
    data = {
        "authenticated_user_id": userID
    }
    result = testGET(baseurl, path, data)
    if result == True:
        print 'SKIP: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
            
    
    path = "account/reset_password.json"
    data = {
        "authenticated_user_id": userID
    }
    #result = testPOST(baseurl, path, data)
    print 'SKIP: %s' % path
        
        
    path = "account/remove.json"
    data = {"authenticated_user_id": userID}
    result = testPOST(baseurl, path, data)
    if result:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception

    print
    
    
# ##### #
# Users #
# ##### #

def userTest(baseurl):

    print    
    print '      USER'
    
    path = "account/create.json"
    data = {
        "first_name": "User",
        "last_name": "A", 
        "email": "usera@stamped.com", 
        "password": "******",
        "screen_name": "UserA"
    }
    userA = testPOST(baseurl, path, data)['user_id']
    data = {
        "first_name": "User",
        "last_name": "B", 
        "email": "userb@stamped.com", 
        "password": "******",
        "screen_name": "UserB"
    }
    userB = testPOST(baseurl, path, data)['user_id']
    if len(userA) == 24 and len(userB) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print userID
        raise Exception
        
        
    path = "users/show.json"
    data = { "user_id": userA }
    user = testGET(baseurl, path, data)
    if user["screen_name"] == "UserA":
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print entity
        raise Exception
        
        
    path = "users/show.json"
    data = { "screen_name": "UserA" }
    user = testGET(baseurl, path, data)
    if user["user_id"] == userA:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print entity
        raise Exception
        
        
    path = "users/lookup.json"
    data = { "user_ids": "%s,%s" % (userA, userB) }
    users = testGET(baseurl, path, data)
    if len(users) == 2:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print users
        raise Exception
        
        
    path = "users/lookup.json"
    data = { "screen_names": "UserA,UserB" }
    users = testGET(baseurl, path, data)
    if len(users) >= 2:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print users
        raise Exception
        
        
    path = "users/search.json"
    data = { "q": "user" }
    users = testGET(baseurl, path, data)
    if len(users) >= 2:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print users
        raise Exception
        
        
    path = "users/privacy.json"
    data = { "user_id": userA }
    privacy = testGET(baseurl, path, data)
    if privacy == True:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print privacy
        raise Exception
        
        
    path = "users/privacy.json"
    data = { "screen_name": "UserA" }
    privacy = testGET(baseurl, path, data)
    if privacy == True:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print privacy
        raise Exception
        
        
    path = "account/remove.json"
    data = {"authenticated_user_id": userA}
    resultA = testPOST(baseurl, path, data)
    data = {"authenticated_user_id": userB}
    resultB = testPOST(baseurl, path, data)
    if resultA and resultB:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception

    print
    
    
# ######## #
# Entities #
# ######## #

def entityTest(baseurl):

    print    
    print '      ENTITY'
    
    
    path = "account/create.json"
    data = {
        "first_name": "Kevin",
        "last_name": "Palms", 
        "email": "kevin@stamped.com", 
        "password": "******",
        "screen_name": "kpalms"
    }
    userID = testPOST(baseurl, path, data)['user_id']
    if len(userID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print userID
        raise Exception
        
    
    path = "entities/create.json"
    data = {
        "authenticated_user_id": userID,
        "title": "Little Owl",
        "desc": "American food in the West Village", 
        "category": "food",
        "subcategory": "restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityID = testPOST(baseurl, path, data)['entity_id']
    if len(entityID) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print entityID
        raise Exception
        
        
    path = "entities/show.json"
    data = { "entity_id": entityID }
    entity = testGET(baseurl, path, data)
    if entity["desc"] == "American food in the West Village":
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print entity
        raise Exception
    
        
    path = "entities/update.json"
    data = {
        "authenticated_user_id": userID,
        "entity_id": entityID,
        "desc": "Gastropub in the West Village, NYC"
    }
    result = testPOST(baseurl, path, data)
    if result['desc'] == "Gastropub in the West Village, NYC":
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "entities/search.json"
    data = {
        "authenticated_user_id": userID,
        "q": "Litt"
    }
    entities = testGET(baseurl, path, data)
    if len(entities) > 0:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print entity
        raise Exception
        
        
    path = "entities/remove.json"
    data = {
        "authenticated_user_id": userID,
        "entity_id": entityID
    }
    result = testPOST(baseurl, path, data)
    if result:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/remove.json"
    data = { "authenticated_user_id": userID }
    result = testPOST(baseurl, path, data)
    if result:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception


    print

    
    
# ###### #
# Stamps #
# ###### #

def stampTest(baseurl):

    print    
    print '      STAMP'
    
    path = "account/create.json"
    data = {
        "first_name": "User",
        "last_name": "A", 
        "email": "usera@stamped.com", 
        "password": "******",
        "screen_name": "UserA"
    }
    userA = testPOST(baseurl, path, data)['user_id']
    data = {
        "first_name": "User",
        "last_name": "B", 
        "email": "userb@stamped.com", 
        "password": "******",
        "screen_name": "UserB"
    }
    userB = testPOST(baseurl, path, data)['user_id']
    if len(userA) == 24 and len(userB) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print userID
        raise Exception
        
    
    path = "entities/create.json"
    data = {
        "authenticated_user_id": userA,
        "title": "Little Owl ",
        "desc": "American food in the West Village", 
        "category": "food",
        "subcategory": "restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityID = testPOST(baseurl, path, data)['entity_id']
    if len(entityID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print entityID
        raise Exception
        
    
    path = "stamps/create.json"
    data = {
        "authenticated_user_id": userA,
        "entity_id": entityID,
        "blurb": "Favorite restaurant in the Village.", 
        "image": "image.png"
    }
    stampID = testPOST(baseurl, path, data)['stamp_id']
    if len(stampID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print stampID
        raise Exception
        
    
    path = "stamps/create.json"
    data = {
        "authenticated_user_id": userB,
        "entity_id": entityID,
        "blurb": "Favorite restaurant in the Village. Thanks, @UserA.", 
        "image": "image.png",
        "credit": "UserA"
    }
    restampID = testPOST(baseurl, path, data)['stamp_id']
    if len(restampID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print stampID
        raise Exception
                
    
    path = "stamps/update.json"
    data = {
        "authenticated_user_id": userA,
        "stamp_id": stampID,
        "image": "image2.png"
    }
    result = testPOST(baseurl, path, data)
    if result['stamp_id'] == stampID:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
    
    path = "stamps/show.json"
    data = {
        "authenticated_user_id": userA,
        "stamp_id": stampID
    }
    result = testGET(baseurl, path, data)
    if result['image'] == 'image2.png':
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
    
    path = "stamps/remove.json"
    data = {
        "authenticated_user_id": userA,
        "stamp_id": restampID
    }
    result = testPOST(baseurl, path, data)
    if result == True:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
    
    path = "stamps/remove.json"
    data = {
        "authenticated_user_id": userA,
        "stamp_id": stampID
    }
    result = testPOST(baseurl, path, data)
    if result == True:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
        
    path = "entities/remove.json"
    data = {
        "authenticated_user_id": userA,
        "entity_id": entityID
    }
    result = testPOST(baseurl, path, data)
    if result:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/remove.json"
    data = {"authenticated_user_id": userA}
    resultA = testPOST(baseurl, path, data)
    data = {"authenticated_user_id": userB}
    resultB = testPOST(baseurl, path, data)
    if resultA and resultB:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    print
    
    
    
# ########### #
# Friendships #
# ########### #

def friendshipTest(baseurl):

    print    
    print '      FRIENDSHIP'
    
    
    path = "account/create.json"
    data = {
        "first_name": "Kevin",
        "last_name": "Palms", 
        "email": "kevin@stamped.com", 
        "password": "******",
        "screen_name": "kpalms"
    }
    userA = testPOST(baseurl, path, data)['user_id']
    data = {
        "first_name": "Robby",
        "last_name": "Stein", 
        "email": "robby@stamped.com", 
        "password": "******",
        "screen_name": "rmstein"
    }
    userB = testPOST(baseurl, path, data)['user_id']
    if len(userA) == 24 and len(userB) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print userID
        raise Exception
        
        
    path = "account/settings.json"
    data = {
        "authenticated_user_id": userA,
        "privacy": False
    }
    result = testPOST(baseurl, path, data)
    data = {
        "authenticated_user_id": userB,
        "privacy": False
    }
    result = testPOST(baseurl, path, data)
    if result['privacy'] == False:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
    
    
    path = "friendships/create.json"
    data = {
        "authenticated_user_id": userA,
        "user_id": userB
    }
    result = testPOST(baseurl, path, data)    
    if result['user_id'] == userB:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
    
    path = "friendships/check.json"
    data = {
        "authenticated_user_id": userA,
        "user_id": userB
    }
    result = testGET(baseurl, path, data)
    if result == True:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "friendships/friends.json"
    data = {
        "authenticated_user_id": userA
    }
    result = testGET(baseurl, path, data)
    if len(result['user_ids']) == 1:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "friendships/followers.json"
    data = {
        "authenticated_user_id": userB
    }
    result = testGET(baseurl, path, data)
    if len(result['user_ids']) == 1:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "friendships/approve.json"
    data = {
        "authenticated_user_id": userA
    }
    print 'SKIP: %s' % path
        
        
    path = "friendships/pending.json"
    data = {
        "authenticated_user_id": userA,
        "user_id": userB
    }
    print 'SKIP: %s' % path
    
    
    path = "friendships/remove.json"
    data = {
        "authenticated_user_id": userA,
        "user_id": userB
    }
    result = testPOST(baseurl, path, data)
    if result == True:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
    
    
    path = "friendships/blocks/create.json"
    data = {
        "authenticated_user_id": userA,
        "user_id": userB
    }
    result = testPOST(baseurl, path, data)    
    if result['user_id'] == userB:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
    
    path = "friendships/blocks/check.json"
    data = {
        "authenticated_user_id": userA,
        "user_id": userB
    }
    result = testGET(baseurl, path, data)
    if result == True:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "friendships/blocking.json"
    data = {
        "authenticated_user_id": userA
    }
    result = testGET(baseurl, path, data)
    if len(result['user_ids']) == 1:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
    
    
    path = "friendships/blocks/remove.json"
    data = {
        "authenticated_user_id": userA,
        "user_id": userB
    }
    result = testPOST(baseurl, path, data)
    if result == True:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/remove.json"
    data = { "authenticated_user_id": userA }
    resultA = testPOST(baseurl, path, data)
    data = { "authenticated_user_id": userB }
    resultB = testPOST(baseurl, path, data)
    if resultA and resultB:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        

    print

    
    
# ########### #
# Collections #
# ########### #

def collectionTest(baseurl):

    print    
    print '      COLLECTION'
    
    
    path = "account/create.json"
    data = {
        "client_id": "stampedtest",
        "client_secret": "august1ftw",
        "first_name": "Kevin",
        "last_name": "Palms", 
        "email": "kevin@stamped.com", 
        "password": "12345",
        "screen_name": "kpalms"
    }
    result = testPOST(baseurl, path, data)
    userA = result['user']['user_id']
    tokenA = result['token']
    data = {
        "client_id": "stampedtest",
        "client_secret": "august1ftw",
        "first_name": "Robby",
        "last_name": "Stein", 
        "email": "robby@stamped.com", 
        "password": "12345",
        "screen_name": "rmstein"
    }
    result = testPOST(baseurl, path, data)
    userB = result['user']['user_id']
    tokenB = result['token']
    if len(userA) == 24 and len(userB) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print userID
        raise Exception

    
    path = "oauth2/login.json"
    data = {
        "client_id": "stampedtest",
        "client_secret": "august1ftw",
        "screen_name": "kpalms",
        "password": "12345"
    }
    tokenA = testPOST(baseurl, path, data)
    if len(tokenA['access_token']) == 22:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print tokenA
        raise Exception
    

    path = "oauth2/login.json"
    data = {
        "client_id": "stampedtest",
        "client_secret": "august1ftw",
        "screen_name": "rmstein",
        "password": "123456789"
    }
    result = testPOST(baseurl, path, data)
    if result[1] == 401:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
    
    
    path = "oauth2/token.json"
    data = {
        "client_id": "stampedtest",
        "client_secret": "august1ftw",
        "refresh_token": tokenB['refresh_token'],
        "grant_type": "refresh_token"
    }
    tokenB = testPOST(baseurl, path, data)
    if len(tokenB['access_token']) == 22:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print tokenA
        raise Exception
        
        
    path = "account/settings.json"
    data = {
        "oauth_token": tokenA['access_token'],
        "privacy": False
    }
    result = testPOST(baseurl, path, data)
    data = {
        "oauth_token": tokenB['access_token'],
        "privacy": False
    }
    result = testPOST(baseurl, path, data)
    if result['privacy'] == False:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/update_profile.json"
    data = {
        "oauth_token": tokenA['access_token'],
        "bio": "My long biography goes here.",
        "color": "333333,999999"
    }
    result = testPOST(baseurl, path, data)
    data = {
        "oauth_token": tokenB['access_token'],
        "bio": "My long biography goes here.",
        "color": "222222,dd00dd"
    }
    result = testPOST(baseurl, path, data)
    if result['color_primary'] == '222222':
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/update_profile_image.json"
    data = {
        "oauth_token": tokenA['access_token'],
        "profile_image": "https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg" ### TEMP!!!
    }
    result = testPOST(baseurl, path, data)
    data = {
        "oauth_token": tokenB['access_token'],
        "profile_image": "https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg" ### TEMP!!!
    }
    result = testPOST(baseurl, path, data)
    if result['profile_image'] == 'https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg':
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
    
    
    path = "friendships/create.json"
    data = {
        "oauth_token": tokenB['access_token'],
        "user_id": userA
    }
    result = testPOST(baseurl, path, data)    
    if result['user_id'] == userA:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
    
    path = "entities/create.json"
    data = {
        "oauth_token": tokenA['access_token'],
        "title": "Little Owl",
        "desc": "American food in the West Village", 
        "category": "food",
        "subcategory": "restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityID = testPOST(baseurl, path, data)['entity_id']
    if len(entityID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print entityID
        raise Exception
        
    
    path = "entities/create.json"
    data = {
        "oauth_token": tokenA['access_token'],
        "title": "Recette",
        "desc": "Great food", 
        "category": "food",
        "subcategory": "restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityIDb = testPOST(baseurl, path, data)['entity_id']
    if len(entityIDb) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print entityID
        raise Exception
        
    
    path = "stamps/create.json"
    data = {
        "oauth_token": tokenA['access_token'],
        "entity_id": entityID,
        "blurb": "Favorite restaurant in the Village.", 
        "image": "image.png"
    }
    stampID = testPOST(baseurl, path, data)['stamp_id']
    if len(stampID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print stampID
        raise Exception
        
        
    path = "stamps/create.json"
    data = {
        "oauth_token": tokenA['access_token'],
        "entity_id": entityIDb,
        "blurb": "Great date spot. Thanks @rmstein!", 
        "image": "image.png"
    }
    stampIDb = testPOST(baseurl, path, data)['stamp_id']
    if len(stampIDb) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print stampID
        raise Exception


    path = "collections/user.json"
    data = {
        "oauth_token": tokenA['access_token'],
        "user_id": userA
    }
    result = testGET(baseurl, path, data)
    if len(result) == 2:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception


    path = "collections/inbox.json"
    data = {
        "oauth_token": tokenB['access_token'],
    }
    result = testGET(baseurl, path, data)
    if len(result) == 2:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
    
    path = "stamps/remove.json"
    data = {
        "oauth_token": tokenA['access_token'],
        "stamp_id": stampID
    }
    result = testPOST(baseurl, path, data)
    if result == True:
        print 'DATA: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
    
    path = "stamps/remove.json"
    data = {
        "oauth_token": tokenA['access_token'],
        "stamp_id": stampIDb
    }
    result = testPOST(baseurl, path, data)
    if result == True:
        print 'DATA: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
        
    path = "entities/remove.json"
    data = {
        "oauth_token": tokenA['access_token'],
        "entity_id": entityID
    }
    result = testPOST(baseurl, path, data)
    if result:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "entities/remove.json"
    data = {
        "oauth_token": tokenA['access_token'],
        "entity_id": entityIDb
    }
    result = testPOST(baseurl, path, data)
    if result:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
    
    
    path = "friendships/remove.json"
    data = {
        "oauth_token": tokenB['access_token'],
        "user_id": userA
    }
    result = testPOST(baseurl, path, data)
    if result == True:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/remove.json"
    data = { "oauth_token": tokenA['access_token'] }
    resultA = testPOST(baseurl, path, data)
    data = { "oauth_token": tokenB['access_token'] }
    resultB = testPOST(baseurl, path, data)
    if resultA and resultB:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    print

    
    
# ######## #
# Comments #
# ######## #

def commentTest(baseurl):

    print    
    print '      COMMENT'
    
    
    path = "account/create.json"
    data = {
        "first_name": "Kevin",
        "last_name": "Palms", 
        "email": "kevin@stamped.com", 
        "password": "******",
        "screen_name": "kpalms"
    }
    userID = testPOST(baseurl, path, data)['user_id']
    if len(userID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print userID
        raise Exception
        
    
    path = "entities/create.json"
    data = {
        "authenticated_user_id": userID,
        "title": "Little Owl",
        "desc": "American food in the West Village", 
        "category": "food",
        "subcategory": "restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityID = testPOST(baseurl, path, data)['entity_id']
    if len(entityID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print entityID
        raise Exception
        
    
    path = "stamps/create.json"
    data = {
        "authenticated_user_id": userID,
        "entity_id": entityID,
        "blurb": "Favorite restaurant in the Village.", 
        "image": "image.png"
    }
    stampID = testPOST(baseurl, path, data)['stamp_id']
    if len(stampID) == 24:
        print 'DATA: %s' % path
    else:
        print 'result: %s' % path
        print stampID
        raise Exception
                
    
    path = "comments/create.json"
    data = {
        "authenticated_user_id": userID,
        "stamp_id": stampID,
        "blurb": "That looks awesome. Well done, @kpalms.."
    }
    commentID = testPOST(baseurl, path, data)['comment_id']
    if len(commentID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
    
    path = "comments/show.json"
    data = {
        "stamp_id": stampID,
        "authenticated_user_id": userID
    }
    result = testGET(baseurl, path, data)
    if len(result) == 1:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
    
    path = "comments/remove.json"
    data = {
        "comment_id": commentID,
        "authenticated_user_id": userID
    }
    result = testPOST(baseurl, path, data)
    if result == True:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
    
    path = "stamps/remove.json"
    data = {
        "authenticated_user_id": userID,
        "stamp_id": stampID
    }
    result = testPOST(baseurl, path, data)
    if result == True:
        print 'DATA: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
        
    path = "entities/remove.json"
    data = {
        "authenticated_user_id": userID,
        "entity_id": entityID
    }
    result = testPOST(baseurl, path, data)
    if result:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/remove.json"
    data = { "authenticated_user_id": userID }
    result = testPOST(baseurl, path, data)
    if result:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    print

    
    
# ######### #
# Favorites #
# ######### #

def favoriteTest(baseurl):

    print    
    print '      FAVORITE'
    
    
    path = "account/create.json"
    data = {
        "first_name": "Kevin",
        "last_name": "Palms", 
        "email": "kevin@stamped.com", 
        "password": "******",
        "screen_name": "kpalms"
    }
    userID = testPOST(baseurl, path, data)['user_id']
    if len(userID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print userID
        raise Exception
        
    
    path = "entities/create.json"
    data = {
        "authenticated_user_id": userID,
        "title": "Little Owl",
        "desc": "American food in the West Village", 
        "category": "food",
        "subcategory": "restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityID = testPOST(baseurl, path, data)['entity_id']
    if len(entityID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print entityID
        raise Exception
        
    
    path = "stamps/create.json"
    data = {
        "authenticated_user_id": userID,
        "entity_id": entityID,
        "blurb": "Favorite restaurant in the Village.", 
        "image": "image.png"
    }
    stampID = testPOST(baseurl, path, data)['stamp_id']
    if len(stampID) == 24:
        print 'DATA: %s' % path
    else:
        print 'result: %s' % path
        print stampID
        raise Exception
                
    
    path = "favorites/create.json"
    data = {
        "authenticated_user_id": userID,
        "entity_id": entityID,
        "stamp_id": stampID
    }
    favoriteID = testPOST(baseurl, path, data)['favorite_id']
    if len(favoriteID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
    
    path = "favorites/show.json"
    data = {
        "authenticated_user_id": userID
    }
    result = testGET(baseurl, path, data)
    if result[-1]['complete'] == False:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
    
    path = "favorites/remove.json"
    data = {
        "authenticated_user_id": userID,
        "favorite_id": favoriteID
    }
    result = testPOST(baseurl, path, data)
    if result == True:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
    
    path = "stamps/remove.json"
    data = {
        "authenticated_user_id": userID,
        "stamp_id": stampID
    }
    result = testPOST(baseurl, path, data)
    if result == True:
        print 'DATA: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
        
    path = "entities/remove.json"
    data = {
        "authenticated_user_id": userID,
        "entity_id": entityID
    }
    result = testPOST(baseurl, path, data)
    if result:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/remove.json"
    data = { "authenticated_user_id": userID }
    result = testPOST(baseurl, path, data)
    if result:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    print

    
    
# ######## #
# Activity #
# ######## #

def activityTest(baseurl):

    print    
    print '      ACTIVITY'
    
    
    path = "account/create.json"
    data = {
        "first_name": "Kevin",
        "last_name": "Palms", 
        "email": "kevin@stamped.com", 
        "password": "******",
        "screen_name": "kpalms"
    }
    userA = testPOST(baseurl, path, data)['user_id']
    data = {
        "first_name": "Robby",
        "last_name": "Stein", 
        "email": "robby@stamped.com", 
        "password": "******",
        "screen_name": "rmstein"
    }
    userB = testPOST(baseurl, path, data)['user_id']
    if len(userA) == 24 and len(userB) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print userID
        raise Exception
        
        
    path = "account/settings.json"
    data = {
        "authenticated_user_id": userA,
        "privacy": False
    }
    result = testPOST(baseurl, path, data)
    data = {
        "authenticated_user_id": userB,
        "privacy": False
    }
    result = testPOST(baseurl, path, data)
    if result['privacy'] == False:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/update_profile.json"
    data = {
        "authenticated_user_id": userA,
        "bio": "My long biography goes here.",
        "color": "333333,999999"
    }
    result = testPOST(baseurl, path, data)
    data = {
        "authenticated_user_id": userB,
        "bio": "My long biography goes here.",
        "color": "333333,999999"
    }
    result = testPOST(baseurl, path, data)
    if result['color_primary'] == '333333':
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/update_profile_image.json"
    data = {
        "authenticated_user_id": userA,
        "profile_image": "https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg" ### TEMP!!!
    }
    result = testPOST(baseurl, path, data)
    data = {
        "authenticated_user_id": userB,
        "profile_image": "https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg" ### TEMP!!!
    }
    result = testPOST(baseurl, path, data)
    if result['profile_image'] == 'https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg':
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
    
    
    path = "friendships/create.json"
    data = {
        "authenticated_user_id": userB,
        "user_id": userA
    }
    result = testPOST(baseurl, path, data)    
    if result['user_id'] == userA:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
    
    path = "entities/create.json"
    data = {
        "authenticated_user_id": userA,
        "title": "Little Owl",
        "desc": "American food in the West Village", 
        "category": "food",
        "subcategory": "restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityID = testPOST(baseurl, path, data)['entity_id']
    if len(entityID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print entityID
        raise Exception
        
    
    path = "entities/create.json"
    data = {
        "authenticated_user_id": userA,
        "title": "Recette",
        "desc": "Great food", 
        "category": "food",
        "subcategory": "restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityIDb = testPOST(baseurl, path, data)['entity_id']
    if len(entityIDb) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print entityID
        raise Exception
        
    
    path = "stamps/create.json"
    data = {
        "authenticated_user_id": userA,
        "entity_id": entityID,
        "blurb": "Favorite restaurant in the Village. (via @rmstein)", 
        "credit": "rmstein",
        "image": "image.png"
    }
    stampID = testPOST(baseurl, path, data)['stamp_id']
    if len(stampID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print stampID
        raise Exception
                
    
    path = "comments/create.json"
    data = {
        "authenticated_user_id": userA,
        "stamp_id": stampID,
        "blurb": "This was awesome. Thanks again, @rmstein.."
    }
    commentID = testPOST(baseurl, path, data)['comment_id']
    if len(commentID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
                
    
    path = "comments/create.json"
    data = {
        "authenticated_user_id": userB,
        "stamp_id": stampID,
        "blurb": "No problem. Next time get the burger."
    }
    commentID = testPOST(baseurl, path, data)['comment_id']
    if len(commentID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
                
    
    path = "comments/create.json"
    data = {
        "authenticated_user_id": userA,
        "stamp_id": stampID,
        "blurb": "Yeah? It's worth getting?"
    }
    commentID = testPOST(baseurl, path, data)['comment_id']
    if len(commentID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
                
    
    path = "comments/create.json"
    data = {
        "authenticated_user_id": userB,
        "stamp_id": stampID,
        "blurb": "Definitely. Go there now, @kpalms."
    }
    commentID = testPOST(baseurl, path, data)['comment_id']
    if len(commentID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
                
    
    path = "comments/create.json"
    data = {
        "authenticated_user_id": userA,
        "stamp_id": stampID,
        "blurb": "Ok will do."
    }
    commentID = testPOST(baseurl, path, data)['comment_id']
    if len(commentID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
                
    
    path = "favorites/create.json"
    data = {
        "authenticated_user_id": userB,
        "entity_id": entityID,
        "stamp_id": stampID
    }
    favoriteID = testPOST(baseurl, path, data)['favorite_id']
    if len(favoriteID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
    
        
        
#     path = "stamps/create.json"
#     data = {
#         "authenticated_user_id": userA,
#         "entity_id": entityIDb,
#         "blurb": "Great date spot. Thanks @rmstein!", 
#         "image": "image.png"
#     }
#     stampIDb = testPOST(baseurl, path, data)['stamp_id']
#     if len(stampIDb) == 24:
#         print 'DATA: %s' % path
#     else:
#         print 'FAIL: %s' % path
#         print stampID
#         raise Exception
        
        
        
        
        


    path = "activity/show.json"
    data = {
        "authenticated_user_id": userA
    }
    result = testGET(baseurl, path, data)
#     print result
    


    path = "activity/show.json"
    data = {
        "authenticated_user_id": userB
    }
    result = testGET(baseurl, path, data)
#     print result
    
    
    
    
    return
    
    
    
    
    
    
    
    
    
    if len(result) == 2:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception


    path = "collections/inbox.json"
    data = {
        "authenticated_user_id": userB
    }
    result = testGET(baseurl, path, data)
    if len(result) == 2:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
    
    path = "stamps/remove.json"
    data = {
        "authenticated_user_id": userA,
        "stamp_id": stampID
    }
    result = testPOST(baseurl, path, data)
    if result == True:
        print 'DATA: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
    
    path = "stamps/remove.json"
    data = {
        "authenticated_user_id": userA,
        "stamp_id": stampIDb
    }
    result = testPOST(baseurl, path, data)
    if result == True:
        print 'DATA: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
        
    path = "entities/remove.json"
    data = {
        "authenticated_user_id": userA,
        "entity_id": entityID
    }
    result = testPOST(baseurl, path, data)
    if result:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "entities/remove.json"
    data = {
        "authenticated_user_id": userA,
        "entity_id": entityIDb
    }
    result = testPOST(baseurl, path, data)
    if result:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
    
    
    path = "friendships/remove.json"
    data = {
        "authenticated_user_id": userB,
        "user_id": userA
    }
    result = testPOST(baseurl, path, data)
    if result == True:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/remove.json"
    data = { "authenticated_user_id": userA }
    resultA = testPOST(baseurl, path, data)
    data = { "authenticated_user_id": userB }
    resultB = testPOST(baseurl, path, data)
    if resultA and resultB:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    print
    

# where all the magic starts
if __name__ == '__main__':
    main()
