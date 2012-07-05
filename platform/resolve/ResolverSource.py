#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'ResolverSource' ]

import Globals
from logs import report

try:
    from resolve.BasicSource    import BasicSource
    import logs
    import re
    from datetime       import datetime
    from libs.LibUtils           import months
    from resolve.StampedSource  import StampedSource
except:
    report()
    raise


class ResolverSource(BasicSource):
    """
    DB-resolution based dedupper
    """
    def __init__(self):
        BasicSource.__init__(self, 'resolver',
            groups=['successor']
        )

    @lazyProperty
    def __stamped(self):
        return StampedSource()

    def enrichEntity(self, entity, controller, decorations, timestamps):
        """
        query = self.__stamped.wrapperFromEntity(entity)
        results = self.resolver.resolve(query, self.matchSource(query),count=5)
        dups = []
        if len(results) != 0:
            best = results[0]
            if best[0]['resolved']:
                entity[self.idField] = best[1].key
        """
        return True

