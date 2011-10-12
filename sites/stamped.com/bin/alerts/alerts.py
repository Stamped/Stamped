#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils
import os, sys, pymongo, json, struct, ssl, binascii
import boto
from optparse import OptionParser
from datetime import *
from socket import socket
 
from errors import Fail

from db.mongodb.MongoAlertCollection import MongoAlertCollection
from db.mongodb.MongoAccountCollection import MongoAccountCollection
from db.mongodb.MongoActivityCollection import MongoActivityCollection

base = os.path.dirname(os.path.abspath(__file__))

AWS_ACCESS_KEY_ID = 'AKIAIXLZZZT4DMTKZBDQ'
AWS_SECRET_KEY = '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'

IPHONE_APN_PUSH_CERT = os.path.join(base, 'apns-dev.pem')


def parseCommandLine():
    usage   = "Usage: %prog [options] command [args]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)

    parser.add_option("-l", "--limit", dest="limit", 
        default=0, type="int", help="Limit number of records processed")
    
    (options, args) = parser.parse_args()

    return options


def main():
    lock = os.path.join(base, 'alerts.lock')
    if os.path.exists(lock):
        print 'LOCKED'
        return
    
    try:
        open(lock, 'w').close()
        print '-' * 40
        print 'BEGIN: %s' % datetime.utcnow()
        runAlerts()
        print 'END:   %s' % datetime.utcnow()
        print '-' * 40
    except Exception as e:
        print e
        print 'FAIL'
        print '-' * 40
    finally:
        os.remove(lock)


def runAlerts():
    # parse commandline
    options     = parseCommandLine()
    options     = options.__dict__

    alertDB     = MongoAlertCollection()
    accountDB   = MongoAccountCollection()
    activityDB  = MongoActivityCollection()

    numAlerts = alertDB.numAlerts()
    alerts  = alertDB.getAlerts(limit=options['limit'])
    userIds   = {}
    userEmailQueue = {}
    userPushQueue = {}

    for alert in alerts:
        userIds[str(alert['user_id'])] = 1
        userIds[str(alert['recipient_id'])] = 1
        
    
    accounts = accountDB.getAccounts(userIds.keys())

    for account in accounts:
        userIds[account.user_id] = account

    print 'Number of alerts: %s' % numAlerts

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
                send_push   = recipient.alerts.ios_alert_credit
                send_email  = recipient.alerts.email_alert_credit
            elif alert.genre == 'like':
                send_push   = recipient.alerts.ios_alert_like
                send_email  = recipient.alerts.email_alert_like
            elif alert.genre == 'favorite':
                send_push   = recipient.alerts.ios_alert_fav
                send_email  = recipient.alerts.email_alert_fav
            elif alert.genre == 'mention':
                send_push   = recipient.alerts.ios_alert_mention
                send_email  = recipient.alerts.email_alert_mention
            elif alert.genre == 'comment':
                send_push   = recipient.alerts.ios_alert_comment
                send_email  = recipient.alerts.email_alert_comment
            elif alert.genre == 'reply':
                send_push   = recipient.alerts.ios_alert_reply
                send_email  = recipient.alerts.email_alert_reply
            elif alert.genre == 'follower':
                send_push   = recipient.alerts.ios_alert_follow
                send_email  = recipient.alerts.email_alert_follow
            else:
                send_push   = None
                send_email  = None

            # Raise if no settings
            if not send_push and not send_email:
                raise

            # Activity
            activity = activityDB.getActivityItem(alert.activity_id)

            # User
            user = userIds[str(alert['user_id'])]

            if send_push:
                try:
                    # Send push notification
                    print 'PUSH'

                    if not recipient.devices.ios_device_tokens:
                        raise
                    print 'DEVICE TOKENS: %s' % recipient.devices.ios_device_tokens

                    # Build push notification
                    for token in recipient.devices.ios_device_tokens:
                        result = buildPushNotification(user, activity, token.value)
                        if token not in userPushQueue:
                            userPushQueue[token] = []
                        userPushQueue[token].append(result)

                    print 'PUSH COMPLETE'
                except:
                    print 'PUSH FAILED'


            if send_email:
                try:
                    # Send email
                    print 'EMAIL'

                    if not recipient.email:
                        raise

                    if recipient.email not in userEmailQueue:
                        userEmailQueue[recipient.email] = []

                    # Build email
                    email = buildEmail(user, recipient, activity)
                    userEmailQueue[recipient.email].append(email)

                    print 'EMAIL COMPLETE'
                except Exception as e:
                    print e
                    print 'EMAIL FAILED'
            
            # Remove the alert
            raise

        except:
            print 'REMOVED'
            alertDB.removeAlert(alert.alert_id)
            continue

    print

    # Send emails
    if len(userEmailQueue) > 0:
        print '-' * 40
        print 'EMAILS:'
        for k, v in userEmailQueue.iteritems():
            for email in v:
                print "%64s | %s" % (email['to'], email['subject'])
        print
        for k, v in userEmailQueue.iteritems():
            print k, len(v)
        sendEmails(userEmailQueue)
        print

    # Send push notifications
    if len(userPushQueue) > 0:
        print '-' * 40
        print 'PUSH:'
        for k, v in userPushQueue.iteritems():
            for push in v:
                print push
        print
        for k, v in userPushQueue.iteritems():
            print k, len(v)
        print
        sendPushNotifications(userPushQueue)
        print


def _setSubject(user, genre):

    if genre == 'restamp':
        msg = '%s (@%s) gave you credit for a stamp' % (user['name'], user.screen_name)

    elif genre == 'like':
        msg = '%s (@%s) liked your stamp' % (user['name'], user.screen_name)

    elif genre == 'favorite':
        msg = '%s (@%s) added your stamp as a to-do' % (user['name'], user.screen_name)

    elif genre == 'mention':
        msg = '%s (@%s) mentioned you on Stamped' % (user['name'], user.screen_name)

    elif genre == 'comment':
        msg = '%s (@%s) commented on your stamp' % (user['name'], user.screen_name)

    elif genre == 'reply':
        msg = '%s (@%s) replied to you on Stamped' % (user['name'], user.screen_name)

    elif genre == 'follower':
        msg = '%s (@%s) is now following you on Stamped' % (user['name'], user.screen_name)
    else:
        ### TODO: Add error logging?
        raise Exception

    return msg

def _setBody(user, activity):

    try:
        path = os.path.join(base, 'templates', 'email_%s.html.j2' % activity.genre)
        template = open(path, 'r')
    except:
        ### TODO: Add error logging?
        raise Exception

    params = {
        'screen_name': user['screen_name'],
        'name': user['name'],
        'title': activity['subject'],
        'blurb': activity['blurb'],
    }

    html = parseTemplate(template, params)

    return html


def parseTemplate(src, params):
    try:
        from jinja2 import Template
    except ImportError:
        print "error installing Jinja2"
        raise
    
    source = src.read()
    template = Template(source)
    return template.render(params)


def buildEmail(user, recipient, activityItem):
    email = {}
    email['to'] = recipient.email
    email['from'] = 'Stamped <noreply@stamped.com>'
    email['subject'] = _setSubject(user, activityItem.genre)
    email['body'] = _setBody(user, activityItem)
    email['activity_id'] = activityItem.activity_id

    return email


def buildPushNotification(user, activityItem, deviceId):
    genre = activityItem.genre

    # Set message
    if genre == 'restamp':
        msg = '%s gave you credit' % (user.screen_name)

    elif genre == 'like':
        msg = u'%s \ue057 your stamp' % (user.screen_name)
    
    elif genre == 'favorite':
        msg = '%s added your stamp as a to-do' % (user.screen_name)

    elif genre == 'mention':
        msg = "%s mentioned you on a stamp" % (user.screen_name)

    elif genre == 'comment':
        msg = '%s commented on your stamp' % (user.screen_name)

    elif genre == 'reply':
        msg = '%s replied to you' % (user.screen_name)

    elif genre == 'follower':
        msg = '%s is now following you' % (user.screen_name)

    # Build payload
    content = {
        'aps': {
            'alert': msg,
            'sound': 'default',
        }
    }

    s_content = json.dumps(content, separators=(',',':'))

    # Format actual notification
    fmt = "!cH32sH%ds" % len(s_content)
    command = '\x00'

    payload = struct.pack(fmt, command, 32, binascii.unhexlify(deviceId), \
                len(s_content), s_content)

    result = {
        'payload': payload,
        'activity_id': activityItem.activity_id,
        'device_id': deviceId
    }

    return result


def sendEmails(queue):
    ses = boto.connect_ses(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)

    # Apply rate limit
    limit = 8

    for user, emailQueue in queue.iteritems():
        count = 0
        emailQueue.reverse()
        for msg in emailQueue:
            try:
                count += 1
                if count > limit:
                    print 'LIMIT EXCEEDED (%s)' % count
                    raise
                ses.send_email(msg['from'], msg['subject'], msg['body'], msg['to'], format='html')
            except:
                print 'EMAIL FAILED (activity_id=%s): "To: %s Subject: %s"' % \
                    (msg['activity_id'], msg['to'], msg['subject'])


def sendPushNotifications(queue):
    host_name = 'gateway.sandbox.push.apple.com'
    # host_name = 'gateway.push.apple.com'

    # Apply rate limit
    limit = 3

    try:
        s = socket()
        c = ssl.wrap_socket(s,
                            ssl_version=ssl.PROTOCOL_SSLv3,
                            certfile=IPHONE_APN_PUSH_CERT)
        c.connect((host_name, 2195))

        for user, pushQueue in queue.iteritems():
            count = 0
            pushQueue.reverse()
            for msg in pushQueue:
                try:
                    count += 1
                    if count > limit:
                        print 'LIMIT EXCEEDED (%s)' % count
                        raise
                    c.write(msg['payload'])
                except:
                    print 'MESSAGE FAILED (activity_id=%s): device_id = %s ' % \
                        (msg['activity_id'], msg['device_id'])
        c.close()
    except:
        print 'FAIL: %s' % queue


if __name__ == '__main__':
    main()

