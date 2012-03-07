#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import atexit, os, json, mimetools, sys, urllib, urllib2

from pprint           import pprint
from StampedTestUtils import *

DEFAULT_CLIENT_ID       = "stampedtest"
CLIENT_SECRETS  = {
    'stampedtest': 'august1ftw',
    'ios8': 'LnIFbmL0a75G8iQeHCV8VOT4fWFAWhzu',
}

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

class AStampedAPITestCase(AStampedTestCase):
    
    _opener = StampedAPIURLOpener()

    def handleGET(self, path, data):
        global _baseurl
        params = urllib.urlencode(data)
        url    = "%s/%s?%s" % (_baseurl, path, params)
        
        #utils.log("GET:  %s" % url)
        raw = self._opener.open(url).read()
        
        try:
            result = json.loads(raw)
        except:
            raise StampedAPIException(raw)
        
        return result
    
    def handlePOST(self, path, data):
        global _baseurl
        params = urllib.urlencode(data)
        url    = "%s/%s" % (_baseurl, path)
        
        #utils.log("POST: %s" % url)
        #pprint(params)
        
        raw = self._opener.open(url, params).read()
        
        try:
            result = json.loads(raw)
        except:
            raise StampedAPIException(raw)
        
        return result
    
    def handleMultiPart(self, path, fields, files, file_type='image/jpeg'):
        global _baseurl
        url             = "%s/%s" % (_baseurl, path)
        headers, data   = self.encodeMultiPart(fields, files, file_type)
        
        request         = urllib2.Request(url, data, headers)
        result          = urllib2.urlopen(request)
        json_result     = json.load(result)
        
        return json_result
    
    def encodeMultiPart(self, fields, files, file_type='image/jpeg'):
        # Inspired by http://code.google.com/apis/cloudprint/docs/pythonCode.html
        
        CRLF = '\r\n'
        BOUNDARY = mimetools.choose_boundary()
        
        """Encodes list of parameters and files for HTTP multipart format.
        
        Args:
          fields: list of tuples containing name and value of parameters.
          files: list of tuples containing param name, filename, and file contents.
          file_type: string if file type different than application/xml.
        Returns:
          A string to be sent as data for the HTTP post request.
        """
        lines = []
        for key, value in fields.iteritems():
            lines.append('--' + BOUNDARY)
            lines.append('Content-Disposition: form-data; name="%s"' % key)
            lines.append('')  # blank line
            lines.append(value)
        for key, value in files.iteritems():
            filename = value['filename']
            data = value['data']
            lines.append('--' + BOUNDARY)
            lines.append(
                'Content-Disposition: form-data; name="%s"; filename="%s"'
                % (key, filename))
            lines.append('Content-Type: %s' % file_type)
            lines.append('')  # blank line
            lines.append(data)
        lines.append('--' + BOUNDARY + '--')
        lines.append('')  # blank line
        
        data = CRLF.join(lines)
        
        headers = {
            'Content-Length': len(data), 
            'Content-Type': 'multipart/form-data; boundary=%s' % BOUNDARY
        }
        
        return headers, data
    
    ### CUSTOM ASSERTIONS
    def assertValidKey(self, key, length=24):
        self.assertIsInstance(key, basestring)
        self.assertLength(key, length)
    
    ### HELPER FUNCTIONS
    def createAccount(self, name='TestUser', password="12345", **kwargs):
        global _test_case, _accounts
        _test_case = self
        
        email       = kwargs.pop('email', '%s@stamped.com' % name)
        c_id        = kwargs.pop('client_id', DEFAULT_CLIENT_ID)
        c_secret    = CLIENT_SECRETS[c_id]
        
        path = "account/create.json"
        data = {
            "client_id": c_id,
            "client_secret": c_secret,
            "name": name,
            "email": email, 
            "password": password,
            "screen_name": name
        }
        response = self.handlePOST(path, data)
        self.assertIn('user', response)
        self.assertIn('token', response)
        
        user  = response['user']
        token = response['token']
        
        _accounts.append((user, token))
        
        self.assertValidKey(user['user_id'])
        self.assertValidKey(token['access_token'], 22)
        self.assertValidKey(token['refresh_token'], 43)
        
        return user, token
    
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
                "category": "food",
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
            data['credit'] = credit
        
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
    
    def createFavorite(self, token, entityId, stampId=None):
        path = "favorites/create.json"
        data = {
            "oauth_token": token['access_token'],
            "entity_id": entityId,
        }
        
        if stampId != None:
            data['stamp_id'] = stampId
        
        favorite = self.handlePOST(path, data)
        self.assertValidKey(favorite['favorite_id'])
        
        return favorite
    
    def deleteFavorite(self, token, entityId):
        path = "favorites/remove.json"
        data = {
            "oauth_token": token['access_token'],
            "entity_id": entityId
        }
        result = self.handlePOST(path, data)
        self.assertTrue(result)
    
    def _loadCollection(self, collection, filename=None, drop=True):
        if filename is None:
            filename = "%s.db" % collection
        
        col = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "api/data"), filename)
        cmd = "mongoimport -d stamped -c %s --stopOnError %s %s" % \
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

