#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

import logs
from utils import lazyProperty

from db.mongodb.MongoInvitationCollection import MongoInvitationCollection

class InvitationDB(object):

    @lazyProperty
    def __invitation_collection(self):
        return MongoInvitationCollection()

    def checkInviteExists(self, email, userId):
        return self.__invitation_collection.checkInviteExists(email, userId)
    
    def inviteUser(self, email, userId):
        return self.__invitation_collection.inviteUser(email, userId)
    
    def getInvitations(self, email):
        return self.__invitation_collection.getInvitations(email)

    def join(self, email):
        return self.__invitation_collection.join(email)
    
    def remove(self, email):
        return self.__invitation_collection.remove(email)
