#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from utils import indentText

class SearchResult(object):
    """
    Encapsulates a search result as returned from a source library. At this point it has been converted to a
    ResolverObject and preliminarily scored.
    """
    def __init__(self, resolverObject):
        self.resolverObject = resolverObject
        self.relevance = 0.0
        self.dataQuality = 1.0
        self.__relevanceDebugInfo = []
        self.__dataQualityDebugInfo = []

    @staticmethod
    def __addDebugInfo(debugInfoList, desc, value):
        if isinstance(desc, unicode):
            desc = desc.encode('utf-8')
        debugInfoList.append((desc, value))

    def addRelevanceComponentDebugInfo(self, componentName, componentValue):
        SearchResult.__addDebugInfo(self.__relevanceDebugInfo, componentName, componentValue)

    def addDataQualityComponentDebugInfo(self, componentName, componentValue):
        SearchResult.__addDebugInfo(self.__dataQualityDebugInfo, componentName, componentValue)

    @property
    def results(self):
        return self

    def __repr__(self):
        relevanceScoringDetails = '\n'.join(['  %s: %f' % component for component in self.__relevanceDebugInfo])

        reprComponents = ['Relevance score: %f' % self.relevance,
                          'Relevance score details:\n%s' % relevanceScoringDetails,
                          'Data quality score: %f' % self.dataQuality ]
        if self.__dataQualityDebugInfo:
            dataQualityScoringDetails = '\n'.join(['  %s: %f' % component for component in self.__dataQualityDebugInfo])
            reprComponents.append('Data quality score details:\n%s' % dataQualityScoringDetails)
        reprComponents.append('Result:\n%s' % indentText(str(self.resolverObject), 4))

        return '\n'.join(reprComponents)
