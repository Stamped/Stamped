#!/usr/bin/env python

from __future__ import division

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from SearchResult import SearchResult
from resolve.Resolver import simplify
from difflib import SequenceMatcher

import math

def scoreResultsWithBasicDropoffScoring(resolverObjectList, sourceScore=1.0, dropoffFactor=0.7):
    """
    Takes a list of resolver objects and does the initial pass of relevance scoring, just accounting for base source
    credibility and position in the list.
    """
    currScore = sourceScore
    searchResults = []
    for rank, resolverObject in enumerate(resolverObjectList):
        result = SearchResult(resolverObject)
        result.relevance = currScore
        result.addRelevanceComponentDebugInfo('Initial score for ranking at %d' % (rank + 1), currScore)
        searchResults.append(result)
        currScore *= dropoffFactor
    return searchResults


def smoothRelevanceScores(searchResultList, minGrowthFactor=1.05):
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
    4. Call smoothRelevanceScores on each result set that has been augmented.
    5. Optionally adjust scores to correct for known issues with ranking WITHIN result sets. (For instance, if iTunes
       always overestimates the values of indie artists without AMG IDs, you'd want to correct for that here, because
       if you penalize the indie artists badly in #3 it might get undone in #4 if there's an artist below that you
       didn't devalue.)
    6. Combine results with interleaveResultsByRelevance.
    """
    if len(searchResultList) <= 1:
        return

    resultsBackwards = list(reversed(searchResultList))
    lastScore = resultsBackwards[0].relevance
    for nextResult in resultsBackwards[1:]:
        lastScore = lastScore * minGrowthFactor
        if nextResult.relevance >= lastScore:
            lastScore = nextResult.relevance
        else:
            nextResult.addRelevanceComponentDebugInfo('Smoothing from %f to %f' % (nextResult.relevance, lastScore),
                                                  lastScore - nextResult.relevance)
            nextResult.relevance = lastScore


def sortByRelevance(results):
    results.sort(key=lambda result: result.relevance, reverse=True)


def stringRelevance(queryText, resultText):
    """Returns a number between 0 and 1, measuring how "relevant" the resultText is for queryText.

    Note that this differs from similarity, in that it is not symmetric. It only matters now much of
    the query text is "fulfilled" by the result text. The result text could have a lot more
    irrelevant terms without affecting the result.
    """
    queryText = simplify(queryText)
    resultText = simplify(resultText)

    # sqrt(2), pulled out of an ass.
    nonContinuityPenalty = 1.414
    matchingBlocks = SequenceMatcher(a=queryText, b=resultText).get_matching_blocks()
    totalMatch = sum(matchSize ** nonContinuityPenalty
            for _, _, matchSize in matchingBlocks if matchSize > 1)
    return totalMatch / (len(queryText) ** nonContinuityPenalty)


def interleaveResultsByRelevance(resultLists):
    allResults = [result for resultList in resultLists for result in resultList]
    sortByRelevance(allResults)
    return allResults


def dedupeById(searchResults, boostFactor=1.0):
    keysToResults = {}
    for searchResult in searchResults:
        key = searchResult.resolverObject.key
        if key in keysToResults:
            priorResult = keysToResults[key]
            # For several sources we send several different types of queries out, and often they can have some overlap.
            # If two queries sent to one source for a specific query both return something with the same key, it's a
            # good sign that the result is relevant.
            priorResult.relevance += searchResult.relevance * boostFactor
            priorResult.addRelevanceComponentDebugInfo('boost from dupe by ID within results from single source',
                                                   boostFactor)
        else:
            keysToResults[key] = searchResult
    return keysToResults.values()


def geoDistance((lat1, lng1), (lat2, lng2)):
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlng = math.radians(lng2-lng1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1))\
                                              * math.cos(math.radians(lat2)) * math.sin(dlng/2) * math.sin(dlng/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d


def augmentScoreForTextRelevance(results, queryText, resultTextExtractor, maxRelevanceBoost):
    for result in results:
        resultText = resultTextExtractor(result)
        titleBoost = maxRelevanceBoost ** stringRelevance(queryText, resultText)
        result.relevance *= titleBoost
        result.addRelevanceComponentDebugInfo('title similarity factor', titleBoost)


def augmentPlaceRelevanceScoresForTitleMatchAndProximity(results, queryText, queryLatLng):
    """
    What I'm really looking for here are hints as to how I should blend between search and autocomplete results.
    TODO: We should do text matching that extends past the title and into the address as well -- queries like
    'Shake Shack Westport' are really good ways to make your intent explicit to Google, but we don't do a good
    job of handling them.
    """
    for result in results:
        # TODO: I think the string matching here underweights substring matches, and especially prefix matches.
        titleSimilarity = SequenceMatcher(',]:-.'.__contains__, queryText, result.resolverObject.name).ratio()
        if titleSimilarity > 0.6:
            factor = 1 + (titleSimilarity - 0.6)
            # Maxes out at 1.5 if it's identical.
            if titleSimilarity == 1:
                factor += 0.1
            result.relevance *= factor
            result.addRelevanceComponentDebugInfo('title similarity factor', factor)

        if queryLatLng and result.resolverObject.coordinates:
            distance = geoDistance(queryLatLng, result.resolverObject.coordinates)
            # Works out to about x2 for being right fucking next to something and x1.2 for being 25km away.
            distance_boost = 1 + math.log(100 / distance, 1000)
            result.relevance *= distance_boost
            result.addRelevanceComponentDebugInfo('proximity score factor', distance_boost)

