#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from utils import lazyProperty
from api.StampedAuth import StampedAuth

from api.db.mongodb.MongoAccountCollection              import MongoAccountCollection
from api.db.mongodb.MongoAuthAccessTokenCollection      import MongoAuthAccessTokenCollection
from api.db.mongodb.MongoAuthRefreshTokenCollection     import MongoAuthRefreshTokenCollection
from api.db.mongodb.MongoAuthPasswordResetCollection    import MongoAuthPasswordResetCollection
from api.db.mongodb.MongoAuthEmailAlertsCollection      import MongoAuthEmailAlertsCollection

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

