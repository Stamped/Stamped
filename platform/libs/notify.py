#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import smtplib, utils

from utils import abstract, lazyProperty
from email.mime.text import MIMEText

class ANotificationHandler(object):
    
    def __init__(self, recipients=None):
        if recipients is not None and not isinstance(recipients, list):
            recipients  = [ recipients ]
        
        self.recipients = recipients
    
    @abstract
    def email(self, subject, message, recipients=None):
        pass
    
    @abstract
    def sms(self, subject, message, recipients=None):
        pass
    
    def __str__(self):
        return self.__class__.__name__

class NotificationRecipient(object):
    _carriers = {
        "alltel"    : "alltelmessage.com", 
        "at&t"      : "mobile.mycingular.com",
        "rogers"    : "pcs.rogers.com", 
        "sprint"    : "messaging.sprintpcs.com",
        "tmobile"   : "t-mobile.net", 
        "telus"     : "msg.telus.com",
        "verizon"   : "vtext.com", 
    }
    
    def __init__(self, name=None, email=None, phone=None, carrier=None):
        self.name  = name
        self.email = email
        self.phone = phone
        
        if phone is not None and carrier is not None:
            self.carrier = carrier.lower()
            self.sms = "%s@%s" % (phone, self._carriers[self.carrier])
        else:
            self.carrier = None
            self.sms = None

class GoogleSMTPNotificationHandler(ANotificationHandler):
    
    def __init__(self, username, password, recipients=None):
        ANotificationHandler.__init__(self, recipients)
        
        self.username = username
        self.password = password
    
    def email(self, subject, message, recipients=None):
        if recipients is None:
            recipients = self.recipients
        
        for recipient in recipients:
            if recipient.email is not None:
                self._sendmail(recipient.email, subject, message)
    
    def sms(self, subject, message, recipients=None):
        if recipients is None:
            recipients = self.recipients
        
        for recipient in recipients:
            if recipient.sms is not None:
                self._sendmail(recipient.sms, subject, message)
    
    @lazyProperty
    def _server(self):
        utils.log('[%s] connecting to gmail SMTP server' % self)
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(self.username, self.password)
        
        return server
    
    def _sendmail(self, recipient, subject, message):
        msg             = MIMEText(message)
        msg['From']     = self.username
        msg['To']       = recipient
        
        if subject is not None:
            msg['Subject']  = subject
        
        server = self._server
        
        utils.log("[%s] sending mail to '%s'" % (self, recipient))
        return server.sendmail(self.username, [ recipient ], msg.as_string())

class StampedNotificationHandler(GoogleSMTPNotificationHandler):
    def __init__(self):
        recipients = [
            NotificationRecipient(name='dev',    email='dev@stamped.com'), 
            NotificationRecipient(name='travis', phone='2622156221', carrier='at&t'), 
            NotificationRecipient(name='kevin',  phone='3123155045', carrier='at&t'), 
        ]
        
        GoogleSMTPNotificationHandler.__init__(self, 'notifications@stamped.com', 'mariotennis', recipients)

if __name__ == "__main__":
    recipients = [
        NotificationRecipient(email='travis@stamped.com'), 
        NotificationRecipient(phone='2622156221', carrier='at&t'), 
    ]
    
    handler = GoogleSMTPNotificationHandler('notifications@stamped.com', 'mariotennis', recipients)
    
    handler.email('[TEST0]', 'test message0')
    handler.sms('[TEST1]',   'test message1')

