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





#Base user class - Should not be called directly
class User(object):
    def __init__(self):
        self.token = None
        self.userId = None
        self.expiration = None
        self._userSessionLength = None
        self._userWaitSpeed = None

        self.stack = []

    def addToStack(self, obj, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        self.stack.append(obj(self.user, *args, **kwargs))
        self.stack[-1].run()
        self.stack.pop()

    # Start and root defined in subclasses
    def run(self):
        raise NotImplementedError


# Class representing users who do not log in or create an account throughout their session
class LoggedOutUser(User):

    def __init__(self):
        User.__init__(self)
        self._userWaitSpeed = 0
        self._userSessionLength = 10 #200 + (random.random() * 200)
        
    def run(self):
        logs.debug("Begin: %s" % self)

        self.expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._userSessionLength)
        logs.debug("Expiration: %s" % self.expiration)


        self.addToStack(TastemakerInbox)



        # """
        # Define possible actions the user can take, including wait time
        # """
        # actions = {}
        # weights = {}

        # # View the user's profile
        # def _viewInbox():
        #     return self.viewTastemakerInbox()

        # actions['inbox'] = _viewInbox
        # weights['inbox'] = 20

        # assert len(actions) == len(weights)

        # """
        # Run the actions
        # """
        # while datetime.datetime.utcnow() < self.expiration:
        #     try:
        #         return self._runAction(actions, weights)
        #     except RootException:
        #         continue









user = LoggedOutUser()
user.run()
print 'DONE'
