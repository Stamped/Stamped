#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import Entity

from abc    import ABCMeta, abstractmethod

class ASuggestedEntities(object):
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def getSuggestedEntities(self, userId=None, coords=None, category=None, subcategory=None, limit=None):
        raise NotImplementedError

