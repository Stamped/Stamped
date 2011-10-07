#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import os, sys, pymongo, json, struct, ssl, binascii
from optparse import OptionParser
from datetime import *
from socket import socket
 
from errors import Fail

from db.mongodb.MongoAlertCollection import MongoAlertCollection
from db.mongodb.MongoAccountCollection import MongoAccountCollection
from db.mongodb.MongoActivityCollection import MongoActivityCollection

def parseCommandLine():
    usage   = "Usage: %prog [options] command [args]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--headers", action="store_true", dest="show_headers", 
        default=False, help="Include HTTP headers in results")
    
    parser.add_option("-f", "--form", action="store_true", dest="show_form", 
        default=False, help="Include user-submitted input form in results")
    
    parser.add_option("-o", "--output", action="store_true", dest="show_output", 
        default=False, help="Include JSON result in results")
    
    parser.add_option("-e", "--errors", action="store_true", dest="show_errors", 
        default=False, help="Only display errors in results")
    
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", 
        default=False, help="Set verbosity of logs")
    
    parser.add_option("-u", "--user-id", dest="user_id", 
        default=None, type="string", help="Filter results on user id")
    
    parser.add_option("-l", "--limit", dest="limit", 
        default=10, type="int", help="Limit number of results returned")
    
    parser.add_option("-p", "--path", dest="path", 
        default=None, type="string", help="Filter results on url path")
    
    parser.add_option("-t", "--severity", dest="severity", 
        default=None, type="string", help="Filter results on severity (debug, info, warning, error, critical)")
    
    (options, args) = parser.parse_args()

    return options

def main():
    # parse commandline
    options     = parseCommandLine()
    options     = options.__dict__

    alertDB     = MongoAlertCollection()
    accountDB   = MongoAccountCollection()
    activityDB  = MongoActivityCollection()

    numAlerts = alertDB.numAlerts()
    alerts  = alertDB.getAlerts()
    userIds   = {}

    for alert in alerts:
        userIds[str(alert['user_id'])] = 1
        userIds[str(alert['recipient_id'])] = 1
        
    
    accounts = accountDB.getAccounts(userIds.keys())

    for account in accounts:
        userIds[account.user_id] = account

    print 'Number of alerts: %s' % numAlerts
    print
    print 'Accounts: %s' % accounts

    pushQueue = []
    emailQueue = []

    for alert in alerts:
        try:
            print 
            print

            print alert
            if userIds[str(alert['recipient_id'])] == 1 \
                or userIds[str(alert['user_id'])] == 1:
                raise

            # Check recipient settings
            recipient = userIds[str(alert['recipient_id'])]

            if alert.genre == 'restamp':
                notification = recipient.alerts.alert_credit
            elif alert.genre == 'like':
                notification = recipient.alerts.alert_like
            elif alert.genre == 'favorite':
                notification = recipient.alerts.alert_fav
            elif alert.genre == 'mention':
                notification = recipient.alerts.alert_mention
            elif alert.genre == 'comment':
                notification = recipient.alerts.alert_comment
            elif alert.genre == 'reply':
                notification = recipient.alerts.alert_reply
            elif alert.genre == 'follower':
                notification = recipient.alerts.alert_follow
            else:
                notification = None


            if notification == 'p':
                # Send push notification
                print 'SEND PUSH NOTIFICATION'

                if not recipient.devices.ios_device_tokens:
                    raise
                print 'DEVICE TOKENS: %s' % recipient.devices.ios_device_tokens

                # User
                user = userIds[str(alert['user_id'])]
                
                # Activity
                activity = activityDB.getActivityItem(alert.activity_id)

                # Build push notification
                for token in recipient.devices.ios_device_tokens:
                    result = buildPushNotification(user, activity, token.value)
                    pushQueue.append(result)


            elif notification == 'e':
                # Send email
                print 'SEND EMAIL'

                if not recipient.email:
                    raise
                print 'EMAIL ADDRESS: %s' % recipient.email

                # User
                user = userIds[str(alert['user_id'])]
                
                # Activity
                activity = activityDB.getActivityItem(alert.activity_id)

                # Build email

                ### TODO: Kick out to fn that actually builds HTML email


            else:
                raise

            # Remove alert
            print 'COMPLETE'
            # alertDB.removeAlert(alert.alert_id)

        except:
            print 'REMOVED'
            # alertDB.removeAlert(alert.alert_id)
            continue

    # Send emails
    if len(emailQueue) > 0:
        print 'EMAILS:'
        print emailQueue
        print

    # Send push notifications
    if len(pushQueue) > 0:
        print 'PUSH:'
        print pushQueue
        print

    print

def sendEmails(emailQueue):
    pass
    
def sendPushNotifications(pushQueue):
    pass

def buildEmail(user, recipient, activityItem):
    pass

def buildPushNotification(user, activityItem, deviceId):
    genre = activityItem.genre

    # Set message
    if genre == 'restamp':
        msg = "Test"

    elif genre == 'like':
        ### TODO: Include emoji in notification -- &#xe057;
        msg = "Test"
    
    elif genre == 'favorite':
        msg = "Test"

    elif genre == 'mention':
        msg = "%s (@%s) mentioned you on %s." % \
            (user.name, user.screen_name, activityItem.subject)

    elif genre == 'comment':
        msg = "Test"

    elif genre == 'reply':
        msg = "Test"

    elif genre == 'follower':
        msg = "Test"

    # Build payload
    payload = {
        'aps': {
            'alert': msg
        }
    }

    s_payload = json.dumps(payload, separators=(',',':'))

    # Format actual notification
    fmt = "!cH32sH%ds" % len(s_payload)
    command = '\x00'

    result = struct.pack(fmt, command, 32, binascii.unhexlify(deviceId), \
                len(s_payload), s_payload)

    return result

if __name__ == '__main__':
    main()

