#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class ASearchEntityDB(object):
    """
    Database for serving semi-rich "search" entities that have been clustered during the search process but not fully
    enriched. On search, we save the entities into this table -- which acts as a cache -- until they expire or are
    promoted to full entities (when the user stamps them.)
    """
    @abstract
    def getSearchEntityByEntityId(self, entity_id):
        pass

    @abstract
    def writeSearchEntity(self, search_entity):
        pass