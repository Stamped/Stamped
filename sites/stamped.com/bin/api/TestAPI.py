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
    
    accountTest(baseurl)
    
    entityTest(baseurl)
    
    userTest(baseurl)
    
    
    
    
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
        "privacy": True
    }
    userA = testPOST(baseurl, path, data)['id']
    data = {
        "first_name": "User",
        "last_name": "B", 
        "username": "userB", 
        "email": "userB@stamped.com", 
        "locale": "en_US", 
        "primary_color": "[255, 255, 255]",
        "password": "******"
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
        "password": "******"
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