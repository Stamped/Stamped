#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import Entity

from abc    import ABCMeta, abstractmethod

class ASuggestedEntities(object):
    
    """
        Base class responsible for suggesting relevant / popular entities.
    """
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def getSuggestedEntities(self, userId=None, coords=None, category=None, subcategory=None, limit=None):
        """
            Returns a list of suggested entities (separated into sections), restricted 
            to the given category / subcategory, and possibly personalized with respect 
            to the given userId.
            
            Each section is a dict, with at least two required attributes, name, and entities.
        """
        raise NotImplementedError

