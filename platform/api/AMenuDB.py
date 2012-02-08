#!/usr/bin/python

__author__    = "Stamped (dev@Stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class AMenuDB(object):
        
    @abstract
    def getMenus(self, entityId):
        pass
    
    @abstract
    def updateMenu(self, entity_id, source, source_id):
        pass
    