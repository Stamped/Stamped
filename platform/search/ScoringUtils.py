#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from SearchResult import SearchResult

def scoreResultsWithBasicDropoffScoring(resolverObjectList, sourceScore=1.0, dropoffFactor=0.7):
    """
    Takes a list of unscored resolver objects and does the initial pass of scoring, just accounting for base source
    credibility and position in the list.
    """
    currScore = sourceScore
    scoredResults = []
    for resolverObject in resolverObjectList:
        scoredResults.append(SearchResult(currScore, resolverObject))
        currScore *= dropoffFactor
    return scoredResults

def sortByScore(results):
    results.sort(lambda r1, r2:cmp(r1.score, r2.score), reverse=True)

def interleaveResultsByScore(resultLists):
    allResults = [result for resultList in resultLists for result in resultList]
    sortByScore(allResults)
    return allResults

