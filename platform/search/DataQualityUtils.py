#!/usr/bin/env python

from __future__ import division

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import math
import re

from resolve.StringComparator import *

# Results with lower data quality than this are summarily dropped pre-clustering.
MIN_RESULT_DATA_QUALITY_TO_CLUSTER = 0.3
# Results with lower data quality than this are allowed to cluster for the purposes of boosting the cluster's final
# score, but are never included in the final result.
MIN_RESULT_DATA_QUALITY_TO_INCLUDE = 0.6
# Clusters with data quality lower than this are not returned to the user.
MIN_CLUSTER_DATA_QUALITY = 0.7

############################################################################################################
################################################    FILM    ################################################
############################################################################################################

def augmentMovieDataQualityOnBasicAttributePresence(movieSearchResult):
    if movieSearchResult.resolverObject.release_date is None:
        # This is a non-trivial penalty because this is a key differentiator of movies with the same title. Case
        # would work, but it's very rarely present on both parties of a comparison. Having a good release date is
        # key.
        penalty = 0.25
        movieSearchResult.dataQuality *= 1 - penalty
        movieSearchResult.addDataQualityComponentDebugInfo("penalty for missing release date", penalty)

    if movieSearchResult.resolverObject.source == 'tmdb':
        boost = 0.1
        movieSearchResult.dataQuality *= 1 + boost
        movieSearchResult.addDataQualityComponentDebugInfo('boost for IMDB', boost)

    if movieSearchResult.resolverObject.directors:
        boost = 0.05
        movieSearchResult.dataQuality *= 1 + boost
        movieSearchResult.addDataQualityComponentDebugInfo("boost for director", boost)

    if movieSearchResult.resolverObject.cast:
        boost = 0.05 * math.log(1 + len(movieSearchResult.resolverObject.cast))
        movieSearchResult.dataQuality *= 1 + boost
        movieSearchResult.addDataQualityComponentDebugInfo(
                "boost for cast of size %d" % len(movieSearchResult.resolverObject.cast), boost)

    titleUncommonness = complexUncommonness(movieSearchResult.resolverObject.name)
    if titleUncommonness < 6:
        penalty = ((6 - titleUncommonness) / 6.0) ** 0.4
        movieSearchResult.dataQuality *= 1 - penalty
        movieSearchResult.addDataQualityComponentDebugInfo(
            'penalty for common shitty title of uncommonness %f' % titleUncommonness, penalty)


def augmentTvDataQualityOnBasicAttributePresence(tvSearchResult):
    if tvSearchResult.resolverObject.release_date is None:
        penalty = 0.15
        tvSearchResult.dataQuality *= 1 - penalty
        tvSearchResult.addDataQualityComponentDebugInfo("penalty for missing release date", penalty)

    if tvSearchResult.resolverObject.source == 'thetvdb':
        boost = 0.1
        tvSearchResult.dataQuality *= 1 + boost
        tvSearchResult.addDataQualityComponentDebugInfo('boost for thetvdb', boost)

    if not tvSearchResult.resolverObject.description:
        penalty = 0.1
        tvSearchResult.dataQuality *= 1 - penalty
        tvSearchResult.addDataQualityComponentDebugInfo("penalty for missing description", penalty)

    titleUncommonness = complexUncommonness(tvSearchResult.resolverObject.name)
    if titleUncommonness < 6:
        penalty = ((6 - titleUncommonness) / 6.0) ** 0.4
        tvSearchResult.dataQuality *= 1 - penalty
        tvSearchResult.addDataQualityComponentDebugInfo(
            'penalty for common shitty title of uncommonness %f' % titleUncommonness, penalty)


############################################################################################################
################################################   MUSIC    ################################################
############################################################################################################

def augmentTrackDataQualityOnBasicAttributePresence(trackSearchResult):
    if (not trackSearchResult.resolverObject.artists or
        'name' not in trackSearchResult.resolverObject.artists[0]):
        penalty = 0.3
        trackSearchResult.dataQuality *= 1 - penalty
        trackSearchResult.addDataQualityComponentDebugInfo('penalty for missing artist', penalty)

def augmentAlbumDataQualityOnBasicAttributePresence(albumSearchResult):
    if (not albumSearchResult.resolverObject.artists or
        'name' not in albumSearchResult.resolverObject.artists[0]):
        penalty = 0.3
        albumSearchResult.dataQuality *= 1 - penalty
        albumSearchResult.addDataQualityComponentDebugInfo('penalty for missing artist', penalty)

def augmentArtistDataQualityOnBasicAttributePresence(artistSearchResult):
    pass

############################################################################################################
################################################   BOOKS    ################################################
############################################################################################################

def augmentBookDataQualityOnBasicAttributePresence(bookSearchResult):
    if (not bookSearchResult.resolverObject.authors or
        'name' not in bookSearchResult.resolverObject.authors[0]):
        penalty = 0.3
        bookSearchResult.dataQuality *= 1 - penalty
        bookSearchResult.addDataQualityComponentDebugInfo('penalty for missing author', penalty)


############################################################################################################
################################################    APPS    ################################################
############################################################################################################

def augmentAppDataQualityOnBasicAttributePresence(appSearchResult):
    pass



############################################################################################################
################################################   PLACES   ################################################
############################################################################################################

US_POSTAL_CODE_RE = re.compile("(\d{5})(-\d{4})?$")
US_STATE_RE = re.compile('[A-Z]{2}')
# Group 1 is city, group 2 is state, group 3 is postal code.
US_ADDRESS_STRING_W_POSTAL_CODE_RE = re.compile("[^,]\s*([A-Za-z. -]+)[ ,]+([A-Z]{2})[ ,]+(\d{5})(-\d{4})?([ ,]+(US))?\s*$")
# Group 1 is city, group 2 is state.
US_ADDRESS_STRING_WO_POSTAL_CODE_RE = re.compile("[^,]\s*([A-Za-z. -]+)[ ,]+([A-Z]{2})([ ,]+(US))?\s*$")

def tryToGetPostalCodeFromPlace(placeResolverObject):
    if placeResolverObject.address and placeResolverObject.address.get('postcode', None):
        reMatch = US_POSTAL_CODE_RE.match(placeResolverObject.address['postcode'])
        if reMatch:
            return int(reMatch.group(1))
    if placeResolverObject.address_string:
        reMatch = US_ADDRESS_STRING_W_POSTAL_CODE_RE.search(placeResolverObject.address_string)
        if reMatch:
            return int(reMatch.group(3))

def tryToGetStateFromPlace(placeResolverObject):
    if placeResolverObject.address and placeResolverObject.address.get('region', None):
        reMatch = US_STATE_RE.match(placeResolverObject.address['region'])
        if reMatch:
            return placeResolverObject.address['region']
    if placeResolverObject.address_string:
        reMatch = US_ADDRESS_STRING_W_POSTAL_CODE_RE.search(placeResolverObject.address_string)
        if reMatch:
            return reMatch.group(2)
        reMatch = US_ADDRESS_STRING_WO_POSTAL_CODE_RE.search(placeResolverObject.address_string)
        if reMatch:
            return reMatch.group(2)

def tryToGetLocalityFromPlace(placeResolverObject):
    if placeResolverObject.address and placeResolverObject.address.get('locality', None):
        return placeResolverObject.address['locality']
    if placeResolverObject.address_string:
        reMatch = US_ADDRESS_STRING_W_POSTAL_CODE_RE.search(placeResolverObject.address_string)
        if reMatch:
            return reMatch.group(1)
        reMatch = US_ADDRESS_STRING_WO_POSTAL_CODE_RE.search(placeResolverObject.address_string)
        if reMatch:
            return reMatch.group(1)

STREET_NUMBER_RE = re.compile('(^|\s)\d+($|[\s.#,])')
NONCRITICAL_ADDRESS_CHARS = re.compile('[^a-zA-Z0-9 ]')

def tryToGetStreetAddressFromPlace(placeResolverObject):
    """
    Given a place, attempts to return the street address only (# and street name) as a string.
    """
    # First try to retrieve it from structured data.
    address = placeResolverObject.address
    # TODO: Is this the right name?
    if address and address.get('street', None):
        return address['street']

    # Next, look in the address string. Peel off the first segment of it and try to determine if it's a street
    # address. A little hacky.
    address_string = placeResolverObject.address_string
    if not address_string:
        return None

    first_term = address_string.split(',')[0]

    # If there's a number in it, it's not a city. It's likely a street address. In the off-chance it's something
    # like a P.O. box we're not really in trouble -- this is used for comparisons, and the real danger is returning
    # something that too many things will have in common, like a city name.
    if STREET_NUMBER_RE.search(first_term):
        return first_term
    first_term_simplified = first_term.lower().strip()
    first_term_simplified = NONCRITICAL_ADDRESS_CHARS.sub(' ', first_term_simplified)
    first_term_words = first_term_simplified.split()
    street_address_terms = ('street', 'st', 'road', 'rd', 'avenue', 'ave', 'highway', 'hwy', 'apt', 'suite', 'ste')
    if any(term in first_term_words for term in street_address_terms):
        return first_term
    return None


def tryToSplitStreetAddress(streetAddressString):
    words = streetAddressString.split()
    if len(words) <= 1 or not words[0].isdigit():
        return (None, streetAddressString)
    return (words[0], ' '.join(words[1:]))


def augmentPlaceDataQualityOnBasicAttributePresence(placeSearchResult):
    resolverObject = placeSearchResult.resolverObject
    if not resolverObject.coordinates:
        penalty = 0.3
        placeSearchResult.dataQuality *= 1 - penalty
        placeSearchResult.addDataQualityComponentDebugInfo("penalty for missing coordinates", penalty)
    streetAddress = tryToGetStreetAddressFromPlace(resolverObject)
    if not streetAddress and not resolverObject.address and not resolverObject.address_string:
        penalty = 0.4
        placeSearchResult.dataQuality *= 1 - penalty
        placeSearchResult.addDataQualityComponentDebugInfo("penalty for missing any address info", penalty)
    elif not streetAddress:
        penalty = 0.15
        placeSearchResult.dataQuality *= 1 - penalty
        placeSearchResult.addDataQualityComponentDebugInfo("penalty for missing street address", penalty)
    else:
        (number, street) = tryToSplitStreetAddress(streetAddress)
        if number:
            boost = 0.2
            placeSearchResult.dataQuality *= 1 + boost
            placeSearchResult.addDataQualityComponentDebugInfo("boost for having street #", boost)
