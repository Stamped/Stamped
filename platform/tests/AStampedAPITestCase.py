#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Schemas import FacebookAccountNew

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import atexit, os, json, mimetools, sys, urllib, urllib2

from pprint           import pprint
from StampedTestUtils import *
from MongoStampedAPI import MongoStampedAPI
from utils           import lazyProperty

TWITTER_KEY     = "322992345-s2s8Pg24XXl1FhUKluxTv57gnR2eetXSyLt2rB6U"
TWITTER_SECRET  = "FlOIbBdvznmNNXPSKbkiYfKS9usFq9FWgNDfPV5hNQ"
FB_TOKEN        = "AAAEOIZBBUXisBAFCF2feHIs8YmbnTFNoiZBbfftMnZCwZCngUGyuZBpcr2tv4Kx7ZCNzcj7mvlurUhBicIFRTlDmuSduiHCucZD"

_accounts  = []
_test_case = None
_baseurl   = "http://localhost:18000/v0"
# _baseurl = "https://dev.stamped.com/v0"

class StampedAPIException(Exception):
    pass

if utils.is_ec2():
    import libs.ec2_utils
    elb = libs.ec2_utils.get_elb()

    if elb is not None:
        _baseurl = "https://%s/v0" % elb.dns_name

print "BASE_URL: %s" % _baseurl

class StampedAPIURLOpener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('stampedtest', 'august1ftw')

class AStampedAPIHttpTestCase(AStampedTestCase):

    @lazyProperty
    def api(self):
        return MongoStampedAPI()

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
        account.email       = kwargs.pop('email', '%s@stamped.com' % name)
        account.password    = kwargs.pop('password', "12345")
        account.screen_name = kwargs.pop('screen_name', name)
        account = self.api.addAccount(account)

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

        twAccount                   = FacebookAccountNew()
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
        linked.user_id                  = kwargs.pop('user_id', None)
        linked.screen_name              = kwargs.pop('screen_name', None)
        linked.name                     = kwargs.pop('name', None)
        linked.token                    = kwargs.pop('token', None)
        linked.secret                   = kwargs.pop('secret', None)
        linked.token_expiration         = kwargs.pop('token_expiration', None)

        self.api.addLinkedAccount(linked)


        c_id        = kwargs.pop('client_id', DEFAULT_CLIENT_ID)
        c_secret    = CLIENT_SECRETS[c_id]

        path = "account/linked/add.json"
        data = {
            "client_id"         : c_id,
            "client_secret"     : c_secret,
            "oauth_token"       : user_token['access_token'],
            }
        data.update(kwargs)
        return self.handlePOST(path, data)

    def removeLinkedAccount(self, token, service_name, **kwargs):
        c_id        = kwargs.pop('client_id', DEFAULT_CLIENT_ID)
        c_secret    = CLIENT_SECRETS[c_id]

        path = "account/linked/remove.json"
        data = {
            "client_id"         : c_id,
            "client_secret"     : c_secret,
            "oauth_token"       : token['access_token'],
            "service_name"      : service_name
        }
        return self.handlePOST(path, data)

    def loginWithFacebook(self, fb_user_token, **kwargs):
        c_id        = kwargs.pop('client_id', DEFAULT_CLIENT_ID)
        c_secret    = CLIENT_SECRETS[c_id]

        path = "oauth2/login/facebook.json"
        data = {
            "client_id":        c_id,
            "client_secret":    c_secret,
            "user_token":       fb_user_token,
            }
        return self.handlePOST(path, data)

    def loginWithTwitter(self, tw_user_token, tw_user_secret, **kwargs):
        c_id        = kwargs.pop('client_id', DEFAULT_CLIENT_ID)
        c_secret    = CLIENT_SECRETS[c_id]

        path = "oauth2/login/twitter.json"
        data = {
            "client_id":      c_id,
            "client_secret":  c_secret,
            "user_token":     tw_user_token,
            "user_secret":    tw_user_secret,
            }
        return self.handlePOST(path, data)

    def deleteAccount(self, token):
        path = "account/remove.json"
        data = { "oauth_token": token['access_token'] }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

    def createFriendship(self, token, friend):
        path = "friendships/create.json"
        data = {
            "oauth_token": token['access_token'],
            "user_id": friend['user_id']
        }
        friend = self.handlePOST(path, data)

        self.assertIn('user_id', friend)
        self.assertValidKey(friend['user_id'])

        return friend

    def deleteFriendship(self, token, friend):
        path = "friendships/remove.json"
        data = {
            "oauth_token": token['access_token'],
            "user_id": friend['user_id']
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)
    #
    #    def addLinkedAccount(self, token, data=None):
    #        """
    #        params should include properties to fill HTTPLinkedAccounts object
    #        """
    #        path = "account/linked_accounts.json"
    #        if "oauth_token" not in data:
    #            data['oauth_token'] = token['access_token']
    #        return self.handlePOST(path, data)
    #
    def showAccount(self, token):
        path = "account/show.json"
        data = {
            'oauth_token'       : token['access_token'],
            }
        return self.handleGET(path, data)

    def showLinkedAccounts(self, token):
        path = "account/linked/show.json"
        data = {
            'oauth_token'       : token['access_token'],
            }
        return self.handleGET(path, data)

    def showActivity(self, token):
        path = "activity/collection.json"
        data = {
            'oauth_token'       : token['access_token'],
            'scope'             : 'me',
            }
        return self.handleGET(path, data)

    def showFriendsActivity(self, token):
        path = "activity/collection.json"
        data = {
            'oauth_token'       : token['access_token'],
            'scope'             : 'friends',
            }
        return self.handleGET(path, data)

    def createEntity(self, token, data=None):
        path = "entities/create.json"
        if data == None:
            data = {
                "oauth_token": token['access_token'],
                "title": "Kanye West",
                "subtitle": "Hubristic Rapper",
                "desc": "Hip-hop artist",
                "category": "music",
                "subcategory": "artist",
                }
        if "oauth_token" not in data:
            data['oauth_token'] = token['access_token']
        entity = self.handlePOST(path, data)
        self.assertValidKey(entity['entity_id'])

        return entity

    def createPlaceEntity(self, token, data=None):
        path = "entities/create.json"
        if data == None:
            data = {
                "oauth_token": token['access_token'],
                "title": "Good Food",
                "subtitle": "Peoria, IL",
                "desc": "American food in America",
                "category": "place",
                "subcategory": "restaurant",
                "address": "123 Main Street, Peoria, IL",
                "coordinates": "40.714623,-74.006605"
            }

        if "oauth_token" not in data:
            data['oauth_token'] = token['access_token']

        entity = self.handlePOST(path, data)
        self.assertValidKey(entity['entity_id'])

        return entity

    def deleteEntity(self, token, entityId):
        path = "entities/remove.json"
        data = {
            "oauth_token": token['access_token'],
            "entity_id": entityId
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

    def createStamp(self, token, entityId, data=None, blurb="Best restaurant in America", credit=None):
        path = "stamps/create.json"
        if data == None:
            data = {
                "oauth_token": token['access_token'],
                "entity_id": entityId,
                "blurb": blurb,
                }

        if "oauth_token" not in data:
            data['oauth_token'] = token['access_token']

        if credit:
            data['credits'] = credit

        stamp = self.handlePOST(path, data)
        self.assertValidKey(stamp['stamp_id'])

        return stamp

    def deleteStamp(self, token, stampId):
        path = "stamps/remove.json"
        data = {
            "oauth_token": token['access_token'],
            "stamp_id": stampId
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

    def createComment(self, token, stampId, blurb="Sample Comment Text"):
        path = "comments/create.json"
        data = {
            "oauth_token": token['access_token'],
            "stamp_id": stampId,
            "blurb": blurb,
            }
        comment = self.handlePOST(path, data)
        self.assertValidKey(comment['comment_id'])

        return comment

    def deleteComment(self, token, commentId):
        path = "comments/remove.json"
        data = {
            "oauth_token": token['access_token'],
            "comment_id": commentId
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

    def createTodo(self, token, entityId, stampId=None):
        path = "todos/create.json"
        data = {
            "oauth_token": token['access_token'],
            "entity_id": entityId,
            }

        if stampId is not None:
            data['stamp_id'] = stampId

        todo = self.handlePOST(path, data)
        self.assertValidKey(todo['todo_id'])

        return todo

    def deleteTodo(self, token, entityId):
        path = "todos/remove.json"
        data = {
            "oauth_token": token['access_token'],
            "entity_id": entityId
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)

    def completeTodo(self, token, entityId, complete):
        path = "todos/complete.json"
        data = {
            "oauth_token":  token['access_token'],
            "entity_id":    entityId,
            "complete":     complete,
            }
        return self.handlePOST(path, data)

    def createLike(self, token, stampId):
        path = "stamps/likes/create.json"
        data = {
            "oauth_token": token['access_token'],
            "stamp_id": stampId
        }
        return self.handlePOST(path, data)

    def deleteLike(self, token, stampId):
        path = "stamps/likes/remove.json"
        data = {
            "oauth_token": token['access_token'],
            "stamp_id": stampId
        }
        return self.handlePOST(path, data)

    def showLikes(self, token, stampId):
        path = "stamps/likes/show.json"
        data = {
            "oauth_token": token['access_token'],
            "stamp_id": stampId
        }
        return self.handleGET(path, data)

    def _loadCollection(self, collection, filename=None, drop=True):
        if filename is None:
            filename = "%s.db" % collection

        col = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "api/data"), filename)
        cmd = "mongoimport -d stamped -c %s --stopOnError %s %s" %\
              (collection, "--drop" if drop else "", col)

        #utils.log(cmd)
        ret = utils.shell(cmd)
        self.assertEqual(ret[1], 0)

    def _dropCollection(self, collection):
        cmd = "mongo stamped --eval \"db.%s.drop()\"" % collection
        ret = utils.shell(cmd)
        self.assertEqual(ret[1], 0)

def __cleanup():
    global _test_case, _accounts

    # attempt to clean up all accounts created in this session
    test = _test_case
    if test is not None:
        print "cleaning up..."

        for acct in _accounts:
            try:
                test.deleteAccount(acct[1])
            except:
                pass

def main():
    atexit.register(__cleanup)
    StampedTestRunner().run()

