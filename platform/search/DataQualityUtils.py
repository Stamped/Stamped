#!/usr/bin/env python

from __future__ import division

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import math
import re

# Results with lower data quality than this are summarily dropped pre-clustering.
MIN_RESULT_DATA_QUALITY_TO_CLUSTER = 0.1  # TODO PRELAUNCH IMMEDIATELY FUCK FUCK FUCK UP THIS
# Results with lower data quality than this are allowed to cluster for the purposes of boosting the cluster's final
# score, but are never included in the final result.
MIN_RESULT_DATA_QUALITY_TO_INCLUDE = 0.3  # TODO PRELAUNCH IMMEDIATELY FUCK FUCK FUCK UP THIS
# Clusters with data quality lower than this are not returned to the user.
MIN_CLUSTER_DATA_QUALITY = 0.7

############################################################################################################
################################################    FILM    ################################################
############################################################################################################

def augmentMovieDataQualityOnBasicAttributePresence(movieSearchResult):
    if movieSearchResult.release_date is None:
        # This is a non-trivial penalty because this is a key differentiator of movies with the same title. Case
        # would work, but it's very rarely present on both parties of a comparison. Having a good release date is
        # key.
        penalty = 0.25
        movieSearchResult.dataQuality *= 1 - penalty
        movieSearchResult.addDataQualityComponentDebugInfo("penalty for missing release date", penalty)

    if movieSearchResult.director:
        boost = 0.1
        movieSearchResult.dataQuality *= 1 + boost
        movieSearchResult.addDataQualityComponentDebugInfo("boost for director", boost)

    if movieSearchResult.cast:
        boost = 0.05 * math.log(1 + len(movieSearchResult.cast))
        movieSearchResult.dataQuality *= 1 + boost
        movieSearchResult.addDataQualityComponentDebugInfo("boost for cast of size %d" % len(movieSearchResult.cast), boost)


def augmentTvDataQualityOnBasicAttributePresence(tvSearchResult):
    pass

############################################################################################################
################################################   MUSIC    ################################################
############################################################################################################

def augmentMusicDataQualityOnBasicAttributePresence(musicSearchResult):
    pass


############################################################################################################
################################################   BOOKS    ################################################
############################################################################################################

def augmentBookDataQualityOnBasicAttributePresence(bookSearchResult):
    pass


############################################################################################################
################################################    APPS    ################################################
############################################################################################################

def augmentAppDataQualityOnBasicAttributePresence(appSearchResult):
    pass



############################################################################################################
################################################   PLACES   ################################################
############################################################################################################

STREET_NUMBER_RE = re.compile('(^|\s)\d+($|[\s.#,])')
NONCRITICAL_ADDRESS_CHARS = re.compile('[^a-zA-Z0-9 ]')

def tryToGetStreetAddressFromPlace(placeResolverObject):
    """
    Given a place, attempts to return the street address only (# and street name) as a string.
    """
    # First try to retrieve it from structured data.
    address = placeResolverObject.address
    # TODO: Is this the right name?
    if address and 'street' in address:
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