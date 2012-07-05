#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import atexit

from api.Schemas                import *
from tests.StampedTestUtils           import *
from tests.framework.FixtureTest                import *
from api.MongoStampedAPI            import MongoStampedAPI
from utils                      import lazyProperty

_accounts  = []
_test_case = None


__globalAPI = None
def globalAPI():
    global __globalAPI
    if __globalAPI is None:
        __globalAPI = MongoStampedAPI()
    return __globalAPI

class StampedAPIException(Exception):
    pass



class AStampedAPITestCase(AStampedFixtureTestCase):

    @lazyProperty
    def api(self):
        return globalAPI()

    ### CUSTOM ASSERTIONS
    def assertValidKey(self, key, length=24):
        self.assertIsInstance(key, basestring)
        self.assertLength(key, length)

    def assertGreater(self, first, second, msg=None):
        try:
            self.assertTrue(first > second)
        except AssertionError:
            if msg is not None:
                raise AssertionError(msg)
            raise AssertionError('"%s" unexpectedly not greater than "%s"' % (first, second))

    def createAccount(self, name='TestUser', **kwargs):
        global _test_case, _accounts
        _test_case = self

        account             = Account()
        account.name        = name
        account.email       = kwargs.pop('email', '%s@stamped.com' % name)
        account.password    = kwargs.pop('password', "12345")
        account.screen_name = kwargs.pop('screen_name', name)
        account             = self.api.addAccount(account)

        self.assertValidKey(account.user_id)
        _accounts.append(account.user_id)

        return account

    #TODO: Consoldiate the facebook and twitter account creation methods? Consolidate all creation methods?

    def createFacebookAccount(self, fb_user_token, name='TestUser', **kwargs):
        global _test_case, _accounts
        _test_case = self

        fbAccount                   = FacebookAccountNew()
        fbAccount.user_token        = fb_user_token
        fbAccount.name              = name
        fbAccount.email             = kwargs.pop('email', None)
        fbAccount.screen_name       = kwargs.pop('screen_name', name)
        fbAccount.phone             = kwargs.pop('phone', None)
        fbAccount.bio               = kwargs.pop('bio', None)
        fbAccount.website           = kwargs.pop('website', None)
        fbAccount.location          = kwargs.pop('location', None)
        fbAccount.color_primary     = kwargs.pop('color_primary', None)
        fbAccount.color_secondary   = kwargs.pop('color_secondary', None)

        account = self.api.addFacebookAccount(fbAccount)

        self.assertValidKey(account.user_id)
        _accounts.append(account.user_id)
        return account

    def createTwitterAccount(self, tw_user_token, tw_user_secret, name='TestUser', **kwargs):
        global _test_case, _accounts
        _test_case = self

        twAccount                   = TwitterAccountNew()
        twAccount.user_token        = tw_user_token
        twAccount.user_secret       = tw_user_secret
        twAccount.name              = name
        twAccount.email             = kwargs.pop('email', None)
        twAccount.screen_name       = kwargs.pop('screen_name', name)
        twAccount.phone             = kwargs.pop('phone', None)
        twAccount.bio               = kwargs.pop('bio', None)
        twAccount.website           = kwargs.pop('website', None)
        twAccount.location          = kwargs.pop('location', None)
        twAccount.color_primary     = kwargs.pop('color_primary', None)
        twAccount.color_secondary   = kwargs.pop('color_secondary', None)

        account = self.api.addTwitterAccount(twAccount)

        self.assertValidKey(account.user_id)
        _accounts.append(account.user_id)
        return account

    def addLinkedAccount(self, authUserId, service_name, **kwargs):
        linked                          = LinkedAccount()
        linked.service_name             = service_name
        linked.linked_user_id           = kwargs.pop('linked_user_id', None)
        linked.linked_screen_name       = kwargs.pop('linked_screen_name', None)
        linked.linked_name              = kwargs.pop('linked_name', None)
        linked.token                    = kwargs.pop('token', None)
        linked.secret                   = kwargs.pop('secret', None)
        linked.token_expiration         = kwargs.pop('token_expiration', None)

        return self.api.addLinkedAccount(authUserId, linked)

    def removeLinkedAccount(self, authuserId, service_name):
        return self.api.removeLinkedAccount(authUserId, service_name)


    def loginWithFacebook(self, fb_user_token, **kwargs):
        c_id        = kwargs.pop('client_id', DEFAULT_CLIENT_ID)

        account, token = self.api.verifyFacebookUserCredentials(c_id, fb_user_token)
        return account, token

    def loginWithTwitter(self, tw_user_token, tw_user_secret, **kwargs):
        c_id        = kwargs.pop('client_id', DEFAULT_CLIENT_ID)

        account, token = self.api.verifyTwitterUserCredentials(c_id, tw_user_token, tw_user_secret)
        return account, token

    def deleteAccount(self, authUserId):
        return self.api.removeAccount(authUserId)

    def createFriendship(self, authUserId, targetUserId=None, targetScreenName=None):
        userTiny = UserTiny()
        userTiny.user_id = targetUserId
        userTiny.screen_name = targetScreenName
        friend = self.api.addFriendship(authUserId, userTiny)

        self.assertValidKey(friend.user_id)
        return friend

    def deleteFriendship(self, authUserId, targetUserId=None, targetScreenName=None):
        userTiny = UserTiny()
        userTiny.user_id = targetUserId
        userTiny.screen_name = targetScreenName
        self.api.removeFriendship(authUserId, userTiny)


    def showAccount(self, authUserId):
        return self.api.getAccount(authUserId)

    def showLinkedAccounts(self, authUserId):
        return self.api.getLinkedAccounts(authuserId)


    def showActivity(self, authUserId, limit, offset):
        return self.api.getActivity(authuserId, 'me', limit, offset)

    def showFriendsActivity(self, authUserId, limit, offset):
        return self.api.getActivity(authUserId, 'friends', limit, offset)


#    def createEntity(self, token, data=None):
#        path = "entities/create.json"
#        if data == None:
#            data = {
#                "oauth_token": token['access_token'],
#                "title": "Kanye West",
#                "subtitle": "Hubristic Rapper",
#                "desc": "Hip-hop artist",
#                "category": "music",
#                "subcategory": "artist",
#                }
#        if "oauth_token" not in data:
#            data['oauth_token'] = token['access_token']
#        entity = self.handlePOST(path, data)
#        self.assertValidKey(entity['entity_id'])
#
#        return entity
#
#    def createPlaceEntity(self, token, data=None):
#        path = "entities/create.json"
#        if data == None:
#            data = {
#                "oauth_token": token['access_token'],
#                "title": "Good Food",
#                "subtitle": "Peoria, IL",
#                "desc": "American food in America",
#                "category": "place",
#                "subcategory": "restaurant",
#                "address": "123 Main Street, Peoria, IL",
#                "coordinates": "40.714623,-74.006605"
#            }
#
#        if "oauth_token" not in data:
#            data['oauth_token'] = token['access_token']
#
#        entity = self.handlePOST(path, data)
#        self.assertValidKey(entity['entity_id'])
#
#        return entity
#
#    def deleteEntity(self, token, entityId):
#        path = "entities/remove.json"
#        data = {
#            "oauth_token": token['access_token'],
#            "entity_id": entityId
#        }
#        result = self.handlePOST(path, data)
#        self.assertTrue(result)

    def createStamp(self, authUserId, entityId=None, blurb="Best restaurant in America", credits=None):
        assert(entityId is not None or searchId is not None)
        data ={
            'blurb' :  blurb,
            'credits' : credits
        }
        entityRequest = {
            'entity_id' : entityId,
            'search_id' : None,
        }
        stamp = self.api.addStamp(authUserId, entityRequest, data)
        self.assertValidKey(stamp.stamp_id)
        return stamp

    def deleteStamp(self, authUserId, stampId):
        return self.api.removeStamp(authUserId, stampId)

    def createComment(self, authUserId, stampId, blurb="Sample Comment Text"):
        comment = self.api.addComment(authUserId, stampId, blurb)
        self.assertValidKey(comment.comment_id)
        return comment

    def deleteComment(self, authuserId, commentId):
        return self.api.removeComment(authUserId, commentId)

    def createTodo(self, authUserId, entityId, stampId=None):
        entityRequest = {
            'entity_id' : entityId,
            'search_id' : None,
        }
        todo = self.api.addTodo(authuserId, entityRequest, stampid)
        self.assertValidKey(todo.todo_id)
        return todo

    def deleteTodo(self, authUserId, entityId):
        return self.api.removeTodo(authUserId, entityId)

    def completeTodo(self, authUserId, entityId, complete):
        return self.api.completeTodo(authUserId, entityId, complete)

    def createLike(self, authUserId, stampId):
        stamp = self.api.addLike(authUserId, stampId)
        self.assertValidKey(stamp.stamp_id)
        return stamp

    def deleteLike(self, authUserId, stampId):
        return self.api.removeLike(authUserId, stampId)

    def showLikes(self, authUserId, stampId):
        return self.api.getLikes(authUserId, stampId)

def __cleanup():
    global _test_case, _accounts

    # attempt to clean up all accounts created in this session
    test = _test_case
    if test is not None:
        print "cleaning up..."

        for acct in _accounts:
            try:
                test.deleteAccount(acct)
            except:
                pass

def main():
    atexit.register(__cleanup)
    StampedTestRunner().run()

