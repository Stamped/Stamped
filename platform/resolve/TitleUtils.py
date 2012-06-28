#!/usr/bin/env python

from __future__ import division

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import re

# TODO: Merge with search/DataQualityUtils.py somewhere common (to avoid dependency loop)

############################################################################################################
################################################   UTILS    ################################################
############################################################################################################

def applyRemovalRegexps(regexps, title):
    modified = True
    while modified:
        modified = False
        for removalRegexp in regexps:
            if removalRegexp.find(text):
                text = removalRegexp.sub('', text)
                modified = True
    return text


class TitleDataQualityTest(object):
    """
    Encapsulates a test
    , in the form of a regular expression, for potential data quality issues in a search result
    based on its title. When the regular expression matches the result title, we apply the score penalty and attach
    the message to the data quality score debug information.

    If rawName==True, we apply the regular expression to the raw_name ResolverObject field instead of the processed
    name property.

    TODO: SKIP ALL
    """
    def __init__(self, penalizedTitleRegexp, message, penalty, exceptionQueryRegexp=None, rawName=False):
        self.titleRegexp = penalizedTitleRegexp
        if isinstance(self.titleRegexp, basestring):
            self.titleRegexp = re.compile(self.titleRegexp, re.IGNORECASE)
        self.exceptionQueryRegexp = exceptionQueryRegexp
        self.message = message
        self.penalty = penalty

    def applyTest(self, searchResult, searchQuery):
        title = searchResult.resolverObject.raw_name if rawName else searchResult.resolverObject.name
        if self.titleRegexp.find(title) and not self.exceptionQueryRegexp.find(searchQuery):
            searchResult.dataQuality *= 1 - self.penalty
            searchResult.addDataQualityComponentDebugInfo(message, self.penalty)


def applyTitleTests(titleTests, searchResult):
    for titleTest in titleTests:
        titleTest.apply(searchResult)


def tokenRegexp(token):
    """Returns a simple regular expression testing whether or not the word appears as a single token in the text."""
    return re.compile("[^ ,-:\[(]%s[$ ,-:\])]", re.IGNORECASE)


############################################################################################################
################################################    FILM    ################################################
############################################################################################################

def cleanTvTitle(tvTitle):
    return tvTitle



# These are things we're so confident don't belong in titles that we're willing to strip them out wantonly.
# These aren't things that reflect badly on a movie for being in its title.
MOVIE_TITLE_REMOVAL_REGEXPS = (
    re.compile("[ ,:\[(-]+Director'?s Cut[ ,:\])-]*$", re.IGNORECASE),
    re.compile("[ ,:\[(-]+Blu-?Ray[ ,:\])-]*$", re.IGNORECASE),
    re.compile("[ ,:\[(-]+Box\s+Set[ ,:\])-]*$", re.IGNORECASE),
    re.compile("[ ,:\[(-]+HD[ ,:\])-]*$"),
    re.compile("[ ,:\[(-]+Collector'?s\s+Edition[ ,:\])-]*$", re.IGNORECASE)
)

def cleanMovieTitle(movieTitle):
    #return applyRemovalRegexps(MOVIE_TITLE_REMOVAL_REGEXPS, movieTitle)
    return movieTitle

# These aren't things we expect, and expect to have to remove. These are things that probably indicate that there's
# something wrong with a movie. Most likely, it's actually a TV show or a box set.
MOVIE_TITLE_QUALITY_TESTS = (
    TitleDataQualityTest('[^:,\[\(-]\s*The Complete ', "'the complete' in title", 0.35,
                         exceptionQueryRegexp=tokenRegexp('complete')),
    TitleDataQualityTest('[:,\[\(-]\s*Seasons? ', "season specification in title", 0.5,
                         exceptionQueryRegexp=tokenRegexp('season')),
    TitleDataQualityTest('[:,\[\(-]\s*The [0-9a-zA-Z-] Seasons?', "season specification in title", 0.5,
                         exceptionQueryRegexp=tokenRegexp('season')),
    TitleDataQualityTest('[:,\[\( -]Box(ed)? Set[:,\]\) $-]', "box set in title", 0.5),
    TitleDataQualityTest('[:,\[\( -]\s*Volumes? [0-9a-zA-Z-]{1,10}[\]) ]+$', "volume specification in title", 0.5,
                         exceptionQueryRegexp=tokenRegexp('volume')),
    TitleDataQualityTest('[^:,\[\( -]\s*The Best of ', "'best of' in title", 0.5,
                         exceptionQueryRegexp=tokenRegexp('best'))
)

def applyMovieTitleDataQualityTests(movieTitle):
    return applyTitleTests(MOVIE_TITLE_QUALITY_TESTS, movieTitle)

############################################################################################################
################################################   MUSIC    ################################################
############################################################################################################

def cleanTrackTitle(trackTitle):
    return trackTitle

def cleanAlbumTitle(albumTitle):
    return albumTitle

def cleanArtistTitle(artistTitle):
    return artistTitle

############################################################################################################
################################################   BOOKS    ################################################
############################################################################################################

def cleanBookTitle(bookTitle):
    return bookTitle

############################################################################################################
################################################    APPS    ################################################
############################################################################################################

def cleanAppTitle(appTitle):
    return appTitle

############################################################################################################
################################################   PLACES   ################################################
############################################################################################################

def cleanPlaceTitle(placeTitle):
    return placeTitle