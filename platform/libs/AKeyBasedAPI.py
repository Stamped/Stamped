#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import random

class AKeyBasedAPI(object):
    """
        Abstract key-based API designed to overcome usage limits placed on a 
        per-key basis by randomly cycling through available API keys.
    """
    
    def __init__(self, apiKeys=None):
        self._apiKeys = apiKeys
    
    def _getAPIKey(self, offset, count):
        index = self._getAPIIndex(offset, count)
        if index is None:
            return None
        else:
            return self._apiKeys[index]
    
    def _getAPIIndex(self, offset, count):
        # return a fresh API key for every call in which offset remains a 
        # random integer and count cycles from 0 to the number of API keys
        # available. once count overflows the API keys, return None.
        if self._apiKeys is None or count >= len(self._apiKeys):
            return None
        else:
            return (offset + count) % len(self._apiKeys)
    
    def _initAPIKeyIndices(self):
        return self._initRandomStartOffset(len(self._apiKeys))
    
    def _initRandomStartOffset(self, length):
        offset = random.randint(0, max(length - 1, 0))
        count  = 0
        
        return (offset, count)
    
    def _removeKey(self, index):
        del self._apiKeys[index]

