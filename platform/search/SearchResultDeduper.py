#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from resolve.ResolverObject import *
from resolve.Resolver import *
from search.ScoringUtils import *
from search.SearchResultCluster import *

class SearchResultDeduper(object):

    def dedupeResults(self, category, resultLists):
        """
        Takes the search category and one list of results per source.
        """
        # We have to cap results here because the deduping process is O(n^2).
        maxResultsPerSource = 30
        for resultList in resultLists:
            resultList[maxResultsPerSource:] = []
        dedupeFnMap = {'music': self.__dedupeMusicResults,
                       'film': self.__dedupeVideoResults,
                       'place': self.__dedupePlaceResults,
                       'app': self.__dedupeAppResults,
                       'book': self.__dedupeBookResults}
        return dedupeFnMap[category](resultLists)

    def __formClusters(self, search_results, cluster_class):
        search_results.sort(key=lambda r: r.dataQuality, reverse=True)
        clusters = []
        # For the most part we just treat clustering as transitive, but every once in a while we find two clusters that
        # we have some overriding reason to believe are not the same. Because these clusters are not the same, but are
        # close, we want to avoid comparing them again and again every time we get in objects that are similar to both.
        # So we keep track of pairs of clusters that we know can't be merged just to avoid the re-comparison.
        known_non_matches = set()
        for result in search_results:
            match_scores_and_clusters = []
            cluster_non_matches = []
            for cluster in clusters:
                comparison = cluster.compare(result)
                if comparison.is_match():
                    match_scores_and_clusters.append((comparison.score, cluster))
                elif comparison.is_definitely_not_match():
                    cluster_non_matches.append(cluster)
            if len(match_scores_and_clusters) == 0:
                cluster = cluster_class(result)
                clusters.append(cluster)
            elif len(match_scores_and_clusters) == 1:
                cluster = match_scores_and_clusters[0][1]
                cluster.add_result(result)
            elif len(match_scores_and_clusters) > 1:
                match_scores_and_clusters.sort(reverse=True)
                cluster = match_scores_and_clusters[0][1]
                cluster.add_result(result)
                unmerged_matches = 0
                for (match_score, secondary_match_cluster) in match_scores_and_clusters[1:]:
                    if (cluster, secondary_match_cluster) in known_non_matches:
                        continue
                    comparison = cluster.compare(secondary_match_cluster)
                    if comparison.is_definitely_not_match():
                        known_non_matches.add((cluster, secondary_match_cluster))
                        known_non_matches.add((secondary_match_cluster, cluster))
                        unmerged_matches += 1
                    else:
                        cluster.grok(secondary_match_cluster)
                        del(clusters[clusters.index(secondary_match_cluster)])
                if unmerged_matches > 0:
                    # If we weren't sure what cluster to put this result in, but we weren't able to merge them, then
                    # we obviously can't be sure this is in the right cluster, so we penalize the shit out of it.
                    penalty = 0.25 * (unmerged_matches ** 0.5)  # As Geoff would put it: "Pulled out of an ass."
                    result.addDataQualityComponentDebugInfo("penalty for %d unmerged matches" % unmerged_matches, penalty)
                    result.dataQuality *= 1 - penalty
            for non_match_cluster in cluster_non_matches:
                known_non_matches.add((cluster, non_match_cluster))
                known_non_matches.add((non_match_cluster, cluster))


        return clusters

    def __dedupeMusicResults(self, resultLists):
        # First, split by type.
        artists, albums, songs = [], [], []
        for resultList in resultLists:
            for result in resultList:
                if isinstance(result.resolverObject, ResolverPerson):
                    artists.append(result)
                elif isinstance(result.resolverObject, ResolverMediaCollection):
                    albums.append(result)
                elif isinstance(result.resolverObject, ResolverMediaItem):
                    songs.append(result)
                else:
                    raise Exception('Unknown result of type: ' + str(result.resolverObject))

        # The behavior of deduping can depend on ordering. In particular, if we have some signal that two entities that
        # look very similar are actually not the same thing, it can be very helpful to cluster those two first, so that
        # other entities that look like the two (but closer to one than the other) can
        artistClusters = self.__formClusters(artists, ArtistSearchResultCluster)
        albumClusters = self.__formClusters(albums, AlbumSearchResultCluster)
        songClusters = self.__formClusters(songs, TrackSearchResultCluster)
        return interleaveResultsByRelevance([artistClusters, albumClusters, songClusters])

    def __dedupeVideoResults(self, resultLists):
        # First, split by type.
        tv, movies = [], []
        for resultList in resultLists:
            for result in resultList:
                if result.resolverObject.types == ['tv']:
                    tv.append(result)
                elif result.resolverObject.types == ['movie']:
                    movies.append(result)
                else:
                    print 'ERROR: Unrecognized result type %s for result:\n\n%s\n\n' % (result.resolverObject.types, str(result))

        tvClusters = self.__formClusters(tv, TvSearchResultCluster)
        movieClusters = self.__formClusters(movies, MovieSearchResultCluster)
        return interleaveResultsByRelevance([tvClusters, movieClusters])

    def __dedupePlaceResults(self, resultLists):
        places = []
        for resultList in resultLists:
            places.extend(resultList)

        placeClusters = self.__formClusters(places, PlaceSearchResultCluster)
        # TODO: I need a pruning phase here. Where I have a good cluster in a city that has street-specific data, and
        # another cluster in the same city that doesn't, just get rid of the second one.
        sortByRelevance(placeClusters)
        return placeClusters

    def __dedupeAppResults(self, resultLists):
        apps = []
        for resultList in resultLists:
            apps.extend(resultList)
        clusters = self.__formClusters(apps, AppSearchResultCluster)
        sortByRelevance(clusters)
        return clusters

    def __dedupeBookResults(self, resultLists):
        books = []
        for resultList in resultLists:
            books.extend(resultList)
        clusters = self.__formClusters(books, BookSearchResultCluster)
        sortByRelevance(clusters)
        return clusters
