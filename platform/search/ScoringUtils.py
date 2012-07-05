#!/usr/bin/env python

from __future__ import division

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from collections import namedtuple
from search.SearchResult import SearchResult
from resolve.Resolver import simplify
from difflib import SequenceMatcher
from search.DataQualityUtils import *

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
    """Computes how well the given result text satisfies the query text.

    Note that this differs from similarity, in that it is not symmetric. It only matters now much of
    the query text is "fulfilled" by the result text. The result text could have a lot more
    irrelevant terms without affecting the result.

    Returns a pair (relevance, matchingBlocks), where relevance is a score in [0, 1], and
    matchingBlocks is a list of (i, n) blocks indicating that queryText[i:i+n] was matched.
    """
    queryText = simplify(queryText)
    resultText = simplify(resultText)

    nonContinuityPenalty = 1.2
    matchingBlocks = SequenceMatcher(a=queryText, b=resultText).get_matching_blocks()
    matchingBlocks = filter(lambda block: block[2] > 1, matchingBlocks)
    totalMatch = sum(matchSize ** nonContinuityPenalty for _, _, matchSize in matchingBlocks)
    return totalMatch / (len(queryText) ** nonContinuityPenalty), [(i, n) for i, _, n in matchingBlocks]


def combineMatchingSections(matchingSections):
    """Given a list of (i, n) pairs, where each (i, n) pair denotes a block starting at ith
    position, with length n, combine overlapping blocks, and return the total length of the combined
    blocks.
    
    For example, if the input is [(0, 3), (2, 4), (20, 2)], the first two blocks overlap, and will
    be combined to (0, 6). The final result would be 6 + 2 = 8.
    """
    if not matchingSections:
        return 0

    matchingSections.sort()
    collapsedBlocks = [matchingSections[0]]
    for i, n in matchingSections[1:]:
        j, m = collapsedBlocks[-1]
        if i <= j + m:
            collapsedBlocks[-1] = (j, max(i - j + n, m))
        else:
            collapsedBlocks.append((i, n))
    return sum(n for i, n in collapsedBlocks)


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


RelevanceFactor = namedtuple('RelevanceFactor', 'fieldName fieldExtractor maxBoost')

def _adjustRelevanceByQueryMatch(searchResult, queryText, factors, fulfillmentFactor=0.5, fulfillmentExponent=0.5):
    def adjustRelevance(matchFactor, maxBoost, factorName):
        if matchFactor:
            factor = maxBoost ** matchFactor
            searchResult.relevance *= factor
            searchResult.addRelevanceComponentDebugInfo('boost for query match against %s' % factorName, factor)

    matchingBlocks = []
    for fieldName, fieldExtractor, maxBoost in factors:
        factor, blocks = stringRelevance(queryText, fieldExtractor(searchResult))
        matchingBlocks.extend(blocks)
        adjustRelevance(factor, maxBoost, fieldName)

    queryFulfilled = combineMatchingSections(matchingBlocks) / len(queryText)
    # If half-fulfilled, that equals out to 1.
    relevanceMultiplier = queryFulfilled * fulfillmentFactor + 1 - (fulfillmentFactor / 2.0)
    relevanceMultiplier = relevanceMultiplier ** fulfillmentExponent
    searchResult.relevance *= relevanceMultiplier
    searchResult.addRelevanceComponentDebugInfo('boost for fulfilling %f%% of query text' % queryFulfilled,
                                                relevanceMultiplier)


BOOKS_RELEVANCE_FACTORS = (
    RelevanceFactor('title', lambda result: result.resolverObject.name, 2),
    RelevanceFactor('author',
        lambda result: ' '.join(author['name'] for author in result.resolverObject.authors), 1.5),
)
def adjustBookRelevanceByQueryMatch(searchResult, queryText):
    _adjustRelevanceByQueryMatch(searchResult, queryText, BOOKS_RELEVANCE_FACTORS)

MOVIE_RELEVANCE_FACTORS = (
    RelevanceFactor('title', lambda result: result.resolverObject.name, 1.4),
    RelevanceFactor('author', lambda result: ' '.join(actor['name'] for actor in result.resolverObject.cast), 1.2),
    RelevanceFactor('year',
        lambda result: str(result.resolverObject.release_date.year) if result.resolverObject.release_date else '', 1.2),
    RelevanceFactor('description', lambda result: result.resolverObject.description, 1.2)
)
def adjustMovieRelevanceByQueryMatch(searchResult, queryText):
    _adjustRelevanceByQueryMatch(searchResult, queryText, MOVIE_RELEVANCE_FACTORS)

TV_RELEVANCE_FACTORS = (
    RelevanceFactor('title', lambda result: result.resolverObject.name, 1.4),
    RelevanceFactor('year',
        lambda result: str(result.resolverObject.release_date.year) if result.resolverObject.release_date else '', 1.2),
    RelevanceFactor('description', lambda result: result.resolverObject.description, 1.2)
)
def adjustTvRelevanceByQueryMatch(searchResult, queryText):
    _adjustRelevanceByQueryMatch(searchResult, queryText, TV_RELEVANCE_FACTORS)



ARTIST_RELEVANCE_FACTORS = (
    RelevanceFactor('title', lambda result: result.resolverObject.name, 2.0),
)
def adjustArtistRelevanceByQueryMatch(searchResult, queryText):
    # If the whole query is consumed by the artist title alone, that's a big deal.
    _adjustRelevanceByQueryMatch(searchResult, queryText, ARTIST_RELEVANCE_FACTORS, fulfillmentFactor=1, fulfillmentExponent=1)

ALBUM_RELEVANCE_FACTORS = (
    RelevanceFactor('title', lambda result: result.resolverObject.name, 2.0),
    RelevanceFactor('artist', lambda result: ' '.join(artist['name'] for artist in result.resolverObject.artists), 1.0)
)
def adjustAlbumRelevanceByQueryMatch(searchResult, queryText):
    _adjustRelevanceByQueryMatch(searchResult, queryText, ALBUM_RELEVANCE_FACTORS)

TRACK_RELEVANCE_FACTORS = (
    RelevanceFactor('title', lambda result: result.resolverObject.name, 2.0),
    RelevanceFactor('artist', lambda result: ' '.join(artist['name'] for artist in result.resolverObject.artists), 1.0),
    RelevanceFactor('album', lambda result: ' '.join(album['name'] for album in result.resolverObject.albums), 1.0)
)
def adjustTrackRelevanceByQueryMatch(searchResult, queryText):
    _adjustRelevanceByQueryMatch(searchResult, queryText, TRACK_RELEVANCE_FACTORS)


PLACE_RELEVANCE_FACTORS = (
    RelevanceFactor('name', lambda result: result.resolverObject.name, 2.0),
    RelevanceFactor('locality', lambda result: tryToGetLocalityFromPlace(result.resolverObject), 1.2),
    RelevanceFactor('street address', lambda result: tryToGetStreetAddressFromPlace(result.resolverObject), 1.2)
)

def augmentPlaceRelevanceScoresForTitleMatchAndProximity(results, queryText, queryLatLng):
    """
    What I'm really looking for here are hints as to how I should blend between search and autocomplete results.
    TODO: We should do text matching that extends past the title and into the address as well -- queries like
    'Shake Shack Westport' are really good ways to make your intent explicit to Google, but we don't do a good
    job of handling them.
    """
    for result in results:
        _adjustRelevanceByQueryMatch(result, queryText, PLACE_RELEVANCE_FACTORS)

        if queryLatLng and result.resolverObject.coordinates:
            distance = geoDistance(queryLatLng, result.resolverObject.coordinates)
            # Works out to about x2 for being right fucking next to something and x1.2 for being 25km away.
            distance_boost = 1 + math.log(100 / distance, 1000)
            result.relevance *= distance_boost
            result.addRelevanceComponentDebugInfo('proximity score factor', distance_boost)