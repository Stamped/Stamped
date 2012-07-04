#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, logs
import os, sys, pymongo, json, struct
import binascii, boto, keys.aws, libs.ec2_utils
 
from optparse               import OptionParser
from errors                 import *
from HTTPSchemas            import *
from SchemaValidation       import validateEmail
from utils                  import lazyProperty
from jinja2                 import Template

from db.mongodb.MongoAlertQueueCollection   import MongoAlertQueueCollection
from db.mongodb.MongoInviteQueueCollection  import MongoInviteQueueCollection
from db.mongodb.MongoAccountCollection      import MongoAccountCollection
from MongoStampedAuth                       import MongoStampedAuth
from MongoStampedAPI                        import MongoStampedAPI

from APNSWrapper import APNSNotificationWrapper, APNSNotification, APNSFeedbackWrapper

base = os.path.dirname(os.path.abspath(__file__))

IPHONE_APN_PUSH_CERT_DEV  = os.path.join(base, 'apns-ether-prod.pem')
IPHONE_APN_PUSH_CERT_PROD = os.path.join(base, 'apns-ether-prod.pem')

IS_PROD = libs.ec2_utils.is_prod_stack()

admins = set(['kevin','robby','bart','travis','ml','landon','anthony','lizwalton','jstaehle'])


stampedAPI = MongoStampedAPI()


class Email(object):
    def __init__(self, recipient):
        self.__recipient = recipient

    @property 
    def recipient(self):
        return self.__recipient

    @property 
    def sender(self):
        return 'Stamped <noreply@stamped.com>'

    @property 
    def title(self):
        return None

    @property 
    def body(self):
        return None

    def _parseTemplate(self, templateFile, params):
        try:
            source = templateFile.read()
            template = Template(source)
            return template.render(params)
        except Exception as e:
            logs.warning("Could not parse template: %s" % e)
            raise

class AlertEmail(Email):
    def __init__(self, recipient, verb, settingsToken, subject=None, objects=None, activityId=None):
        Email.__init__(self, recipient)
        self.__verb = verb 
        self.__subject = subject
        self.__objects = objects
        self.__activityId = activityId
        self.__settingsUrl = 'http://www.stamped.com/settings/alerts?token=%s' % settingsToken

    def __repr__(self):
        return "<Alert Email: recipient='%s', verb='%s', title='%s'>" % (self.__recipient, self.__verb, self.title)

    @property 
    def activityId(self):
        return self.__activityId

    @lazyProperty 
    def title(self):
        assert self.__subject is not None 

        if self.__verb == 'credit':
            msg = u'%s (@%s) gave you credit for a stamp' % (self.__subject.name, self.__subject.screen_name)

        elif self.__verb == 'like':
            msg = u'%s (@%s) liked your stamp' % (self.__subject.name, self.__subject.screen_name)

        elif self.__verb == 'todo':
            msg = u'%s (@%s) added your stamp as a to-do' % (self.__subject.name, self.__subject.screen_name)

        elif self.__verb == 'mention':
            msg = u'%s (@%s) mentioned you on Stamped' % (self.__subject.name, self.__subject.screen_name)

        elif self.__verb == 'comment':
            msg = u'%s (@%s) commented on your stamp' % (self.__subject.name, self.__subject.screen_name)

        elif self.__verb == 'reply':
            msg = u'%s (@%s) replied to you on Stamped' % (self.__subject.name, self.__subject.screen_name)

        elif self.__verb == 'follow':
            msg = u'%s (@%s) is now following you on Stamped' % (self.__subject.name, self.__subject.screen_name)

        else:
            logs.warning("Invalid verb for title: %s" % verb)
            raise

        if not IS_PROD:
            msg = u'DEV: %s' % msg

        return msg

    @lazyProperty 
    def body(self):
        try:
            path = os.path.join(base, 'templates', 'email_%s.html.j2' % self.__verb)
            template = open(path, 'r')
        except Exception as e:
            logs.warning("Unable to get email template: %s" % self.__verb)
            raise

        assert self.__subject is not None
        params = HTTPUser().importUser(self.__subject).dataExport()

        if self.__objects is not None:
            if self.__objects.stamp_ids is not None and len(self.__objects.stamp_ids) > 0:
                stampId = self.__objects.stamp_ids[-1]
                ### TODO: Cache stamp objects
                #if stampId in stampIds:
                stamp = stampedAPI.getStamp(stampId)
                params['title'] = stamp.entity.title
                if self.__verb == 'credit' or self.__verb == 'mention':
                    params['blurb'] = stamp.contents[-1].blurb

            if self.__objects.comment_ids is not None and len(self.__objects.comment_ids) > 0:
                commentId = self.__objects.comment_ids[-1]
                comment = stampedAPI._commentDB.getComment(commentId)
                if 'title' not in params:
                    stampId = comment.stamp_id 
                    stamp = stampedAPI.getStamp(stampId)
                    params['title'] = stamp.entity.title
                params['blurb'] = comment.blurb

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
        params['settings_url'] = self.__settingsUrl

        return self._parseTemplate(template, params)


class InviteEmail(Email):
    def __init__(self, recipient, subject, inviteId=None):
        Email.__init__(self, recipient)
        self.__subject = subject
        self.__inviteId = inviteId

    def __repr__(self):
        return "<Invite Email: recipient='%s', title='%s'>" % (self.__recipient, self.title)

    @property 
    def inviteId(self):
        return self.__inviteId

    @lazyProperty 
    def title(self):
        title = u'%s thinks you have great taste' % self.__subject.name

        if not IS_PROD:
            title = u'DEV: %s' % title

        return title

    @lazyProperty 
    def body(self):
        try:
            path = os.path.join(base, 'templates', 'email_invite.html.j2')
            template = open(path, 'r')
        except Exception as e:
            logs.warning("Unable to get email template: %s" % self.__verb)
            raise

        params = HTTPUser().importUser(self.__subject).dataExport()

        return parseTemplate(template, params)


class PushNotification(object):
    def __init__(self, recipient, subject=None, verb=None, unreadCount=0, activityId=None):
        self.__recipient = recipient
        self.__subject = subject 
        self.__verb = verb 
        self.__unreadCount = unreadCount
        self.__activityId = activityId

    @property 
    def activityId(self):
        return self.__activityId

    @property 
    def message(self):
        if self.__verb is None or self.__subject is None:
            return None 

        if self.__verb == 'credit':
            msg = '%s gave you credit' % (self.__subject.screen_name)

        elif self.__verb == 'like':
            #msg = u'%s \ue057 your stamp' % (user.screen_name)
            msg = '%s liked your stamp' % (self.__subject.screen_name)

        elif self.__verb == 'todo':
            msg = '%s added your stamp as a to-do' % (self.__subject.screen_name)

        elif self.__verb == 'mention':
            msg = "%s mentioned you" % (self.__subject.screen_name)

        elif self.__verb == 'comment':
            msg = '%s commented on your stamp' % (self.__subject.screen_name)

        elif self.__verb == 'reply':
            msg = '%s replied' % (self.__subject.screen_name)

        elif self.__verb == 'follow':
            msg = '%s is now following you' % (self.__subject.screen_name)

        elif self.__verb == 'friend_twitter':
            msg = 'Your Twitter friend %s joined Stamped' % (self.__subject.screen_name)
        elif self.__verb == 'friend_facebook':
            msg = 'Your Facebook friend %s joined Stamped' % (self.__subject.screen_name)
        elif self.__verb.startswith('friend_'):
            msg = 'Your friend %s joined Stamped' % (self.__subject.screen_name)

        else:
            raise Exception("Unrecognized verb: %s" % verb)

        if not IS_PROD:
            msg = 'DEV: %s' % msg

        msg = msg.encode('ascii', 'ignore')

        return msg

    @property 
    def badge(self):
        if self.__unreadCount > 0:
            return self.__unreadCount
        return -1


class NotificationQueue(object):
    def __init__(self, sandbox=True, admins=None):
        self.__admins = set()
        self.__adminEmails = set()
        self.__adminTokens = set()

        if admins is not None:
            self.__admins = set(admins)

        if sandbox:
            self.__sandbox = True 
            self.__apnsCert = IPHONE_APN_PUSH_CERT_DEV
        else:
            self.__sandbox = False
            self.__apnsCert = IPHONE_APN_PUSH_CERT_PROD

        self.__users = {}
        self.__unreadCount = {}
        self.__emailQueue = {}
        self.__pushQueue = {}

    @lazyProperty
    def _auth(self):
        return MongoStampedAuth()

    @lazyProperty
    def _alertDB(self):
        return MongoAlertQueueCollection()

    @lazyProperty
    def _accountDB(self):
        return MongoAccountCollection()

    @lazyProperty
    def _inviteDB(self):
        return MongoInviteQueueCollection()


    def buildAlerts(self, limit=0, noop=False):
        alerts = self._alertDB.getAlerts(limit=limit)
        
        logs.info('Number of alerts: %s' % len(alerts))

        if len(alerts) == 0:
            logs.debug('Aborting')
            return
        
        for alert in alerts:
            if alert.subject not in self.__users:
                self.__users[str(alert.subject)] = None
            if alert.recipient_id not in self.__users:
                self.__users[str(alert.recipient_id)] = None
        
        missingAccounts = set()
        for k, v in self.__users.iteritems():
            if v is None:
                missingAccounts.add(k)
        accounts = self._accountDB.getAccounts(list(missingAccounts))
        
        for account in accounts:
            self.__users[account.user_id] = account

        # Get email settings tokens
        tokens = self._auth.ensureEmailAlertTokensForUsers(self.__users.keys())
        
        for alert in alerts:
            try:
                if self.__users[str(alert.recipient_id)] is None or self.__users[str(alert.subject)] is None:
                    msg = "Recipient (%s) or user (%s) not found" % (alert.recipient_id, alert.subject)
                    raise StampedUnavailableError(msg)

                # Check recipient settings
                recipient = self.__users[str(alert.recipient_id)]
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
                    send_push   = False ## TODO: Add
                    send_email  = False ## TODO: Add
                elif alert.verb.startswith('action_'):
                    send_push   = False ## TODO: Add
                    send_email  = False ## TODO: Add
                else:
                    send_push   = False
                    send_email  = False
                
                # Subject
                subject = self.__users[str(alert.subject)]
                
                # Build admin list
                if recipient.screen_name in self.__admins:
                    self.__adminEmails.add(recipient.email)
                    for token in recipient.devices.ios_device_tokens:
                        self.__adminTokens.add(token)

                # Build unread count
                if alert.recipient_id not in self.__unreadCount:
                    try:
                        self.__unreadCount[alert.recipient_id] = stampedAPI.getUnreadActivityCount(alert.recipient_id)
                    except Exception as e:
                        logs.warning("Unable to set unread count: %s" % e)
                        self.__unreadCount[alert.recipient_id] = 0
                
                # Build APNS notifications
                if send_push:
                    try:
                        if recipient.devices is not None and recipient.devices.ios_device_tokens is not None:
                            for deviceId in recipient.devices.ios_device_tokens:
                                # Build push notification and add to queue
                                notification = PushNotification(recipient=deviceId, 
                                                                subject=subject, 
                                                                verb=alert.verb, 
                                                                unreadCount=self.__unreadCount[alert.recipient_id], 
                                                                activityId=alert.activity_id)
                                if deviceId not in self.__pushQueue:
                                    self.__pushQueue[deviceId] = []
                                self.__pushQueue[deviceId].append(notification)
                        else:
                            logs.info("No devices found for recipient '%s'" % recipient.user_id)

                    except Exception as e:
                        logs.warning("Push generation failed for alert '%s': %s" % (alert.alert_id, e))
                        logs.debug("Subject: %s" % subject.user_id)
                        logs.debug("Recipient: %s" % recipient.user_id)

                # Build email
                if send_email:
                    try:
                        if recipient.email is not None: 
                            emailAddress = validateEmail(recipient.email)

                            # Add email address
                            if recipient.email not in self.__emailQueue:
                                self.__emailQueue[recipient.email] = []

                            # Grab settings token
                            token = tokens[recipient.user_id]

                            # Build email
                            email = AlertEmail(recipient=recipient.email, 
                                                verb=alert.verb, 
                                                settingsToken=token, 
                                                subject=subject, 
                                                objects=alert.objects, 
                                                activityId=alert.activity_id)

                            self.__emailQueue[recipient.email].append(email)
                        else:
                            logs.info("No email address found for recipient '%s'" % recipient.user_id)

                    except StampedInvalidEmailError:
                        logs.debug("Invalid email address: %s" % recipient.email)
                    except Exception as e:
                        logs.warning("Email generation failed for alert '%s': %s" % (alert.alert_id, e))
                        logs.debug("Subject: %s" % subject.user_id)
                        logs.debug("Recipient: %s" % recipient.user_id)

            except Exception as e:
                logs.warning("An error occurred: %s" % e)
                logs.warning("Alert removed: %s" % alert)

            finally:
                if not noop:
                    self._alertDB.removeAlert(alert.alert_id)

        """
        If the user doesn't have alerts enabled but we have an APNS token for them, send them a notification 
        with just the badge count. This should only occur if no other push notifications exist.
        """
        for recipientId, unreadCount in self.__unreadCount.iteritems():
            try:
                if unreadCount > 0:
                    recipient = self.__users[recipientId]
                    if recipient.devices is not None and recipient.devices.ios_device_tokens is not None:
                        notification = PushNotification(recipient=recipient, unreadCount=unreadCount)
                        for deviceId in recipient.devices.ios_device_tokens:
                            if deviceId not in self.__pushQueue:
                                self.__pushQueue[deviceId] = [ notification ]
            except Exception as e:
                logs.warning("Push count generation failed for recipient '%s': %s" % (recipientId, e))

    def buildInvitations(self, limit=0, noop=False):
        invites = self._inviteDB.getInvites(limit=limit)
        
        logs.info('Number of invitations: %s' % len(invites))

        if len(invites) == 0:
            logs.debug('Aborting')
            return
        
        for invite in invites:
            if invite.user_id not in self.__users:
                self.__users[str(invite.user_id)] = None
        
        missingAccounts = set()
        for k, v in self.__users:
            if v is None:
                missingAccounts.add(k)
        accounts = self._accountDB.getAccounts(list(missingAccounts))
        
        for account in accounts:
            self.__users[account.user_id] = account
        
        for invite in invites:
            try:
                if self.__users[str(invite.user_id)] is None:
                    raise StampedUnavailableError("User (%s) not found" % (invite.user_id))

                subject = self.__users[str(invite.user_id)]
                emailAddress = invite.recipient_email
                emailAddress = validateEmail(emailAddress)

                # Add email address
                if emailAddress not in self.__emailQueue:
                    self.__emailQueue[emailAddress] = []

                # Build email
                email = InviteEmail(recipient=emailAddress, subject=subject, inviteId=invite.invite_id)
                
                self.__emailQueue[emailAddress].append(email)

            except StampedInvalidEmailError:
                logs.debug("Invalid email address: %s" % invite.recipient_email)
            except Exception as e:
                logs.warning("An error occurred: %s" % e)
                logs.warning("Invite removed: %s" % invite)

            finally:
                if not noop:
                    inviteDB.removeInvite(invite.invite_id)

    def sendEmails(self, noop=False):
        logs.info("Submitting emails to %s users" % len(self.__emailQueue))

        # Apply rate limit
        limit = 8

        ses = boto.connect_ses(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)

        for emailAddress, emailQueue in self.__emailQueue.iteritems():
            if IS_PROD or emailAddress in self.__adminEmails:
                count = 0
                emailQueue.reverse()
                for email in emailQueue:
                    count += 1
                    if count > limit:
                        logs.debug("Limit exceeded for email '%s'" % emailAddress)
                        break

                    try:
                        logs.debug("Email activityId '%s' to address '%s'" % (email.activityId, emailAddress))
                        if not noop:
                            ses.send_email(email.sender, email.title, email.body, emailAddress, format='html')

                    except Exception as e:
                        logs.warning("Email failed: %s" % email)
                        logs.warning(utils.getFormattedException())

        logs.info("Success!")

    def sendPush(self, noop=False):
        # Apply rate limit
        limit = 3

        apns_wrapper = APNSNotificationWrapper(self.__apnsCert, not self.__sandbox)
        
        for deviceId, pushQueue in self.__pushQueue.iteritems():
            if IS_PROD or deviceId in self.__adminTokens:
                count = 0
                
                pushQueue.reverse()
                for notification in pushQueue:
                    count += 1
                    if count > limit:
                        logs.debug("Limit exceeded for device '%s'" % deviceId)
                        break
                    
                    try:
                        # Build APNS notification
                        logs.debug("Push activityId '%s' to device '%s'" % (notification.activityId, deviceId))

                        apnsNotification = APNSNotification()
                        apnsNotification.token(binascii.unhexlify(deviceId))

                        if notification.message is not None:
                            msg = notification.message.encode('ascii', 'ignore')
                            apnsNotification.alert(msg)
                        
                        if notification.badge is not None:
                            apnsNotification.badge(notification.badge)

                        # Add notification to wrapper
                        apns_wrapper.append(apnsNotification)

                    except Exception as e:
                        logs.warning("Push failed: '%s'" % notification)
                        logs.warning(utils.getFormattedException())

        logs.info("Submitting %s push notifications" % apns_wrapper.count())
        if not noop:
            apns_wrapper.notify()
        logs.info("Success!")

    def cleanupPush(self, noop=False):
        # Only run this on prod
        if not IS_PROD or noop:
            logs.warning("Skipping APNS cleanup (not prod / noop)")
            return

        feedback = APNSFeedbackWrapper(self.__apnsCert, not self.__sandbox)

        for d, t in feedback.tuples():
            token = binascii.hexlify(t)
            try:
                self._accountDB.removeAPNSToken(token)
                logs.debug("Removed token: %s" % token)
            except Exception as e:
                logs.debug("Failed to remove token: %s" % token)

    def run(self, options):
        logs.begin(
            saveLog=stampedAPI._logsDB.saveLog,
            saveStat=stampedAPI._statsDB.addStat,
            nodeName=stampedAPI.node_name
        )
        logs.async_request('alerts')

        logs.warning('WARNING: USING PUSH NOTIFICATION CERTS FOR "ETHER" APP')

        lock = os.path.join(base, 'alerts.lock')
        if os.path.exists(lock):
            logs.warning('Locked - aborting')
            return
        
        try:
            open(lock, 'w').close()
            self.buildAlerts(limit=options.limit, noop=options.noop)
            self.buildInvitations(limit=options.limit, noop=options.noop)
            self.sendEmails(noop=options.noop)
            self.sendPush(noop=options.noop)
            self.cleanupPush(noop=options.noop)

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
    options = parseCommandLine()
    queue = NotificationQueue(sandbox=False, admins=admins)
    queue.run(options)

if __name__ == '__main__':
    main()

