#!/usr/bin/env python
#Robby test script to activate new accounts

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import sys, thread, urllib, urllib2, json
from pprint import pprint

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
    result = apiOpener().open("%s/%s" % (baseurl, path), params)
    jsonResult = json.load(result)
    return jsonResult


def main():
    print    
    print '      BEGIN'
    
    baseurl = "http://0.0.0.0:5000/api/v1"
    #baseurl = "http://192.168.0.10:5000/api/v1"
    #baseurl = "http://api.stamped.com:5000/api/v1"
    
    # betaAccountData(baseurl)
    # betaAccountDataOAuth(baseurl)
    
    friendship = addFriend(baseurl)
    print friendship


def addFriend(baseurl):
    
    path = "friendships/create.json"
    data = {
        "oauth_token": 'Wdurfu7AGEh2hWcyl12XWV',
        "screen_name": 'robby',
    }
    result = testPOST(baseurl, path, data)
    return result



def createUser(baseurl, userData):

    print 'CREATE USER: %s %s' % (userData['first_name'], userData['last_name'])
    
    path = "account/create.json"
    data = {
        "client_id": "stampedtest",
        "client_secret": "august1ftw",
        "first_name": userData['first_name'],
        "last_name": userData['last_name'], 
        "email": userData['email'], 
        "password": userData['password'],
        "screen_name": userData['screen_name']
    }
    result = testPOST(baseurl, path, data)
    user = result['user']
    token = result['token']
    if len(user['user_id']) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/settings.json"
    data = {
        "oauth_token": token['access_token'],
        "privacy": userData['privacy'],
    }
    result = testPOST(baseurl, path, data)
    if result['privacy'] == userData['privacy']:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/update_profile.json"
    data = {
        "oauth_token": token['access_token'],
        "bio": userData['bio'],
        "color": userData['color']
    }
    result = testPOST(baseurl, path, data)
    if result['user_id'] == user['user_id']:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/update_profile_image.json"
    data = {
        "oauth_token": token['access_token'],
        "profile_image": userData['profile_image']
    }
    result = testPOST(baseurl, path, data)
    if result['profile_image'] == userData['profile_image']:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
        raise Exception
    
    print 

    return user, token


def betaAccountDataOAuth(baseurl):
    users = []

    userData = {
        "first_name": "Danielle",
        "last_name": "Zilberstein", 
        "email": "danielle.zilberstein@gmail.com", 
        "password": "12345",
        "screen_name": "danielle",
        "privacy": False,
        "bio": "I'm cute. And small. And fun.",
        "color": "33B6DA,006C89",
        "profile_image": "https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg" ### TEMP!!!        
    }
    users.append(createUser(baseurl, userData))



    print users

    path = "friendships/create.json"
    for user, token in users:
        for friend, friendToken in users:
            if user['user_id'] != friend['user_id']:
                data = {
                    "oauth_token": token['access_token'],
                    "user_id": friend['user_id']
                }
                result = testPOST(baseurl, path, data)    
                if result['user_id'] == friend['user_id']:
                    print 'PASS: %s' % path
                else:
                    print 'FAIL: %s' % path
                    raise Exception
            else:
                print 'SKIP'




        

# where all the magic starts
if __name__ == '__main__':
    main()
