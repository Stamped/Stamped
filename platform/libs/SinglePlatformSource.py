#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'SinglePlatformSource' ]

import Globals
from logs import log, report

try:
    from AExternalSource        import AExternalSource
    from SinglePlatform         import StampedSinglePlatform
    from utils                  import lazyProperty
    from datetime               import datetime
    from functools              import partial
    from LibUtils               import states
except:
    report()
    raise

class SinglePlatformSource(AExternalSource):

    """
    Data-Source wrapper for SinglePlatform.
    """
    def __init__(self):
        AExternalSource.__init__(self)

    @lazyProperty
    def __singleplatform(self):
        return StampedSinglePlatform()

    def resolveEntity(self, entity, controller):
        return False
    
    def enrichEntity(self, entity, controller):
        return False

    def decorateEntity(self, entity, controller, decoration_db):
        result = False
        singleplatform_id = entity['singleplatform_id']
        if singleplatform_id is not None:
            if controller.shouldDecorate('menu', self.sourceName, entity):
                menu = self.__singleplatform.get_menu_schema(singleplatform_id)
                if menu is not None:
                    menu['entity_id'] = entity['entity_id']
                    entity['menu_source'] = self.sourceName
                    entity['menu_timestamp'] = datetime.utcnow()
                    decoration_db.updateDecoration('menu', menu)
                    log.info('Regenerated menu for %s',singleplatform_id)
                    result = True
        return result

    @property
    def sourceName(self):
        return 'singleplatform'

