#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
from abc import abstractmethod
from AEntitySink import AEntitySink
from api.Entity import Entity

class TestEntitySink(AEntitySink):
    
    def __init__(self):
        AEntitySink.__init__(self, "TestEntitySink")
    
    def _processItem(self, item):
        assert isinstance(item, Entity)
        #from pprint import pprint
        #pprint(item._data)
        
        if 'place' in item['details']:
            assert 'googlePlaces' in item.sources
        
        utils.log("%s) %s" % (item.title, item.sources['googlePlaces']['gid']))
    
    def _processItems(self, items):
        for item in items:
            self._processItem(item)

