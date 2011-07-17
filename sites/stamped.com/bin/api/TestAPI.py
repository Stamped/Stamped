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
    
#     accountTest(baseurl)
#     
#     entityTest(baseurl)
#     
#     userTest(baseurl)
#     
#     friendshipTest(baseurl)
# 
    stampTest(baseurl)
# 
#     collectionTest(baseurl)
# 
#     commentTest(baseurl)
    
    
    
# ########### #
# Collections #
# ########### #

def collectionTest(baseurl):

    print    
    print '      COLLECTION'
    
    
    path = "addAccount"
    data = {
        "first_name": "User",
        "last_name": "A", 
        "username": "userA", 
        "email": "userA@stamped.com", 
        "locale": "en_US", 
        "primary_color": "[255, 255, 255]",
        "password": "******",
        "privacy": False,
        "img": "userA.png"
    }
    userA = testPOST(baseurl, path, data)['id']
    data = {
        "first_name": "User",
        "last_name": "B", 
        "username": "userB", 
        "email": "userB@stamped.com", 
        "locale": "en_US", 
        "primary_color": "[255, 255, 255]",
        "password": "******",
        "img": "userB.png"
    }
    userB = testPOST(baseurl, path, data)['id']
    if len(userA) == 24 and len(userB) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print userID
        raise Exception
    
    
    path = "addFriendship"
    data = {
        "user_id": userB,
        "friend_id": userA
    }
    result = testPOST(baseurl, path, data)['_data']
    if result['user_id'] == userB and result['friend_id'] == userA:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
    
    path = "addEntity"
    data = {
        "title": "Little Owl",
        "desc": "American food in the West Village", 
        "category": "Restaurant"
    }
    entityID = testPOST(baseurl, path, data)['id']
    if len(entityID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print entityID
        raise Exception
        
    
    path = "stamps/add.json"
    data = {
        "user_id": userA,
        "entity_id": entityID,
        "blurb": "Favorite restaurant in the Village.", 
        "img": "image.png",
        "mentions": "userA,userB"
    }
    stampID = testPOST(baseurl, path, data)['id']
    if len(stampID) == 24:
        print 'DATA: %s' % path
    else:
        print 'result: %s' % path
        print stampID
        raise Exception


    path = "collections/user.json"
    data = {"user_id": userA}
    result = testGET(baseurl, path, data)
    if len(result) == 1:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception


    path = "collections/inbox.json"
    data = {"user_id": userB}
    result = testGET(baseurl, path, data)
    stamps = []
    for stamp in result:
        stamps.append(stamp['_data'])
    if len(stamps) == 1:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
    
    path = "stamps/remove.json"
    data = {
        "stamp_id": stampID,
        "user_id": userA
    }
    result = testPOST(baseurl, path, data)['id']
    if result == stampID:
        print 'DATA: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
        
    path = "removeEntity"
    data = {"entity_id": entityID}
    result = testPOST(baseurl, path, data)
    if result:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
    
    
    path = "removeFriendship"
    data = {
        "user_id": userB,
        "friend_id": userA
    }
    result = testPOST(baseurl, path, data)['_data']
    if result['user_id'] == userB and result['friend_id'] == userA:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "removeAccount"
    data = {"account_id": userA}
    resultA = testPOST(baseurl, path, data)
    data = {"account_id": userB}
    resultB = testPOST(baseurl, path, data)
    if resultA and resultB:
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
    
    
    path = "addAccount"
    data = {
        "first_name": "User",
        "last_name": "A", 
        "username": "userA", 
        "email": "userA@stamped.com", 
        "locale": "en_US", 
        "primary_color": "[255, 255, 255]",
        "password": "******",
        "privacy": False,
        "img": "user.png"
    }
    userA = testPOST(baseurl, path, data)['id']
    if len(userA) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print userID
        raise Exception
        
    
    path = "addEntity"
    data = {
        "title": "Little Owl",
        "desc": "American food in the West Village", 
        "category": "Restaurant"
    }
    entityID = testPOST(baseurl, path, data)['id']
    if len(entityID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print entityID
        raise Exception
        
    
    path = "stamps/add.json"
    data = {
        "user_id": userA,
        "entity_id": entityID,
        "blurb": "Favorite restaurant in the Village.", 
        "img": "image.png",
        "mentions": "userA,userB"
    }
    stampID = testPOST(baseurl, path, data)['id']
    if len(stampID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print stampID
        raise Exception
        
    
    path = "stamps/update.json"
    data = {
        "stamp_id": stampID,
        "img": "image2.png"
    }
    result = testPOST(baseurl, path, data)['id']
    if result == stampID:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
    
    path = "stamps/show"
    data = {"stamp_id": stampID}
    url = "%s/%s.json" % (path, stampID)
    result = json.load(urllib.urlopen("%s/%s" % (baseurl, url)))
    if result['img'] == 'image2.png':
        print 'PASS: %s' % url
    else:
        print 'result: %s' % url
        print result
        raise Exception
        
    
    path = "getStamps"
    data = {"stamp_ids": stampID}
    result = testGET(baseurl, path, data)
    if len(result) == 1:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
    
    path = "stamps/remove.json"
    data = {
        "stamp_id": stampID,
        "user_id": userA
    }
    result = testPOST(baseurl, path, data)['id']
    if result == stampID:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
        
    path = "removeEntity"
    data = {"entity_id": entityID}
    result = testPOST(baseurl, path, data)
    if result:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "removeAccount"
    data = {"account_id": userA}
    resultA = testPOST(baseurl, path, data)
    if resultA:
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
    
    
    path = "addAccount"
    data = {
        "first_name": "User",
        "last_name": "A", 
        "username": "userA", 
        "email": "userA@stamped.com", 
        "locale": "en_US", 
        "primary_color": "[255, 255, 255]",
        "password": "******",
        "privacy": False,
        "img": "user.png"
    }
    userA = testPOST(baseurl, path, data)['id']
    if len(userA) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print userID
        raise Exception
        
    
    path = "addEntity"
    data = {
        "title": "Little Owl",
        "desc": "American food in the West Village", 
        "category": "Restaurant"
    }
    entityID = testPOST(baseurl, path, data)['id']
    if len(entityID) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print entityID
        raise Exception
        
    
    path = "stamps/add.json"
    data = {
        "user_id": userA,
        "entity_id": entityID,
        "blurb": "Favorite restaurant in the Village.", 
        "img": "image.png",
        "mentions": "userA,userB"
    }
    stampID = testPOST(baseurl, path, data)['id']
    if len(stampID) == 24:
        print 'DATA: %s' % path
    else:
        print 'result: %s' % path
        print stampID
        raise Exception
        
    
    path = "addComment"
    data = {
        "user_id": userA,
        "stamp_id": stampID,
        "blurb": "Should I check this place out?", 
        "mentions": "userA,userB"
    }
    commentID = testPOST(baseurl, path, data)['id']
    if len(commentID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print commentID
        raise Exception
        
        
    path = "getComments"
    data = {"stamp_id": stampID}
    result = testGET(baseurl, path, data)
    comments = []
    for comment in result:
        comments.append(comment['_data'])
    if len(comments) == 1:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
                
    
    path = "removeComment"
    data = {
        "comment_id": commentID
    }
    result = testPOST(baseurl, path, data)['id']
    if result == commentID:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
    
    path = "stamps/remove.json"
    data = {
        "stamp_id": stampID,
        "user_id": userA
    }
    result = testPOST(baseurl, path, data)['id']
    if result == stampID:
        print 'DATA: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
        
    path = "removeEntity"
    data = {"entity_id": entityID}
    result = testPOST(baseurl, path, data)
    if result:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "removeAccount"
    data = {"account_id": userA}
    resultA = testPOST(baseurl, path, data)
    if resultA:
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
    
    path = "addAccount"
    data = {
        "first_name": "User",
        "last_name": "A", 
        "username": "userA", 
        "email": "userA@stamped.com", 
        "locale": "en_US", 
        "primary_color": "[255, 255, 255]",
        "password": "******",
        "privacy": False,
        "img": "userA.png"
    }
    userA = testPOST(baseurl, path, data)['id']
    data = {
        "first_name": "User",
        "last_name": "B", 
        "username": "userB", 
        "email": "userB@stamped.com", 
        "locale": "en_US", 
        "primary_color": "[255, 255, 255]",
        "password": "******",
        "img": "userB.png"
    }
    userB = testPOST(baseurl, path, data)['id']
    if len(userA) == 24 and len(userB) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print userID
        raise Exception
    
    
    path = "addFriendship"
    data = {
        "user_id": userA,
        "friend_id": userB
    }
    result = testPOST(baseurl, path, data)['_data']
    if result['user_id'] == userA and result['friend_id'] == userB:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
    
    path = "checkFriendship"
    data = {
        "user_id": userA,
        "friend_id": userB
    }
    result = testGET(baseurl, path, data)
    if result == True:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "getFriends"
    data = {"user_id": userA}
    result = testGET(baseurl, path, data)[-1]
    if result == userB:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "getFollowers"
    data = {"user_id": userB}
    result = testGET(baseurl, path, data)[-1]
    if result == userA:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "approveFriendship"
    print 'SKIP: %s' % path
    
    
    path = "removeFriendship"
    data = {
        "user_id": userA,
        "friend_id": userB
    }
    result = testPOST(baseurl, path, data)['_data']
    if result['user_id'] == userA and result['friend_id'] == userB:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
    
    
    path = "addBlock"
    data = {
        "user_id": userA,
        "friend_id": userB
    }
    result = testPOST(baseurl, path, data)['_data']
    if result['user_id'] == userA and result['friend_id'] == userB:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
    
    path = "checkBlock"
    data = {
        "user_id": userA,
        "friend_id": userB
    }
    result = testGET(baseurl, path, data)
    if result == True:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "getBlocks"
    data = {"user_id": userA}
    result = testGET(baseurl, path, data)[-1]
    if result == userB:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
    
    
    path = "removeBlock"
    data = {
        "user_id": userA,
        "friend_id": userB
    }
    result = testPOST(baseurl, path, data)['_data']
    if result['user_id'] == userA and result['friend_id'] == userB:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "removeAccount"
    data = {"account_id": userA}
    resultA = testPOST(baseurl, path, data)
    data = {"account_id": userB}
    resultB = testPOST(baseurl, path, data)
    if resultA and resultB:
        print 'DATA: %s' % path
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
    
    path = "addAccount"
    data = {
        "first_name": "User",
        "last_name": "A", 
        "username": "userA", 
        "email": "userA@stamped.com", 
        "locale": "en_US", 
        "primary_color": "[255, 255, 255]",
        "password": "******",
        "privacy": True,
        "img": "userA.png"
    }
    userA = testPOST(baseurl, path, data)['id']
    data = {
        "first_name": "User",
        "last_name": "B", 
        "username": "userB", 
        "email": "userB@stamped.com", 
        "locale": "en_US", 
        "primary_color": "[255, 255, 255]",
        "password": "******",
        "img": "userB.png"
    }
    userB = testPOST(baseurl, path, data)['id']
    if len(userA) == 24 and len(userB) == 24:
        print 'DATA: %s' % path
    else:
        print 'FAIL: %s' % path
        print userID
        raise Exception
        
        
    path = "getUser"
    data = {"user_id": userA}
    user = testGET(baseurl, path, data)['_data']
    if user["username"] == "userA":
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print entity
        raise Exception
        
        
    path = "getUsers"
    data = {"user_ids": "%s,%s" % (userA, userB)}
    usersData = testGET(baseurl, path, data)
    users = []
    for user in usersData:
        users.append(user['_data'])
    if len(users) == 2:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print users
        raise Exception
        
        
    path = "getUserByName"
    data = {"username": "userA"}
    user = testGET(baseurl, path, data)['_data']
    if user["username"] == "userA":
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print user
        raise Exception
        
        
    path = "getUsersByName"
    data = {"usernames": "userA,userB"}
    usersData = testGET(baseurl, path, data)['users']
    users = []
    for user in usersData:
        users.append(user['_data'])
    if len(users) >= 2:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print users
        raise Exception
        
        
    path = "searchUsers"
    data = {"query": "user"}
    users = testGET(baseurl, path, data)['users']
    if len(users) > 0:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print users
        raise Exception
        
        
    path = "getPrivacy"
    data = {"user_id": userA}
    privacy = testGET(baseurl, path, data)
    if privacy == True:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print privacy
        raise Exception
        
        
    path = "removeAccount"
    data = {"account_id": userA}
    resultA = testPOST(baseurl, path, data)
    data = {"account_id": userB}
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
    
    path = "addEntity"
    data = {
        "title": "Little Owl",
        "desc": "American food in the West Village", 
        "category": "Restaurant"
    }
    entityID = testPOST(baseurl, path, data)['id']
    if len(entityID) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print entityID
        raise Exception
    
    
    path = "updateEntity"
    data = {
        "entity_id": entityID,
        "desc": "Great American food in the West Village"
    }
    result = testPOST(baseurl, path, data)
    if result:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "getEntity"
    data = {"entity_id": entityID}
    entity = testGET(baseurl, path, data)['_data']
    if entity["desc"] == "Great American food in the West Village":
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print entity
        raise Exception
        
        
    path = "searchEntities"
    data = {"query": "Litt"}
    entities = testGET(baseurl, path, data)['entities']
    if len(entities) > 0:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print entity
        raise Exception
        
        
    path = "removeEntity"
    data = {"entity_id": entityID}
    result = testPOST(baseurl, path, data)
    if result:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception

    print

    
# ######## #
# Accounts #
# ######## #

def accountTest(baseurl):

    print    
    print '      ACCOUNT'
    
    path = "addAccount"
    data = {
        "first_name": "Kevin",
        "last_name": "Palms", 
        "username": "kpalms!", 
        "email": "kevin@stamped.com", 
        "locale": "en_US", 
        "primary_color": "[255, 255, 255]",
        "password": "******",
        "img": "user.png"
    }
    userID = testPOST(baseurl, path, data)['id']
    if len(userID) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print userID
        raise Exception
        
        
    path = "updateAccount"
    data = {
        "account_id": userID,
        "first_name": "Robby",
        "last_name": "Stein",
        "email": "robby@stamped.com"
    }
    result = testPOST(baseurl, path, data)
    if result:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
        
        
    path = "getAccount"
    data = {"account_id": userID}
    user = testGET(baseurl, path, data)['_data']
    if user["email"] == "robby@stamped.com":
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print user
        raise Exception
        
        
    path = "removeAccount"
    data = {"account_id": userID}
    result = testPOST(baseurl, path, data)
    if result:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception

    print


# where all the magic starts
if __name__ == '__main__':
    main()