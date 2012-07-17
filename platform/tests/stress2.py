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

class ContinueException(Exception):
    pass

class DoneException(Exception):
    pass

class FinishedException(Exception):
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

coordinates = [
    (42.667, 73.75), (35.083, 106.65), (35.183, 101.83), (61.21667, 149.9), (33.75, 84.383), (30.267, 97.733), 
    (44.783, 117.83), (39.3, 76.633), (44.8, 68.783), (33.5, 86.833), (46.8, 100.7833), (43.6, 116.2167), 
    (42.35, 71.083), (42.91667, 78.833), (51.01667, 114.0167), (32.433, 104.25), (32.783, 79.933), (38.35, 81.633), 
    (35.233, 80.833), (41.15, 104.8667), (41.833, 87.61667), (39.133, 84.5), (41.467, 81.61667), (34, 81.033), 
    (40, 83.01667), (32.767, 96.767), (39.75, 105), (41.583, 93.61667), (42.3, 83.05), (42.51667, 90.667), 
    (46.81667, 92.083), (44.9, 67), (53.567, 113.4667), (32.633, 115.55), (31.767, 106.4833), (44.05, 123.0833), 
    (46.867, 96.8), (35.21667, 111.6833), (32.71667, 97.31667), (36.733, 119.8), (39.083, 108.55), (42.967, 85.667), 
    (48.55, 109.7167), (46.583, 112.03), (21.3, 157.83), (34.51667, 93.05), (29.75, 95.35), (43.5, 112.0167), 
    (39.767, 86.167), (32.3, 90.2), (30.367, 81.667), (58.3, 134.4), (39.1, 94.583), (24.55, 81.8), 
    (44.25, 76.5), (42.167, 121.73), (35.95, 83.933), (36.167, 115.2), (46.4, 117.03), (40.833, 96.667), 
    (43.033, 81.567), (33.767, 118.1833), (34.05, 118.25), (38.25, 85.767), (43, 71.5), (35.15, 90.05), 
    (25.767, 80.2), (43.033, 87.91667), (44.983, 93.233), (30.7, 88.05), (32.35, 86.3), (44.25, 72.533), 
    (45.5, 73.583), (50.61667, 105.5167), (36.167, 86.783), (49.5, 117.2833), (40.733, 74.167), (41.31667, 72.91667), 
    (29.95, 90.067), (40.783, 73.967), (64.41667, 165.5), (37.8, 122.2667), (35.433, 97.467), (41.25, 95.933), 
    (45.4, 75.71667), (39.95, 75.167), (33.483, 112.0667), (44.367, 100.35), (40.45, 79.95), (43.667, 70.25), 
    (45.51667, 122.6833), (41.833, 71.4), (46.81667, 71.183), (35.767, 78.65), (39.5, 119.8167), (38.767, 112.0833), 
    (37.55, 77.483), (37.283, 79.95), (38.583, 121.5), (45.3, 66.167), (38.583, 90.2), (40.767, 111.9), 
    (29.383, 98.55), (32.7, 117.1667), (37.783, 122.43), (37.3, 121.8833), (18.5, 66.167), (35.683, 105.95), 
    (32.083, 81.083), (47.61667, 122.33), (32.467, 93.7), (43.55, 96.733), (57.167, 135.25), (47.667, 117.43), 
    (39.8, 89.633), (42.1, 72.567), (37.21667, 93.283), (43.033, 76.133), (27.95, 82.45), (41.65, 83.55), 
    (43.667, 79.4), (36.15, 95.983), (49.21667, 123.1), (48.41667, 123.35), (36.85, 75.967), (38.883, 77.033), 
    (37.71667, 97.283), (34.233, 77.95), (49.9, 97.11667), 
]

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






class View(object):
    def __init__(self, user):
        self.user = user 
        self.indent = ("  " * len(self.user.stack))
        logs.debug("%sView %s" % (self.indent, self.__class__.__name__))

        self.__weights = {}
        self.__actions = {}

    def addToStack(self, obj, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        self.user.stack.append(obj(self.user, *args, **kwargs))
        self.user.stack[-1].run()
        self.user.stack.pop()

    @property 
    def weights(self):
        return self.__weights

    @property 
    def actions(self):
        return self.__actions

    def setWeight(self, key, value):
        self.__weights[key] = value

    def getWeight(self, key):
        return self.__weights[key]

    def getTotalWeight(self):
        return sum(v for k, v in self.__weights.items())

    def setAction(self, key, value):
        self.__actions[key] = value

    def getAction(self, key):
        return self.__actions[key]

    def load(self):
        raise NotImplementedError

    def run(self):
        # Import data
        self.load()

        try:
            while datetime.datetime.utcnow() < self.user.expiration:

                totalWeight = sum(v for k, v in self.weights.items())
                cumulativeWeight = 0
                r = random.randint(0, totalWeight)

                for key, weight in self.weights.items():
                    if r < weight:
                        break
                    r -= weight
                logs.debug("%sCHOSE ACTION: %s" % (self.indent, key))
                self.actions[key]()

        except DoneException:
            logs.debug("%sDONE: %s" % (self.indent, self.__class__.__name__))

        except RootException:
            logs.debug("%sGOING TO ROOT" % self.indent)

    # Go back to root
    def _back(self):
        time.sleep(random.randint(4, 12) * self.user._userWaitSpeed)
        raise DoneException("Done!")


class TastemakerInbox(View):

    def __init__(self, user):
        View.__init__(self, user)
        
        self.stamps = []
        self.offset = 0

        self.setAction('back', self._back)
        self.setWeight('back', 2)

        self.setAction('stamp', self._viewStamp)
        self.setWeight('stamp', 20)

        self.setAction('page', self._page)
        self.setWeight('page', 10)

    def load(self):
        self.loadStamps()
        self.loadStamps()

    def loadStamps(self):
        self.stamps += _get_stamps_collection(scope='popular', offset=self.offset, token=self.user.token)
        self.offset += 20

    # View the stamp detail
    def _viewStamp(self):
        if len(self.stamps) > 0:
            time.sleep(random.randint(2, 6) * self.user._userWaitSpeed)
            self.addToStack(StampDetail, kwargs={'stamp': random.choice(self.stamps)})
        else:
            self.setWeight('stamp', 0)

    # Load more stamps
    def _page(self):
        time.sleep(random.randint(1, 2) * self.user._userWaitSpeed)
        numStamps = len(self.stamps)
        self.loadStamps()
        if numStamps == len(self.stamps):
            # Nothing loaded!
            self.setWeight('page', 0)


class StampDetail(View):

    def __init__(self, user, stamp=None, stampId=None):
        View.__init__(self, user)
    
        self.stamp = stamp
        self.stampId = stampId

        self.setAction('back', self._back)
        self.setWeight('back', 20)

        self.setAction('profile', self._viewProfile)
        self.setWeight('profile', 20)

        self.setAction('entity', self._viewEntity)
        self.setWeight('entity', 20)

        self.setAction('credit', self._viewCredit)
        self.setWeight('credit', 2)

        self.setAction('comment', self._viewComment)
        self.setWeight('comment', 2)

    def load(self):
        if self.stamp is None:
            self.stamp = _get_stamps_show(self.stampId, token=self.user.token)

        self.stampId = self.stamp['stamp_id']
        self.entityId = self.stamp['entity']['entity_id']
        self.entity = _get_entities_show(self.entityId, token=self.user.token)
        self.alsoStampedBy = _get_entities_stamped_by(self.entityId, token=self.user.token)

    """
    Define possible actions the user can take, including wait time
    """

    # View the user's profile
    def _viewProfile(self):
        time.sleep(random.randint(4, 12) * self.user._userWaitSpeed)
        self.setWeight('profile', 0)
        self.addToStack(Profile, kwargs={'userId': self.stamp['user']['user_id']})

    # View entity details
    def _viewEntity(self):
        time.sleep(random.randint(4, 12) * self.user._userWaitSpeed)
        self.setWeight('entity', 0)
        self.addToStack(EntityDetail, kwargs={'entity': self.entity})

    def _viewCredit(self):
        if 'previews' in self.stamp and self.stamp['previews'] is not None:
            previews = self.stamp['previews']
            if 'credits' in previews and previews['credits'] is not None and len(previews['credits']) > 0:
                time.sleep(random.randint(4, 12) * self.user._userWaitSpeed)
                self.addToStack(StampDetail, kwargs={'stampId': random.choice(previews['credits'])['stamp_id']})
            else:
                self.setWeight('credit', 0)

    def _viewComment(self):
        if 'previews' in self.stamp and self.stamp['previews'] is not None:
            previews = self.stamp['previews']
            if 'comments' in previews and previews['comments'] is not None and len(previews['comments']) > 0:
                time.sleep(random.randint(4, 12) * self.user._userWaitSpeed)
                self.addToStack(Profile, kwargs={'userId': random.choice(previews['comments'])['user']['user_id']})
            else:
                self.setWeight('comment', 0)


class Profile(View):

    def __init__(self, user, userId=None):
        View.__init__(self, user)
    
        self.userId = userId
        self.stamps = []
        self.offset = 0

        self.setAction('back', self._back)
        self.setWeight('back', 20)

        self.setAction('stamp', self._viewStamp)
        self.setWeight('stamp', 20)

        self.setAction('page', self._page)
        self.setWeight('page', 5)

    def load(self):
        self.userObject = _get_users_show(self.userId, token=self.user.token)
        self.loadStamps()

    def loadStamps(self):
        self.stamps += _get_stamps_collection(scope='user', userId=self.userId, offset=self.offset, token=self.user.token)
        self.offset += 20

    # View stamp
    def _viewStamp(self):
        if len(self.stamps) > 0:
            time.sleep(random.randint(4, 12) * self.user._userWaitSpeed)
            self.addToStack(StampDetail, kwargs={'stamp': random.choice(self.stamps)})
        else:
            self.setWeight('stamp', 0)

    # Load more stamps
    def _page(self):
        time.sleep(random.randint(1, 2) * self.user._userWaitSpeed)
        numStamps = len(self.stamps)
        self.loadStamps()
        if numStamps == len(self.stamps):
            # Nothing loaded!
            self.setWeight('page', 0)


class EntityDetail(View):

    def __init__(self, user, entity=None, entityId=None, alsoStampedBy=None):
        View.__init__(self, user)
    
        self.entity = entity
        self.entityId = entityId
        self.alsoStampedBy = alsoStampedBy

        self.setAction('back', self._back)
        self.setWeight('back', 20)

        self.setAction('also', self._viewAlsoStampedBy)
        self.setWeight('also', 10)


    def load(self):
        if self.entity is None:
            self.entity = _get_entities_show(self.entityId, token=self.user.token)

        self.entityId = self.entity['entity_id']

        if self.alsoStampedBy is None:
            self.alsoStampedBy = _get_entities_stamped_by(self.entityId, token=self.user.token)

    """
    Define possible actions the user can take, including wait time
    """
    
    def _viewAlsoStampedBy(self):
        if 'friends' in self.alsoStampedBy and 'stamps' in self.alsoStampedBy['friends']:
            stamps = self.alsoStampedBy['friends']['stamps']
            if len(stamps) > 0:
                time.sleep(random.randint(4, 12) * self.user._userWaitSpeed)
                self.addToStack(StampDetail, kwargs={'stampId': random.choice(stamps)['stamp_id']})
                return

        if 'all' in self.alsoStampedBy and 'stamps' in self.alsoStampedBy['all']:
            stamps = self.alsoStampedBy['all']['stamps']
            if len(stamps) > 0:
                time.sleep(random.randint(4, 12) * self.user._userWaitSpeed)
                self.addToStack(StampDetail, kwargs={'stampId': random.choice(stamps)['stamp_id']})
                return

        self.setWeight('also', 0)


class GuideMenu(View):

    def __init__(self, user):
        View.__init__(self, user)

        self.setAction('back', self._back)
        self.setWeight('back', 20)

        self.setAction('food', self._viewFood)
        self.setWeight('food', 50)

        self.setAction('music', self._viewMusic)
        self.setWeight('music', 30)

        self.setAction('book', self._viewBook)
        self.setWeight('book', 30)

        self.setAction('film', self._viewFilm)
        self.setWeight('film', 30)

        self.setAction('app', self._viewApp)
        self.setWeight('app', 30)

    def load(self):
        pass

    def _viewMusic(self):
        time.sleep(random.randint(1, 2) * self.user._userWaitSpeed)
        self.addToStack(GuideList, kwargs={'section': 'music'})

    def _viewBook(self):
        time.sleep(random.randint(1, 2) * self.user._userWaitSpeed)
        self.addToStack(GuideList, kwargs={'section': 'book'})

    def _viewFilm(self):
        time.sleep(random.randint(1, 2) * self.user._userWaitSpeed)
        self.addToStack(GuideList, kwargs={'section': 'film'})

    def _viewApp(self):
        time.sleep(random.randint(1, 2) * self.user._userWaitSpeed)
        self.addToStack(GuideList, kwargs={'section': 'app'})

    def _viewFood(self):
        time.sleep(random.randint(1, 2) * self.user._userWaitSpeed)
        self.addToStack(GuideMap, kwargs={'section': 'food'})


class GuideView(View):

    def __init__(self, user, section, scope):
        View.__init__(self, user)

        self.section = section
        self.scope = scope
        self.entities = []
        self.stampIds = set()

    # View stamp detail
    def _viewStamp(self):
        if len(self.stampIds) > 0:
            time.sleep(random.randint(1, 8) * self.user._userWaitSpeed)
            self.addToStack(StampDetail, kwargs={'stampId': random.choice(self.stampIds)})
        else:
            self.setWeight('stamp', 0)
            self.setWeight('entity', 0)

    # View entity details
    def _viewEntity(self):
        if len(self.entities) > 0:
            time.sleep(random.randint(1, 8) * self.user._userWaitSpeed)
            self.addToStack(EntityDetail, kwargs={'entity': random.choice(self.entities)})
        else:
            self.setWeight('stamp', 0)
            self.setWeight('entity', 0)


class GuideList(GuideView):

    def __init__(self, user, section, scope='popular'):
        GuideView.__init__(self, user, section, scope)

        self.offset = 0

        self.setAction('back', self._back)
        self.setWeight('back', 20)

        self.setAction('entity', self._viewEntity)
        self.setWeight('entity', 45)

        self.setAction('page', self._page)
        self.setWeight('page', 10)

    def load(self):
        self.loadEntities()
        self.loadEntities()

    def loadEntities(self):
        entities = _get_guide_collection(section=self.section, scope=self.scope, 
                                            offset=self.offset, token=self.user.token)
        for entity in entities:
            if 'previews' in entity and 'stamps' in entity['previews']:
                stamps = entity['previews']['stamps']
                if stamps is not None and len(stamps) > 0:
                    self.stampIds.union(set(map(lambda x: x['stamp_id'], stamps)))
        self.offset += 20
        self.entities += entities

    # Load more entities
    def _page(self):
        time.sleep(random.randint(1, 2) * self.user._userWaitSpeed)
        numEntities = len(self.entities)
        self.loadEntities()
        if numEntities == len(self.entities):
            # Nothing loaded!
            self.setWeight('page', 0)


class GuideMap(GuideView):

    def __init__(self, user, section, scope='popular'):
        GuideView.__init__(self, user, section, scope)

        self.viewport = None
        self.query = None

        self.setAction('back', self._back)
        self.setWeight('back', 20)

        self.setAction('entity', self._viewEntity)
        self.setWeight('entity', 45)

        self.setAction('pan', self._pan)
        self.setWeight('pan', 40)

        self.setAction('zoom', self._zoom)
        self.setWeight('zoom', 40)

        self.setAction('search', self._search)
        self.setWeight('search', 40)

        self.setAction('clearSearch', self._clearSearch)
        self.setWeight('clearSearch', 0)

    def load(self):
        self.setViewport()
        self.loadEntities()

    def setViewport(self):
        coordinate = random.choice(coordinates)
        zoom = random.uniform(0, 0.1)
        self.viewport = (coordinate[0]-zoom, coordinate[1]-zoom, coordinate[0]+zoom, coordinate[1]+zoom)

    def loadEntities(self):
        viewport = ','.join(map(lambda x: str(x), self.viewport))

        if self.query is not None:
            entities = _get_guide_search(query=self.query, section=self.section, scope=self.scope, viewport=viewport, 
                                            token=self.user.token, limit=50)
        else:
            entities = _get_guide_collection(section=self.section, scope=self.scope, viewport=viewport, 
                                                token=self.user.token, limit=50)

        for entity in entities:
            if 'previews' in entity and 'stamps' in entity['previews']:
                stamps = entity['previews']['stamps']
                if stamps is not None and len(stamps) > 0:
                    self.stampIds.union(set(map(lambda x: x['stamp_id'], stamps)))
        self.entities = entities

    # Pan over the map
    def _pan(self):
        time.sleep(random.randint(1, 2) * self.user._userWaitSpeed)
        v = random.uniform(-0.1, 0.1)
        self.viewport = (
            self.viewport[0] + v,
            self.viewport[1] + v,
            self.viewport[2] + v,
            self.viewport[3] + v,
        )
        self.loadEntities()

    # Zoom in / out of the map
    def _zoom(self):
        time.sleep(random.randint(1, 2) * self.user._userWaitSpeed)
        latDiff = self.viewport[2] - self.viewport[0]
        lngDiff = self.viewport[3] - self.viewport[1]
        v = random.uniform(-0.9, 0.9)
        self.viewport = (
            self.viewport[0] - (latDiff * v),
            self.viewport[1] - (lngDiff * v),
            self.viewport[2] + (latDiff * v),
            self.viewport[3] + (latDiff * v),
        )
        self.loadEntities()

    def _search(self):
        queries = ['sushi', 'indian', 'mexican', 'chinese', 'korean', 'japanese', 'bbq', 'coffee', 
                    'tea', 'bakery', 'burger', 'cuban', 'italian', 'kosher', 'thai', 'sandwich', 
                    'salad', 'pizza', 'organic', 'wings', 'vegan']
        self.query = random.choice(queries)
        self.loadEntities()
        self.setWeight('clearSearch', max(1, int(self.getTotalWeight() * 0.3)))

    def _clearSearch(self):
        self.query = None
        self.setWeight('clearSearch', 0)





# Base user class - Should not be called directly
class User(object):
    def __init__(self):
        self.token = None
        self.userId = None
        self.expiration = None
        self._userSessionLength = None
        self._userWaitSpeed = None

        self.stack = []

        self.__weights = {}
        self.__actions = {}

    @property 
    def weights(self):
        return self.__weights

    @property 
    def actions(self):
        return self.__actions

    def setWeight(self, key, value):
        self.__weights[key] = value

    def getWeight(self, key):
        return self.__weights[key]

    def setAction(self, key, value):
        self.__actions[key] = value

    def getAction(self, key):
        return self.__actions[key]

    def addToStack(self, obj, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        self.stack.append(obj(self, *args, **kwargs))
        self.stack[-1].run()
        self.stack.pop()

    # Start and root defined in subclasses
    def run(self):
        logs.debug("Running %s" % self.__class__.__name__)

        self.expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._userSessionLength)
        logs.debug("Expiration: %s" % self.expiration)

        while datetime.datetime.utcnow() < self.expiration:
            logs.info("BEGIN: %s" % self.__class__.__name__)
            try:

                totalWeight = sum(v for k, v in self.weights.items())
                cumulativeWeight = 0
                r = random.randint(0, totalWeight)

                for key, weight in self.weights.items():
                    if r < weight:
                        break
                    r -= weight
                logs.debug("CHOSE ACTION: %s" % (key))
                self.actions[key]()

            except (DoneException, RootException):
                time.sleep(3)

            logs.info("DONE: %s" % (self.__class__.__name__))
            print


# Class representing users who do not log in or create an account throughout their session
class LoggedOutUser(User):

    def __init__(self):
        User.__init__(self)
        self._userWaitSpeed = 0
        self._userSessionLength = 10 #200 + (random.random() * 200)
        
        self.setAction('inbox', self._viewInbox)
        self.setWeight('inbox', 10)
        
        self.setAction('guide', self._viewGuide)
        self.setWeight('guide', 30)


    # View stamp
    def _viewInbox(self):
        time.sleep(random.randint(4, 12) * self._userWaitSpeed)
        self.addToStack(TastemakerInbox)

    # View guide
    def _viewGuide(self):
        time.sleep(random.randint(4, 12) * self._userWaitSpeed)
        self.addToStack(GuideMenu)







user = LoggedOutUser()
user.run()
print 'DONE'
