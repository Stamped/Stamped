#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import sys, thread, urllib, json

# import StampedAPI from StampedAPI

def testGET(baseurl, path, data):
    params = urllib.urlencode(data)
#     print params
    result = json.load(urllib.urlopen("%s/%s?%s" % (baseurl, path, params)))
    return result
    
def testPOST(baseurl, path, data):
    params = urllib.urlencode(data)
#     print params
    result = urllib.urlopen("%s/%s" % (baseurl, path), params)
    jsonResult = json.load(result)
    return jsonResult


def main():

    print    
    print '      BEGIN'
    
    baseurl = "http://0.0.0.0:5000/api/v1"
#     baseurl = "http://50.19.163.247:5000/api/v1"
    
#     accountTest(baseurl)
#     
#     userTest(baseurl)
#     
#     entityTest(baseurl)
# 
#     stampTest(baseurl)
#     
#     friendshipTest(baseurl)
# 
#     collectionTest(baseurl)
#
    commentTest(baseurl)
#
#     favoriteTest(baseurl)

#     regexTest()
 
    print '      COMPLETE'
    print      


def regexTest():
    import re
    
    sampleText = []
    sampleText.append("This is a comment with @robby and @kevin in it.")
    sampleText.append("@robby what do you think?")
    sampleText.append("Normal comment")
    sampleText.append("Sending an email to robby@stamped.com")
    sampleText.append("My handle is @sample_kevin")
    sampleText.append("LOOK.ITS.@KEVIN.")
    sampleText.append("Oh @reallyLongNameThatShouldBreak, really?")
    sampleText.append("Maybe he'll finally find his keys. @peterfalk")
    
    user_regex = re.compile(r'([^a-zA-Z0-9_])@([a-zA-Z0-9+_]{1,20})', re.IGNORECASE)
    reply_regex = re.compile(r'@([a-zA-Z0-9+_]{1,20})', re.IGNORECASE)
        
    for text in sampleText:
        print 'TEST:', text  
        mentions = [] 
        reply = reply_regex.match(text)
        if reply:
            data = {}
            data['indices'] = [(reply.start()), reply.end()]
            data['screen_name'] = reply.group(0)[1:]
            mentions.append(data)
        for user in user_regex.finditer(text):
            data = {}
            data['indices'] = [(user.start()+1), user.end()]
            data['screen_name'] = user.group(0)[2:]
            mentions.append(data)
        print mentions


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
        "authorized_user_id": userID
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
    #result = testGET(baseurl, path, data)
    print 'SKIP: %s' % path
        
        
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
        "category": "Restaurant",
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
        "title": "Little Owl",
        "desc": "American food in the West Village", 
        "category": "Restaurant",
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
        "category": "Restaurant",
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
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print stampID
        raise Exception


    path = "collections/user.json"
    data = {
        "user_id": userA
    }
    result = testGET(baseurl, path, data)
    if len(result) == 1:
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
    if len(result) == 1:
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
        "category": "Restaurant",
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
        "category": "Restaurant",
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
    

# where all the magic starts
if __name__ == '__main__':
    main()
