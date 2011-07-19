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
    baseurl = "http://192.168.0.10:5000/api/v1"
    
    betaAccountData(baseurl)





def betaAccountData(baseurl):

    
    path = "account/create.json"
    data = {
        "first_name": "Kevin",
        "last_name": "Palms", 
        "email": "kevin@stamped.com", 
        "password": "12345",
        "screen_name": "sample_kevin"
    }
    kevin = testPOST(baseurl, path, data)['user_id']
    if len(kevin) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/settings.json"
    data = {
        "authenticated_user_id": kevin,
        "privacy": False,
    }
    result = testPOST(baseurl, path, data)
    if result['privacy'] == False:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/update_profile.json"
    data = {
        "authenticated_user_id": kevin,
        "bio": "The very purpose of existence is to reconcile the glowing opinion we have of ourselves with the appalling things that other people think about us.",
        "color": "51-182-218,0-108-137"
    }
    result = testPOST(baseurl, path, data)
    if result['user_id'] == kevin:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
    ####
    
    
    path = "account/create.json"
    data = {
        "first_name": "Robby",
        "last_name": "Stein", 
        "email": "robby@stamped.com", 
        "password": "12345",
        "screen_name": "sample_robby"
    }
    robby = testPOST(baseurl, path, data)['user_id']
    if len(robby) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/settings.json"
    data = {
        "authenticated_user_id": robby,
        "privacy": False,
    }
    result = testPOST(baseurl, path, data)
    if result['privacy'] == False:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/update_profile.json"
    data = {
        "authenticated_user_id": robby,
        "bio": "Starting something new in NYC. Former Google product manager.",
        "color": "22-115-255,146-197-22"
    }
    result = testPOST(baseurl, path, data)
    if result['user_id'] == robby:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
    ####
    
    
    path = "account/create.json"
    data = {
        "first_name": "Bart",
        "last_name": "Stein", 
        "email": "bart@stamped.com", 
        "password": "12345",
        "screen_name": "sample_bart"
    }
    bart = testPOST(baseurl, path, data)['user_id']
    if len(bart) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/settings.json"
    data = {
        "authenticated_user_id": bart,
        "privacy": True,
    }
    result = testPOST(baseurl, path, data)
    if result['privacy'] == True:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/update_profile.json"
    data = {
        "authenticated_user_id": bart,
        "bio": "Co-Founder of a new startup in NYC. Formerly at Google Creative Lab.",
        "color": "85-151-170,0-47-73"
    }
    result = testPOST(baseurl, path, data)
    if result['user_id'] == bart:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
    ####
    
    
    path = "account/create.json"
    data = {
        "first_name": "Ed",
        "last_name": "Kim", 
        "email": "ed@stamped.com", 
        "password": "12345",
        "screen_name": "sample_ed"
    }
    ed = testPOST(baseurl, path, data)['user_id']
    if len(ed) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/settings.json"
    data = {
        "authenticated_user_id": ed,
        "privacy": False,
    }
    result = testPOST(baseurl, path, data)
    if result['privacy'] == False:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/update_profile.json"
    data = {
        "authenticated_user_id": ed,
        "bio": "Product Designer at new NYC start-up. Formerly at Google and Apple.",
        "website": "http://weartoday.tumblr.com",
        "color": "225-0-25,255-91-91"
    }
    result = testPOST(baseurl, path, data)
    if result['user_id'] == ed:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
    ####
    
    
    path = "account/create.json"
    data = {
        "first_name": "Jake",
        "last_name": "Zien", 
        "email": "jake@stamped.com", 
        "password": "12345",
        "screen_name": "sample_jake"
    }
    jake = testPOST(baseurl, path, data)['user_id']
    if len(jake) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/settings.json"
    data = {
        "authenticated_user_id": jake,
        "privacy": False,
    }
    result = testPOST(baseurl, path, data)
    if result['privacy'] == False:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/update_profile.json"
    data = {
        "authenticated_user_id": jake,
        "bio": "Designer and programmer with a particular focus on building awesome interfaces. Working at a startup that, with any luck, you'll hear about later this year.",
        "website": "http://www.jakezien.com",
        "color": "204-41-41,93-217-209"
    }
    result = testPOST(baseurl, path, data)
    if result['user_id'] == jake:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
    ####
    
    
    path = "account/create.json"
    data = {
        "first_name": "Travis",
        "last_name": "Fischer", 
        "email": "travis@stamped.com", 
        "password": "12345",
        "screen_name": "sample_travis"
    }
    travis = testPOST(baseurl, path, data)['user_id']
    if len(travis) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/settings.json"
    data = {
        "authenticated_user_id": travis,
        "privacy": False,
    }
    result = testPOST(baseurl, path, data)
    if result['privacy'] == False:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/update_profile.json"
    data = {
        "authenticated_user_id": travis,
        "bio": "Lead engineer at NYC Startup; formerly worked at Microsoft and Pixar.",
        "color": "255-96-0,255-186-0"
    }
    result = testPOST(baseurl, path, data)
    if result['user_id'] == travis:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
    ####
    
    
    path = "account/create.json"
    data = {
        "first_name": "Andy",
        "last_name": "Bonventre", 
        "email": "andybons@stamped.com", 
        "password": "12345",
        "screen_name": "sample_andybons"
    }
    bons = testPOST(baseurl, path, data)['user_id']
    if len(bons) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/settings.json"
    data = {
        "authenticated_user_id": bons,
        "privacy": False,
    }
    result = testPOST(baseurl, path, data)
    if result['privacy'] == False:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/update_profile.json"
    data = {
        "authenticated_user_id": bons,
        "bio": "Head of mobile awesomeness at NYC startup. Formerly at the Google. Went to Tufts. It was not my safety school.",
        "website": "http://about.me/andybons",
        "color": "20-168-0,93-217-96"
    }
    result = testPOST(baseurl, path, data)
    if result['user_id'] == bons:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
    ############
    
    
    path = "friendships/create.json"
    data = {
        "authenticated_user_id": bons,
        "user_id": kevin
    }
    result = testPOST(baseurl, path, data)    
    if result['user_id'] == kevin:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
    
    
    path = "friendships/create.json"
    data = {
        "authenticated_user_id": bons,
        "user_id": robby
    }
    result = testPOST(baseurl, path, data)    
    if result['user_id'] == robby:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
    
    
    path = "friendships/create.json"
    data = {
        "authenticated_user_id": bons,
        "user_id": bart
    }
    result = testPOST(baseurl, path, data)    
    if result['user_id'] == bart:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
    
    
    path = "friendships/create.json"
    data = {
        "authenticated_user_id": bons,
        "user_id": ed
    }
    result = testPOST(baseurl, path, data)    
    if result['user_id'] == ed:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
    
    
    path = "friendships/create.json"
    data = {
        "authenticated_user_id": bons,
        "user_id": jake
    }
    result = testPOST(baseurl, path, data)    
    if result['user_id'] == jake:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
    
    
    path = "friendships/create.json"
    data = {
        "authenticated_user_id": bons,
        "user_id": travis
    }
    result = testPOST(baseurl, path, data)    
    if result['user_id'] == travis:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
    ###############
        
    
    path = "entities/create.json"
    data = {
        "authenticated_user_id": kevin,
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
        raise Exception        
    
    path = "stamps/create.json"
    data = {
        "authenticated_user_id": kevin,
        "entity_id": entityID,
        "blurb": "Favorite restaurant in the Village."
    }
    stampID = testPOST(baseurl, path, data)['stamp_id']
    if len(stampID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        raise Exception
        
    ###        
    
    path = "entities/create.json"
    data = {
        "authenticated_user_id": robby,
        "title": "Spotted Pig",
        "desc": "Gastropub in the West Village, NYC.", 
        "category": "Restaurant",
        "coordinates": "40.714623,-74.006605"
    }
    entityID = testPOST(baseurl, path, data)['entity_id']
    if len(entityID) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception        
    
    path = "stamps/create.json"
    data = {
        "authenticated_user_id": robby,
        "entity_id": entityID,
        "blurb": "This is my favorite burger."
    }
    stampID = testPOST(baseurl, path, data)['stamp_id']
    if len(stampID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        raise Exception
        
    ###
    
    path = "entities/create.json"
    data = {
        "authenticated_user_id": bart,
        "title": "Freedom",
        "desc": "Jonathan Franzen", 
        "category": "Book"
    }
    entityID = testPOST(baseurl, path, data)['entity_id']
    if len(entityID) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception        
    
    path = "stamps/create.json"
    data = {
        "authenticated_user_id": bart,
        "entity_id": entityID,
        "blurb": "Best book I've read all year."
    }
    stampID = testPOST(baseurl, path, data)['stamp_id']
    if len(stampID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        raise Exception
        
    ###
    
    path = "entities/create.json"
    data = {
        "authenticated_user_id": ed,
        "title": "Ramen Takumi",
        "desc": "Ramen noodles in Union Square", 
        "category": "Restaurant"
    }
    entityID = testPOST(baseurl, path, data)['entity_id']
    if len(entityID) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception        
    
    path = "stamps/create.json"
    data = {
        "authenticated_user_id": ed,
        "entity_id": entityID,
        "blurb": "My summer noodle spot."
    }
    stampID = testPOST(baseurl, path, data)['stamp_id']
    if len(stampID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        raise Exception
        
    ###
    
    path = "entities/create.json"
    data = {
        "authenticated_user_id": jake,
        "title": "Hurt Locker",
        "desc": "Film", 
        "category": "Film"
    }
    entityID = testPOST(baseurl, path, data)['entity_id']
    if len(entityID) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception        
    
    path = "stamps/create.json"
    data = {
        "authenticated_user_id": ed,
        "entity_id": entityID,
        "blurb": "Suffocatingly intense, but one of the best Films of the year."
    }
    stampID = testPOST(baseurl, path, data)['stamp_id']
    if len(stampID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        raise Exception
        
    ###
    
    path = "entities/create.json"
    data = {
        "authenticated_user_id": travis,
        "title": "Phantogram",
        "desc": "Electronic music", 
        "category": "Music"
    }
    entityID = testPOST(baseurl, path, data)['entity_id']
    if len(entityID) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception        
    
    path = "stamps/create.json"
    data = {
        "authenticated_user_id": ed,
        "entity_id": entityID,
        "blurb": "Softer electronica with a perfect blend of harder beats mixed in."
    }
    stampID = testPOST(baseurl, path, data)['stamp_id']
    if len(stampID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        raise Exception
        
        
        
        

# where all the magic starts
if __name__ == '__main__':
    main()