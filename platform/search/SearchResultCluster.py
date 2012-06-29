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
from libs.LRUCache import lru_cache
from resolve.Resolver import *
from resolve.TitleUtils import cleanBookTitle
from search.SearchResult import SearchResult
from search import ScoringUtils

@lru_cache()
def cached_simplify(string):
    return simplify(string)

@lru_cache()
def cached_string_comparison(s1, s2):
    return stringComparison(s1, s2, strict=True)

@lru_cache()
def cached_artist_simplify(artist_name):
    return artistSimplify(artist_name)

@lru_cache()
def cached_album_simplify(album_name):
    return albumSimplify(album_name)

@lru_cache()
def cached_track_simplify(track_name):
    return trackSimplify(track_name)

@lru_cache()
def cached_movie_simplify(movie_name):
    movie_name = re.compile('(^|\s)the(\s|$)', re.IGNORECASE).sub(' ', movie_name)
    movie_name = re.compile('(-\s|\s-)').sub(' ', movie_name)
    movie_name = re.compile('\s+').sub(' ', movie_name)
    movie_name = movie_name.strip()
    # TODO: Roman numerals -> Arabic?
    return movieSimplify(movie_name)

class CompareResult(object):
    """
    Used to describe the result of a comparison between two search results or clusters of search results.

    Originally it was binary -- this is a match, or it isn't -- and we made matching transitive, so if A matched B and
    B matched C we'd make all three a cluster. That caused some problems, so now it's ternary. If A matches B and B
    matches C, we'll join the three unless B and C fall into our third category, "definitely not matching." In that
    case we will not join B and C. We also added a score to the "matching" category so that, in this case, we can
    determine which of B or C result A should join with.
    """
    MATCH = 1
    UNKNOWN = 2
    DEFINITELY_NOT_MATCH = 3

    def __init__(self, result_enum, score=None):
        self.__result_enum = result_enum
        self.score = score

    def is_match(self):
        return self.__result_enum == self.MATCH

    def is_definitely_not_match(self):
        return self.__result_enum == self.DEFINITELY_NOT_MATCH

    @classmethod
    def match(cls, score):
        return cls(cls.MATCH, score)

    @classmethod
    def unknown(cls):
        return cls(cls.UNKNOWN)

    @classmethod
    def definitely_not_match(cls):
        return cls(cls.DEFINITELY_NOT_MATCH)


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

    @classmethod
    def _compare_proxies(cls, proxy1, proxy2):
        raise NotImplementedError()

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
                comparison = self._compare_proxies(result.resolverObject, other_result.resolverObject)
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
    @classmethod
    def _compare_proxies(cls, artist1, artist2):
        # TODO: It might be worth it here to get the songs that have been linked to these sources at the
        # ____Source.searchLite() level and compare names.
        if (hasattr(artist1, 'amgId') and
            hasattr(artist2, 'amgId') and
            artist1.amgId != artist2.amgId):
            return CompareResult.definitely_not_match()
        if type(artist1) == type(artist2) and artist1.source != 'stamped':
            # If they're from the same source, we are extremely conservative about assuming that they might be the
            # same artist. If iTunes tells us that Foxes is not the same band as Foxes!, we believe them. On the other
            # hand, dupes in our database can definitely happen.
            # TODO: This all-or-nothing logic is probably not the way to go in the long run. We'd like to have a
            # weight-of-the-evidence approach, but that takes a lot of tweaking. For instance, in this case, if we
            # happened to see that artists with both of these names are cited on other sources as having albums with
            # the same names, we would want to override this and merge.
            if artist1.name != artist2.name:
                return CompareResult.definitely_not_match()
            else:
                return CompareResult.unknown()
        else:
            name1 = artist1.name
            name2 = artist2.name
            if name1 == name2:
                return CompareResult.match(1.0)
            if cached_string_comparison(name1, name2) > 0.9:
                return CompareResult.match(cached_string_comparison(name1, name2))

            name1_simple = cached_artist_simplify(name1)
            name2_simple = cached_artist_simplify(name2)

            if name1_simple == name2_simple:
                return CompareResult.match(0.9)
            if cached_string_comparison(name1_simple, name2_simple) > 0.9:
                return CompareResult(cached_string_comparison(name1_simple, name2_simple) - 0.1)
            return CompareResult.unknown()


class AlbumSearchResultCluster(SearchResultCluster):
    @classmethod
    def _compare_proxies(cls, album1, album2):
        """
        Album comparison is easy -- just album name and artist name.
        """
        album1_name_simple = cached_album_simplify(album1.name)
        album2_name_simple = cached_album_simplify(album2.name)
        album_name_sim = cached_string_comparison(album1_name_simple, album2_name_simple)
        if album_name_sim <= 0.9:
            return CompareResult.unknown()
        # TODO: Handle case with multiple artists? Does this come up?

        try:
            artist1_name_simple = cached_artist_simplify(album1.artists[0]['name'])
            artist2_name_simple = cached_artist_simplify(album2.artists[0]['name'])
        except IndexError:
            # TODO: Better handling here. Maybe pare out the artist-less album. Maybe check to see if both are by
            # 'Various Artists' or whatever.
            return CompareResult.unknown()

        artist_name_sim = cached_string_comparison(artist1_name_simple, artist2_name_simple)
        if artist_name_sim <= 0.9:
            return CompareResult.unknown()
        score = album_name_sim * album_name_sim * artist_name_sim
        return CompareResult.match(score)


class TrackSearchResultCluster(SearchResultCluster):
    @classmethod
    def _compare_proxies(cls, track1, track2):
        """
        Track comparison is easy -- just track name and artist name.
        """
        track1_name_simple = cached_track_simplify(track1.name)
        track2_name_simple = cached_track_simplify(track2.name)
        track_name_sim = cached_string_comparison(track1_name_simple, track2_name_simple)
        if track_name_sim <= 0.9:
            return CompareResult.unknown()
        # TODO: Handle case with multiple artists? Does this come up?

        try:
            artist1_name_simple = cached_artist_simplify(track1.artists[0]['name'])
            artist2_name_simple = cached_artist_simplify(track2.artists[0]['name'])
        except IndexError:
            # TODO: Better handling here. Maybe pare out the artist-less album. Maybe check to see if both are by
            # 'Various Artists' or whatever.
            return CompareResult.unknown()

        artist_name_sim = cached_string_comparison(artist1_name_simple, artist2_name_simple)
        if artist_name_sim <= 0.9:
            return CompareResult.unknown()
        score = track_name_sim * artist_name_sim
        return CompareResult.match(score)


class PlaceSearchResultCluster(SearchResultCluster):
    @classmethod
    def get_data_richness_score(cls, place):
        """
        Returns a score indicating how much information the ResolverPlace argument place contains that we can use for
        clustering purposes.
        """
        score = 0
        if place.coordinates:
            # 5 points for lat/lng
            score += 5
        if place.address or place.address_string:
            # 5 points for presence of any address info at all.
            score += 2
        if cls._try_to_get_street_address(place):
            # 2 points if we have a street name.
            score += 2
            (number, name) = cls._split_street_address(cls._try_to_get_street_address(place))
            if number:
                # 2 points if we have a street number.
                score += 2
        return score

    STREET_NUMBER_RE = re.compile('(^|\s)\d+($|[\s.,])')
    NONCRITICAL_CHARS = re.compile('[^a-zA-Z0-9 ]')
    @classmethod
    def _try_to_get_street_address(cls, place):
        """
        Given a place, attempts to return the street address only (# and street name) as a string.
        """
        # First try to retrieve it from structured data.
        address = place.address
        # TODO: Is this the right name?
        if address and 'street' in address:
            return address['street']

        # Next, look in the address string. Peel off the first segment of it and try to determine if it's a street
        # address. A little hacky.
        address_string = place.address_string
        if not address_string:
            return None

        first_term = address_string.split(',')[0]

        # If there's a number in it, it's not a city. It's likely a street address. In the off-chance it's something
        # like a P.O. box we're not really in trouble -- this is used for comparisons, and the real danger is returning
        # something that too many things will have in common, like a city name.
        if cls.STREET_NUMBER_RE.search(first_term):
            return first_term
        first_term_simplified = first_term.lower().strip()
        first_term_simplified = cls.NONCRITICAL_CHARS.sub(' ', first_term_simplified)
        first_term_words = first_term_simplified.split()
        street_address_terms = ('street', 'st', 'road', 'rd', 'avenue', 'ave', 'highway', 'hwy', 'apt', 'suite', 'ste')
        if any(term in first_term_words for term in street_address_terms):
            return first_term
        return None

    @classmethod
    def _simplify_address(cls, address_string):
        # TODO: Share somewhere common with resolve/etc.!
        address_string = cached_simplify(address_string)
        mappings = { 'rd': 'road',
                     'st': 'street',
                     'ste': 'suite',
                     'apt': 'apartment',
                     'hwy': 'highway',
                     'rte': 'route',
                     'dr': 'drive',
                     'w': 'west',
                     'e': 'east',
                     'n': 'north',
                     's': 'south'}
        # TODO: Should possibly also normalize 1/1st/first, 50th/50, etc.
        address_words = address_string.split()
        for (idx, word) in enumerate(address_words):
            if word[-1] == '.':
                word = word[:-1]
            if word in mappings:
                address_words[idx] = mappings[word]
        return ' '.join(address_words)

    @classmethod
    def _split_street_address(cls, street_address):
        """
        Splits a street address into number/name components and returns them in a tuple.
        """
        words = street_address.split()
        if len(words) <= 1 or not words[0].isdigit():
            return (None, street_address)
        return (words[0], ' '.join(words[1:]))

    @classmethod
    def _compare_proxies(cls, place1, place2):
        place1_name = cached_simplify(place1.name)
        place2_name = cached_simplify(place2.name)
        name_similarity = cached_string_comparison(place1_name, place2_name)

        #print 'COMPARING', place1.name, cls._try_to_get_street_address(place1), "    TO   ", place2.name, cls._try_to_get_street_address(place2)

        if name_similarity < 0.5:
            return CompareResult.unknown()
        similarity_score = name_similarity - 0.5
        if place1.name == place2.name:
            # Boost for being identical pre-simplification.
            similarity_score += 0.1

        compared_locations = False

        if place1.coordinates and place2.coordinates:
            distance_in_km = ScoringUtils.geoDistance(place1.coordinates, place2.coordinates)
            if distance_in_km > 10:
                # print "CRAPPING OUT"
                return CompareResult.unknown()

            # Min of 0.01m away.
            distance_in_km = max(distance_in_km, 0.01)

            # .08 if 1km apart, .35 if 0.1km, 0.622 if 0.01km.
            similarity_score += math.log(1.0 / distance_in_km, 5000)
            compared_locations = True

        if similarity_score > 0.9:
            # If we think these two businesses are extremely likely to be the same based on name and latlng, exit early.
            # The reason for this is that sometimes a business will have two addresses if it's on a corner or has two
            # entrances. We'll tank it in the address comparison. Exiting early makes sure that, when the latlngs and
            # names are close enough, we don't second-guess it because of an address issue.
            # print "Matching after lat-lng with sim score", similarity_score
            return CompareResult.match(similarity_score)

        # This would probably be good enough, except that Google Places national/autocomplete results don't have
        # latitude and longitude; they only have address strings. And other things don't have full address string; they
        # just have addresses. Ugh.

        street_address1 = cls._try_to_get_street_address(place1)
        street_address2 = cls._try_to_get_street_address(place2)
        if street_address1 and street_address2:
            # TODO: Is cached_simplify really what we want here for the street addresses?
            street_address1 = cls._simplify_address(street_address1)
            street_address2 = cls._simplify_address(street_address2)

            (street_number1, street_name1) = cls._split_street_address(street_address1)
            (street_number2, street_name2) = cls._split_street_address(street_address2)
            if street_number2 and not street_number1:
                street_address2 = street_name2
            elif street_number1 and not street_number2:
                street_address1 = street_name1
            elif street_number1 and street_number2:
                # Street # differences up until 5 are actually positive signals. But street # differences past that
                # point are strongly negative; a difference of 100 is a penalty of 0.65.
                if int(street_number1) == int(street_number2):
                    similarity_score += 0.5
                else:
                    # print "Deducting for street #s:", math.log(abs(int(street_number1) - int(street_number2)) / 5.0, 100)
                    similarity_score -= math.log(abs(int(street_number1) - int(street_number2)) / 5.0, 100)
                    # print "Score is now", similarity_score
                # We then go on to do the full address string similarity, which is a bit duplicative. TODO: There might
                # be an issue here, because we're double-counting street # similarities, where things on two different
                # streets with the same street # and short string names get counted as the same. It seems like a rare
                # case, though.

            # print "COMPARING", street_address1, "TO", street_address2
            street_address_similarity = cached_string_comparison(street_address1, street_address2)
            # If street addresses are significantly different, we totally tank the comparison. If they're identical,
            # it's a boost of 0.6.
            #print "BOOSTING BY ", ((street_address_similarity - 0.7) * 2), "FOR STREET ADDRESS"
            similarity_score += (street_address_similarity - 0.7) * 2
            #print "SCORE IS NOW", similarity_score
            compared_locations = True

        if not compared_locations and place1.address_string and place2.address_string:
            # Default to raw address string comparison. Maybe they're both in the same city, and that's all we know
            # about either of them. In that case, it's fine to de-dupe them.
            address_string1 = cls._simplify_address(place1.address_string)
            address_string2 = cls._simplify_address(place2.address_string)

            address_string_similarity = cached_string_comparison(address_string1, address_string2)

            # Completely tanks similarity for different address strings, max boost of 0.6 for identical. TODO: I might
            # want to be even stricter here.
            similarity_score += (address_string_similarity - 0.7) * 2

        # TODO: The big case we're not catching yet is duplicates where one source knows the city and street and the
        # other just knows the city. This isn't always feasible because half of Google results lack structured address
        # data but might be worth doing for the other half.

        if similarity_score > 0.75:
            #print "MATCHED MATCHED MATCHED MATCHED MATCHED MATCHED MATCHED MATCHED MATCHED WITH SCORE", similarity_score
            return CompareResult.match(similarity_score)
        elif similarity_score < 0.25:
            return CompareResult.definitely_not_match()
        else:
            return CompareResult.unknown()


class BookSearchResultCluster(SearchResultCluster):
    SUBTITLE_RE = re.compile('(\w)\s*[:|-]+\s\w+.*$')
    @classmethod
    def _strip_subtitle(cls, title):
        without_subtitle = cls.SUBTITLE_RE.sub('\\1', title)
        if len(without_subtitle) > 5:
            return without_subtitle
        return title

    @classmethod
    def _compare_titles(cls, title1, title2):
        title1 = cleanBookTitle(title1)
        title2 = cleanBookTitle(title2)
        book1_name_simple = cached_simplify(title1)
        book2_name_simple = cached_simplify(title2)
        if book1_name_simple == book2_name_simple:
            return 1

        similarity = cached_string_comparison(book1_name_simple, book2_name_simple)
        title1_without_subtitle = cls._strip_subtitle(book1_name_simple)
        title2_without_subtitle = cls._strip_subtitle(book2_name_simple)
        if book1_name_simple == title2_without_subtitle or book2_name_simple == title1_without_subtitle:
            similarity = max(similarity, 0.95)
        elif title1_without_subtitle == title2_without_subtitle:
            similarity = max(similarity, 0.9)
        else:
            subtitle_similarity = cached_string_comparison(title1_without_subtitle, title2_without_subtitle)
            similarity = max(similarity, subtitle_similarity - 0.1)
        return similarity

    @classmethod
    def _compare_proxies(cls, book1, book2):
        """
        """
        title_similarity = cls._compare_titles(book1.name, book2.name)
        if title_similarity < 0.75:
            return CompareResult.unknown()

        try:
            author1_name_simple = cached_simplify(book1.authors[0]['name'])
            author2_name_simple = cached_simplify(book2.authors[0]['name'])
            # TODO: Look for multiple authors, try to match intelligently.
            author_similarity = cached_string_comparison(author1_name_simple, author2_name_simple)
            if title_similarity + author_similarity > 1.7:
                return CompareResult.match(title_similarity + author_similarity)
        except Exception:
            pass

        return CompareResult.unknown()


class AppSearchResultCluster(SearchResultCluster):
    @classmethod
    def _compare_proxies(cls, app1, app2):
        """
        """
        return CompareResult.unknown()


class TvSearchResultCluster(SearchResultCluster):
    @classmethod
    def _compare_proxies(cls, tv_show1, tv_show2):
        """
        The tricky thing about comparing TV shows is that they're often elements for different seasons of the show,
        and we want to cluster those together, so things like runtime and release date don't work. Title is really
        the meat of the comparison, and if title isn't decisive we hope for some clue like publisher, etc.
        """
        # TODO: THIS NEEDS WORK. Related to the ongoing AmazonSource work.
        show1_name_simple = cached_movie_simplify(tv_show1.name)
        show2_name_simple = cached_movie_simplify(tv_show2.name)
        if cached_string_comparison(show1_name_simple, show2_name_simple) > 0.95:
            return CompareResult.match(1)
        return CompareResult.unknown()


class MovieSearchResultCluster(SearchResultCluster):
    @classmethod
    def _compare_proxies(cls, movie1, movie2):
        # Our task here is a bit harder than normal. There are often remakes, so name is not decisive. There are often
        # digital re-masterings and re-releases, so dates are not decisive. Cast data is spotty.
        #
        # TODO: Try to use MPAA rating, especially if we can get it from TMDB.

        movie1_name_simple = cached_movie_simplify(movie1.name)
        movie2_name_simple = cached_movie_simplify(movie2.name)
        name_similarity = cached_string_comparison(movie1_name_simple, movie2_name_simple)

        # TODO: We almost certainly want to weaken this once we have batch processes to really see the effects of
        # changes in the other pieces of the comparison.
        if movie1_name_simple != movie2_name_simple:
            return CompareResult.unknown()

        score = name_similarity - 0.9

        movie1_length, movie2_length = None, None
        if movie1.length and movie2.length:
            if movie1.length == movie2.length:
                score += 0.3
            elif abs(movie1.length - movie2.length) <= 60:
                # Here, it might be really nice to actually check if one of them has been rounded to minutes and
                # then converted back.
                score += 0.1

        if movie1.release_date and movie2.release_date:
            time_difference = abs(movie1.release_date - movie2.release_date)
            if time_difference < datetime.timedelta(7):
                score += 0.4
            elif time_difference < datetime.timedelta(30):
                score += 0.3
            elif time_difference < datetime.timedelta(365):
                # Within 1 year + exact title match = cluster.
                score += 0.2

        cast1_names = set([cached_simplify(actor['name']) for actor in movie1.cast])
        cast2_names = set([cached_simplify(actor['name']) for actor in movie2.cast])
        if cast1_names and cast2_names:
            overlap_fraction = float(len(cast1_names.intersection(cast2_names))) / min(len(cast1_names), len(cast2_names))
            # So the midpoint here is at 20% matching. If less than that matches, it's a bad sign. If more than that
            # matches, it's a good sign.
            # TODO: This is totally not the best way to do this.
            score += (overlap_fraction / 2) - 0.1

        try:
            movie1_director = cached_simplify(movie1.directors[0]['name'])
            movie2_director = cached_simplify(movie2.directors[0]['name'])
            if movie1_director == movie2_director:
                score += 0.2
            else:
                score -= 0.2
        except IndexError:
            pass

        # TODO: Pull out helper function here!
        # TODO: Publisher?
        # TODO: Genre, only as a potential gain?
        try:
            movie1_studio = cached_simplify(movie1.studios[0]['name'])
            movie2_studio = cached_simplify(movie2.studios[0]['name'])
            if movie1_studio == movie2_studio:
                score += 0.2
            # Don't subtract otherwise because sometimes it gets billed differently.
        except IndexError:
            pass

        # TODO: MPAA rating (can we get this from TMDB?)
        # TODO: Genres
        if score >= 0.3:
            return CompareResult.match(score)
        else:
            return CompareResult.unknown()
