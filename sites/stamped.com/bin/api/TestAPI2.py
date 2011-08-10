#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import sys, thread, urllib, json

# import StampedAPI from StampedAPI

class StampedAPIURLOpener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('stampedtest', 'august1ftw')

def self.handleGET(path, data):
    params = urllib.urlencode(data)
#     print params
    result = json.load(StampedAPIURLOpener().open("%s/%s?%s" % (path, params)))
    return result
    
def self.handlePOST(path, data):
    params = urllib.urlencode(data)
#     print params
    result = StampedAPIURLOpener().open("%s/%s" % (path), params)
    jsonResult = json.load(result)
    return jsonResult


def main():

    print    
    print '      BEGIN'
    
    baseurl = "http://0.0.0.0:5000/api/v1"
#     baseurl = "http://50.19.163.247:5000/api/v1"
    
    accountTest(baseurl)
    
    userTest(baseurl)
    
    entityTest(baseurl)

    stampTest(baseurl)
    
    friendshipTest(baseurl)

    collectionTest(baseurl)

    commentTest(baseurl)

    favoriteTest(baseurl)

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
    userID = self.handlePOST(path, data)['user_id']
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
    result = self.handlePOST(path, data)
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
    result = self.handleGET(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handleGET(path, data)
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
    #result = self.handlePOST(path, data)
    print 'SKIP: %s' % path
        
        
    path = "account/remove.json"
    data = {"authenticated_user_id": userID}
    result = self.handlePOST(path, data)
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
    userA = self.handlePOST(path, data)['user_id']
    data = {
        "first_name": "User",
        "last_name": "B", 
        "email": "userb@stamped.com", 
        "password": "******",
        "screen_name": "UserB"
    }
    userB = self.handlePOST(path, data)['user_id']
    if len(userA) == 24 and len(userB) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print userID
        raise Exception
        
        
    path = "users/show.json"
    data = { "user_id": userA }
    user = self.handleGET(path, data)
    if user["screen_name"] == "UserA":
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print entity
        raise Exception
        
        
    path = "users/show.json"
    data = { "screen_name": "UserA" }
    user = self.handleGET(path, data)
    if user["user_id"] == userA:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print entity
        raise Exception
        
        
    path = "users/lookup.json"
    data = { "user_ids": "%s,%s" % (userA, userB) }
    users = self.handleGET(path, data)
    if len(users) == 2:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print users
        raise Exception
        
        
    path = "users/lookup.json"
    data = { "screen_names": "UserA,UserB" }
    users = self.handleGET(path, data)
    if len(users) >= 2:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print users
        raise Exception
        
        
    path = "users/search.json"
    data = { "q": "user" }
    users = self.handleGET(path, data)
    if len(users) >= 2:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print users
        raise Exception
        
        
    path = "users/privacy.json"
    data = { "user_id": userA }
    privacy = self.handleGET(path, data)
    if privacy == True:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print privacy
        raise Exception
        
        
    path = "users/privacy.json"
    data = { "screen_name": "UserA" }
    privacy = self.handleGET(path, data)
    if privacy == True:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print privacy
        raise Exception
        
        
    path = "account/remove.json"
    data = {"authenticated_user_id": userA}
    resultA = self.handlePOST(path, data)
    data = {"authenticated_user_id": userB}
    resultB = self.handlePOST(path, data)
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
    userID = self.handlePOST(path, data)['user_id']
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
        "category": "Restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityID = self.handlePOST(path, data)['entity_id']
    if len(entityID) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print entityID
        raise Exception
        
        
    path = "entities/show.json"
    data = { "entity_id": entityID }
    entity = self.handleGET(path, data)
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
    result = self.handlePOST(path, data)
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
    entities = self.handleGET(path, data)
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
    result = self.handlePOST(path, data)
    if result:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/remove.json"
    data = { "authenticated_user_id": userID }
    result = self.handlePOST(path, data)
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
    userA = self.handlePOST(path, data)['user_id']
    data = {
        "first_name": "User",
        "last_name": "B", 
        "email": "userb@stamped.com", 
        "password": "******",
        "screen_name": "UserB"
    }
    userB = self.handlePOST(path, data)['user_id']
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
        "category": "Restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityID = self.handlePOST(path, data)['entity_id']
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
    stampID = self.handlePOST(path, data)['stamp_id']
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
    restampID = self.handlePOST(path, data)['stamp_id']
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
    result = self.handlePOST(path, data)
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
    result = self.handleGET(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
    if result:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/remove.json"
    data = {"authenticated_user_id": userA}
    resultA = self.handlePOST(path, data)
    data = {"authenticated_user_id": userB}
    resultB = self.handlePOST(path, data)
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
    userA = self.handlePOST(path, data)['user_id']
    data = {
        "first_name": "Robby",
        "last_name": "Stein", 
        "email": "robby@stamped.com", 
        "password": "******",
        "screen_name": "rmstein"
    }
    userB = self.handlePOST(path, data)['user_id']
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
    result = self.handlePOST(path, data)
    data = {
        "authenticated_user_id": userB,
        "privacy": False
    }
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)    
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
    result = self.handleGET(path, data)
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
    result = self.handleGET(path, data)
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
    result = self.handleGET(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)    
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
    result = self.handleGET(path, data)
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
    result = self.handleGET(path, data)
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
    result = self.handlePOST(path, data)
    if result == True:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/remove.json"
    data = { "authenticated_user_id": userA }
    resultA = self.handlePOST(path, data)
    data = { "authenticated_user_id": userB }
    resultB = self.handlePOST(path, data)
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
        "first_name": "Kevin",
        "last_name": "Palms", 
        "email": "kevin@stamped.com", 
        "password": "******",
        "screen_name": "kpalms"
    }
    userA = self.handlePOST(path, data)['user_id']
    data = {
        "first_name": "Robby",
        "last_name": "Stein", 
        "email": "robby@stamped.com", 
        "password": "******",
        "screen_name": "rmstein"
    }
    userB = self.handlePOST(path, data)['user_id']
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
    result = self.handlePOST(path, data)
    data = {
        "authenticated_user_id": userB,
        "privacy": False
    }
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
    data = {
        "authenticated_user_id": userB,
        "bio": "My long biography goes here.",
        "color": "333333,999999"
    }
    result = self.handlePOST(path, data)
    if result['color_primary'] == '333333':
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/update_profile_image.json"
    data = {
        "authenticated_user_id": userA,
        "profile_image": "https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg" ### TEMP!!!
    }
    result = self.handlePOST(path, data)
    data = {
        "authenticated_user_id": userB,
        "profile_image": "https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg" ### TEMP!!!
    }
    result = self.handlePOST(path, data)
    if result['profile_image'] == 'https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg':
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
    
    
    path = "friendships/create.json"
    data = {
        "authenticated_user_id": userB,
        "user_id": userA
    }
    result = self.handlePOST(path, data)    
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
        "category": "Restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityID = self.handlePOST(path, data)['entity_id']
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
        "category": "Restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityIDb = self.handlePOST(path, data)['entity_id']
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
        "blurb": "Favorite restaurant in the Village.", 
        "image": "image.png"
    }
    stampID = self.handlePOST(path, data)['stamp_id']
    if len(stampID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print stampID
        raise Exception
        
        
    path = "stamps/create.json"
    data = {
        "authenticated_user_id": userA,
        "entity_id": entityIDb,
        "blurb": "Great date spot. Thanks @rmstein!", 
        "image": "image.png"
    }
    stampIDb = self.handlePOST(path, data)['stamp_id']
    if len(stampIDb) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print stampID
        raise Exception


    path = "collections/user.json"
    data = {
        "user_id": userA
    }
    result = self.handleGET(path, data)
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
    result = self.handleGET(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
    if result == True:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/remove.json"
    data = { "authenticated_user_id": userA }
    resultA = self.handlePOST(path, data)
    data = { "authenticated_user_id": userB }
    resultB = self.handlePOST(path, data)
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
    userID = self.handlePOST(path, data)['user_id']
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
        "category": "Restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityID = self.handlePOST(path, data)['entity_id']
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
    stampID = self.handlePOST(path, data)['stamp_id']
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
    commentID = self.handlePOST(path, data)['comment_id']
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
    result = self.handleGET(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
    if result:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/remove.json"
    data = { "authenticated_user_id": userID }
    result = self.handlePOST(path, data)
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
    userID = self.handlePOST(path, data)['user_id']
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
        "category": "Restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityID = self.handlePOST(path, data)['entity_id']
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
    stampID = self.handlePOST(path, data)['stamp_id']
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
    favoriteID = self.handlePOST(path, data)['favorite_id']
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
    result = self.handleGET(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
    if result:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/remove.json"
    data = { "authenticated_user_id": userID }
    result = self.handlePOST(path, data)
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
    userA = self.handlePOST(path, data)['user_id']
    data = {
        "first_name": "Robby",
        "last_name": "Stein", 
        "email": "robby@stamped.com", 
        "password": "******",
        "screen_name": "rmstein"
    }
    userB = self.handlePOST(path, data)['user_id']
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
    result = self.handlePOST(path, data)
    data = {
        "authenticated_user_id": userB,
        "privacy": False
    }
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
    data = {
        "authenticated_user_id": userB,
        "bio": "My long biography goes here.",
        "color": "333333,999999"
    }
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
    data = {
        "authenticated_user_id": userB,
        "profile_image": "https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg" ### TEMP!!!
    }
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)    
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
        "category": "Restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityID = self.handlePOST(path, data)['entity_id']
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
        "category": "Restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityIDb = self.handlePOST(path, data)['entity_id']
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
    stampID = self.handlePOST(path, data)['stamp_id']
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
    commentID = self.handlePOST(path, data)['comment_id']
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
    commentID = self.handlePOST(path, data)['comment_id']
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
    commentID = self.handlePOST(path, data)['comment_id']
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
    commentID = self.handlePOST(path, data)['comment_id']
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
    commentID = self.handlePOST(path, data)['comment_id']
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
    favoriteID = self.handlePOST(path, data)['favorite_id']
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
#     stampIDb = self.handlePOST(path, data)['stamp_id']
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
    result = self.handleGET(path, data)
#     print result
    


    path = "activity/show.json"
    data = {
        "authenticated_user_id": userB
    }
    result = self.handleGET(path, data)
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
    result = self.handleGET(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
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
    result = self.handlePOST(path, data)
    if result == True:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "account/remove.json"
    data = { "authenticated_user_id": userA }
    resultA = self.handlePOST(path, data)
    data = { "authenticated_user_id": userB }
    resultB = self.handlePOST(path, data)
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

import os, unittest

class StampedAPITestSuite(unittest.TestSuite):
    def __init__(self):
        self.addTest(StampedAPIAccountTests())
        self.addTest(StampedAPIUserTests())
        self.addTest(StampedAPIEntityTests())
        self.addTest(StampedAPIStampTests())
        self.addTest(StampedAPIFriendshipTests())
        self.addTest(StampedAPICollectionTests())
        self.addTest(StampedAPICommentTests())
        self.addTest(StampedAPIFavoriteTests())
        self.addTest(StampedAPIActivityTests())

class AStampedAPITestCase(unittest.TestCase):
    def __init__(self, baseurl):
        self.baseurl = baseurl
        self._opener = StampedAPIURLOpener()
    
    def handleGET(path, data):
        params = urllib.urlencode(data)
        result = json.load(self._opener.open("%s/%s?%s" % (self.baseurl, path, params)))
        return result
    
    def handlePOST(path, data):
        params = urllib.urlencode(data)
        result = json.load(self._opener.open("%s/%s" % (self.baseurl, path), params))
        return result
    
    def assertValidKey(self, key):
        self.assertIsInstance(key, basestring)
        self.assertEqual(len(key), 24)

class StampedAPIAccountTests(AStampedAPITestCase):
    def setUp(self):
        path = "account/create.json"
        data = {
            "first_name": "Kevin",
            "last_name": "Palms", 
            "email": "kevin@stamped.com", 
            "password": "******",
            "screen_name": "kpalms"
        }
        response = self.handlePOST(path, data)
        self.assertIn('user_id', response)
        
        self.userID = response['user_id']
        self.assertValidKey(self.userID)
    
    def test_settings(self):
        path = "account/settings.json"
        data = {
            "authenticated_user_id": self.userID,
            "screen_name": "kevin",
            "privacy": False,
        }
        
        result = self.handlePOST(path, data)
        self.assertEqual(result['privacy'], False)
        
        path = "account/settings.json"
        data = {
            "authenticated_user_id": self.userID
        }
        
        result = self.handleGET(path, data)
        self.assertEqual(result['privacy'], False)
    
    def test_update_profile(self):
        path = "account/update_profile.json"
        data = {
            "authenticated_user_id": self.userID,
            "bio": "My long biography goes here.",
            "color": "333333,999999"
        }
        
        result = self.handlePOST(path, data)
        self.assertEqual(result['color_primary'], '333333')
        self.assertEqual(result['color_secondary'], '999999')
    
    def test_update_profile_image(self):
        # TODO: this url is temporary!
        url = 'https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg'
        
        path = "account/update_profile_image.json"
        data = {
            "authenticated_user_id": self.userID,
            "profile_image": url, 
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['profile_image'], url)
    
    def test_verify_credentials(self):
        path = "account/verify_credentials.json"
        data = {
            "authenticated_user_id": self.userID
        }
        
        result = self.handleGET(path, data)
        self.assertTrue(result)
    
    def test_reset_password(self):
        # TODO (@kpalms): why are we skipping this test case?
        return
        path = "account/reset_password.json"
        data = {
            "authenticated_user_id": self.userID
        }
        
        result = self.handlePOST(path, data)
    
    def test_remove(self):
        path = "account/remove.json"
        data = {
            "authenticated_user_id": self.userID
        }
        
        result = self.handlePOST(path, data)
        self.assertTrue(result)

class StampedAPIUserTests(AStampedAPITestCase):
    def setUp(self):
        path = "account/create.json"
        data = {
            "first_name": "User",
            "last_name": "A", 
            "email": "usera@stamped.com", 
            "password": "******",
            "screen_name": "UserA"
        }
        self.userA = self.handlePOST(path, data)['user_id']
        
        data = {
            "first_name": "User",
            "last_name": "B", 
            "email": "userb@stamped.com", 
            "password": "******",
            "screen_name": "UserB"
        }
        self.userB = self.handlePOST(path, data)['user_id']
        
        self.assertEqual(len(self.userA))
        self.assertEqual(len(self.userB))
    
    def test_show(self):
        # test show via user_id
        path = "users/show.json"
        data = { "user_id": self.userA }
        
        user = self.handleGET(path, data)
        self.assertEqual(user['screen_name'], 'UserA')
        
        # test show via screen_name
        path = "users/show.json"
        data = { "screen_name": "UserA" }
        
        user = self.handleGET(path, data)
        self.assertEqual(user['user_id'], self.userA)
    
    def test_lookup(self):
        # test lookup via user_ids
        path = "users/lookup.json"
        data = { "user_ids": "%s,%s" % (self.userA, self.userB) }
        
        users = self.handleGET(path, data)
        self.assertEqual(len(users), 2)
        
        # test lookup via screen_name
        path = "users/lookup.json"
        data = { "screen_names": "UserA,UserB" }
        
        users = self.handleGET(path, data)
        self.assertTrue(len(users) >= 2)
    
    def test_search(self):
        path = "users/search.json"
        data = { "q": "user" }
        
        users = self.handleGET(path, data)
        self.assertTrue(len(users) >= 2)
    
    def test_privacy(self):
        # test privacy via user_id
        path = "users/privacy.json"
        data = { "user_id": self.userA }
        
        privacy = self.handleGET(path, data)
        self.assertTrue(privacy)
        
        # test privacy via screen_name
        path = "users/privacy.json"
        data = { "screen_name": "UserA" }
        
        privacy = self.handleGET(path, data)
        self.assertTrue(privacy)
    
    def test_remove(self):
        path = "account/remove.json"
        data = {"authenticated_user_id": self.userA}
        
        resultA = self.handlePOST(path, data)
        self.assertTrue(resultA)
        
        data = {"authenticated_user_id": self.userB}
        
        resultB = self.handlePOST(path, data)
        self.assertTrue(resultB)

class StampedAPIEntityTests(AStampedAPITestCase):
    def __init__(self, baseurl):
        AStampedAPITestCase.__init__(self, baseurl)
    
    def setUp(self):
        path = "account/create.json"
        data = {
            "first_name": "Kevin",
            "last_name": "Palms", 
            "email": "kevin@stamped.com", 
            "password": "******",
            "screen_name": "kpalms"
        }
        
        response = self.handlePOST(path, data)
        self.userID = response['user_id']
        self.assertValidKey(self.userID)
    
    def test_create_show_update(self):
        path = "entities/create.json"
        desc = "American food in the West Village"
        data = {
            "authenticated_user_id": self.userID,
            "title": "Little Owl",
            "desc": desc, 
            "category": "Restaurant",
            "coordinates": "40.714623,-74.006605"
        }
        
        entityID = self.handlePOST(path, data)['entity_id']
        self.assertValidKey(entityID)
        
        path = "entities/show.json"
        data = { "entity_id": entityID }
        
        entity = self.handleGET(path, data)
        self.assertEqual(entity['desc'], desc)
        
        desc2 = "Gastropub in the West Village, NYC"
        path = "entities/update.json"
        data = {
            "authenticated_user_id": self.userID,
            "entity_id": entityID,
            "desc": desc2, 
        }
        result = self.handlePOST(path, data)
        self.assertEqual(entity['desc'], desc2)
    
    def test_search(self):
        path = "entities/search.json"
        data = {
            "authenticated_user_id": self.userID,
            "q": "Litt"
        }
        
        entities = self.handleGET(path, data)
        self.assertTrue(len(entities) > 0)
    
    def test_remove(self):
        path = "entities/remove.json"
        data = {
            "authenticated_user_id": self.userID,
            "entity_id": entityID
        }
        
        result = self.handlePOST(path, data)
        self.assertTrue(result)
    
    def tearDown(self):
        path = "account/remove.json"
        data = { "authenticated_user_id": self.userID }
        
        result = self.handlePOST(path, data)
        self.assertTrue(result)

class StampedAPStampTests(AStampedAPITestCase):
    def __init__(self, baseurl):
        AStampedAPITestCase.__init__(self, baseurl)
    
    def setUp(self):
        path = "account/create.json"
        data = {
            "first_name": "User",
            "last_name": "A", 
            "email": "usera@stamped.com", 
            "password": "******",
            "screen_name": "UserA"
        }
        
        self.userA = self.handlePOST(path, data)['user_id']
        self.assertValidKey(userA)
        
        data = {
            "first_name": "User",
            "last_name": "B", 
            "email": "userb@stamped.com", 
            "password": "******",
            "screen_name": "UserB"
        }
        
        self.userB = self.handlePOST(path, data)['user_id']
        self.assertValidKey(userB)
        
        path = "entities/create.json"
        data = {
            "authenticated_user_id": userA,
            "title": "Little Owl ",
            "desc": "American food in the West Village", 
            "category": "food",
            "subcategory": "restaurant",
            "coordinates": "40.714623,-74.006605"
        }
        
        self.entityID = self.handlePOST(path, data)['entity_id']
        self.assertValidKey(self.entityID)
        
    def test_create_show_update(self):
        path = "stamps/create.json"
        data = {
            "authenticated_user_id": self.userA,
            "entity_id": self.entityID,
            "blurb": "Favorite restaurant in the Village.", 
            "image": "image.png"
        }
        stampID = self.handlePOST(path, data)['stamp_id']
        self.assertValidKey(stampID)
        
        path = "stamps/create.json"
        data = {
            "authenticated_user_id": self.userB,
            "entity_id": self.entityID,
            "blurb": "Favorite restaurant in the Village. Thanks, @UserA.", 
            "image": "image.png",
            "credit": "UserA"
        }
        restampID = self.handlePOST(path, data)['stamp_id']
        self.assertValidKey(restampID)
        
        path = "stamps/update.json"
        data = {
            "authenticated_user_id": self.userA,
            "stamp_id": self.stampID,
            "image": "image2.png"
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['stamp_id'], stampID)
        
        path = "stamps/show.json"
        data = {
            "authenticated_user_id": self.userA,
            "stamp_id": self.stampID
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['image'], 'image2.png')
        
        path = "stamps/remove.json"
        data = {
            "authenticated_user_id": self.userA,
            "stamp_id": self.restampID
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)
        
        path = "stamps/remove.json"
        data = {
            "authenticated_user_id": self.userA,
            "stamp_id": self.stampID
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)
    
    def tearDown(self):
        path = "entities/remove.json"
        data = {
            "authenticated_user_id": self.userA,
            "entity_id": self.entityID
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)
        
        path = "account/remove.json"
        data = {"authenticated_user_id": userA}
        resultA = self.handlePOST(path, data)
        self.assertTrue(resultA)
        
        data = {"authenticated_user_id": userB}
        resultB = self.handlePOST(path, data)
        self.assertTrue(resultB)

class StampedAPIFriendshipTests(AStampedAPITestCase):
    def __init__(self, baseurl):
        AStampedAPITestCase.__init__(self, baseurl)
    
    def setUp(self):
    
    
    
        TODO
        # TODO
        TODO
        
        
        
        
        
        path = "account/create.json"
        data = {
            "first_name": "Kevin",
            "last_name": "Palms", 
            "email": "kevin@stamped.com", 
            "password": "******",
            "screen_name": "kpalms"
        }
        userA = self.handlePOST(path, data)['user_id']
        data = {
            "first_name": "Robby",
            "last_name": "Stein", 
            "email": "robby@stamped.com", 
            "password": "******",
            "screen_name": "rmstein"
        }
        userB = self.handlePOST(path, data)['user_id']
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
        result = self.handlePOST(path, data)
        data = {
            "authenticated_user_id": userB,
            "privacy": False
        }
        result = self.handlePOST(path, data)
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
        result = self.handlePOST(path, data)    
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
        result = self.handleGET(path, data)
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
        result = self.handleGET(path, data)
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
        result = self.handleGET(path, data)
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
        result = self.handlePOST(path, data)
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
        result = self.handlePOST(path, data)    
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
        result = self.handleGET(path, data)
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
        result = self.handleGET(path, data)
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
        result = self.handlePOST(path, data)
        if result == True:
            print 'PASS: %s' % path
        else:
            print 'FAIL: %s' % path
            print result
            raise Exception
            
            
        path = "account/remove.json"
        data = { "authenticated_user_id": userA }
        resultA = self.handlePOST(path, data)
        data = { "authenticated_user_id": userB }
        resultB = self.handlePOST(path, data)
        if resultA and resultB:
            print 'DATA: %s' % path
        else:
            print 'FAIL: %s' % path
            print result
            raise Exception

        path = "account/create.json"
        data = {
            "first_name": "User",
            "last_name": "A", 
            "email": "usera@stamped.com", 
            "password": "******",
            "screen_name": "UserA"
        }
        
        self.userA = self.handlePOST(path, data)['user_id']
        self.assertValidKey(userA)
        
        data = {
            "first_name": "User",
            "last_name": "B", 
            "email": "userb@stamped.com", 
            "password": "******",
            "screen_name": "UserB"
        }
        
        self.userB = self.handlePOST(path, data)['user_id']
        self.assertValidKey(userB)
        
        path = "entities/create.json"
        data = {
            "authenticated_user_id": userA,
            "title": "Little Owl ",
            "desc": "American food in the West Village", 
            "category": "food",
            "subcategory": "restaurant",
            "coordinates": "40.714623,-74.006605"
        }
        
        entityID = self.handlePOST(path, data)['entity_id']
        self.assertValidKey(entityID)
        
    def test_create_show_update(self):
        path = "stamps/create.json"
        data = {
            "authenticated_user_id": self.userA,
            "entity_id": self.entityID,
            "blurb": "Favorite restaurant in the Village.", 
            "image": "image.png"
        }
        stampID = self.handlePOST(path, data)['stamp_id']
        self.assertValidKey(stampID)
        
        path = "stamps/create.json"
        data = {
            "authenticated_user_id": self.userB,
            "entity_id": self.entityID,
            "blurb": "Favorite restaurant in the Village. Thanks, @UserA.", 
            "image": "image.png",
            "credit": "UserA"
        }
        restampID = self.handlePOST(path, data)['stamp_id']
        self.assertValidKey(restampID)
        
        path = "stamps/update.json"
        data = {
            "authenticated_user_id": self.userA,
            "stamp_id": self.stampID,
            "image": "image2.png"
        }
        result = self.handlePOST(path, data)
        self.assertEqual(result['stamp_id'], stampID)
        
        path = "stamps/show.json"
        data = {
            "authenticated_user_id": self.userA,
            "stamp_id": self.stampID
        }
        result = self.handleGET(path, data)
        self.assertEqual(result['image'], 'image2.png')
        
        path = "stamps/remove.json"
        data = {
            "authenticated_user_id": self.userA,
            "stamp_id": self.restampID
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)
        
        path = "stamps/remove.json"
        data = {
            "authenticated_user_id": self.userA,
            "stamp_id": self.stampID
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)
    
    def tearDown(self):
        path = "entities/remove.json"
        data = {
            "authenticated_user_id": self.userA,
            "entity_id": self.entityID
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)
        
        path = "account/remove.json"
        data = {"authenticated_user_id": userA}
        resultA = self.handlePOST(path, data)
        self.assertTrue(resultA)
        
        data = {"authenticated_user_id": userB}
        resultB = self.handlePOST(path, data)
        self.assertTrue(resultB)


if __name__ == '__main__':
    unittest.main()

