#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from utils import lazyProperty
from api_old.StampedAuth import StampedAuth

from db.mongodb.MongoAccountCollection              import MongoAccountCollection
from db.mongodb.MongoAuthAccessTokenCollection      import MongoAuthAccessTokenCollection
from db.mongodb.MongoAuthRefreshTokenCollection     import MongoAuthRefreshTokenCollection
from db.mongodb.MongoAuthPasswordResetCollection    import MongoAuthPasswordResetCollection
from db.mongodb.MongoAuthEmailAlertsCollection      import MongoAuthEmailAlertsCollection

class MongoStampedAuth(StampedAuth):
    """
        Implementation of Stamped Authentication atop MongoDB.
    """
    
    def __init__(self):
        StampedAuth.__init__(self, "MongoStampedAuth")

    @lazyProperty
    def _accountDB(self):
        return MongoAccountCollection()
    
    @lazyProperty
    def _accessTokenDB(self):
        return MongoAuthAccessTokenCollection()

    @lazyProperty
    def _refreshTokenDB(self):
        return MongoAuthRefreshTokenCollection()

    @lazyProperty
    def _passwordResetDB(self):
        return MongoAuthPasswordResetCollection()

    @lazyProperty
    def _emailAlertDB(self):
        return MongoAuthEmailAlertsCollection()

