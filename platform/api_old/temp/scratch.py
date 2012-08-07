#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
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

result = None

USER = 'kevin'
PASS = '12345'

path = "oauth2/login.json"
data = { 
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "login": USER,
    "password": PASS
}
account = handlePOST(path, data)
token = account['token']


# path = "favorites/remove.json"
# data = { 
#     "oauth_token": token['access_token'],
#     "entity_id": '4e7d0f42d6970356a60008b9'
# }
# result = handlePOST(path, data)

# print
# print
# for i in xrange(len(result)):
#     print '%2s | %14s | %s' % (i+1, result[i]['screen_name'], result[i]['name'])

# path = "favorites/create.json"
# data = { 
#     "oauth_token": token['access_token'],
#     "entity_id": "4e4c684df15dd72f5300023c",
#     "stamp_id": "4e7f8a9ed35f7313f500000e",
# }
# result = handlePOST(path, data)

# path = "account/alerts/update.json"
# data = {
#     "oauth_token": token['access_token'],
#     "ios_alert_credit": True,
#     "ios_alert_like": True,
#     "ios_alert_fav": True,
#     "ios_alert_mention": True,
#     "ios_alert_comment": True,
#     "ios_alert_reply": True,
#     "ios_alert_follow": True,
#     "email_alert_credit": True,
#     "email_alert_like": True,
#     "email_alert_fav": True,
#     "email_alert_mention": True,
#     "email_alert_comment": True,
#     "email_alert_reply": True,
#     "email_alert_follow": True,

# }

# path = "account/alerts/ios/update.json"
# data = {
#     "oauth_token": token['access_token'],
#     "token": "cf061c5538ac48a066429449188ccb0b0574aeb068a6a6c56f3115a5c4085329"
# }
# result = handlePOST(path, data)

# path = "entities/nearby.json"
# data = {
#     "oauth_token": token['access_token'],
#     "coordinates": "38.5,-122.56"
# }
# result = handleGET(path, data)

# path = "account/customize_stamp.json"
# data = {
#     "oauth_token": token['access_token'],
#     "color_primary": "000000",
#     "color_secondary": "000000",
# }
# result = handlePOST(path, data)

# path = "friendships/invite.json"
# data = {
#     "oauth_token": token['access_token'],
#     "email": "ed@stamped.com",
# }
# result = handlePOST(path, data)

# path = "account/reset_password.json"
# data = {
#     'client_id': 'stampedtest',
#     'client_secret': 'august1ftw',
#     "email": "kevin@stamped.com",
# }
# result = handlePOST(path, data)

# path = "stamps/likes/show.json"
# data = {
#     "oauth_token": token['access_token'],
#     "stamp_id": "4ea866d532a7ba4fc0000406",
# }
# result = handleGET(path, data)

path = "account/settings.json"
data = {
    "oauth_token": token['access_token'],
    "screen_name": "kevin1",
}
result = handlePOST(path, data)


print result

print
print


