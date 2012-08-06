#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from twilio.rest import TwilioRestClient

ACCOUNT = "ACf58c6c70f623299adb2aa20ea64d8b5a"
TOKEN   = "fc27f2652e0e49e2dcf763224e9cb51e"

"""
347

STAMPED = 7826733
"""

class SMSClient(object):
    
    def __init__(self):
        self.client  = TwilioRestClient(ACCOUNT, TOKEN)
        self.index   = 0
        self.senders = [
            "+19177467420", 
            "+19177466420", 
            "+19177465420", 
            "+19177463420", 
            "+19177461420", 
            "+19177460420", 
            "+12628067069", 
            "+19177464205", 
            "+19177464207", 
            "+19177464209", 
        ]
    
    def send_sms(self, recipient_number, sender_number=None, body="stamped.com/download"):
        # round-robin sender number
        if sender_number is None:
            sender_number = self.senders[self.index]
            self.index   += 1
            
            if self.index >= len(self.senders):
                self.index = 0
        
        return self.client.sms.messages.create(to=recipient_number, from_=sender_number, body=body)

__globalSMSClient = None

def globalSMSClient():
    global __globalSMSClient
    
    if __globalSMSClient is None:
        __globalSMSClient = SMSClient()
    
    return __globalSMSClient

