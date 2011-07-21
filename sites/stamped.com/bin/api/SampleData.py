#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import sys, thread, urllib, urllib2, json
from pprint import pprint

# import StampedAPI from StampedAPI

def testGET(baseurl, path, data):
    params = urllib.urlencode(data)
#     print params
    result = json.load(urllib2.urlopen("%s/%s?%s" % (baseurl, path, params)))
    return result
    
def testPOST(baseurl, path, data):
    params = urllib.urlencode(data)
#     print params
    result = urllib2.urlopen("%s/%s" % (baseurl, path), params)
    pprint(result)
    jsonResult = json.load(result)
    return jsonResult


def main():
    print    
    print '      BEGIN'
    
    baseurl = "http://0.0.0.0:5000/api/v1"
    baseurl = "http://192.168.0.46:5000/api/v1"
    #baseurl = "http://192.168.0.10:5000/api/v1"
    
    betaAccountData(baseurl)


def createStamp(baseurl, user, title, category, comment):
    
    path = "entities/create.json"
    data = {
        "authenticated_user_id": user,
        "title": title,
        "desc": "Custom entity", 
        "category": category
    }
    entityID = testPOST(baseurl, path, data)['entity_id']
    if len(entityID) == 24:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception        
    
    path = "stamps/create.json"
    data = {
        "authenticated_user_id": user,
        "entity_id": entityID,
        "blurb": comment
    }
    stampID = testPOST(baseurl, path, data)['stamp_id']
    if len(stampID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        raise Exception
        
    return stampID


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
        "color": "33B6DA,006C89"
    }
    result = testPOST(baseurl, path, data)
    if result['user_id'] == kevin:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/update_profile_image.json"
    data = {
        "authenticated_user_id": kevin,
        "profile_image": "https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg" ### TEMP!!!
    }
    result = testPOST(baseurl, path, data)
    if result['profile_image'] == 'https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg':
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
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
        "color": "1673FF,92C516"
    }
    result = testPOST(baseurl, path, data)
    if result['user_id'] == robby:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/update_profile_image.json"
    data = {
        "authenticated_user_id": robby,
        "profile_image": "https://si0.twimg.com/profile_images/1381824457/robby_profile_squarer_reasonably_small.png" ### TEMP!!!
    }
    result = testPOST(baseurl, path, data)
    if result['profile_image'] == 'https://si0.twimg.com/profile_images/1381824457/robby_profile_squarer_reasonably_small.png':
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
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
        "color": "5597AA,002F49"
    }
    result = testPOST(baseurl, path, data)
    if result['user_id'] == bart:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/update_profile_image.json"
    data = {
        "authenticated_user_id": bart,
        "profile_image": "https://si0.twimg.com/profile_images/1275778019/bart_photo_reasonably_small.jpg" ### TEMP!!!
    }
    result = testPOST(baseurl, path, data)
    if result['profile_image'] == 'https://si0.twimg.com/profile_images/1275778019/bart_photo_reasonably_small.jpg':
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
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
        "color": "E10019,FF5B5B"
    }
    result = testPOST(baseurl, path, data)
    if result['user_id'] == ed:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/update_profile_image.json"
    data = {
        "authenticated_user_id": ed,
        "profile_image": "https://si0.twimg.com/profile_images/1195985261/edacorn_sq2_reasonably_small.jpg" ### TEMP!!!
    }
    result = testPOST(baseurl, path, data)
    if result['profile_image'] == 'https://si0.twimg.com/profile_images/1195985261/edacorn_sq2_reasonably_small.jpg':
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
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
        "color": "CC2929,5DD9D1"
    }
    result = testPOST(baseurl, path, data)
    if result['user_id'] == jake:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/update_profile_image.json"
    data = {
        "authenticated_user_id": jake,
        "profile_image": "https://si0.twimg.com/profile_images/1296522588/hypercube_reasonably_small.png" ### TEMP!!!
    }
    result = testPOST(baseurl, path, data)
    if result['profile_image'] == 'https://si0.twimg.com/profile_images/1296522588/hypercube_reasonably_small.png':
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
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
        "color": "FF6000"
    }
    result = testPOST(baseurl, path, data)
    if result['user_id'] == travis:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/update_profile_image.json"
    data = {
        "authenticated_user_id": travis,
        "profile_image": "https://si0.twimg.com/profile_images/1420965568/fb_reasonably_small.jpg" ### TEMP!!!
    }
    result = testPOST(baseurl, path, data)
    if result['profile_image'] == 'https://si0.twimg.com/profile_images/1420965568/fb_reasonably_small.jpg':
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
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
        "color": "14A800,5DD960"
    }
    result = testPOST(baseurl, path, data)
    if result['user_id'] == bons:
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        raise Exception
        
        
    path = "account/update_profile_image.json"
    data = {
        "authenticated_user_id": bons,
        "profile_image": "https://si0.twimg.com/profile_images/1443373911/image_reasonably_small.jpg" ### TEMP!!!
    }
    result = testPOST(baseurl, path, data)
    if result['profile_image'] == 'https://si0.twimg.com/profile_images/1443373911/image_reasonably_small.jpg':
        print 'PASS: %s' % path
    else:
        print 'FAIL: %s' % path
        print result
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
    
    """
    
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
        "authenticated_user_id": jake,
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
        "authenticated_user_id": travis,
        "entity_id": entityID,
        "blurb": "Softer electronica with a perfect blend of harder beats mixed in."
    }
    stampID = testPOST(baseurl, path, data)['stamp_id']
    if len(stampID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        raise Exception
    """
      
    createStamp(baseurl=baseurl, user=travis, title='Frankenstein', category='Book', comment='Absolute favorite book of all time -- nothing like the film depictions.')
    createStamp(baseurl=baseurl, user=travis, title='Tiny Wings', category='App', comment='I love this game.')
    createStamp(baseurl=baseurl, user=robby, title='Meatball Shop', category='Place', comment='Meatball smash! It\'s the meatball sandwich to write home about. ')
    createStamp(baseurl=baseurl, user=travis, title='Transformers 3', category='Film', comment='Amazing graphics coupled with a surprisingly decent storyline.')
    createStamp(baseurl=baseurl, user=travis, title='The Safehouse', category='Place', comment='Amazing non-descript secret agent-styled Place & Place. Favorite Place in Wisconsin!')
    createStamp(baseurl=baseurl, user=robby, title='Salt', category='Place', comment='Egg dish and potato -- fantastic brunch! ')
    createStamp(baseurl=baseurl, user=robby, title='Westville', category='Place', comment='The turkey burger is the best <$15 meal in the West Village. ')
    createStamp(baseurl=baseurl, user=travis, title='Temptation Resort', category='Place', comment='Favorite all-inclusive resort in Cancun')
    createStamp(baseurl=baseurl, user=robby, title='Blue Smoke ', category='Place', comment='Standard brisket -- the best BBQ in New York City')
    createStamp(baseurl=baseurl, user=robby, title='Boqueria ', category='Place', comment='Incredible high end Spanish tapas')
    createStamp(baseurl=baseurl, user=robby, title='Pearl Oyster Place', category='Place', comment='Definitively the best lobster role in NYC. Ask anyone. ')
    createStamp(baseurl=baseurl, user=robby, title='Cut the Rope', category='App', comment='Most addictive app that I\'ve played in a long time. ')
    createStamp(baseurl=baseurl, user=kevin, title='Avec', category='Place', comment='Chorizo-stuffed dates wrapped in bacon are still the best. Can\'t recommend this place enough')
    createStamp(baseurl=baseurl, user=robby, title='SPIN NY', category='Place', comment='Really fun place to play pingpong and drink beer. A Place and rec room in one place!')
    createStamp(baseurl=baseurl, user=jake, title='Liveview', category='App', comment='Great way to share mocks with hovering art directors')
    createStamp(baseurl=baseurl, user=jake, title='Diablo Royale', category='Place', comment='Skirt steak tacos -- if only the place was not so packed!')
    createStamp(baseurl=baseurl, user=bart, title='The Departed', category='Film', comment='Makes Boston really cool.')
    createStamp(baseurl=baseurl, user=kevin, title='Lost in Translation', category='Film', comment='Still love it')
    createStamp(baseurl=baseurl, user=travis, title='Waterfront Seafood Grill', category='Place', comment='Great location for an upscale seafood date.')
    createStamp(baseurl=baseurl, user=robby, title='Purple Cow', category='Book', comment='Great book on marketing and the need to be different.')
    createStamp(baseurl=baseurl, user=jake, title='675 Placet', category='Place', comment='Love this low key and trendy Place during the week (too crowded on the weekend).')
    createStamp(baseurl=baseurl, user=travis, title='Vokab Kompany', category='Music', comment=' Best source for chill Socal rap.')
    createStamp(baseurl=baseurl, user=travis, title='Place Solamar', category='Place', comment='Favorite Place in downtown San Diego')
    createStamp(baseurl=baseurl, user=ed, title='The Road', category='Book', comment='Depressed for days after reading it. Seriously good.')
    createStamp(baseurl=baseurl, user=jake, title='Hurt Locker', category='Film', comment='Suffocatingly intense, but one of the best Films of the year. ')
    createStamp(baseurl=baseurl, user=bart, title='Instagram', category='App', comment='Fun, simple way to share photos with friends.')
    createStamp(baseurl=baseurl, user=robby, title='Pulino\'s Place and Pizzeria ', category='Place', comment='Fantastic individual pizza in a scenester environment')
    createStamp(baseurl=baseurl, user=bart, title='The New New Thing', category='Book', comment=' ')
    createStamp(baseurl=baseurl, user=jake, title='Bourbon and Branch', category='Place', comment='Exclusive and low key speak easy in SF. Great bourbon and mixed drink selection. ')
    createStamp(baseurl=baseurl, user=kevin, title='Rockhouse', category='Place', comment='You can jump into the ocean from liff.  Any questions?')
    createStamp(baseurl=baseurl, user=bart, title='Buried Secrets', category='Book', comment='Great thriller for vacation read.  Not beautiful literature but very exciting.')
    createStamp(baseurl=baseurl, user=kevin, title='Compass', category='App', comment='I use this every time I get off the subway.')
    createStamp(baseurl=baseurl, user=bart, title='Paranoia', category='Book', comment='Joseph Finder knows how to write a page-turner. A rare thriller that is also sort of about technology')
    createStamp(baseurl=baseurl, user=bart, title='Rework', category='Book', comment='This is my business bible. These guys are contrarian for sure, but have lots of unique insights.')
    createStamp(baseurl=baseurl, user=bart, title='Pacific Catch', category='Place', comment='Poke bowl is so good and so cheap for what you get.')
    createStamp(baseurl=baseurl, user=robby, title='The Fighter ', category='Film', comment='Honestly, my favorite Film of the year. Christian Bale was spectacular. ')
    createStamp(baseurl=baseurl, user=bart, title='Shutters', category='Place', comment='Such beautiful rooms and right on the beach.  Great place to go with a girlfriend.')
    createStamp(baseurl=baseurl, user=robby, title='Place Griffou', category='Place', comment='Lobster fettuccine -- are you kidding me? Get this. ')
    createStamp(baseurl=baseurl, user=robby, title='X-Men First Class', category='Film', comment='If you love X-Men, you\'ll love this Film. ')
    createStamp(baseurl=baseurl, user=robby, title='1898 Place', category='Place', comment='Really terrific Place in the heart of Placecelona. Great quality and design for the price. ')
    createStamp(baseurl=baseurl, user=bart, title='Brooklyn Bowl', category='Place', comment='Fried chicken is surprisingly incredible.  Oh, and you can bowl too. ')
    createStamp(baseurl=baseurl, user=bart, title='Camera Obscura', category='Music', comment='Really great band for upbeat, indie-pop music. Listen to it all the time when I am going for a walk.')
    createStamp(baseurl=baseurl, user=travis, title='Backgammon NJ', category='App', comment='Best Backgammon app for the iPhone, though I swear the AI cheats...')
    createStamp(baseurl=baseurl, user=bart, title='Vol De Nuit', category='Place', comment='Hidden beer garden in the village. Great spot for a date or a hangout.')
    createStamp(baseurl=baseurl, user=travis, title='Al Forno', category='Place', comment='Amazing wood-burning oven Italian food with an atmosphere to match.')
    createStamp(baseurl=baseurl, user=travis, title='Glitch Mob', category='Music', comment='Favorite dubstep band, hands down.')
    createStamp(baseurl=baseurl, user=kevin, title='Lupe Fiasco', category='Music', comment='The Show Goes On')
    createStamp(baseurl=baseurl, user=bart, title='Funny People', category='Film', comment='One of my favorite Films.  Funny but also serious.  Apatow\'s best.')
    createStamp(baseurl=baseurl, user=travis, title='Cha-Cha', category='Place', comment='Chill / cheap Mexican Place in Capitol Hill.')
    createStamp(baseurl=baseurl, user=kevin, title='Deliveries', category='App', comment='Good place for tracking deliveries.')
    createStamp(baseurl=baseurl, user=bart, title='Place Vitale', category='Place', comment='Best value in SF.  Place is delicious too.')
    createStamp(baseurl=baseurl, user=travis, title='Tilth', category='Place', comment='Favorite healthy breakfast spot in Seattle.')
    createStamp(baseurl=baseurl, user=jake, title='Yank Sing', category='Place', comment='My other of 2 favorite dim sum places in NYC. Higher end place than @Tong Kiang.')
    createStamp(baseurl=baseurl, user=robby, title='Cafe Engelique', category='Place', comment='Israeli Bagal toast with hardboiled egg and pesto.')
    createStamp(baseurl=baseurl, user=robby, title='Old Homestead Steak House', category='Place', comment='Bone in filet, creamed spinach and hashbrowns. Wow. ')
    createStamp(baseurl=baseurl, user=jake, title='A16', category='Place', comment='Best Italian place in SF. Love the Prosciutto pizza, but all are good.  ')
    createStamp(baseurl=baseurl, user=robby, title='Alta ', category='Place', comment='40 types of tapas! "The whole shebang" with 9+ people. Life changing. ')
    createStamp(baseurl=baseurl, user=robby, title='Joseph Leonard ', category='Place', comment='Monk fish with butter sauce and the patte plate. ')
    createStamp(baseurl=baseurl, user=kevin, title='Employees Only', category='Place', comment='Bourbon, egg whites, and a bit of red wine, combined with some bitters and a touch of spice. Seriously amazing.')
    createStamp(baseurl=baseurl, user=robby, title='Kuma Inn', category='Place', comment='This place has unbelievable chinese tapas food. Fantastic for dates. Any pork dish is amazing. Any dish at all is actually amazing. Just go and eat.')
    createStamp(baseurl=baseurl, user=bart, title='The Big Short', category='Book', comment='Fascinating insight into the financial crisis from otally different perspective.')
    createStamp(baseurl=baseurl, user=kevin, title='When Genius Failed', category='Book', comment='Really good book about LTCM and everything that went down. Scary parallels between this and what happened ten years later.')
    createStamp(baseurl=baseurl, user=jake, title='Tong Kiang ', category='Place', comment='One of my 2 favorite dim sum places in NYC. It changed everything. ')
    createStamp(baseurl=baseurl, user=bart, title='Nick\'s Crispy Tacos', category='Place', comment='Get guacemole on them.  They smother it.')
    createStamp(baseurl=baseurl, user=bart, title='Winning the war, losing the peace', category='Book', comment='Best, most informative book on the Iraq war I\'ve ever read.')
    createStamp(baseurl=baseurl, user=travis, title='Bathtub Gin Co', category='Place', comment='Swanky speakeasy where quality gin runs like water.')
    createStamp(baseurl=baseurl, user=bart, title='Old Pro', category='Place', comment='Burger is delicious.')
    createStamp(baseurl=baseurl, user=jake, title='Slanted Door', category='Place', comment='Fantastic dungeness crab pasta. ')
    createStamp(baseurl=baseurl, user=jake, title='Pizza Delphina ', category='Place', comment='Incredible Neapolitan style pizzas. Go to Ritual coffee nextdoor after.  ')
    createStamp(baseurl=baseurl, user=jake, title='Milk (The Film)', category='Film', comment='One of my top 3 favorite Films of all time. Touching storytelling. ')
    createStamp(baseurl=baseurl, user=bart, title='Just Friends', category='Film', comment='It\'s not going to win an Oscar, but if a girl has ever put you in the friend-zone, you should watch this.')
    createStamp(baseurl=baseurl, user=bart, title='Tickle Pink Inn', category='Place', comment='1.5 hr drive from and a different world.  Free wine and cheese at 4:30 is enough for a meal.')
    createStamp(baseurl=baseurl, user=robby, title='Blue Hill', category='Place', comment='Egg appetizer and whole crispy chicken.  ')
    createStamp(baseurl=baseurl, user=kevin, title='The James Hotel', category='Place', comment='Best hotel in the city')
    createStamp(baseurl=baseurl, user=robby, title='Ariana Afghan Kebab Place', category='Place', comment='Kabuli palow and kabobs -- great price for the place. ')
    createStamp(baseurl=baseurl, user=jake, title='Pacific Catch', category='Place', comment='Fantastic fish tacos -- but really small beware. Go if you\'ve never been. ')
    createStamp(baseurl=baseurl, user=robby, title='Stamped', category='App', comment='This is the best app on the market. ')
    toRestamp = createStamp(baseurl=baseurl, user=robby, title='The Breslin', category='Place', comment='The lamb burger or the entire pig feast with large groups. ')
    createStamp(baseurl=baseurl, user=ed, title='Freedom', category='Book', comment='Worthy follow-up to The Corrections.  ')
    createStamp(baseurl=baseurl, user=bart, title='Four Seasons Boston', category='Place', comment='If you want to spend a lot of money, this Place is extremely nice.  Gorgeous pool overlooking the park.')
    createStamp(baseurl=baseurl, user=travis, title='Phantogram', category='Music', comment='Softer electronica with a perfect blend of harder beats mixed in.')
    createStamp(baseurl=baseurl, user=robby, title='DGBG', category='Place', comment='Frenchie burger and Thai sausage appetizer ')
    createStamp(baseurl=baseurl, user=robby, title='Rickhouse', category='Place', comment='Fantastic bourbon selection from  floor to the ceiling (literally). Great for low key drinks')
    createStamp(baseurl=baseurl, user=jake, title='Empire Place', category='Place', comment='Great Place in uptown that\'s trendy and high quality for the price. Use the Google discount.')
    createStamp(baseurl=baseurl, user=bart, title='The Last Waltz', category='Music', comment='Great album and great DVD.  One of the best bands ever.')
    createStamp(baseurl=baseurl, user=kevin, title='Winter\'s Tale', category='Book', comment='You would love this.')
    stampID = createStamp(baseurl=baseurl, user=bart, title='Timer', category='Film', comment='Indie Film that makes really interesting points about relationships.  Not incredible but very thought-provoking.')       
    createStamp(baseurl=baseurl, user=robby, title='The Elegant Universe', category='Book', comment='This books makes me feel smart.')
    createStamp(baseurl=baseurl, user=bart, title='The Tipsy Pig', category='Place', comment='Mac and cheese and burger.  Incredible.')
    
    
    ## COMMENTS

    path = "comments/create.json"
    data = {
        "authenticated_user_id": ed,
        "stamp_id": stampID,
        "blurb": "If it's not incredible, why are you stamping it? You're using this product all wrong!"
    }
    commentID = testPOST(baseurl, path, data)['comment_id']
    if len(commentID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception

    path = "comments/create.json"
    data = {
        "authenticated_user_id": bart,
        "stamp_id": stampID,
        "blurb": "Yeah, my bad..."
    }
    commentID = testPOST(baseurl, path, data)['comment_id']
    if len(commentID) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
        
        
    ## RESTAMP
    
    path = "stamps/show.json"
    data = {
        "authenticated_user_id": kevin,
        "stamp_id": toRestamp
    }
    restamp = testGET(baseurl, path, data)
    if len(restamp['stamp_id']) == 24:
        print 'PASS: %s' % path
    else:
        print 'result: %s' % path
        print result
        raise Exception
    
    
    path = "stamps/create.json"
    data = {
        "authenticated_user_id": kevin,
        "entity_id": restamp['entity']['entity_id'],
        "blurb": "Lamb burger rocked my world.",
        "credit": 'sample_robby'
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
