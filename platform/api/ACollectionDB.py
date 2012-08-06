#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@Stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped, Inc."
__license__   = "TODO"

import Globals
from utils import abstract

class ACollectionDB(object):
    
    @abstract
    def getInboxStampIDs(self, userId):
        pass
    
    @abstract
    def getUserStampIDs(self, userId):
        pass
    
    @abstract
    def getMentions(self, userId):
        pass

