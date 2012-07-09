#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'BasicSource' ]

import Globals
from logs import report

try:
    from resolve.AExternalSource        import AExternalSource
except:
    report()
    raise

class BasicSource(AExternalSource):
    """
    """
    def __init__(self, name, groups=None, kinds=None, types=None):
        AExternalSource.__init__(self)
        self.__name   = name
        self.__groups = set()
        self.__kinds  = set()
        self.__types  = set()
        
        if groups is not None:
            self.__groups = set(groups)
        if kinds is not None:
            self.__kinds = set(kinds)
        if types is not None:
            self.__types = set(types)
    
    @property
    def sourceName(self):
        return self.__name

    @property
    def kinds(self):
        return set(self.__kinds)

    @property
    def types(self):
        return set(self.__types)

    def getGroups(self, entity=None):
        try:
            return set(self.__groups)
        except:
            return set()

    def addGroup(self, group):
        self.__groups.add(group)

    def __str__(self):
        return "Source:%s" % self.__name

