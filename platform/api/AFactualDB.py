#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@Stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class AFactualDB(object):

    @abstract
    def factual_data(self, entity):
        pass

    @abstract
    def factual_update(self, entity, force_update=False, force_resolve=False, force_enrich=False):
        pass
    
    @abstract
    def stale(self,entity):
        pass
    
