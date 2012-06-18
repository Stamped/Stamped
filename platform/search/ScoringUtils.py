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

def smoothScores(searchResultList, minGrowthFactor=1.05):
    """
    For several sources and verticals -- the biggest example is music -- we have to issue several requests to the same
    source to capture different subsets of the vertical. (For music, we often have to request tracks/songs/albums
    separately.) We often trust the sources for ranking within these separate requests but are unsure how to interleave
    the different sets. Sometimes we get signals that strongly indicate that certain results in one set are important,
    but these signals are sparse. But we can infer more information from them given the original ranking. For instance,
    if iTunes gives us 10 artists for a query, and we know that the 2nd is highly relevant, and we trust iTunes
    ranking, we can infer that the 1st is at least slightly more relevant.

    That's where this function comes in. It enforces the assumption that every result is at least slightly more relevant
    than the result below it. It is appropriate to use before blending of different result sets from the same trusted
    provider. So the expected workflow is:

    1. Get several result sets.
    2. Call scoreResultsWithBasicDropoffScoring() on each.
    3. Use other insights to adjust scores to address issues with prominence between the result sets. (Correlate songs
       with albums, etc.)
    4. Call smoothScores on each result set that has been augmented.
    5. Optionally adjust scores to correct for known issues with ranking WITHIN result sets. (For instance, if iTunes
       always overestimates the values of indie artists without AMG IDs, you'd want to correct for that here, because
       if you penalize the indie artists badly in #3 it might get undone in #4 if there's an artist below that you
       didn't devalue.)
    6. Combine results with interleaveResultsByScore.
    """
    if len(searchResultList) <= 1:
        return

    resultsBackwards = list(reversed(searchResultList))
    lastScore = resultsBackwards[0].score
    for nextResult in resultsBackwards[1:]:
        lastScore = lastScore * minGrowthFactor
        if nextResult.score >= lastScore:
            lastScore = nextResult.score
        else:
            nextResult.addScoreComponentDebugInfo('Smoothing from %f to %f' % (nextResult.score, lastScore),
                                                  lastScore - nextResult.score)
            nextResult.score = lastScore

def sortByScore(results):
    results.sort(lambda r1, r2:cmp(r1.score, r2.score), reverse=True)

def interleaveResultsByScore(resultLists):
    allResults = [result for resultList in resultLists for result in resultList]
    sortByScore(allResults)
    return allResults

