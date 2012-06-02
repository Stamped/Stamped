#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

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
    
    # baseurl = "http://0.0.0.0:5000/api/v1"
    # baseurl = "https://dev.stamped.com/v0"
    baseurl = "https://0.0.0.0/v0"
    
    # betaAccountData(baseurl)
    betaAccountDataOAuth(baseurl)


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
        
        
    path = "account/update.json"
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
        "first_name": "Kevin",
        "last_name": "Palms", 
        "email": "kevin@stamped.com", 
        "password": "12345",
        "screen_name": "kevin",
        "privacy": False,
        "bio": "The very purpose of existence is to reconcile the glowing opinion we have of ourselves with the appalling things that other people think about us.",
        "color": "33B6DA,006C89",
        "profile_image": "https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg" ### TEMP!!!        
    }
    users.append(createUser(baseurl, userData))


    userData = {   
        "first_name": "Robby",
        "last_name": "Stein", 
        "email": "robby@stamped.com", 
        "password": "12345",
        "screen_name": "robby",
        "privacy": False,
        "bio": "Starting something new in NYC. Former Google product manager.",
        "color": "1673FF,92C516",
        "profile_image": "https://si0.twimg.com/profile_images/1381824457/robby_profile_squarer_reasonably_small.png" ### TEMP!!!
    }
    users.append(createUser(baseurl, userData))


    userData = {
        "first_name": "Bart",
        "last_name": "Stein", 
        "email": "bart@stamped.com", 
        "password": "12345",
        "screen_name": "bart",
        "privacy": False,
        "bio": "Co-Founder of a new startup in NYC. Formerly at Google Creative Lab.",
        "color": "5597AA,002F49",
        "profile_image": "https://si0.twimg.com/profile_images/1275778019/bart_photo_reasonably_small.jpg" ### TEMP!!!
    }
    users.append(createUser(baseurl, userData))


    userData = {
        "first_name": "Ed",
        "last_name": "Kim", 
        "email": "ed@stamped.com", 
        "password": "12345",
        "screen_name": "ed",
        "privacy": False,
        "bio": "Product Designer at new NYC start-up. Formerly at Google and Apple.",
        "website": "http://weartoday.tumblr.com",
        "color": "E10019,FF5B5B",
        "profile_image": "https://si0.twimg.com/profile_images/1195985261/edacorn_sq2_reasonably_small.jpg" ### TEMP!!!
    }
    users.append(createUser(baseurl, userData))


    userData = {
        "first_name": "Jake",
        "last_name": "Zien", 
        "email": "jake@stamped.com", 
        "password": "12345",
        "screen_name": "jake",
        "privacy": False,
        "bio": "Designer and programmer with a particular focus on building awesome interfaces. Working at a startup that, with any luck, you'll hear about later this year.",
        "website": "http://www.jakezien.com",
        "color": "CC2929,5DD9D1",
        "profile_image": "https://si0.twimg.com/profile_images/1296522588/hypercube_reasonably_small.png" ### TEMP!!!
    }
    users.append(createUser(baseurl, userData))
        
    
    userData = {
        "first_name": "Travis",
        "last_name": "Fischer", 
        "email": "travis@stamped.com", 
        "password": "12345",
        "screen_name": "travis",
        "privacy": False,
        "bio": "Lead engineer at NYC Startup; formerly worked at Microsoft and Pixar.",
        "color": "FF6000",
        "profile_image": "https://si0.twimg.com/profile_images/1420965568/fb_reasonably_small.jpg" ### TEMP!!!
    }
    users.append(createUser(baseurl, userData))


    userData = {
        "first_name": "Andy",
        "last_name": "Bonventre", 
        "email": "andybons@stamped.com", 
        "password": "12345",
        "screen_name": "andybons",
        "privacy": False,
        "bio": "Head of mobile awesomeness at NYC startup. Formerly at the Google. Went to Tufts. It was not my safety school.",
        "website": "http://about.me/andybons",
        "color": "14A800,5DD960",
        "profile_image": "https://twimg0-a.akamaihd.net/profile_images/1492360014/me.jpg" ### TEMP!!!
    }
    users.append(createUser(baseurl, userData))


    userData = {
        "first_name": "Rando",
        "last_name": "Manchester", 
        "email": "rando@stamped.com", 
        "password": "12345",
        "screen_name": "rando",
        "privacy": False,
        "bio": "You don't know me but my taste is top notch. Cheers!",
        "color": "E330B3,FF0096",
        "profile_image": "http://img.fannation.com/upload/truth_rumor/photo_upload/119/452/full/Rajon-Rondo-mug.jpg" ### TEMP!!!
    }
    users.append(createUser(baseurl, userData))



    userData = {
        "first_name": "Danielle",
        "last_name": "Zilberstein", 
        "email": "danielle.zilberstein@gmail.com", 
        "password": "12345",
        "screen_name": "danielle",
        "privacy": False,
        "bio": "I'm cute. And small. And fun.",
        "color": "8C1FC3,A02BCF",
        "profile_image": "http://a2.twimg.com/profile_images/1507664855/165735_776996026577_602907_42417430_6887446_n.jpg" ### TEMP!!!        
    }
    users.append(createUser(baseurl, userData))
    
    userData = {
        "first_name": "Jill",
        "last_name": "Lubochinski", 
        "email": "jlubo3@gmail.com", 
        "password": "12345",
        "screen_name": "jill",
        "privacy": False,
        "bio": "i love tv and watch a lot of it. way more than you.",
        "color": "F2DF11,F2DF11",
        "profile_image": "http://media.linkedin.com/mpr/pub/image-0JORppVmtUmZQKn00DB6pRGNbCEPliQ0rIsyprAQbN-8AWh9/jill-lubochinski.jpg"        
    }
    users.append(createUser(baseurl, userData))
    
    userData = {
        "first_name": "Andy",
        "last_name": "Kraut", 
        "email": "andykraut@gmail.com", 
        "password": "12345",
        "screen_name": "andy",
        "privacy": False,
        "bio": "Coolest things about me: FunnyOrDie employee. Live in NYC. Literate.",
        "color": "09876A,09876A",
        "profile_image": "http://a2.twimg.com/profile_images/1469480706/image.jpg" ### TEMP!!!        
    }
    users.append(createUser(baseurl, userData))
    
    userData = {
        "first_name": "Eli",
        "last_name": "Horne", 
        "email": "elihorne@gmail.com", 
        "password": "12345",
        "screen_name": "elihorne",
        "privacy": False,
        "bio": "UX designer @ Google.",
        "color": "80e2f2,43afc1",
        "profile_image": "http://a0.twimg.com/profile_images/1310573812/tweeters-square.png" ### TEMP!!!        
    }
    users.append(createUser(baseurl, userData))
    
    userData = {
        "first_name": "Robert",
        "last_name": "Sesek", 
        "email": "rsesek@gmail.com", 
        "password": "12345",
        "screen_name": "rsesek",
        "privacy": False,
        "bio": "Google Chrome Software Engineer / open source software developer / photographer",
        "color": "0072BC,005480",
        "profile_image": "http://media02.linkedin.com/media/p/3/000/024/03b/3297d26.jpg" ### TEMP!!!        
    }
    users.append(createUser(baseurl, userData))

    userData = {
        "first_name": "Liz",
        "last_name": "Tan", 
        "email": "lizxtan@gmail.com", 
        "password": "12345",
        "screen_name": "liztan",
        "privacy": False,
        "bio": "I'm cute. And small. And fun.",
        "color": "000000,000000",
        "profile_image": "https://twimg0-a.akamaihd.net/profile_images/1259707017/blackminimaliz.jpg" ### TEMP!!!        
    }
    users.append(createUser(baseurl, userData))



    coreUsers = ['kevin', 'robby', 'bart', 'ed', 'travis', 'jake', 'andybons', 'rando']

    robbyUsers = ['robby', 'danielle', 'jill', 'bart', 'andy']

    bonsUsers = ['andybons', 'elihorne', 'rsesek', 'liztan']


    path = "friendships/create.json"
    for user, token in users:
        for friend, friendToken in users:
            if user['user_id'] != friend['user_id']:
                if (user['screen_name'] in coreUsers and friend['screen_name'] in coreUsers) \
                    or (user['screen_name'] in robbyUsers and friend['screen_name'] in robbyUsers) \
                    or (user['screen_name'] in bonsUsers and friend['screen_name'] in bonsUsers):
                    data = {
                        "oauth_token": token['access_token'],
                        "user_id": friend['user_id']
                    }
                    result = testPOST(baseurl, path, data)    
                    if result['user_id'] == friend['user_id']:
                        print 'PASS: (%s & %s)' % (user['screen_name'], friend['screen_name'])
                    else:
                        print 'FAIL: %s' % path
                        raise Exception
                else:
                    print 'SKIP: (%s & %s)' % (user['screen_name'], friend['screen_name'])




# where all the magic starts
if __name__ == '__main__':
    main()
