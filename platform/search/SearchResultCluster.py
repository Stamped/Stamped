#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import datetime
import math
import re
from utils import indentText
from search.SearchResult import SearchResult
from resolve.EntityProxyComparator import *

class SearchResultCluster(object):
    """
    Encapsulates a cluster of search results that we believe belong to the same entity.
    """
    def __init__(self, initial_result):
        self.__primary_result = None
        self.__results = []
        self.__relevance = None
        self.__dataQuality = None
        self.__names = set([])
        self.add_result(initial_result)

    @property
    def comparator(self):
        raise NotImplementedError()

    @property
    def primary_result(self):
        return self.__primary_result

    def add_result(self, result):
        self.__results.append(result)
        self.__names.add(result.resolverObject.name)
        # TODO PRELAUNCH: Should use data quality here once it's reliably populated!
        if self.__primary_result is None or result.relevance > self.__primary_result.relevance:
            self.__primary_result = result
        self.__relevance = None
        self.__dataQuality = None

    def grok(self, other_cluster):
        """
        If I chopped you up and made a stew of you, you and the stew, whatever else was in it, would grok--and when I
        ate you, we would go together and nothing would be lost and it would not matter which one of us did the chopping
        up and eating.
        """
        for result in other_cluster.results:
            self.add_result(result)

    @property
    def names(self):
        return self.__names

    @property
    def dataQuality(self):
        if self.__dataQuality is not None:
            return self.__dataQuality
        # For now, just take the max score.
        # TODO PRELAUNCH: Revisit this.
        dataQuality = 0
        for result in self.__results:
            dataQuality = max(dataQuality, result.dataQuality)
        return dataQuality

    @property
    def relevance(self):
        if self.__relevance is not None:
            return self.__relevance
        relevance_scores_by_source = {}
        for result in self.__results:
            relevance_scores_by_source.setdefault(result.resolverObject.source, []).append(result.relevance)
        composite_scores = []
        for (source, source_scores) in relevance_scores_by_source.items():
            source_scores.sort(reverse=True)
            source_score = source_scores[0]
            for (score_idx, secondary_score) in list(enumerate(source_scores))[1:]:
                # The marginal value that additional elements within the same source can contribute is small.
                source_score += secondary_score * (0.7 ** score_idx)
            composite_scores.append(source_score)
        composite_scores.sort(reverse=True)
        cluster_relevance_score = composite_scores[0]
        for (score_idx, secondary_score) in list(enumerate(composite_scores))[1:]:
            # Supporting results across other sources are completely additive.
            cluster_relevance_score += secondary_score
        self.__relevance = cluster_relevance_score
        return self.__relevance

    @property
    def results(self):
        return self.__results[:]

    def compare(self, other):
        """
        Compares a SearchResultCluster to either another full cluster or another single result.
        """
        if isinstance(other, SearchResultCluster):
            other_results = other.results
        elif isinstance(other, SearchResult):
            other_results = [other]
        else:
            raise Exception("Unrecognized argument to SearchResultCluster.compare of type %s" % type(other))
        match_score = None
        for result in self.results:
            for other_result in other_results:
                comparison = self.comparator.compare_proxies(result.resolverObject, other_result.resolverObject)
                if comparison.is_definitely_not_match():
                    return CompareResult.definitely_not_match()
                if comparison.is_match():
                    match_score = max(comparison.score, match_score)
        if match_score is None:
            return CompareResult.unknown()
        else:
            return CompareResult.match(match_score)

    def __repr__(self):
        # TODO: Indicate which one is the "primary"
        return 'Cluster, "%s", of %d elements with relevance %f, dataQuality %f.\n%s' % \
            (self.primary_result.resolverObject.name.encode('utf-8'),
             len(self.__results),
             self.relevance,
             self.dataQuality,
             '\n'.join(indentText(str(result), 4) for result in self.__results))


class ArtistSearchResultCluster(SearchResultCluster):
    @property
    def comparator(self):
        return ArtistEntityProxyComparator()

class AlbumSearchResultCluster(SearchResultCluster):
    @property
    def comparator(self):
        return AlbumEntityProxyComparator()

class TrackSearchResultCluster(SearchResultCluster):
    @property
    def comparator(self):
        return TrackEntityProxyComparator()

class MovieSearchResultCluster(SearchResultCluster):
    @property
    def comparator(self):
        return MovieEntityProxyComparator()

class TvSearchResultCluster(SearchResultCluster):
    @property
    def comparator(self):
        return TvEntityProxyComparator()

class BookSearchResultCluster(SearchResultCluster):
    @property
    def comparator(self):
        return BookEntityProxyComparator()

class PlaceSearchResultCluster(SearchResultCluster):
    @property
    def comparator(self):
        return PlaceEntityProxyComparator()

class AppSearchResultCluster(SearchResultCluster):
    @property
    def comparator(self):
        return AppEntityProxyComparator()
