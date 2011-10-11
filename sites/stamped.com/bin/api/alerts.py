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

AWS_ACCESS_KEY_ID = 'AKIAIXLZZZT4DMTKZBDQ'
AWS_SECRET_KEY = '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'

IPHONE_APN_PUSH_CERT = 'apns-dev.pem'

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
    alerts  = alertDB.getAlerts(limit=100)
    userIds   = {}

    for alert in alerts:
        userIds[str(alert['user_id'])] = 1
        userIds[str(alert['recipient_id'])] = 1
        
    
    accounts = accountDB.getAccounts(userIds.keys())

    for account in accounts:
        userIds[account.user_id] = account

    print 'Number of alerts: %s' % numAlerts
    print
    print 'Accounts:'
    for k, v in userIds.iteritems():
        print v.value
    print

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
                        pushQueue.append(result)

                    print 'PUSH COMPLETE'
                except:
                    print 'PUSH FAILED'


            if send_email:
                try:
                    # Send email
                    print 'EMAIL'

                    if not recipient.email:
                        raise

                    # Build email
                    email = buildEmail(user, recipient, activity)
                    emailQueue.append(email)

                    print 'EMAIL COMPLETE'
                except:
                    print 'EMAIL FAILED'
            
            # Remove the alert
            raise

        except:
            print 'REMOVED'
            # alertDB.removeAlert(alert.alert_id)
            continue

    print

    # Send emails
    if len(emailQueue) > 0:
        print '-' * 40
        print 'EMAILS:'
        print emailQueue
        print

    # Send push notifications
    if len(pushQueue) > 0:
        print '-' * 40
        print 'PUSH:'
        print pushQueue
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

    commentHTML = """
        <tr><td width="600" align="center"><table cellpadding="0" cellspacing="0"><tr><td rowspan=2 width="94" 
        height="94"><img src="http://static.stamped.com/users/%(screen_name)s-92x92.jpg" width="92" height="92" border="1" 
        alt="%(screen_name)s" style="border-size:1px;border-style:solid;border-color:#e6e6e6"></td><td rowspan=2 width="20" 
        height="92">&nbsp;</td><td width="455" valign="top" height="28" style="color:#999;font-family:Helvetica,Arial;
        font-weight:bold;font-size:16px">%(screen_name)s</td></tr><tr><td width="445" style="color:#333;font-family:Helvetica,Arial;
        font-size:16px;" valign="top">%(blurb)s</td></tr></table></td></tr><tr><td width="600" height="44" align="center" 
        valign="middle"><img src="http://static.stamped.com/assets/img/email-line.png" width="593" height="3"></td></tr>
    """

    userHTML = """
        <tr><td width="600" align="center"><table cellpadding="0" cellspacing="0"><tr><td rowspan=2 width="94" 
        height="94"><img src="http://static.stamped.com/users/%(screen_name)s-92x92.jpg" width="92" height="92" border="1" 
        alt="%(screen_name)s" style="border-size:1px;border-style:solid;border-color:#e6e6e6"></td><td rowspan=2 width="20" 
        height="92">&nbsp;</td><td width="455" valign="top" height="28" style="color:#999;font-family:Helvetica,Arial;
        font-weight:bold;font-size:16px">%(screen_name)s</td></tr><tr><td width="445" style="color:#333;font-family:Helvetica,Arial;
        font-size:16px;" valign="top">%(blurb)s</td></tr></table></td></tr><tr><td width="600" height="44" align="center" 
        valign="middle"><img src="http://static.stamped.com/assets/img/email-line.png" width="593" height="3"></td></tr>
    """

    content = ''

    if activity.genre == 'follower':
        msg = '<strong>%s</strong> (@%s) is now following you on Stamped.' % \
            (user['name'], user.screen_name)
        content = userHTML % {'screen_name': user.screen_name, 'blurb': activity.blurb}

    elif activity.genre == 'like':
        msg = '<strong>%s</strong> (@%s) liked your stamp of <strong>%s</strong>.' % \
            (user['name'], user.screen_name, activity.subject)

    elif activity.genre == 'favorite':
        msg = '<strong>%s</strong> (@%s) added <strong>%s</strong> as a to-do.' % \
            (user['name'], user.screen_name, activity.subject)

    elif activity.genre == 'restamp':
        msg = '<strong>%s</strong> (@%s) gave you credit for <strong>%s</strong>.' % \
            (user['name'], user.screen_name, activity.subject)
        content = commentHTML % {'screen_name': user.screen_name, 'blurb': activity.blurb}

    elif activity.genre == 'mention':
        msg = '<strong>%s</strong> (@%s) mentioned you <strong>%s</strong>.' % \
            (user['name'], user.screen_name, activity.subject)
        content = commentHTML % {'screen_name': user.screen_name, 'blurb': activity.blurb}

    elif activity.genre == 'comment':
        msg = '<strong>%s</strong> (@%s) commented on <strong>%s</strong>.' % \
            (user['name'], user.screen_name, activity.subject)
        content = commentHTML % {'screen_name': user.screen_name, 'blurb': activity.blurb}

    elif activity.genre == 'reply':
        msg = '<strong>%s</strong> (@%s) replied to you on <strong>%s</strong>.' % \
            (user['name'], user.screen_name, activity.subject)
        content = commentHTML % {'screen_name': user.screen_name, 'blurb': activity.blurb}
        
    else:
        ### TODO: Add error logging?
        raise Exception


    template = """<html><body bgcolor="#f3f3f3"><table id="fullbody" width="100%" cellpadding="0" cellspacing="0"><tr><td 
        align="center" bgcolor="#f3f3f3"><table id="body" cellpadding="0" cellspacing="0"><tr><td width="5"></td><td width="650" 
        height="40" align="center" valign="bottom"><img src="http://static.stamped.com/assets/img/email-logo-top.png" width="650" 
        height="30" style="display:block;"></td><td width="5"></td></tr><tr><td width="5"></td><td width="650" height="160" 
        align="center" bgcolor="white"><img src="http://static.stamped.com/assets/img/email-logo.png" width="650" height="160" 
        alt="Stamped Logo" style="display:block;"></td><td width="5"></td></tr><tr><td width="5"></td><td width="650" align="center" 
        bgcolor="white"><table id="content" cellpadding="0" cellspacing="0"><tr><td height="6" style="font-size:3px;">&nbsp;</td>
        </tr><tr><td align="center" bgcolor="white"><table width="600" cellpadding="0" cellspacing="0"><tr><td width="600" 
        height="36" align="center" valign="bottom" style="color:#333;font-family:Helvetica,Arial;font-size:16px">%s</td></tr><tr>
        <td width="600" height="44" align="center" valign="middle"><img src="http://static.stamped.com/assets/img/email-line.png" 
        width="593" height="3"></td></tr>
        %s
        <tr><td width="600" height="72" align="center" valign="middle"><img 
        src="http://static.stamped.com/assets/img/email-icon.png" width="68" height="64" alt="App Icon"></td></tr><tr><td 
        width="600" height="24" align="center" valign="middle" style="color:#397de0;font-family:Helvetica,Arial;font-size:16px;
        font-weight:bold;margin:0;padding:0;">Launch Stamped</td></tr><tr><td width="600" height="40" align="center" valign="top" 
        style="color:#666;font-family:Helvetica,Arial;font-size:12px;margin:0;padding:0;">
        to reply to @%s</td></tr></table></td></tr></table></td><td width="5"></td></tr><tr><td width="5"></td><td width="650" 
        height="18" align="center"><img src="http://static.stamped.com/assets/img/email-ribbon-bottom.png" width="650" height="18">
        </td><td width="5"></td></tr><tr><td width="5"></td><td width="650" height="18" align="center">&nbsp;</td><td width="5">
        </td></tr><tr><td colspan="3" width="660" height="24" align="center" valign="middle"><a href="" style="color:#779bc3;
        text-decoration:none;font-family:Helvetica,Arial;font-size:12px;">Change your notification settings</a></td></tr><tr>
        <td colspan="3" width="660" height="80" align="center" valign="top" style="color:#999;font-family:Helvetica,Arial;
        font-size:12px;">&copy;2011 Stamped, Inc.</td></tr></table></td></tr></table></body></html>""" % \
        (msg, content, user.screen_name)

    return template


def buildEmail(user, recipient, activityItem):
    email = {}
    email['to'] = recipient.email
    email['from'] = 'Stamped <noreply@stamped.com>'
    email['subject'] = _setSubject(user, activityItem.genre)
    email['body'] = _setBody(user, activityItem)

    return email


def buildPushNotification(user, activityItem, deviceId):
    genre = activityItem.genre

    # Set message
    if genre == 'restamp':
        msg = '%s (@%s) gave you credit for a stamp' % (user['name'], user.screen_name)

    elif genre == 'like':
        ### TODO: Include emoji in notification -- &#xe057;
        msg = '%s (@%s) liked your stamp' % (user['name'], user.screen_name)
    
    elif genre == 'favorite':
        msg = '%s (@%s) added your stamp as a to-do' % (user['name'], user.screen_name)

    elif genre == 'mention':
        msg = "%s (@%s) mentioned you on %s." % \
            (user['name'], user.screen_name, activityItem.subject)

    elif genre == 'comment':
        msg = '%s (@%s) commented on your stamp' % (user['name'], user.screen_name)

    elif genre == 'reply':
        msg = '%s (@%s) replied to you on Stamped' % (user['name'], user.screen_name)

    elif genre == 'follower':
        msg = '%s (@%s) is now following you on Stamped' % (user['name'], user.screen_name)

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


def sendEmails(emailQueue):
    ses = boto.connect_ses(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)

    for msg in emailQueue:
        try:
            ses.send_email(msg['from'], msg['subject'], msg['body'], msg['to'])
        except:
            print 'EMAIL FAILED: %s' % msg


def sendPushNotifications(pushQueue):
    host_name = 'gateway.sandbox.push.apple.com'
    # host_name = 'gateway.push.apple.com'
    try:
        s = socket()
        c = ssl.wrap_socket(s,
                            ssl_version=ssl.PROTOCOL_SSLv3,
                            certfile=IPHONE_APN_PUSH_CERT)
        c.connect((host_name, 2195))
        for msg in pushQueue:
            try:
                c.write(msg)
            except:
                print 'MESSAGE FAILED: %s' % msg
        c.close()
    except:
        print 'FAIL: %s' % pushQueue


if __name__ == '__main__':
    main()

