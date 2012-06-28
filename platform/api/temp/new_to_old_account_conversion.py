#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from MongoStampedAPI import MongoStampedAPI
from Schemas import *
from HTTPSchemas import *
from pprint import pprint
from bson.objectid import ObjectId

api = MongoStampedAPI()

print api._accountDB.getAccountByScreenName('landon')

print api._stampDB.getStamp('4fec9a7264c7944e9300000d')

"""

data = api._userDB._collection.find_one({'screen_name_lower': 'landon'})
pprint(data)
print '-' * 40

# Linked Accounts
linked = data.pop('linked', None)
if linked is not None:
    linkedAccounts = {}

    facebook = linked.pop('facebook', None)
    if facebook is not None:
        linkedAccounts['facebook'] = {}
        if 'linked_user_id' in facebook:
            linkedAccounts['facebook']['facebook_id'] = facebook['linked_user_id']
        if 'linked_name' in facebook:
            linkedAccounts['facebook']['facebook_name'] = facebook['linked_name']
        if 'linked_screen_name' in facebook:
            linkedAccounts['facebook']['facebook_screen_name'] = facebook['linked_screen_name']
        linkedAccounts['facebook']['facebook_alerts_sent'] = True

    twitter = linked.pop('twitter', None)
    if twitter is not None:
        linkedAccounts['twitter'] = {}
        if 'linked_user_id' in twitter:
            linkedAccounts['twitter']['twitter_id'] = twitter['linked_user_id']
        if 'linked_screen_name' in twitter:
            linkedAccounts['twitter']['twitter_screen_name'] = twitter['linked_screen_name']
        linkedAccounts['twitter']['twitter_alerts_sent'] = True

    data['linked_accounts'] = linkedAccounts

if 'auth_service' in data:
    del(data['auth_service'])

# Alerts
alerts = data.pop('alert_settings', None)
if alerts is not None:
    alertMapping = {
        'alerts_credits_apns'       : 'ios_alert_credit',
        'alerts_credits_email'      : 'email_alert_credit',
        'alerts_likes_apns'         : 'ios_alert_like',
        'alerts_likes_email'        : 'email_alert_like',
        'alerts_todos_apns'         : 'ios_alert_fav',
        'alerts_todos_email'        : 'email_alert_fav',
        'alerts_mentions_apns'      : 'ios_alert_mention',
        'alerts_mentions_email'     : 'email_alert_mention',
        'alerts_comments_apns'      : 'ios_alert_comment',
        'alerts_comments_email'     : 'email_alert_comment',
        'alerts_replies_apns'       : 'ios_alert_reply',
        'alerts_replies_email'      : 'email_alert_reply',
        'alerts_followers_apns'     : 'ios_alert_follow',
        'alerts_followers_email'    : 'email_alert_follow',
    }

    alertSettings = {}
    for k, v in alerts.iteritems():
        if k in alertMapping.values():
            alertSettings[k] = v 
        elif k in alertMapping:
            alertSettings[alertMapping[k]] = v
    data['alerts'] = alertSettings 

# Stats
stats = data.pop('stats')
if 'distribution' in stats:
    del(stats['distribution'])
if 'num_todos' in stats:
    stats['num_faves'] = stats['num_todos']
    del(stats['num_todos'])
data['stats'] = stats

account = Account(data, overflow=True)
pprint(account.value)
"""

