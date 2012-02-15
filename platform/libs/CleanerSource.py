#!/usr/bin/python

"""
Not finished
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'CleanerSource' ]

import Globals
from logs import log, report

try:
    from AExternalSource    import AExternalSource
except:
    report()
    raise

class CleanerSource(AExternalSource):
    """
    Data-Source wrapper for Factual services.
    """
    def __init__(self):
        AExternalSource.__init__(self)

    def resolveEntity(self, entity, controller):
        """
        Attempt to fill populate id fields based on seed data.

        Returns True if the entity was modified.
        """
        result = False
        return result
    
    def enrichEntity(self, entity, controller):
        """
        Attempt to populate data fields based on id data.

        Returns True if the entity was modified.
        """
        result = False
        return result

    def decorateEntity(self, entity, controller, decoration_db):
        return False

    @property
    def sourceName(self):
        """
        Returns the name of this source as would be used with a SourceController.
        """
        return 'cleaner'
    

