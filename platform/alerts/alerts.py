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
from api.HTTPSchemas            import *
from api.SchemaValidation       import validateEmail
from utils                  import lazyProperty
from jinja2                 import Template

from api.db.mongodb.MongoAlertQueueCollection   import MongoAlertQueueCollection
from api.db.mongodb.MongoInviteQueueCollection  import MongoInviteQueueCollection
from api.db.mongodb.MongoAccountCollection      import MongoAccountCollection
from api.MongoStampedAuth                       import MongoStampedAuth
from api.MongoStampedAPI                        import MongoStampedAPI

from APNSWrapper import APNSNotificationWrapper, APNSNotification, APNSFeedbackWrapper

base = os.path.dirname(os.path.abspath(__file__))

IPHONE_APN_PUSH_CERT_DEV  = os.path.join(base, 'apns-ether-prod.pem')
IPHONE_APN_PUSH_CERT_PROD = os.path.join(base, 'apns-ether-prod.pem')

IS_PROD = libs.ec2_utils.is_prod_stack()

admins = set(['kevin','robby','bart','travis','ml','landon','anthony','lizwalton','jstaehle','geoffliu'])


stampedAPI = MongoStampedAPI()


class Email(object):
    def __init__(self, recipient):
        self._recipient = recipient

    @property 
    def recipient(self):
        return self._recipient

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
        self._verb = verb 
        self._subject = subject
        self._objects = objects
        self._activityId = activityId
        self._settingsUrl = 'http://www.stamped.com/settings/alerts?token=%s' % settingsToken

    def __repr__(self):
        return "<Alert Email: activity='%s', recipient='%s', verb='%s', title='%s'>" % \
            (self._activityId, self._recipient, self._verb, self.title)

    @property 
    def activityId(self):
        return self._activityId

    @lazyProperty 
    def title(self):
        assert self._subject is not None 

        if self._verb == 'credit':
            msg = u'%s (@%s) gave you credit for a stamp' % (self._subject.name, self._subject.screen_name)

        elif self._verb == 'like':
            msg = u'%s (@%s) liked your stamp' % (self._subject.name, self._subject.screen_name)

        elif self._verb == 'todo':
            msg = u'%s (@%s) added your stamp as a to-do' % (self._subject.name, self._subject.screen_name)

        elif self._verb == 'mention':
            msg = u'%s (@%s) mentioned you on Stamped' % (self._subject.name, self._subject.screen_name)

        elif self._verb == 'comment':
            msg = u'%s (@%s) commented on your stamp' % (self._subject.name, self._subject.screen_name)

        elif self._verb == 'reply':
            msg = u'%s (@%s) replied to you on Stamped' % (self._subject.name, self._subject.screen_name)

        elif self._verb == 'follow':
            msg = u'%s (@%s) is now following you on Stamped' % (self._subject.name, self._subject.screen_name)

        elif self._verb == 'friend':
            msg = u'Your friend %s (@%s) joined Stamped' % (self._subject.name, self._subject.screen_name)

        elif self._verb == 'action':
            msg = u'%s (@%s) did something to your stamp' % (self._subject.name, self._subject.screen_name)

        else:
            logs.warning("Invalid verb for title: %s" % verb)
            raise

        if not IS_PROD:
            msg = u'DEV: %s' % msg

        return msg

    @lazyProperty 
    def body(self):
        try:
            path = os.path.join(base, 'templates', 'email_%s.html.j2' % self._verb.split('_')[0])
            template = open(path, 'r')
        except Exception as e:
            logs.warning("Unable to get email template: %s" % self._verb)
            raise

        assert self._subject is not None
        params = HTTPUser().importUser(self._subject).dataExport()

        if self._objects is not None:
            if self._objects.stamp_ids is not None and len(self._objects.stamp_ids) > 0:
                stampId = self._objects.stamp_ids[-1]
                ### TODO: Cache stamp objects
                #if stampId in stampIds:
                stamp = stampedAPI.getStamp(stampId)
                params['title'] = stamp.entity.title
                if self._verb == 'credit' or self._verb == 'mention':
                    params['blurb'] = stamp.contents[-1].blurb

            if self._objects.comment_ids is not None and len(self._objects.comment_ids) > 0:
                commentId = self._objects.comment_ids[-1]
                comment = stampedAPI._commentDB.getComment(commentId)
                if 'title' not in params:
                    stampId = comment.stamp_id 
                    stamp = stampedAPI.getStamp(stampId)
                    params['title'] = stamp.entity.title
                params['blurb'] = comment.blurb

            if self._objects.entity_ids is not None and len(self._objects.entity_ids) > 0 and 'title' not in params:
                entityId = self._objects.entity_ids[-1]
                entity = stampedAPI._entityDB.getEntity(entityId)
                params['title'] = entity.title

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
        params['settings_url'] = self._settingsUrl

        return self._parseTemplate(template, params)


class InviteEmail(Email):
    def __init__(self, recipient, subject, inviteId=None):
        Email.__init__(self, recipient)
        self._subject = subject
        self._inviteId = inviteId

    def __repr__(self):
        return "<Invite Email: invite='%s', recipient='%s', title='%s'>" % \
            (self._inviteId, self._recipient, self.title)

    @property 
    def inviteId(self):
        return self._inviteId

    @lazyProperty 
    def title(self):
        title = u'%s thinks you have great taste' % self._subject.name

        if not IS_PROD:
            title = u'DEV: %s' % title

        return title

    @lazyProperty 
    def body(self):
        try:
            path = os.path.join(base, 'templates', 'email_invite.html.j2')
            template = open(path, 'r')
        except Exception as e:
            logs.warning("Unable to get email template: %s" % self._verb)
            raise

        params = HTTPUser().importUser(self._subject).dataExport()

        return self._parseTemplate(template, params)


class PushNotification(object):
    def __init__(self, recipient, subject=None, verb=None, unreadCount=0, activityId=None):
        self._recipient = recipient
        self._subject = subject 
        self._verb = verb 
        self._unreadCount = unreadCount
        self._activityId = activityId

    def __repr__(self):
        return "<Push Notification: activity='%s', verb='%s', recipient='%s'" % \
            (self._activityId, self._verb, self._recipient)

    @property 
    def activityId(self):
        return self._activityId

    @property 
    def message(self):
        if self._verb is None or self._subject is None:
            return None 

        if self._verb == 'credit':
            msg = '%s gave you credit' % (self._subject.screen_name)

        elif self._verb == 'like':
            #msg = u'%s \ue057 your stamp' % (user.screen_name)
            msg = '%s liked your stamp' % (self._subject.screen_name)

        elif self._verb == 'todo':
            msg = '%s added your stamp as a to-do' % (self._subject.screen_name)

        elif self._verb == 'mention':
            msg = "%s mentioned you" % (self._subject.screen_name)

        elif self._verb == 'comment':
            msg = '%s commented on your stamp' % (self._subject.screen_name)

        elif self._verb == 'reply':
            msg = '%s replied' % (self._subject.screen_name)

        elif self._verb == 'follow':
            msg = '%s is now following you' % (self._subject.screen_name)

        elif self._verb == 'friend_twitter':
            msg = 'Your Twitter friend %s joined Stamped' % (self._subject.screen_name)
        elif self._verb == 'friend_facebook':
            msg = 'Your Facebook friend %s joined Stamped' % (self._subject.screen_name)
        elif self._verb.startswith('friend_'):
            msg = 'Your friend %s joined Stamped' % (self._subject.screen_name)

        elif self.verb.startswith('action_'):
            msg = '%s interacted with your stamp'

        else:
            raise Exception("Unrecognized verb: %s" % verb)

        if not IS_PROD:
            msg = 'DEV: %s' % msg

        msg = msg.encode('ascii', 'ignore')

        return msg

    @property 
    def badge(self):
        try:
            if self._unreadCount > 0:
                return self._unreadCount
        except Exception as e:
            logs.warning('Unable to get unread count: %s' % e)
        return -1


class NotificationQueue(object):
    def __init__(self, sandbox=True, admins=None):
        self._admins = set()
        self._adminEmails = set(['test-invite@stamped.com'])
        self._adminTokens = set()

        if admins is not None:
            self._admins = set(admins)

        if sandbox:
            self._sandbox = True 
            self._apnsCert = IPHONE_APN_PUSH_CERT_DEV
        else:
            self._sandbox = False
            self._apnsCert = IPHONE_APN_PUSH_CERT_PROD

        self._users = {}
        self._unreadCount = {}
        self._emailQueue = {}
        self._pushQueue = {}

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
            if alert.subject not in self._users:
                self._users[str(alert.subject)] = None
            if alert.recipient_id not in self._users:
                self._users[str(alert.recipient_id)] = None
        
        missingAccounts = set()
        for k, v in self._users.iteritems():
            if v is None:
                missingAccounts.add(k)
        accounts = self._accountDB.getAccounts(list(missingAccounts))
        
        for account in accounts:
            self._users[account.user_id] = account

        # Get email settings tokens
        tokens = self._auth.ensureEmailAlertTokensForUsers(self._users.keys())
        
        for alert in alerts:
            try:
                if self._users[str(alert.recipient_id)] is None or self._users[str(alert.subject)] is None:
                    msg = "Recipient (%s) or user (%s) not found" % (alert.recipient_id, alert.subject)
                    raise StampedUnavailableError(msg)

                # Check recipient settings
                recipient = self._users[str(alert.recipient_id)]
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
                    send_push   = settings.alerts_friends_apns
                    send_email  = settings.alerts_friends_email
                elif alert.verb.startswith('action_'):
                    send_push   = settings.alert_actions_apns
                    send_email  = settings.alert_actions_email
                else:
                    send_push   = False
                    send_email  = False
                
                # Subject
                subject = self._users[str(alert.subject)]
                
                # Build admin list
                if recipient.screen_name in self._admins:
                    self._adminEmails.add(recipient.email)
                    for token in recipient.devices.ios_device_tokens:
                        self._adminTokens.add(token)

                # Build unread count
                if alert.recipient_id not in self._unreadCount:
                    try:
                        self._unreadCount[alert.recipient_id] = stampedAPI.getUnreadActivityCount(alert.recipient_id)
                    except Exception as e:
                        logs.warning("Unable to set unread count: %s" % e)
                        self._unreadCount[alert.recipient_id] = 0
                
                # Build APNS notifications
                if send_push:
                    try:
                        if recipient.devices is not None and recipient.devices.ios_device_tokens is not None:
                            for deviceId in recipient.devices.ios_device_tokens:
                                # Build push notification and add to queue
                                notification = PushNotification(recipient=deviceId, 
                                                                subject=subject, 
                                                                verb=alert.verb, 
                                                                unreadCount=self._unreadCount[alert.recipient_id], 
                                                                activityId=alert.activity_id)
                                if deviceId not in self._pushQueue:
                                    self._pushQueue[deviceId] = []
                                self._pushQueue[deviceId].append(notification)
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
                            if recipient.email not in self._emailQueue:
                                self._emailQueue[recipient.email] = []

                            # Grab settings token
                            token = tokens[recipient.user_id]

                            # Build email
                            email = AlertEmail(recipient=recipient.email, 
                                                verb=alert.verb, 
                                                settingsToken=token, 
                                                subject=subject, 
                                                objects=alert.objects, 
                                                activityId=alert.activity_id)

                            self._emailQueue[recipient.email].append(email)
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
        for recipientId, unreadCount in self._unreadCount.iteritems():
            try:
                if unreadCount > 0:
                    recipient = self._users[recipientId]
                    if recipient.devices is not None and recipient.devices.ios_device_tokens is not None:
                        notification = PushNotification(recipient=recipient, unreadCount=unreadCount)
                        for deviceId in recipient.devices.ios_device_tokens:
                            if deviceId not in self._pushQueue:
                                self._pushQueue[deviceId] = [ notification ]
            except Exception as e:
                logs.warning("Push count generation failed for recipient '%s': %s" % (recipientId, e))

    def buildInvitations(self, limit=0, noop=False):
        invites = self._inviteDB.getInvites(limit=limit)
        
        logs.info('Number of invitations: %s' % len(invites))

        if len(invites) == 0:
            logs.debug('Aborting')
            return
        
        for invite in invites:
            if invite.user_id not in self._users:
                self._users[str(invite.user_id)] = None
        
        missingAccounts = set()
        for k, v in self._users.iteritems():
            if v is None:
                missingAccounts.add(k)
        accounts = self._accountDB.getAccounts(list(missingAccounts))
        
        for account in accounts:
            self._users[account.user_id] = account
        
        for invite in invites:
            try:
                if self._users[str(invite.user_id)] is None:
                    raise StampedUnavailableError("User (%s) not found" % (invite.user_id))

                subject = self._users[str(invite.user_id)]
                emailAddress = invite.recipient_email
                emailAddress = validateEmail(emailAddress)

                # Add email address
                if emailAddress not in self._emailQueue:
                    self._emailQueue[emailAddress] = []

                # Build email
                email = InviteEmail(recipient=emailAddress, subject=subject, inviteId=invite.invite_id)
                
                self._emailQueue[emailAddress].append(email)

            except StampedInvalidEmailError:
                logs.debug("Invalid email address: %s" % invite.recipient_email)
            except Exception as e:
                logs.warning("An error occurred: %s" % e)
                logs.warning("Invite removed: %s" % invite)

            finally:
                if not noop:
                    self._inviteDB.removeInvite(invite.invite_id)

    def sendEmails(self, noop=False):
        logs.info("Submitting emails to %s users" % len(self._emailQueue))

        # Apply rate limit
        limit = 8

        ses = boto.connect_ses(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)

        for emailAddress, emailQueue in self._emailQueue.iteritems():
            if IS_PROD or emailAddress in self._adminEmails:
                count = 0
                emailQueue.reverse()
                for email in emailQueue:
                    count += 1
                    if count > limit:
                        logs.debug("Limit exceeded for email '%s'" % emailAddress)
                        break

                    try:
                        logs.debug("Send email: %s" % (email))
                        if not noop:
                            ses.send_email(email.sender, email.title, email.body, emailAddress, format='html')

                    except Exception as e:
                        logs.warning("Email failed: %s" % email)
                        logs.warning(utils.getFormattedException())

        logs.info("Success!")

    def sendPush(self, noop=False):
        logs.info("Submitting push notifications to %s devices" % len(self._pushQueue))
        # Apply rate limit
        limit = 3
        
        for deviceId, pushQueue in self._pushQueue.iteritems():
            if IS_PROD or deviceId in self._adminTokens:
                count = 0
                
                apns_wrapper = APNSNotificationWrapper(self._apnsCert, sandbox=self._sandbox)

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

                if apns_wrapper.count() > 0:
                    if not noop:
                        apns_wrapper.notify()

        logs.info("Success!")

    def cleanupPush(self, noop=False):
        # Only run this on prod
        if not IS_PROD or noop:
            logs.info("Skipping APNS cleanup (not prod / noop)")
            return

        feedback = APNSFeedbackWrapper(self._apnsCert, sandbox=self._sandbox)

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
            if len(self._emailQueue) > 0:
                self.sendEmails(noop=options.noop)
            if len(self._pushQueue) > 0:
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

