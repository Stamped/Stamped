#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs
import os, json, mimetools, sys, urllib, urllib2
import datetime, time, random, hashlib, string
import random
import copy

from errors import *


class DoneException(Exception):
    pass

class RootException(Exception):
    pass

"""
HTTP Helper Functions
"""

baseurl = "https://dev.stamped.com/v1"
baseurl = "http://localhost:18000/v1"

class StampedAPIURLOpener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('iphone8@2x', 'LnIFbmL0a75G8iQeHCV8VOT4fWFAWhzu')
opener = StampedAPIURLOpener()

def handleGET(path, data, handleExceptions=True):
    params = urllib.urlencode(data)
    url    = "%s/%s?%s" % (baseurl, path, params)
    
    raw = opener.open(url).read()
    # logs.info("GET: %s" % url)
    
    try:
        result = json.loads(raw)
    except Exception:
        raise StampedAPIException(raw)

    if handleExceptions and 'error' in result:
        raise Exception("GET failed: \n  URI:   %s \n  Form:  %s \n  Error: %s" % (path, data, result))
    
    return result

def handlePOST(path, data, handleExceptions=True):
    params = urllib.urlencode(data)
    url    = "%s/%s" % (baseurl, path)
    
    raw = opener.open(url, params).read()
    # logs.info("POST: %s" % url)
    
    try:
        result = json.loads(raw)
    except:
        raise StampedAPIException(raw)

    if handleExceptions and 'error' in result:
        raise Exception("POST failed: \n  URI:   %s \n  Form:  %s \n  Error: %s" % (path, data, result))
    
    return result


"""

### ACCOUNT

(r'v1/account/linked/show.json',                        'v0.functions.linked.show'),

### ACTIONS
(r'v1/actions/complete.json',                           'v0.functions.entities.completeAction'),


### COMMENTS
(r'v1/comments/create.json',                            'v0.functions.comments.create'),
(r'v1/comments/remove.json',                            'v0.functions.comments.remove'),
(r'v1/comments/collection.json',                        'v0.functions.comments.collection'),

### TODOS
(r'v1/todos/create.json',                               'v0.functions.todos.create'),
(r'v1/todos/complete.json',                             'v0.functions.todos.complete'),
(r'v1/todos/remove.json',                               'v0.functions.todos.remove'),
(r'v1/todos/collection.json',                           'v0.functions.todos.collection'),

### ACTIVITY
(r'v1/activity/collection.json',                        'v0.functions.activity.collection'),
(r'v1/activity/unread.json',                            'v0.functions.activity.unread'),
"""

### OAUTH

# /oauth2/token.json
def _post_oauth2_login(screenName, password):
    params = {
        'login': screenName,
        'password': password,
    }
    
    return handlePOST('oauth2/login.json', params)

# /oauth2/token.json
def _post_oauth2_token(refreshToken):
    params = {
        'refresh_token': refreshToken,
        'grant_type': 'refresh_token',
    }
    
    return handlePOST('oauth2/token.json', params)


### ACCOUNT

# /account/create.json
def _post_account_create(screenName, phone=None, bio=None, website=None, location=None, colorPrimary=None, 
                            colorSecondary=None, tempImageUrl=None):
    params = {
        'name': 'User %s' % screenName,
        'screen_name': screenName,
        'email': '%s@stamped.com' % screenName,
        'password': '12345',
    }
    
    if phone is not None:
        params['phone'] = phone
    
    if bio is not None:
        params['bio'] = bio 
    
    if website is not None:
        params['website'] = website
    
    if location is not None:
        params['location'] = location
    
    if colorPrimary is not None:
        params['color_primary'] = colorPrimary
    
    if colorSecondary is not None:
        params['color_secondary'] = colorSecondary
    
    if tempImageUrl is not None:
        params['temp_image_url'] = tempImageUrl
    
    return handlePOST('account/create.json', params)

# /account/remove.json
def _post_account_remove(token):
    raise NotImplementedError

# /account/update.json
def _post_account_update(token, name=None, screenName=None, phone=None, bio=None, website=None, location=None, 
                            colorPrimary=None, colorSecondary=None, tempImageUrl=None):
    params = {
        'oauth_token': token,
    }
    
    if name is not None:
        params['name'] = name 
    
    if screenName is not None:
        params['screen_name'] = screenName
    
    if phone is not None:
        params['phone'] = phone
    
    if bio is not None:
        params['bio'] = bio 
    
    if website is not None:
        params['website'] = website
    
    if location is not None:
        params['location'] = location
    
    if colorPrimary is not None:
        params['color_primary'] = colorPrimary
    
    if colorSecondary is not None:
        params['color_secondary'] = colorSecondary
    
    if tempImageUrl is not None:
        params['temp_image_url'] = tempImageUrl
    
    return handlePOST('account/update.json', params)

# /acount/show.json
def _get_account_show(token):
    params = {
        'oauth_token': token,
    }
    
    return handleGET('account/show.json', params)

# /account/check.json
def _post_account_check(login):
    params = {
        'login': login
    }
    
    return handlePOST('account/check.json', params)

# /account/customize_stamp.json
def _post_account_customize_stamp(token, colorPrimary, colorSecondary):
    params = {
        'oauth_token': token,
        'color_primary': colorPrimary,
        'color_secondary': colorSecondary,
    }
    
    return handlePOST('account/customize_stamp.json', params)

# /account/alerts/show.json
def _get_account_alerts_show(token):
    params = {
        'oauth_token': token,
    }
    
    return handleGET('account/alerts/show.json', params)

# /account/alerts/update.json
def _post_account_alerts_update(token, **kwargs):
    raise NotImplementedError

# /account/alerts/ios/update.json
def _post_account_alerts_ios_update(token, apns):
    params = {
        'oauth_token': token,
        'token': apns,
    }
    
    return handlePOST('account/alerts/ios/update.json', params)

# /account/alerts/update.json
def _post_account_alerts_ios_remove(token, **kwargs):
    raise NotImplementedError


### USERS

# /users/show.json
def _get_users_show(userId, token=None):
    params = {
        'user_id': userId,
    }
    
    if token is not None:
        params['oauth_token'] = token
    
    return handleGET('users/show.json', params)

# /users/lookup.json
def _post_users_lookup(userIds, token=None):
    params = {
        'user_ids': ','.join(userIds)
    }
    
    if token is not None:
        params['oauth_token'] = token
    
    return handlePOST('users/lookup.json', params)

# /users/search.json
def _post_users_search(token, query, limit=20, relationship=None):
    params = {
        'oauth_token': token,
        'query': query,
        'limit': limit,
    }
    
    if relationship is not None:
        params['relationship'] = relationship
    
    return handlePOST('users/search.json', params)

# /users/suggested.json
def _get_users_suggested(token, limit=20, offset=0):
    params = {
        'oauth_token': token,
        'limit': limit,
        'offset': offset,
    }
    
    return handleGET('users/suggested.json', params)

# /users/find/email.json
def _post_users_find_email(token, query):
    raise NotImplementedError

# /users/find/phone.json
def _post_users_find_phone(token, query):
    raise NotImplementedError

# /users/find/twitter.json
def _get_users_find_twitter(token, query):
    raise NotImplementedError

# /users/find/facebook.json
def _get_users_find_facebook(token, query):
    raise NotImplementedError

# /users/invite/facebook/collection.json
def _post_users_invite_facebook_collection(token, **kwargs):
    raise NotImplementedError

# /users/invite/twitter/collection.json
def _post_users_invite_twitter_collection(token, **kwargs):
    raise NotImplementedError

# /users/invite/email.json
def _post_users_invite_email(token, **kwargs):
    raise NotImplementedError


### FRIENDS

# /friendships/create.json
def _post_friendships_create(token, userId):
    params = {
        'oauth_token': token,
        'user_id': userId,
    }
    
    return handlePOST('friendships/create.json', params)

# /friendships/remove.json
def _post_friendships_remove(token, userId):
    params = {
        'oauth_token': token,
        'user_id': userId,
    }
    
    return handlePOST('friendships/remove.json', params)

# /friendships/check.json
def _get_friendships_check(token, userIdA, userIdB):
    params = {
        'oauth_token': token,
        'user_id_a': userIdA,
        'user_id_b': userIdB,
    }
    
    return handleGET('friendships/check.json', params)

# /friendships/friends.json
def _get_friendships_friends(userId, token=None):
    params = {
        'user_id': userId,
    }
    
    if token is not None:
        params['oauth_token'] = token
    
    return handleGET('friendships/friends.json', params)

# /friendships/followers.json
def _get_friendships_followers(userId, token=None):
    params = {
        'user_id': userId,
    }
    
    if token is not None:
        params['oauth_token'] = token
    
    return handleGET('friendships/followers.json', params)

# /friendships/invite.json
def _post_friendships_invite(token, userId):
    raise NotImplementedError


### ENTITIES

# /entities/create.json
def _post_entities_create(token, **kwargs):
    raise NotImplementedError

# /entities/remove.json
def _post_entities_remove(token, **kwargs):
    raise NotImplementedError

# /entities/show.json
def _get_entities_show(entityId, token=None):
    params = {
        'entity_id': entityId,
    }
    
    if token is not None:
        params['oauth_token'] = token
    
    return handleGET('entities/show.json', params)

# /entities/autosuggest.json
def _get_entities_autosuggest(category, query, coordinates=None):
    params = {
        'query': query,
        'category': category,
    }
    
    if coordinates is not None:
        params['coordinates'] = coordinates
    
    return handleGET('entities/autosuggest.json', params)

# /entities/search.json
def _get_entities_search(token, query, category, coordinates=None):
    params = {
        'oauth_token': token,
        'query': query,
        'category': category,
    }
    
    if coordinates is not None:
        params['coordinates'] = coordinates
    
    return handleGET('entities/search.json', params)

# /entities/suggested.json
def _get_entities_suggested(token, category, coordinates=None):
    params = {
        'oauth_token': token,
        'category': category,
    }
    
    if coordinates is not None:
        params['coordinates'] = coordinates
    
    return handleGET('entities/suggested.json', params)

# /entities/menu.json
def _get_entities_menu(entityId, token=None):
    params = {
        'entity_id': entityId,
    }
    
    if token is not None:
        params['oauth_token'] = token
    
    return handleGET('entities/menu.json', params)

# /entities/stamped_by.json
def _get_entities_stamped_by(entityId, token=None):
    params = {
        'entity_id': entityId,
    }
    
    if token is not None:
        params['oauth_token'] = token
    
    return handleGET('entities/stamped_by.json', params)


### STAMPS

# /stamps/create.json
def _post_stamps_create(token, entityId, blurb=None, credits=None):
    params = {
        'oauth_token': token,
        'entity_id': entityId,
    }
    
    if blurb is not None:
        params['blurb'] = blurb
    
    if credits is not None:
        params['credits'] = credits
    
    return handlePOST('stamps/create.json', params)

# /stamps/show.json
def _get_stamps_show(stampId, token=None):
    params = {
        'stamp_id': stampId,
    }
    if token is not None:
        params['oauth_token'] = token
        
    return handleGET('stamps/show.json', params)
    

# /stamps/share/facebook.json
def _post_stamps_share_facebook(token, stampId):
    raise NotImplementedError

# /stamps/remove.json
def _post_stamps_remove(token, stampId):
    params = {
        'oauth_token': token,
        'stamp_id': stampId,
    }
    
    return handlePOST('stamps/remove.json', params)

# /stamps/collection.json
def _get_stamps_collection(scope, token=None, limit=20, before=None, offset=None, 
                            userId=None, category=None, viewport=None):
    params = {
        'scope': scope,
        'limit': limit,
    }
    if token is not None:
        params['oauth_token'] = token
        
    if before is not None:
        params['before'] = before
        
    if offset is not None:
        params['offset'] = offset
        
    if userId is not None:
        params['user_id'] = userId
        
    if category is not None:
        params['category'] = category
        
    if viewport is not None:
        params['viewport'] = viewport
    
    return handleGET('stamps/collection.json', params)

# /stamps/search.json
def _get_stamps_search(scope, query, token=None, limit=20, before=None, offset=None, 
                        userId=None, category=None, viewport=None):
    params = {
        'scope': scope,
        'query': query,
        'limit': limit,
    }
    if token is not None:
        params['oauth_token'] = token
        
    if before is not None:
        params['before'] = before
        
    if offset is not None:
        params['offset'] = offset
        
    if userId is not None:
        params['user_id'] = userId
        
    if category is not None:
        params['category'] = category
        
    if viewport is not None:
        params['viewport'] = viewport
    
    return handleGET('stamps/search.json', params)

# /stamps/likes/create.json
def _post_stamps_likes_create(token, stampId):
    params = {
        'oauth_token': token,
        'stamp_id': stampId,
    }
    
    return handlePOST('stamps/likes/create.json', params)

# /stamps/likes/remove.json
def _post_stamps_likes_remove(token, stampId):
    params = {
        'oauth_token': token,
        'stamp_id': stampId,
    }
    
    return handlePOST('stamps/likes/remove.json', params)


### GUIDE

# /guide/collection.json
def _get_guide_collection(scope, section, subsection=None, viewport=None, offset=0, limit=20, token=None):
    params = {
        'scope': scope,
        'section': section,
        'offset': offset,
        'limit': limit,
    }
    
    if subsection is not None:
        params['subsection'] = subsection
    
    if viewport is not None:
        params['viewport'] = viewport
    
    if token is not None:
        params['token'] = token
    
    return handleGET('guide/collection.json', params)

# /guide/search.json
def _get_guide_search(scope, section, query, subsection=None, viewport=None, offset=0, limit=20, token=None):
    params = {
        'scope': scope,
        'section': section,
        'query': query,
        'offset': offset,
        'limit': limit,
    }
    
    if subsection is not None:
        params['subsection'] = subsection
    
    if viewport is not None:
        params['viewport'] = viewport
    
    if token is not None:
        params['token'] = token
    
    return handleGET('guide/search.json', params)














def generateToken(length):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for x in xrange(length))
    
randomScreenNames = ['robby','bart','kevin','jstaehle']



###########################
##### User simulation #####
###########################

#Base user class - Should not be called directly
class User(object):
    def __init__(self):
        self.token = None
        self.userId = None
        self.expiration = None
        self._userSessionLength = None
        self._userWaitSpeed = None

        self._stack = []

    # Start and root defined in subclasses
    def start(self):
        raise NotImplementedError

    def root(self):
        raise NotImplementedError

    def _runAction(self, actions, weights):
        while datetime.datetime.utcnow() < self.expiration:
            try:
                totalWeight = sum(v for k, v in weights.items())
                cumulativeWeight = 0
                r = random.randint(0, totalWeight)

                for key, weight in weights.items():
                    if r < weight:
                        logs.debug("%sCHOSE ACTION: %s" % ((' '*2*len(self._stack)), key))
                        if key != 'pass':
                            self._stack.append(key)
                        break
                    r -= weight
                actions[key]()

            except DoneException:
                print self._stack
                action = self._stack.pop()
                logs.debug("%s  DONE: %s" % ((' '*2*len(self._stack)), action))
                print self._stack
                # logs.debug("STACK LENGTH: %s" % len(self._stack))
                raise
            except RootException:
                logs.debug("GOING TO ROOT")
                raise

    # Functions for viewing different pages in the stamped app
    def viewStampDetail(self, stamp=None, stampId=None):
        logs.debug("%sView Stamp Detail" % (' '*2*len(self._stack)))
        print self._stack

        """
        Make API calls
        """
        if stampId is not None:
            stamp = _get_stamps_show(stampId, token=self.token)

        assert stamp is not None 

        stampId = stamp['stamp_id']
        entityId = stamp['entity']['entity_id']
        entity = _get_entities_show(entityId, token=self.token)
        alsoStampedBy = _get_entities_stamped_by(entityId, token=self.token)

        """
        Define possible actions the user can take, including wait time
        """
        actions = {}
        weights = {}

        # Go back to inbox
        def _pass():
            time.sleep(random.randint(4, 12) * self._userWaitSpeed)
            raise DoneException("Done!")

        actions['pass'] = _pass
        weights['pass'] = 5

        # View the user's profile
        def _viewProfile():
            time.sleep(random.randint(4, 12) * self._userWaitSpeed)
            try:
                return self.viewProfile(userId=stamp['user']['user_id'])
            except DoneException:
                if random.random() < 0.3:
                    raise

        actions['profile'] = _viewProfile
        weights['profile'] = 20

        # View a credit given to the stamp
        if 'previews' in stamp and stamp['previews'] is not None:
            previews = stamp['previews']
            if 'credits' in previews and previews['credits'] is not None and len(previews['credits']) > 0:
                def _viewCredit():
                    time.sleep(random.randint(4, 12) * self._userWaitSpeed)
                    return self.viewProfile(stampId=random.choice(previews['credits'])['stamp_id'])
            
                actions['credit'] = _viewCredit
                weights['credit'] = 1

        # View the profile of a commenting user
        if 'previews' in stamp and stamp['previews'] is not None:
            previews = stamp['previews']
            if 'comments' in previews and previews['comments'] is not None and len(previews['comments']) > 0:
                def _viewComment():
                    time.sleep(random.randint(4, 12) * self._userWaitSpeed)
                    return self.viewProfile(userId=random.choice(previews['comments'])['user']['user_id'])

                actions['comment'] = _viewComment
                weights['comment'] = 1

        assert len(actions) == len(weights)

        """
        Run the actions
        """
        return self._runAction(actions, weights)

    # Function to simulate the viewing of a profile. Takes a user id and fromAddFriends, a boolean 
    # denoting whether or not the profile was viewed from the Add Friends page
    def viewProfile(self, userId, fromAddFriends=False):
        logs.debug("%sView Profile (%s)" % ((' '*2*len(self._stack)), userId))
        print self._stack

        #Initial API Calls
        user = _get_users_show(userId)
        userStamps = _get_stamps_collection(scope='user', userId=userId, token=self.token)

        """
        Define possible actions the user can take, including wait time
        """
        actions = {}
        weights = {}

        # Go back
        def _pass():
            time.sleep(random.randint(4, 12) * self._userWaitSpeed)
            raise DoneException("Done!")

        actions['pass'] = _pass
        weights['pass'] = 50

        # View stamp
        def _viewStamp():
            time.sleep(random.randint(4, 12) * self._userWaitSpeed)
            try:
                return self.viewStampDetail(stamp=userStamps[0])
            except DoneException:
                if random.random() < 0.75:
                    raise

        actions['stamp'] = _viewStamp
        weights['stamp'] = 10

        assert len(actions) == len(weights)

        """
        Run the actions
        """
        return self._runAction(actions, weights)


    # def viewAddFriends(self,tastemakersToFollow=None,screenNamesToFollow=[]):
    #     logs.debug("View Add Friends")

    #     #Initial API Call
    #     suggested = _get_users_suggested(self.token)
    #     friends = []
        
    #     # Wait
    #     expectedWaitTime = 5
    #     time.sleep(random.random() * expectedWaitTime * self._userWaitSpeed)
        
    #     # Follow some tastemakers
    #     for i in range (0,tastemakersToFollow):
    #         r = random.random()

    #         tastemaker = suggested[int(random.random() * len(suggested))]
    #         if r < 0.2:
    #             self.viewProfile(tastemaker[user_id],fromAddFriends=True)
            
    #         friends.append(_post_friendships_create(self.token, tastemaker[user_id]))


    #     #Search for some friends and follow them
    #     for screenName in screenNamesToFollow:
    #         users = _post_users_search(self.token, screenName)
    #         if len(users) > 0:
    #             r = random.random()
    #             if r < 0.2:
    #                 self.viewProfile(users[0][user_id],fromAddFriends=True)
    #             friends.append(_post_friendships_create(self.token,users[0][user_id]))

    #     return friends
        
    # Inbox Functions

    def viewTastemakerInbox(self, offset=0):
        logs.debug("%sView Tastemaker Inbox" % (' '*2*len(self._stack)))
        
        # API Calls
        stamps = []
        stamps += _get_stamps_collection(scope='popular', offset=offset)
        offset += 20
        stamps += _get_stamps_collection(scope='popular', offset=offset)
        offset += 20

        """
        Define possible actions the user can take, including wait time
        """
        actions = {}
        weights = {}

        # Go back to root
        def _pass():
            time.sleep(random.randint(4, 12) * self._userWaitSpeed)
            print 'RAISE PASS FROM INBOX'
            raise DoneException("Done!")

        actions['pass'] = _pass
        weights['pass'] = 2

        # View the user's profile
        def _viewStamp():
            time.sleep(random.randint(2, 6) * self._userWaitSpeed)
            try:
                return self.viewStampDetail(stamp=random.choice(stamps))
            except DoneException:
                if random.random() < 0.3:
                    print 'RAISE VIEW STAMP FROM INBOX'
                    raise

        actions['stamp'] = _viewStamp
        weights['stamp'] = 20

        # Load more stamps
        def _page():
            time.sleep(random.randint(1, 2) * self._userWaitSpeed)
            stamps += _get_stamps_collection(scope='popular', offset=offset)
            offset += 20

        actions['page'] = _page
        weights['page'] = 0

        assert len(actions) == len(weights)

        """
        Run the actions
        """
        return self._runAction(actions, weights)


    def viewInbox(self,offset=None):
        if offset is not None:
            raise NotImplementedError
        stamps = _get_stamps_collection(scope='inbox',token=self.token)
        return stamps
        

    # Guide functions

    def viewGuide(self):
        # No API calls on main guide page
        
        # Wait (user is studying the options)
        expectedWaitTime = 4
        time.sleep(random.random() * expectedWaitTime * self._userWaitSpeed)

        while datetime.datetime.utcnow() < self.expiration:
            try: 
                r = random.random()
                if r < 0.2:
                    self.viewPlacesGuide()
                elif r < 0.35:
                    self.viewBookGuide()
                elif r < 0.6:
                    self.viewMusicGuide()
                elif r < 0.8:
                    self.viewMovieGuide()
                elif r < 0.9:
                    self.viewSoftwareGuide()
                else:
                    raise DoneException
            except DoneException:
                if random.random() < 0.5:
                    continue
                if random.random() < 0.9:
                    return
                raise

        
    # TODO for all of these: Implement paging

    def viewPlacesGuide(self, scope='inbox'):
        
        if self.token == None:
            scope = 'popular'

        # API Calls
        guide = _get_guide_collection(scope=scope, section='food', token=self.token)
        
        # Wait
        expectedWaitTime = 4
        time.sleep(random.random() * expectedWaitTime * self._userWaitSpeed)
        
        return guide

    def viewBookGuide(self, scope='inbox'):
        
        if self.token == None:
            scope = 'popular'

        # API Calls
        guide = _get_guide_collection(scope=scope, section='book', token=self.token)
        
        # Wait
        expectedWaitTime = 4
        time.sleep(random.random() * expectedWaitTime * self._userWaitSpeed)
        
        return guide

    def viewMusicGuide(self, scope='inbox'):
        
        if self.token == None:
            scope = 'popular'

        # API Calls
        guide = _get_guide_collection(scope=scope, section='music', token=self.token)
        
        # Wait
        expectedWaitTime = 4
        time.sleep(random.random() * expectedWaitTime * self._userWaitSpeed)
        
        return guide

    def viewMovieGuide(self,scope='inbox'):
        
        if self.token == None:
            scope = 'popular'

        # API Calls
        guide = _get_guide_collection(scope=scope, section='film', token=self.token)
        
        # Wait
        expectedWaitTime = 4
        time.sleep(random.random() * expectedWaitTime * self._userWaitSpeed)
        
        return guide

    def viewSoftwareGuide(self, scope='inbox'):
        
        if self.token == None:
            scope = 'popular'

        # API Calls
        guide = _get_guide_collection(scope=scope, section='app', token=self.token)
        
        # Wait
        expectedWaitTime = 4
        time.sleep(random.random() * expectedWaitTime * self._userWaitSpeed)
        
        return guide



    #Other

    def viewEdetail(self):
        print "view eDetail"
        pass
        
    def viewActivity(self):
        print "view Activity"
        pass
        
    def viewTodoList(self):
        print "view Todos"
        pass
        
    def viewSettings(self):
        print "view settings"
        pass
        
    def viewCreditsStampList(self):
        print "view credits stamp list"
        pass


# Specific instances of different types of users


# Base class for a user creating a new account - should not be called directly
class NewUser(User):
    def __init__(self):
        User.__init__(self)
        self.createAccountAndLogin()
            
    def createAccountAndLogin(self):
        screenName = generateToken(19)
        
        #Create account
        _post_account_create(screenName)
        
        #Login to that account
        user, token = _post_oauth2_login(screenName, "12345")
        self.token = token
        self.userId = user[user_id]


# Base class for a user with an existing account - should not be called directly
class ExistingUser(User):
    def __init__(self,screenName=None):
        User.__init__(self)
        
        if screenName is not None:
            self.login()
            
    def login(self):
        user, token = _post_oauth2_login(self.screen_name, "12345")
        self.token = token
        self.userId = user[user_id]



# Class representing users who do not log in or create an account throughout their session
class LoggedOutUser(User):

    def __init__(self):
        User.__init__(self)
        self._userWaitSpeed = 0
        self._userSessionLength = 30 #200 + (random.random() * 200)
        
    def start(self):
        logs.debug("Begin: %s" % self)

        self.expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._userSessionLength)
        logs.debug("Expiration: %s" % self.expiration)




        """
        Define possible actions the user can take, including wait time
        """
        actions = {}
        weights = {}

        # View the user's profile
        def _viewInbox():
            return self.viewTastemakerInbox()

        actions['inbox'] = _viewInbox
        weights['inbox'] = 20

        assert len(actions) == len(weights)

        """
        Run the actions
        """
        return self._runAction(actions, weights)







    #     # Start out in the inbox
    #     try:
    #         self.viewTastemakerInbox()
    #     except DoneException:
    #         pass
        
    #     # Move to root menu upon return or exception
    #     while datetime.datetime.utcnow() < self.expiration:
    #         self.root()

    #     logs.debug("Finish: %s" % self)
            
    # def root(self):
    #     logs.debug("ROOT")
    #     self._stack = []

    #     r = random.random()
    #     try:
    #         if r < 0.0:
    #             self.viewGuide()
    #         else:
    #             self.viewTastemakerInbox()

    #     except DoneException:
    #         pass
        
# Class representing either a new or existing user who 
class PowerUser(ExistingUser):
    def __init__(self, bExisting, screenName=None):
        if bExisting:
            self.existing = True
            ExistingUser.__init__(self, screenName=screenName)
        else:
            NewUser.__init__(self)
            self.existing = False
        self._userWaitSpeed = 0.8
        self._userSessionLength = 750 + (random.random() * 500)

    def start(self):
        self.expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._userSessionLength)
        
        #New users add friends (5 tastemakers and 5 random friends)
        if self.existing:
            try:
                friendsToAdd = set()
                while len(friendsToAdd) < 5:
                    friendsToAdd.add(randomScreenNames[int(random.random() * len(randomScreenNames))])
                self.viewAddFriends(tastemakersToFollow=5,sreenNamesToFollow=friendsToAdd)
            except DoneException:
                pass
        
        #Start out in the inbox
        try:
            self.viewInbox()
        except DoneException:
            pass
        
        #Move to root menu upon return or exception
        while datetime.datetime.utcnow() < self.expiration:
            self.root()

    def root(self):     
        r = random.random()
        try:
            if r < 0.2:
                self.viewInbox()
            elif r < 0.7:
                self.viewGuide()
            elif r < 0.8:
                self.viewActivity()
            elif r < 0.85:
                self.viewTodoList()
            elif r < 0.9:
                self.viewAddFriends()
            elif r < 0.95:
                self.viewProfile()
            else:
                self.viewSettings()
        except DoneException:
            pass

#Class representing a fan of justin beiber (or other tastemaker)
class BeiberUser(NewUser):
    def __init__(self):
        NewUser.__init__(self)
        self._userWaitSpeed = 1
        self._userSessionLength = 750 + (random.random() * 500)
    
    def start(self):
        self.expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._userSessionLength)
        
        try:
            self.viewAddFriends(tastemakersToFollow = 6)
        except DoneException:
            pass
            
        #Start out in the inbox
        try:
            self.viewInbox()
        except DoneException:
            pass
        
        #Move to root menu upon return or exception
        while datetime.datetime.utcnow() < self.expiration:
            self.root()

    def root(self):     
        r = random.random()
        try:
            if r < 0.3:
                self.viewInbox()
            elif r < 0.8:
                self.viewGuide()
            elif r < 0.85:
                self.viewActivity()
            elif r < 0.9:
                self.viewSettings()
            else:
                self.viewAddFriends()

        except DoneException:
            pass

class CasualUser(ExistingUser):
    def __init__(self,bExisting,screenName=None):
        if bExisting:
            ExistingUser.__init__(self, screenName=screenName)
            self.existing = True
        else:
            NewUser.__init__(self)
            self.existing = False
        self._userWaitSpeed = 1.25
        self._userSessionLength = 300 + (random.random() * 300)

        #New users add friends (3 tastemakers and 2 random friends)
        if self.existing:
            try:
                friendsToAdd = set()
                while len(friendsToAdd) < 2:
                    friendsToAdd.add(randomScreenNames[int(random.random() * len(randomScreenNames))])
                self.viewAddFriends(tastemakersToFollow=3,sreenNamesToFollow=friendsToAdd)
            except DoneException:
                pass

    def start(self):
        self.expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._userSessionLength)
        #Start out in the inbox
        try:
            self.viewInbox()
        except DoneException:
            pass
        
        #Move to root menu upon return or exception
        while datetime.datetime.utcnow() < self.expiration:
            self.root()

    def root(self):     
        r = random.random()
        try:
            if r < 0.4:
                self.viewInbox()
            elif r < 0.4:
                self.viewGuide()
            elif r < 0.95:
                self.viewActivity()
            else:
                self.viewSettings()
        except DoneException:
            pass



user = LoggedOutUser()
user.start()
print 'DONE'
