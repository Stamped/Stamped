#!/usr/bin/env python

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
        self.client = TwilioRestClient(ACCOUNT, TOKEN)
        
    def send_sms(self, recipient_number, sender_number="+19177460420", body="stamped.com/download"):
        return self.client.sms.messages.create(to=recipient_number, from_=sender_number, body=body)

__globalSMSClient = None

def globalSMSClient():
    global __globalSMSClient
    
    if __globalSMSClient is None:
        __globalSMSClient = SMSClient()
    
    return __globalSMSClient

