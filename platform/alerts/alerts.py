#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import os, sys, pymongo, json, struct, ssl, binascii
import binascii, boto, keys.aws, libs.ec2_utils
 
from optparse       import OptionParser
from datetime       import *
from socket         import socket
from errors         import Fail
from HTTPSchemas    import *

from db.mongodb.MongoAlertQueueCollection   import MongoAlertQueueCollection
from db.mongodb.MongoInviteQueueCollection  import MongoInviteQueueCollection
from db.mongodb.MongoAccountCollection      import MongoAccountCollection
from db.mongodb.MongoActivityCollection     import MongoActivityCollection
from MongoStampedAuth                       import MongoStampedAuth

from APNSWrapper import APNSNotificationWrapper, APNSNotification, APNSFeedbackWrapper

base = os.path.dirname(os.path.abspath(__file__))

IPHONE_APN_PUSH_CERT_DEV  = os.path.join(base, 'apns-dev.pem')
IPHONE_APN_PUSH_CERT_PROD = os.path.join(base, 'apns-prod.pem')

IS_PROD       = libs.ec2_utils.is_prod_stack()
USE_PROD_CERT = True

admins = set(['kevin','robby','bart','travis','andybons','landon','edmuki'])
admin_emails = set([
    'kevin@stamped.com',
    'robby@stamped.com',
    'bart@stamped.com',
    'travis@stamped.com',
    'andybons@stamped.com',
    'landon@stamped.com',
    'ed@stamped.com',
])
admin_tokens = set([])

# create wrapper
if USE_PROD_CERT:
    pem = IPHONE_APN_PUSH_CERT_PROD
else:
    pem = IPHONE_APN_PUSH_CERT_DEV

# DB Connections
alertDB             = MongoAlertQueueCollection()
accountDB           = MongoAccountCollection()
activityDB          = MongoActivityCollection()
inviteDB            = MongoInviteQueueCollection()


def parseCommandLine():
    usage   = "Usage: %prog [options] command [args]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)

    parser.add_option("-l", "--limit", dest="limit", 
        default=0, type="int", help="Limit number of records processed")
    
    parser.add_option("-n", "--noop", action="store_true", 
        default=False, help="don't make any actual changes or notifications")
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", help="db to connect to for output")
    
    (options, args) = parser.parse_args()
    
    if options.db:
        utils.init_db_config(options.db)
    
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

        options = parseCommandLine()
        runAlerts(options)
        runInvites(options)
        
        print 'END:   %s' % datetime.utcnow()
        print '-' * 40
    except Exception as e:
        print e
        utils.printException()
        print 'FAIL!'
        print '-' * 40
    finally:
        os.remove(lock)


def runAlerts(options):
    stampedAuth = MongoStampedAuth()

    numAlerts = alertDB.numAlerts()
    alerts  = alertDB.getAlerts(limit=options.limit)
    userIds = {}
    userEmailQueue = {}
    userPushQueue  = {}

    if len(alerts) == 0:
        print 'No alerts!'
        return
    
    for alert in alerts:
        userIds[str(alert['user_id'])] = 1
        userIds[str(alert['recipient_id'])] = 1
    
    accounts = accountDB.getAccounts(userIds.keys())
    
    for account in accounts:
        userIds[account.user_id] = account

    # Get email settings tokens
    tokens = stampedAuth.ensureEmailAlertTokensForUsers(userIds.keys())
    
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
            elif alert.genre == 'friend':
                send_push   = recipient.alerts.ios_alert_follow
                send_email  = None
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
            
            # Build admin list
            if recipient.screen_name in admins:
                admin_emails.add(recipient.email)
                for token in recipient.devices.ios_device_tokens:
                    admin_tokens.add(token)
            
            if send_push:
                try:
                    # Send push notification
                    print 'PUSH'
                    
                    if not recipient.devices.ios_device_tokens:
                        raise
                    print 'DEVICE TOKENS: %s' % recipient.devices.ios_device_tokens

                    # Build push notification
                    for token in recipient.devices.ios_device_tokens:
                        result = buildPushNotification(user, activity, token.dataExport())
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

                    # Add email address
                    if recipient.email not in userEmailQueue:
                        userEmailQueue[recipient.email] = []

                    # Grab settings token
                    token = tokens[recipient.user_id]

                    # Build email
                    email = buildEmail(user, recipient, activity, token)
                    userEmailQueue[recipient.email].append(email)

                    print 'EMAIL COMPLETE'
                except Exception as e:
                    print e
                    print 'EMAIL FAILED'
            
            # Remove the alert
            raise

        except:
            print 'REMOVED'
            if not options.noop:
                alertDB.removeAlert(alert.alert_id)
            
            continue
    
    print
    
    # Send emails
    if len(userEmailQueue) > 0:
        print '-' * 40
        print 'ALERT EMAILS:'
        for k, v in userEmailQueue.iteritems():
            for email in v:
                try:
                    print u"%64s | %s" % (email['to'], email['subject'])
                except Exception as e:
                    print e
        print
        for k, v in userEmailQueue.iteritems():
            print k, len(v)
        print
        sendEmails(userEmailQueue, options)
        print
    
    # Send push notifications
    if len(userPushQueue) > 0:
        print '-' * 40
        print 'ALERT PUSH NOTIFICATIONS:'
        for k, v in userPushQueue.iteritems():
            for push in v:
                print push
        print
        for k, v in userPushQueue.iteritems():
            print k, len(v)
        print
        sendPushNotifications(userPushQueue, options)
        print


def runInvites(options):
    numInvites = inviteDB.numInvites()
    invites  = inviteDB.getInvites(limit=options.limit)
    userIds   = {}
    userEmailQueue = {}
    
    for invite in invites:
        userIds[str(invite['user_id'])] = 1
    
    accounts = accountDB.getAccounts(userIds.keys())
    
    for account in accounts:
        userIds[account.user_id] = account
    
    print 'Number of invitations: %s' % numInvites
    
    for invite in invites:
        try:
            print 
            print

            print invite
            if userIds[str(invite['user_id'])] == 1:
                raise

            ### TODO: Check if recipient is already a member?
            ### TODO: Check if user is on email blacklist

            user = userIds[str(invite['user_id'])]
            emailAddress = invite.recipient_email

            try:
                # Send email
                print 'EMAIL'

                if not emailAddress:
                    raise

                if emailAddress not in userEmailQueue:
                    userEmailQueue[emailAddress] = []

                # Grab template
                try:
                    path = os.path.join(base, 'templates', 'email_invite.html.j2')
                    print path
                    template = open(path, 'r')
                except:
                    ### TODO: Add error logging?
                    raise

                # Build email
                email = {}
                email['to'] = emailAddress
                email['from'] = 'Stamped <noreply@stamped.com>'
                email['subject'] = u'%s thinks you have great taste' % user['name']
                email['invite_id'] = invite.invite_id

                if not IS_PROD:
                    email['subject'] = u'DEV: %s' % email['subject']
                
                params = HTTPUser().importSchema(user).dataExport()
                html = parseTemplate(template, params)
                email['body'] = html

                userEmailQueue[emailAddress].append(email)

                print 'EMAIL COMPLETE'
            except Exception as e:
                print e
                print 'EMAIL FAILED'
            
            # Remove the invite
            raise

        except:
            print 'REMOVED'
            if not options.noop:
                inviteDB.removeInvite(invite.invite_id)
            
            continue

    print

    # Send emails
    if len(userEmailQueue) > 0:
        print '-' * 40
        print 'INVITE EMAILS:'
        for k, v in userEmailQueue.iteritems():
            for email in v:
                try:
                    print u"%64s | %s" % (email['to'], email['subject'])
                except Exception as e:
                    print e
        print
        for k, v in userEmailQueue.iteritems():
            print k, len(v)
        print
        sendEmails(userEmailQueue, options)
        print


def _setSubject(user, genre):

    if genre == 'restamp':
        msg = u'%s (@%s) gave you credit for a stamp' % (user['name'], user.screen_name)

    elif genre == 'like':
        msg = u'%s (@%s) liked your stamp' % (user['name'], user.screen_name)

    elif genre == 'favorite':
        msg = u'%s (@%s) added your stamp as a to-do' % (user['name'], user.screen_name)

    elif genre == 'mention':
        msg = u'%s (@%s) mentioned you on Stamped' % (user['name'], user.screen_name)

    elif genre == 'comment':
        msg = u'%s (@%s) commented on your stamp' % (user['name'], user.screen_name)

    elif genre == 'reply':
        msg = u'%s (@%s) replied to you on Stamped' % (user['name'], user.screen_name)

    elif genre == 'follower':
        msg = u'%s (@%s) is now following you on Stamped' % (user['name'], user.screen_name)
    else:
        ### TODO: Add error logging?
        raise

    if not IS_PROD:
        msg = u'DEV: %s' % msg

    return msg

def _setBody(user, activity, emailAddress, settingsToken):

    try:
        path = os.path.join(base, 'templates', 'email_%s.html.j2' % activity.genre)
        template = open(path, 'r')
    except:
        ### TODO: Add error logging?
        raise

    params = HTTPUser().dataImport(user.dataExport()).dataExport()
    params['title'] = activity['subject']
    params['blurb'] = activity['blurb']

    # HTML Encode the bio?
    if 'bio' not in params:
        params['bio'] = ''
    else:
        params['bio'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

    params['image_url_92'] = params['image_url'].replace('.jpg', '-92x92.jpg')

    # Add email address
    params['email_address'] = emailAddress

    # Add settings url
    settingsUrl = 'http://www.stamped.com/settings/alerts?token=%s' % settingsToken
    params['settings_url'] = settingsUrl

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


def buildEmail(user, recipient, activityItem, settingsToken):
    email = {}
    email['to'] = recipient.email
    email['from'] = 'Stamped <noreply@stamped.com>'
    email['subject'] = _setSubject(user, activityItem.genre)
    email['body'] = _setBody(user, activityItem, recipient.email, settingsToken)
    email['activity_id'] = activityItem.activity_id

    return email


def buildPushNotification(user, activityItem, deviceId):
    genre = activityItem.genre
    
    # Set message
    if genre == 'restamp':
        msg = '%s gave you credit' % (user.screen_name)
    
    elif genre == 'like':
        #msg = u'%s \ue057 your stamp' % (user.screen_name)
        msg = '%s liked your stamp' % (user.screen_name)
    
    elif genre == 'favorite':
        msg = '%s added your stamp as a to-do' % (user.screen_name)

    elif genre == 'mention':
        msg = "%s mentioned you" % (user.screen_name)

    elif genre == 'comment':
        msg = '%s commented on your stamp' % (user.screen_name)

    elif genre == 'reply':
        msg = '%s replied' % (user.screen_name)

    elif genre == 'follower':
        msg = '%s is now following you' % (user.screen_name)

    elif genre == 'friend':
        msg = 'Your friend %s joined Stamped' % (user.screen_name)

    if not IS_PROD:
        msg = 'DEV: %s' % msg
    
    msg = msg.encode('ascii', 'ignore')
    
    """
    # Build payload
    content = {
        'aps': {
            'alert': msg,
            # 'sound': 'default',
        }
    }
    
    # if user.stats.num_unread_news:
    #     content['aps']['badge'] = user.stats.num_unread_news
    
    s_content = json.dumps(content, separators=(',',':'))
    
    # Format actual notification
    fmt = "!cH32sH%ds" % len(s_content)
    command = '\x00'
    
    payload = struct.pack(fmt, command, 32, binascii.unhexlify(deviceId), \
                          len(s_content), s_content)
    """
    
    result = {
        #'payload': payload, 
        'payload': msg, 
        'activity_id': activityItem.activity_id, 
        'device_id': deviceId
    }
    
    return result


def sendEmails(queue, options):
    ses = boto.connect_ses(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
    
    # Apply rate limit
    limit = 8
    
    for user, emailQueue in queue.iteritems():
        if IS_PROD or user in admin_emails:
            count = 0
            emailQueue.reverse()
            for msg in emailQueue:
                try:
                    count += 1
                    if count > limit:
                        print 'LIMIT EXCEEDED (%s)' % count
                        raise
                    
                    if options.noop:
                        print 'EMAIL (activity_id=%s): "To: %s Subject: %s"' % \
                            (msg['activity_id'], msg['to'], msg['subject'])
                        continue
                    
                    ses.send_email(msg['from'], msg['subject'], msg['body'], msg['to'], format='html')
                except Exception as e:
                    try:
                        print 'EMAIL FAILED (activity_id=%s): "To: %s Subject: %s"' % \
                            (msg['activity_id'], msg['to'], msg['subject'])
                    except:
                        print 'EMAIL FAILED (activity_id=%s)' % msg['activity_id']
                    print e
        else:
            print 'SKIPPED: %s' % user


def sendPushNotifications(queue, options):
    # Apply rate limit
    limit = 3
    
    for user, pushQueue in queue.iteritems():
        if IS_PROD or user in admin_tokens:
            apns_wrapper = APNSNotificationWrapper(pem, not USE_PROD_CERT)
            count = 0
            
            pushQueue.reverse()
            for msg in pushQueue:
                count += 1
                if count > limit:
                    print 'LIMIT EXCEEDED (%s)' % count
                
                if options.noop:
                    print 'PUSH MSG (activity_id=%s): device_id = %s ' % \
                        (msg['activity_id'], msg['device_id'])
                    
                    utils.log(msg['payload'])
                    #utils.log(type(msg['payload']))
                    continue
                
                try:
                    # create message
                    message = APNSNotification()
                    
                    #deviceId = 'f02e7b4c384e32404645443203dd0b71750e54fe13b5d0a8a434a12a0f5e7a25' # bart
                    #deviceId = '8b78c702f8c8d5e02c925146d07c28f615283bc862b226343f013b5f8765ba5a' # travis
                    deviceId = str(msg['device_id'])
                    
                    message.token(binascii.unhexlify(deviceId))
                    payload = msg['payload'].encode('ascii', 'ignore')
                    message.alert(payload)
                    #message.badge(num_unread_count)
                    
                    # add message to tuple and send it to APNS server
                    apns_wrapper.append(message)
                except:
                    print 'PUSH MSG FAILED (activity_id=%s): device_id = %s ' % \
                        (msg['activity_id'], msg['device_id'])
                    utils.printException()
            
            apns_wrapper.notify()
    
    return

def removeAPNSTokens():
    # Only run this on prod
    if not IS_PROD or not USE_PROD_CERT:
        print "NOT PROD!"
        raise 

    feedback = APNSFeedbackWrapper(pem, not USE_PROD_CERT)

    for d, t in feedback.tuples():
        token = binascii.hexlify(t)
        try:
            accountDB.removeAPNSToken(token)
            print "REMOVED TOKEN: %s" % token
        except:
            print "FAILED TO REMOVE TOKEN: %s" % token


if __name__ == '__main__':
    main()

