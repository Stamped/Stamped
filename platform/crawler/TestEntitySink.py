#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from api_old.AEntitySink import AEntitySink
from Schemas import Entity
from pprint import pprint

class TestEntitySink(AEntitySink):
    
    def __init__(self):
        AEntitySink.__init__(self, "TestEntitySink")
    
    def _processItem(self, item):
        assert isinstance(item, Entity)
        pprint(item.value)
        return
        
        utils.log("%s" % (item.title, ))
    
    def _processItems(self, items):
        for item in items:
            self._processItem(item)

