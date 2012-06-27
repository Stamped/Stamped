#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from copy import deepcopy
from utils import indentText, basicNestedObjectToString, normalize

class SearchResult(object):
    """
    Encapsulates a search result as returned from a source library. At this point it has been converted to a
    ResolverObject and preliminarily scored.
    """
    def __init__(self, score, resolverObject):
        self.score = score
        self.__scoreDebugInfo = [ ('base score', score) ]
        self.resolverObject = resolverObject

    def addScoreComponentDebugInfo(self, componentName, componentValue):
        if isinstance(componentName, unicode):
            componentName = componentName.encode('utf-8')
        self.__scoreDebugInfo.append((componentName, componentValue))

    @property
    def scoreDebugInfo(self):
        return deepcopy(self.__scoreDebugInfo)

    @property
    def results(self):
        return self

    def __repr__(self):
        scoreDetails = '\n'.join(['  %s: %f' % componentInfo for componentInfo in self.__scoreDebugInfo])
        return 'Score: %f\nSource: %s\nScore details: %s\nResult:\n%s' % \
               (self.score, self.resolverObject.source, scoreDetails, indentText(str(self.resolverObject), 4))
