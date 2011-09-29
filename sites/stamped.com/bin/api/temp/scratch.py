#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import atexit, urllib, json, urllib2, pprint

class StampedAPIURLOpener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('stampedtest', 'august1ftw')

CLIENT_ID     = "stampedtest"
CLIENT_SECRET = "august1ftw"

_opener = StampedAPIURLOpener()
client_auth = {
    'client_id': 'stampedtest',
    'client_secret': 'august1ftw'
}

_baseurl = "https://dev.stamped.com/v0"
_baseurl = "http://localhost:18000/v0"

def handleGET(path, data):
    params = urllib.urlencode(data)
    url    = "%s/%s?%s" % (_baseurl, path, params)
    result = json.load(_opener.open(url))
    
    return result

def handlePOST(path, data):
    params = urllib.urlencode(data)
    url    = "%s/%s" % (_baseurl, path)
    result = json.load(_opener.open(url, params))
    
    return result



USER = 'kevin'
PASS = '12345'

path = "oauth2/login.json"
data = { 
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "login": USER,
    "password": PASS
}
token = handlePOST(path, data)

path = "users/search.json"
data = { 
    "oauth_token": token['token']['access_token'],
    "q": 'e'
}
result = handlePOST(path, data)

print
print
for i in xrange(len(result)):
    print '%2s | %14s | %s' % (i+1, result[i]['screen_name'], result[i]['name'])

# path = "favorites/create.json"
# data = { 
#     "oauth_token": token['access_token'],
#     "entity_id": "4e4c684df15dd72f5300023c",
#     "stamp_id": "4e7f8a9ed35f7313f500000e",
# }
# result = handlePOST(path, data)

# path = "friendships/remove.json"
# data = {
#     "oauth_token": token['access_token'],
#     "screen_name": 'zoe'
# }
# result = handlePOST(path, data)

# print result

print
print


