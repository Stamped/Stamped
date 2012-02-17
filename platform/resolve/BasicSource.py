#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'BasicSource' ]

import Globals
from logs import report

try:
    from AExternalSource        import AExternalSource
except:
    report()
    raise

class BasicSource(AExternalSource):
    """
    """
    def __init__(self, name, *groups):
        AExternalSource.__init__(self)
        self.__name = name
        self.__groups = set(groups)
    
    @property
    def sourceName(self):
        return self.__name

    @property
    def groups(self):
        return set(self.__groups)

    def addGroup(self, group):
        self.__groups.add(group)

    def __str__(self):
        return "Source:%s" % self.__name
    