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

path = "stamps/create.json"
data = { 
    "oauth_token": token['access_token'],
    "entity_id": "4e5eaf41ccc217205900000c",
    "blurb": "Sample stamp"
}
stamp = handlePOST(path, data)

path = "stamps/remove.json"
data = { 
    "oauth_token": token['access_token'],
    "stamp_id": stamp['stamp_id']
}
result = handlePOST(path, data)

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

print result

print 'COMPLETE'


