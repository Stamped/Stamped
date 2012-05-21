#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'EntitySource' ]

import Globals
from logs import report

try:
    from BasicSource    import BasicSource
    import logs
    import re
    from datetime       import datetime
    from libs.LibUtils           import months
except:
    report()
    raise


class EntitySource(BasicSource):
    """
    Entity merger
    """
    def __init__(self, entity, groups):
        BasicSource.__init__(self, 'entity')
        self.__groups = set(groups)
        self.__entity = entity
        for group in groups:
            if group.groupName != 'stamped':
                self.addGroup(group.groupName)

    def enrichEntity(self, entity, controller, decorations, timestamps):
        modified = False
        for group in self.__groups:
            mod = group.syncFields(self.__entity, entity)
            if mod:
                modified = True
        return True

