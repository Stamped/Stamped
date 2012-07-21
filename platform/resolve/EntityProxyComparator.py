#!/usr/bin/env python

from __future__ import division

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import report

try:
    import utils, re, string, sys, traceback
    import logs
    from pprint                     import pprint, pformat
    from libs.LibUtils              import parseDateString
    from datetime                   import datetime, timedelta
    from resolve.TitleUtils import *
    from search.DataQualityUtils import *
    from resolve.StringNormalizationUtils import *
    from search import ScoringUtils
    from resolve.StringComparator   import *
except:
    report()
    raise

logComparisonLogic = False

class CompareResult(object):
    """
    Used to describe the result of a comparison between two entity proxies.

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

    def __repr__(self):
        if self.is_match():
            return 'CompareResult.match(%f)' % self.score
        elif self.is_definitely_not_match():
            return 'CompareResult.not_a_fucking_match()'
        else:
            return 'CompareResult.unknown()'


class AEntityProxyComparator(object):
    @classmethod
    def compare_proxies(cls, proxy1, proxy2):
        raise NotImplementedError()


class ArtistEntityProxyComparator(AEntityProxyComparator):
    @classmethod
    def compare_proxies(cls, artist1, artist2):
        sim_score = titleComparison(artist1.name, artist2.name, artistSimplify)
        if logComparisonLogic:
            print '\n\nCOMPARING %s (%s:%s) WITH %s (%s:%s)\n' % (
                repr(artist1.raw_name), artist1.source, artist1.key,
                repr(artist2.raw_name), artist2.source, artist2.key,
                )
            print 'sim score after title', sim_score

        # TODO: It might be worth it here to get the songs that have been linked to these sources at the
        # ____Source.searchLite() level and compare names.
        if (hasattr(artist1, 'amgId') and
            hasattr(artist2, 'amgId') and
            artist1.amgId != artist2.amgId):
            sim_score *= 0.3
            if logComparisonLogic:
                print 'sim score after penalty for different AMG IDs', sim_score

        if type(artist1) == type(artist2) and artist1.source != 'stamped':
            sim_score *= 0.85
            if logComparisonLogic:
                print 'sim score after penalty for being from same source', sim_score


        if sim_score > 0.95:
            return CompareResult.match(sim_score)
        if sim_score < 0.5:
            return CompareResult.definitely_not_match()
        return CompareResult.unknown()



class AlbumEntityProxyComparator(AEntityProxyComparator):
    @classmethod
    def compare_proxies(cls, album1, album2):
        """
        Album comparison is easy -- just album name and artist name.
        """
        raw_name_similarity = StringComparator.get_ratio(album1.name, album2.name)
        simple_name_similarity = StringComparator.get_ratio(albumSimplify(album1.name),
            albumSimplify(album2.name))
        album_name_sim = max(raw_name_similarity, simple_name_similarity - 0.1)
        if album_name_sim <= 0.8:
            return CompareResult.unknown()
            # TODO: Handle case with multiple artists? Does this come up?

        try:
            artist1_name = album1.artists[0]['name']
            artist2_name = album2.artists[0]['name']
            raw_artist_similarity = StringComparator.get_ratio(artist1_name, artist2_name)
            simple_artist_similarity = StringComparator.get_ratio(artistSimplify(artist1_name),
                artistSimplify(artist2_name))
            artist_name_sim = max(raw_artist_similarity, simple_artist_similarity - 0.1)
            if artist1_name.startswith(artist2_name) or artist2_name.startswith(artist1_name):
                artist_name_sim = max(artist_name_sim, 0.9)
        except IndexError:
            # TODO: Better handling here. Maybe pare out the artist-less album. Maybe check to see if both are by
            # 'Various Artists' or whatever.
            return CompareResult.unknown()

        if artist_name_sim <= 0.8:
            return CompareResult.unknown()
        score = album_name_sim * album_name_sim * artist_name_sim
        return CompareResult.match(score)


class TrackEntityProxyComparator(AEntityProxyComparator):
    @classmethod
    def compare_proxies(cls, track1, track2):
        """
        Track comparison is easy -- just track name and artist name.
        """
        raw_name_similarity = StringComparator.get_ratio(track1.name, track2.name)
        simple_name_similarity = StringComparator.get_ratio(trackSimplify(track1.name),
            trackSimplify(track2.name))
        track_name_sim = max(raw_name_similarity, simple_name_similarity - 0.1)
        if track_name_sim <= 0.8:
            return CompareResult.unknown()
            # TODO: Handle case with multiple artists? Does this come up?

        try:
            artist1_name = track1.artists[0]['name']
            artist2_name = track2.artists[0]['name']
            raw_artist_similarity = StringComparator.get_ratio(artist1_name, artist2_name)
            simple_artist_similarity = StringComparator.get_ratio(artistSimplify(artist1_name),
                artistSimplify(artist2_name))
            artist_name_sim = max(raw_artist_similarity, simple_artist_similarity - 0.1)
            if artist1_name.startswith(artist2_name) or artist2_name.startswith(artist1_name):
                artist_name_sim = max(artist_name_sim, 0.9)
        except IndexError:
            # TODO: Better handling here. Maybe pare out the artist-less album. Maybe check to see if both are by
            # 'Various Artists' or whatever.
            return CompareResult.unknown()

        if artist_name_sim <= 0.8:
            return CompareResult.unknown()
        score = track_name_sim * artist_name_sim
        return CompareResult.match(score)


class MovieEntityProxyComparator(AEntityProxyComparator):
    ENDING_NUMBER_RE = re.compile(r'(\d+)\s*(:|$)')
    @classmethod
    def _endsInDifferentNumbers(cls, title1, title2):
        title1 = convertRomanNumerals(title1)
        title2 = convertRomanNumerals(title2)
        match1 = cls.ENDING_NUMBER_RE.search(title1)
        match2 = cls.ENDING_NUMBER_RE.search(title2)
        if match1 and match2 and match1.group(1) != match2.group(1):
            return True
        if match1 and not match2 and int(match1.group(1)) != 1:
            return True
        if match2 and not match1 and int(match2.group(1)) != 1:
            return True
        return False

    @classmethod
    def compare_proxies(self, movie1, movie2):
        sim_score = titleComparison(movie1.name, movie2.name, movieSimplify)        
        if logComparisonLogic:
            print '\n\nCOMPARING %s (%s:%s) WITH %s (%s:%s)\n' % (
                repr(movie1.raw_name), movie1.source, movie1.key,
                repr(movie2.raw_name), movie2.source, movie2.key,
            )
            print 'sim score after title', sim_score

        if movie1.source == 'tmdb' and movie2.source == 'tmdb' and movie1.key != movie2.key:
            sim_score *= 0.7
            if logComparisonLogic:
                print 'demoting to', sim_score, 'for double tmdb IDs'

        if self._endsInDifferentNumbers(movie1.name, movie2.name):
            sim_score *= 0.4
            if logComparisonLogic:
                print 'demoting to', sim_score, 'for ending numbers'

        if movie1.release_date and movie2.release_date:
            time_difference = abs(movie1.release_date - movie2.release_date)
            # TODO: Smooth this.
            if time_difference < timedelta(30):
                release_date_odds = 2.5
            elif time_difference < timedelta(365):
                release_date_odds = 1.8
            elif time_difference < timedelta(750):
                release_date_odds = 1.4
            elif movie1.source != 'stamped' and movie2.source != 'stamped' and time_difference > timedelta(365*5):
                release_date_odds = 0.3
            else:
                release_date_odds = 0.7

            sim_score *= release_date_odds
            if logComparisonLogic:
                print 'changing to', sim_score, 'for release dates'


        if movie1.length and movie2.length:
            movie_length_odds = None
            if movie1.length == movie2.length and movie1.length % 60 != 0:
                movie_length_odds = 2.0
            elif movie1.length == movie2.length:
                movie_length_odds = 1.5
            elif abs(movie1.length - movie2.length) <= 120:
                movie_length_odds = 1.25
            else:
                movie_length_odds = 0.9
            sim_score *= movie_length_odds
            if logComparisonLogic:
                print 'changing to', sim_score, 'for movie lengths'

        if logComparisonLogic:
            print 'final score:', sim_score, '\n'
        if sim_score > 0.99:
            return CompareResult.match(sim_score)
        elif sim_score < 0.5:
            return CompareResult.definitely_not_match()
        else:
            return CompareResult.unknown()


class TvEntityProxyComparator(AEntityProxyComparator):
    @classmethod
    def compare_proxies(cls, tv_show1, tv_show2):
        """
        The tricky thing about comparing TV shows is that they're often elements for different seasons of the show,
        and we want to cluster those together, so things like runtime and release date don't work. Title is really
        the meat of the comparison.
        """
        sim_score = titleComparison(tv_show1.name, tv_show2.name, tvSimplify)
        if logComparisonLogic:
            print '\n\nCOMPARING %s (%s:%s) WITH %s (%s:%s)\n' % (
                repr(tv_show1.raw_name), tv_show1.source, tv_show1.key,
                repr(tv_show2.raw_name), tv_show2.source, tv_show2.key,
                )
            print 'sim score after title', sim_score

        if tv_show1.release_date and tv_show2.release_date:
            time_difference = abs(tv_show1.release_date - tv_show2.release_date)
            if time_difference > timedelta(365 * 5):
                sim_score *= 0.5
            elif time_difference < timedelta(365 * 2):
                sim_score *= 1.1
            elif time_difference < timedelta(365 * 1):
                sim_score *= 1.3
            if logComparisonLogic:
                print 'After release date, sim score is:', sim_score

        if tv_show1.source == 'thetvdb' and tv_show2.source == 'thetvdb' and tv_show1.key != tv_show2.key:
            sim_score *= 0.7
            if logComparisonLogic:
                print 'After penalty for different thetvdb IDs, sim score is:', sim_score

        if logComparisonLogic:
            print 'Final sim score is:', sim_score
        if sim_score > 1:
            return CompareResult.match(sim_score)
        elif sim_score < 0.5:
            return CompareResult.definitely_not_match()
        else:
            return CompareResult.unknown()


class AppEntityProxyComparator(AEntityProxyComparator):
    @classmethod
    def compare_proxies(cls, app1, app2):
        # TODO: Yeah this TOTALLY needs work.
        if app1.name == app2.name:
            return CompareResult.match(1.0)
        return CompareResult.unknown()


class BookEntityProxyComparator(AEntityProxyComparator):
    SUBTITLE_RE = re.compile('(\w)\s*[:|-]+\s\w+.*$')
    COMMA_SUBTITLE_RE = re.compile('(\w)\s*,\s*\w+.*$')
    @classmethod
    def _strip_subtitle(cls, title):
        without_subtitle = cls.SUBTITLE_RE.sub('\\1', title)
        if without_subtitle != title and len(without_subtitle) > 3:
            return without_subtitle

        # Sometimes a comma is used for subtitles, but we want to be a lot more conservative with
        # them. So we will only split it if there is only one comma.
        if title.count(',') == 1 and title.find(',') >= 3:
            return cls.COMMA_SUBTITLE_RE.sub('\\1', title)
        return title

    @classmethod
    def _compare_titles(cls, title1, title2):
        title1 = cleanBookTitle(title1)
        title2 = cleanBookTitle(title2)
        book1_name_simple = simplify(title1)
        book2_name_simple = simplify(title2)
        if book1_name_simple == book2_name_simple:
            return 1

        similarity = StringComparator.get_ratio(book1_name_simple, book2_name_simple)
        title1_without_subtitle = cls._strip_subtitle(book1_name_simple)
        title2_without_subtitle = cls._strip_subtitle(book2_name_simple)
        if book1_name_simple == title2_without_subtitle or book2_name_simple == title1_without_subtitle:
            similarity = max(similarity, 0.95)
        elif title1_without_subtitle == title2_without_subtitle:
            similarity = max(similarity, 0.9)
        elif isSuspiciousPrefixBookTitle(book1_name_simple, book2_name_simple):
            similarity = max(similarity, 0.9)
        else:
            subtitle_similarity = StringComparator.get_ratio(title1_without_subtitle, title2_without_subtitle)
            similarity = max(similarity, subtitle_similarity - 0.1)
        return similarity

    @classmethod
    def _compare_authors(cls, author1, author2):
        author1_name_simple = simplify(author1)
        author2_name_simple = simplify(author2)
        author1_tokens = set(tokenizeString(author1_name_simple))
        author2_tokens = set(tokenizeString(author2_name_simple))
        if author1_tokens == author2_tokens:
            return 1.0
            # This makes "Todd Gardner" and "Todd Manci Gardner" match.
        if author1_tokens > author2_tokens or author2_tokens > author1_tokens:
            return 0.9
        return StringComparator.get_ratio(author1_name_simple, author2_name_simple)

    @classmethod
    def compare_proxies(cls, book1, book2):
        """
        """
        title_similarity = cls._compare_titles(book1.name, book2.name)
        if book1.isbn and book1.isbn == book2.isbn and title_similarity > 0.5:
            return CompareResult.match(title_similarity + 1)
        if title_similarity < 0.75:
            return CompareResult.unknown()

        try:
            # TODO: Look for multiple authors, try to match intelligently.
            author_similarity = cls._compare_authors(book1.authors[0]['name'], book2.authors[0]['name'])
            if title_similarity + author_similarity > 1.7:
                return CompareResult.match(title_similarity + author_similarity)
        except KeyError:
            pass
        except IndexError:
            pass

        return CompareResult.unknown()


class PlaceEntityProxyComparator(AEntityProxyComparator):
    @classmethod
    def _simplify_address(cls, address_string):
        # TODO: Share somewhere common with resolve/etc.!
        address_string = simplify(address_string)
        mappings = { 'rd': 'road',
                     'st': 'street',
                     'ste': 'suite',
                     'ave': 'avenue',
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
    def compare_proxies(cls, place1, place2):
        #print "COMPARING PLACES:", place1.name, "--", tryToGetStreetAddressFromPlace(place1), "--", place1.key, \
        #      "       AND    ", place2.name, "--", tryToGetStreetAddressFromPlace(place2), "--", place2.key

        raw_name_similarity = StringComparator.get_ratio(place1.name, place2.name)
        simple_name_similarity = StringComparator.get_ratio(simplify(place1.name),
            simplify(place2.name))
        name_similarity = max(raw_name_similarity, simple_name_similarity - 0.15)
        if place1.name.startswith(place2.name) or place2.name.startswith(place1.name):
            name_similarity = max(name_similarity, 0.9)

        #print "NAME SIM IS", name_similarity

        if name_similarity < 0.5:
            return CompareResult.definitely_not_match()

        compared_locations = False
        location_similarity = 0.0

        if place1.coordinates and place2.coordinates:
            distance_in_km = ScoringUtils.geoDistance(place1.coordinates, place2.coordinates)
            if distance_in_km > 10:
                #print "CRAPPING OUT"
                return CompareResult.unknown()

            # Min of 0.01m away.
            distance_in_km = max(distance_in_km, 0.01)

            # 0 if 1km apart, .27 if 0.1km, 0.54 if 0.01km.
            location_similarity = math.log(1.0 / distance_in_km, 5000)
            #print "COORD-BASED LOCATION SIM IS", location_similarity
            compared_locations = True

        state1 = tryToGetStateFromPlace(place1)
        state2 = tryToGetStateFromPlace(place2)
        if state1 and state2 and state1 != state2:
            compared_locations = True
            #print "DROPPING 0.3 for STATE"
            location_similarity -= 0.4

        zip1 = tryToGetPostalCodeFromPlace(place1)
        zip2 = tryToGetPostalCodeFromPlace(place2)
        if zip1 and zip2:
            compared_locations = True
            if int(zip1 / 1000) != int(zip2 / 1000):
                location_similarity -= 0.4
                #print "DROPPING 0.4 for ZIP"
            elif zip1 == zip2:
                location_similarity += 0.1

        if compared_locations and name_similarity + location_similarity > 0.9:
            #print "HOT DAMN! QUITTIN EARLY."
            # If we think these two businesses are extremely likely to be the same based on name and latlng, exit early.
            # The reason for this is that sometimes a business will have two addresses if it's on a corner or has two
            # entrances. We'll tank it in the address comparison. Exiting early makes sure that, when the latlngs and
            # names are close enough, we don't second-guess it because of an address issue.
            # #print "Matching after lat-lng with sim score", similarity_score
            return CompareResult.match(name_similarity + location_similarity)

        # TODO: Should really just get parsed-out map in one call since it's repeating same regexp matches over and
        # over again.
        locality1 = tryToGetLocalityFromPlace(place1)
        locality2 = tryToGetLocalityFromPlace(place2)
        if locality1 and locality2:
            compared_locations = True
            if StringComparator.get_ratio(simplify(locality1), simplify(locality2)) != 1:
                #print "DROPPING 0.3 for LOCALITY"
                location_similarity -= 0.3

        # This would probably be good enough, except that Google Places national/autocomplete results don't have
        # latitude and longitude; they only have address strings. And other things don't have full address string; they
        # just have addresses. Ugh.

        street_address1 = tryToGetStreetAddressFromPlace(place1)
        street_address2 = tryToGetStreetAddressFromPlace(place2)
        if street_address1 and street_address2:
            # TODO: Is simplify really what we want here for the street addresses?
            street_address1 = cls._simplify_address(street_address1)
            street_address2 = cls._simplify_address(street_address2)

            (street_number1, street_name1) = tryToSplitStreetAddress(street_address1)
            (street_number2, street_name2) = tryToSplitStreetAddress(street_address2)
            if street_number2 and not street_number1:
                street_address2 = street_name2
            elif street_number1 and not street_number2:
                street_address1 = street_name1
            elif street_number1 and street_number2:
                # Street # differences up until 5 are actually positive signals. But street # differences past that
                # point are strongly negative; a difference of 100 is a penalty of 0.65.
                if int(street_number1) == int(street_number2):
                    location_similarity += 0.4
                else:
                    # #print "Deducting for street #s:", math.log(abs(int(street_number1) - int(street_number2)) / 5.0, 100)
                    location_similarity -= math.log(abs(int(street_number1) - int(street_number2)) / 5.0, 100)
                    # #print "Score is now", similarity_score
                    # We then go on to do the full address string similarity, which is a bit duplicative. TODO: There might
                    # be an issue here, because we're double-counting street # similarities, where things on two different
                    # streets with the same street # and short string names get counted as the same. It seems like a rare
                    # case, though.

            #print "COMPARING", street_address1, "TO", street_address2
            street_address_similarity = StringComparator.get_ratio(street_address1, street_address2)
            if ((street_address1 in street_address2 and set(street_address1.split()) < set(street_address2.split())) or
                (street_address2 in street_address1 and set(street_address2.split()) < set(street_address1.split()))):
                street_address_similarity = max(street_address_similarity, 0.9)
                # If street addresses are significantly different, we totally tank the comparison. If they're identical,
            # it's a boost of 0.4.
            #print "STREET ADDRESS SIM IS", street_address_similarity
            location_similarity += (street_address_similarity - 0.8) * 2
            #print "SCORE IS NOW", name_similarity + location_similarity
            compared_locations = True

        if not compared_locations and place1.address_string and place2.address_string:
            # Default to raw address string comparison. Maybe they're both in the same city, and that's all we know
            # about either of them. In that case, it's fine to de-dupe them.
            address_string1 = cls._simplify_address(place1.address_string)
            address_string2 = cls._simplify_address(place2.address_string)

            address_string_similarity = StringComparator.get_ratio(address_string1, address_string2)

            # Completely tanks similarity for different address strings, max boost of 0.6 for identical. TODO: I might
            # want to be even stricter here.
            location_similarity += (address_string_similarity - 0.7) * 2

        # TODO: The big case we're not catching yet is duplicates where one source knows the city and street and the
        # other just knows the city. This isn't always feasible because half of Google results lack structured address
        # data but might be worth doing for the other half.

        similarity_score = location_similarity + name_similarity
        #print "FINAL TOTAL SIM IS", similarity_score
        if similarity_score > 0.9:
            #print "MATCHED MATCHED MATCHED MATCHED MATCHED MATCHED MATCHED MATCHED MATCHED WITH SCORE", similarity_score
            return CompareResult.match(similarity_score)
        elif similarity_score < 0.3:
            return CompareResult.definitely_not_match()
        else:
            return CompareResult.unknown()
