#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, logs
import os, sys, pymongo, json, struct, ssl, binascii
import binascii, boto, keys.aws, libs.ec2_utils
 
from optparse       import OptionParser
from datetime       import *
from socket         import socket
from errors         import *
from HTTPSchemas    import *

from db.mongodb.MongoAlertQueueCollection   import MongoAlertQueueCollection
from db.mongodb.MongoInviteQueueCollection  import MongoInviteQueueCollection
from db.mongodb.MongoAccountCollection      import MongoAccountCollection
from db.mongodb.MongoActivityCollection     import MongoActivityCollection
from MongoStampedAuth                       import MongoStampedAuth
from MongoStampedAPI                        import MongoStampedAPI

from APNSWrapper import APNSNotificationWrapper, APNSNotification, APNSFeedbackWrapper

base = os.path.dirname(os.path.abspath(__file__))

IPHONE_APN_PUSH_CERT_DEV  = os.path.join(base, 'apns-ether-prod.pem')
IPHONE_APN_PUSH_CERT_PROD = os.path.join(base, 'apns-ether-prod.pem')

IS_PROD       = libs.ec2_utils.is_prod_stack()
USE_PROD_CERT = True

admins = set(['kevin','robby','bart','travis','ml','landon','anthony','lizwalton','jstaehle'])
admin_emails = set([
    'kevin@stamped.com',
    'robby@stamped.com',
    'bart@stamped.com',
    'travis@stamped.com',
    'mike@stamped.com',
    'landon@stamped.com',
    'anthony@stamped.com',
    'liz@stamped.com',
    'paul@stamped.com',
    'geoff@stamped.com',
    'joey@stamped.com',         'jws295@cornell.edu',
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

# API
api                 = MongoStampedAPI()


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
    logs.begin(
        saveLog=api._logsDB.saveLog,
        saveStat=api._statsDB.addStat,
        nodeName=api.node_name
    )
    logs.async_request('alerts')

    logs.warning('WARNING: USING PUSH NOTIFICATION CERTS FOR "ETHER" APP')

    lock = os.path.join(base, 'alerts.lock')
    if os.path.exists(lock):
        logs.warning('Locked - aborting')
        return
    
    try:
        open(lock, 'w').close()
        options = parseCommandLine()
        runAlerts(options)
        # runInvites(options)

    except Exception as e:
        logs.warning('Exception: %s' % e)
        logs.warning(utils.getFormattedException())
        logs.error(500)

    finally:
        os.remove(lock)
        try:
            logs.save()
        except Exception:
            print '\n\n\nWARNING: UNABLE TO SAVE LOGS\n\n\n'


def runAlerts(options):
    stampedAuth = MongoStampedAuth()

    numAlerts = alertDB.numAlerts()
    alerts = alertDB.getAlerts(limit=options.limit)
    userIds = {}
    userUnreadCount = {}
    userEmailQueue = {}
    userPushQueue = {}
    userPushUnread = {}

    if len(alerts) == 0:
        logs.info('No alerts!')
        return
    
    for alert in alerts:
        userIds[str(alert.subject)] = None
        userIds[str(alert.recipient_id)] = None
    
    accounts = accountDB.getAccounts(userIds.keys())
    
    for account in accounts:
        userIds[account.user_id] = account

    # Get email settings tokens
    tokens = stampedAuth.ensureEmailAlertTokensForUsers(userIds.keys())
    
    logs.info('Number of alerts: %s' % numAlerts)
    
    for alert in alerts:
        try:
            if userIds[str(alert.recipient_id)] is None or userIds[str(alert.subject)] is None:
                msg = "Recipient (%s) or user (%s) not found" % (alert.recipient_id, alert.subject)
                raise StampedUnavailableError(msg)

            # Check recipient settings
            recipient = userIds[str(alert.recipient_id)]
            settings = recipient.alert_settings

            if alert.verb == 'credit':
                send_push   = settings.alerts_credits_apns
                send_email  = settings.alerts_credits_email
            elif alert.verb == 'like':
                send_push   = settings.alerts_likes_apns
                send_email  = settings.alerts_likes_email
            elif alert.verb == 'todo':
                send_push   = settings.alerts_todos_apns
                send_email  = settings.alerts_todos_email
            elif alert.verb == 'mention':
                send_push   = settings.alerts_mentions_apns
                send_email  = settings.alerts_mentions_email
            elif alert.verb == 'comment':
                send_push   = settings.alerts_comments_apns
                send_email  = settings.alerts_comments_email
            elif alert.verb == 'reply':
                send_push   = settings.alerts_replies_apns
                send_email  = settings.alerts_replies_email
            elif alert.verb == 'follow':
                send_push   = settings.alerts_followers_apns
                send_email  = settings.alerts_followers_email
            elif alert.verb.startswith('friend_'):
                send_push   = None ## TODO: Add
                send_email  = None ## TODO: Add
            elif alert.verb.startswith('action_'):
                send_push   = None ## TODO: Add
                send_email  = None ## TODO: Add
            else:
                send_push   = None
                send_email  = None
            
            # User
            user = userIds[str(alert.subject)]
            
            # Build admin list
            if recipient.screen_name in admins:
                admin_emails.add(recipient.email)
                for token in recipient.devices.ios_device_tokens:
                    admin_tokens.add(token)

            # Build unread count
            if alert.recipient_id not in userUnreadCount:
                try:
                    userUnreadCount[alert.recipient_id] = api.getUnreadActivityCount(alert.recipient_id)
                except Exception as e:
                    logs.warning("Unable to set unread count: %s" % e)
                    userUnreadCount[alert.recipient_id] = 0
            
            # Build APNS notifications
            if send_push:
                try:
                    if recipient.devices is not None and recipient.devices.ios_device_tokens is not None:
                        # Build push notification and add to queue
                        numUnread = userUnreadCount[alert.recipient_id]
                        msg = _pushNotificationMessage(alert.verb, user)
                        for deviceId in recipient.devices.ios_device_tokens:
                            result = buildPushNotification(alert.activity_id, msg=msg, numUnread=numUnread)
                            if deviceId not in userPushQueue:
                                userPushQueue[deviceId] = []
                            userPushQueue[deviceId].append(result)
                    else:
                        logs.info("No devices found for recipient '%s'" % recipient.user_id)

                except Exception as e:
                    logs.warning("Push generation failed for alert '%s': %s" % (alert.alert_id, e))
                    logs.debug("User: %s" % user.user_id)
                    logs.debug("Recipient: %s" % recipient.user_id)

            elif userUnreadCount[alert.recipient_id] > 0 and alert.recipient_id not in userPushUnread:
                """
                If the user doesn't have alerts enabled but we have an APNS token for them, send them a notification 
                with just the badge count. This will only be applied during sending if no other push notifications are 
                sent.
                """
                try:
                    if recipient.devices is not None and recipient.devices.ios_device_tokens is not None:
                        numUnread = userUnreadCount[alert.recipient_id]
                        for deviceId in recipient.devices.ios_device_tokens:
                            userPushUnread[deviceId] = numUnread
                    else:
                        logs.info("No devices found for recipient '%s'" % recipient.user_id)

                except Exception as e:
                    logs.warning("Push count generation failed for alert '%s': %s" % (alert.alert_id, e))
                    logs.debug("User: %s" % user.user_id)
                    logs.debug("Recipient: %s" % recipient.user_id)

            # Build email
            if send_email:
                try:
                    if recipient.email is not None: ### TODO: Check for validity of email address

                        # Add email address
                        if recipient.email not in userEmailQueue:
                            userEmailQueue[recipient.email] = []

                        # Grab settings token
                        token = tokens[recipient.user_id]

                        # Build email
                        subject = _setSubject(alert.verb, user)
                        body = _setBody(alert.verb, token, user, alert.objects)
                        email = buildEmail(alert.activity_id, subject, body)
                        userEmailQueue[recipient.email].append(email)
                    else:
                        logs.info("No email address found for recipient '%s'" % recipient.user_id)

                except Exception as e:
                    logs.warning("Email generation failed for alert '%s': %s" % (alert.alert_id, e))
                    logs.debug("User: %s" % user.user_id)
                    logs.debug("Recipient: %s" % recipient.user_id)

        except Exception as e:
            logs.warning("An error occurred: %s" % e)
            logs.warning("Alert removed: %s" % alert)

        finally:
            if not options.noop:
                alertDB.removeAlert(alert.alert_id)
    
    # Send emails
    if len(userEmailQueue) > 0:
        sendEmails(userEmailQueue, options)
    
    # Send push notifications
    if len(userPushQueue) > 0:
        sendPushNotifications(userPushQueue, userPushUnread, options)

"""
def runInvites(options):
    numInvites = inviteDB.numInvites()
    invites  = inviteDB.getInvites(limit=options.limit)
    userIds   = {}
    userEmailQueue = {}
    
    for invite in invites:
        userIds[str(invite.user_id)] = 1
    
    accounts = accountDB.getAccounts(userIds.keys())
    
    for account in accounts:
        userIds[account.user_id] = account
    
    print 'Number of invitations: %s' % numInvites
    
    for invite in invites:
        try:
            print 
            print

            print invite
            if userIds[str(invite.user_id)] == 1:
                raise

            ### TODO: Check if recipient is already a member?
            ### TODO: Check if user is on email blacklist

            user = userIds[str(invite.user_id)]
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
                email['subject'] = u'%s thinks you have great taste' % user.name
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
                pass
                # inviteDB.removeInvite(invite.invite_id)

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
"""

def _setSubject(verb, user):

    if verb == 'credit':
        msg = u'%s (@%s) gave you credit for a stamp' % (user.name, user.screen_name)

    elif verb == 'like':
        msg = u'%s (@%s) liked your stamp' % (user.name, user.screen_name)

    elif verb == 'todo':
        msg = u'%s (@%s) added your stamp as a to-do' % (user.name, user.screen_name)

    elif verb == 'mention':
        msg = u'%s (@%s) mentioned you on Stamped' % (user.name, user.screen_name)

    elif verb == 'comment':
        msg = u'%s (@%s) commented on your stamp' % (user.name, user.screen_name)

    elif verb == 'reply':
        msg = u'%s (@%s) replied to you on Stamped' % (user.name, user.screen_name)

    elif verb == 'follow':
        msg = u'%s (@%s) is now following you on Stamped' % (user.name, user.screen_name)
    else:
        logs.warning("Invalid verb for subject: %s" % verb)
        raise

    if not IS_PROD:
        msg = u'DEV: %s' % msg

    return msg

def _setBody(verb, settingsToken, user, objects=None):

    try:
        path = os.path.join(base, 'templates', 'email_%s.html.j2' % verb)
        template = open(path, 'r')
    except Exception as e:
        logs.warning("Unable to get email template: %s" % verb)
        raise

    params = HTTPUser().importUser(user).dataExport()

    if objects is not None:
        if objects.stamp_ids is not None and len(objects.stamp_ids) > 0:
            stampId = objects.stamp_ids[-1]
            ### TODO: Cache stamp objects
            #if stampId in stampIds:
            stamp = api.getStamp(stampId)
            params['title'] = stamp.entity.title
            if verb == 'credit' or verb == 'mention':
                params['blurb'] = stamp.contents[-1].blurb

        if objects.comment_ids is not None and len(objects.comment_ids) > 0:
            commentId = objects.comment_ids[-1]
            comment = self._commentDB.getComment(commentId)
            if 'title' not in params:
                stampId = comment.stamp_id 
                stamp = api.getStamp(stampId)
                params['title'] = stamp.entity.title
            params['blurb'] = comment.blurb

    # HTML Encode the bio?
    if 'bio' not in params:
        params['bio'] = ''
    else:
        replacements = [
            ('&', '&amp;'),
            ('<', '&lt;'),
            ('>', '&gt;'),
            ('"', '&quot;'),
            ("'", '&#39;'),
        ]
        for replacement in replacements:
            params['bio'].replace(replacement[0], replacement[1])

    params['image_url_96'] = params['image_url'].replace('.jpg', '-96x96.jpg')

    # Add settings url
    params['settings_url'] = 'http://www.stamped.com/settings/alerts?token=%s' % settingsToken

    try:
        html = parseTemplate(template, params)
    except Exception as e:
        logs.warning("Could not parse template: %s" % e)
        raise

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


def buildEmail(activityId, subject, body):
    email = {}
    email['from'] = 'Stamped <noreply@stamped.com>'
    email['subject'] = subject
    email['body'] = body
    email['activity_id'] = activityId

    return email


def _pushNotificationMessage(verb, user):
    if verb == 'credit':
        msg = '%s gave you credit' % (user.screen_name)

    elif verb == 'like':
        #msg = u'%s \ue057 your stamp' % (user.screen_name)
        msg = '%s liked your stamp' % (user.screen_name)

    elif verb == 'todo':
        msg = '%s added your stamp as a to-do' % (user.screen_name)

    elif verb == 'mention':
        msg = "%s mentioned you" % (user.screen_name)

    elif verb == 'comment':
        msg = '%s commented on your stamp' % (user.screen_name)

    elif verb == 'reply':
        msg = '%s replied' % (user.screen_name)

    elif verb == 'follow':
        msg = '%s is now following you' % (user.screen_name)

    elif verb.startswith('friend_'):
        if verb == 'friend_twitter':
            msg = 'Your Twitter friend %s joined Stamped' % (user.screen_name)
        elif verb == 'friend_facebook':
            msg = 'Your Facebook friend %s joined Stamped' % (user.screen_name)
        else:
            msg = 'Your friend %s joined Stamped' % (user.screen_name)

    else:
        raise Exception("Unrecognized verb: %s" % verb)

    if not IS_PROD:
        msg = 'DEV: %s' % msg

    msg = msg.encode('ascii', 'ignore')

    return msg

def buildPushNotification(activityId, msg=None, numUnread=0):
    # Convert the number of unread news items for badge count
    badge = -1
    if numUnread > 0:
        badge = numUnread

    result = {
        'activity_id'   : activityId,
        'badge'         : badge,
    }

    if msg is not None:
        result['message'] = msg
    
    return result


def sendEmails(queue, options):
    # Apply rate limit
    limit = 8

    ses = boto.connect_ses(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
    
    for emailAddress, emailQueue in queue.iteritems():
        if IS_PROD or emailAddress in admin_emails:
            count = 0
            emailQueue.reverse()
            for item in emailQueue:
                count += 1
                if count > limit:
                    logs.debug("Limit exceeded for email '%s'" % emailAddress)
                    break

                try:
                    logs.debug("Email activity_id '%s' to address '%s'" % (item['activity_id'], emailAddress))
                    if not options.noop:
                        ses.send_email(item['from'], item['subject'], item['body'], emailAddress, format='html')

                except Exception as e:
                    logs.warning("Email failed for activity_id '%s' to address '%s'" % \
                        (item['activity_id'], emailAddress))
                    logs.warning(utils.getFormattedException())

    logs.info("Success!")


def sendPushNotifications(queue, unreadQueue, options):
    # Apply rate limit
    limit = 3

    apns_wrapper = APNSNotificationWrapper(pem, not USE_PROD_CERT)
    
    for deviceId, pushQueue in queue.iteritems():
        if IS_PROD or deviceId in admin_tokens:
            count = 0
            
            pushQueue.reverse()
            for item in pushQueue:
                count += 1
                if count > limit:
                    logs.debug("Limit exceeded for device '%s'" % deviceId)
                    break
                
                try:
                    # Build APNS notification
                    logs.debug("Push activity_id '%s' to device '%s'" % (item['activity_id'], deviceId))

                    apnsNotification = APNSNotification()
                    apnsNotification.token(binascii.unhexlify(deviceId))

                    if 'message' in item:
                        msg = item['message'].encode('ascii', 'ignore')
                        apnsNotification.alert(msg)
                    
                    if 'badge' in item:
                        apnsNotification.badge(item['badge'])

                    # Add notification to wrapper
                    apns_wrapper.append(apnsNotification)

                except Exception as e:
                    logs.warning("Push failed for activity_id '%s' to device_id '%s'" % (item['activity_id'], deviceId))
                    logs.warning(utils.getFormattedException())

    for deviceId, numUnread in unreadQueue.iteritems():
        if IS_PROD or deviceId in admin_tokens:
            if deviceId not in queue:
                try:
                    # Build APNS notification
                    logs.debug("Push unread count to device '%s'" % (deviceId))

                    apnsNotification = APNSNotification()
                    apnsNotification.token(binascii.unhexlify(deviceId))
                    apnsNotification.badge(numUnread)

                    # Add notification to wrapper
                    apns_wrapper.append(apnsNotification)

                except Exception as e:
                    logs.warning("Push failed for unread count to device_id '%s'" % deviceId)
                    logs.warning(utils.getFormattedException())

    logs.info("Submitting %s push notifications" % apns_wrapper.count())
    if not options.noop:
        apns_wrapper.notify()
    logs.info("Success!")

def removeAPNSTokens():
    raise NotImplementedError 

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

