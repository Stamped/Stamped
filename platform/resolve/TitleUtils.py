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

# Tools for fixing up titles.

def applyRemovalRegexps(regexps, title):
    modified = True
    while modified:
        modified = False
        for removalRegexp in regexps:
            if removalRegexp.search(title):
                title = removalRegexp.sub('', title)
                modified = True
    return title


# Tools for demoting based on regepx title matches.

class TitleDataQualityRegexpTest(object):
    """
    Encapsulates a test
    , in the form of a regular expression, for potential data quality issues in a search result
    based on its title. When the regular expression matches the result title, we apply the score penalty and attach
    the message to the data quality score debug information.

    If rawName==True, we apply the regular expression to the raw_name ResolverObject field instead of the processed
    name property.
    """
    def __init__(self, penalizedTitleRegexp, message, penalty, exceptionQueryRegexp=None, rawName=False):
        self.titleRegexp = penalizedTitleRegexp
        if isinstance(self.titleRegexp, basestring):
            self.titleRegexp = re.compile(self.titleRegexp, re.IGNORECASE)
        self.exceptionQueryRegexp = exceptionQueryRegexp
        self.message = message
        self.penalty = penalty
        self.rawName = rawName

    def __matchesException(self, query):
        try:
            return self.exceptionQueryRegexp.search(query)
        except:
            return any(regexp.search(query) for regexp in self.exceptionQueryRegexp)

    def applyTest(self, searchResult, searchQuery):
        title = searchResult.resolverObject.raw_name if self.rawName else searchResult.resolverObject.name
        anyMatches = False
        if self.titleRegexp.search(title) and not self.__matchesException(searchQuery):
            searchResult.dataQuality *= 1 - self.penalty
            searchResult.addDataQualityComponentDebugInfo(self.message, self.penalty)
            anyMatches = True
        return anyMatches


def applyTitleTests(titleTests, searchResult, searchQuery):
    modified = [titleTest.applyTest(searchResult, searchQuery) for titleTest in titleTests]
    return any(modified)


def makeTokenRegexp(token):
    """Returns a simple regular expression testing whether or not the word appears as a single token in the text."""
    return re.compile("[^ ,-:\[(]%s[$ ,-:\])]" % token, re.IGNORECASE)


def makeDelimitedSectionRe(pattern):
    """Returns a regex that matches an entire delimited section (by () or []) if the
    section contains the given pattern.
    """
    return re.compile("[(\[](.+ )?%s( .+)?[)\]]" % pattern, re.IGNORECASE)


POSSESSIVE_RE = re.compile('\'s[$\s]', re.IGNORECASE)
NON_CHAR_LETTER_RE = re.compile('[ .,:;"\'&-]')
def tokenizeString(string):
    withoutPossessives = POSSESSIVE_RE.sub(' ', string)
    withoutPunctuation = NON_CHAR_LETTER_RE.sub(' ', withoutPossessives)
    return withoutPunctuation.lower().split()


# Tools for demoting based on title token matches.
class Token(object):
    def __init__(self, text, penalty=None):
        self.text = text
        self.penalty = penalty

    def isIn(self, tokenList):
        if ' ' not in self.text:
            return self.text in tokenList
        else:
            # This is actually multiple words. So we'll hack a little.
            return self.text in ' '.join(tokenList)


def applyTokenTests(tokens, searchResult, searchQuery, defaultPenalty=0.1):
    queryTokens = tokenizeString(searchQuery)
    # TODO: Should I use raw_name?
    titleTokens = tokenizeString(searchResult.resolverObject.name)
    anyMatches = False
    for token in tokens:
        if token.isIn(titleTokens) and not token.isIn(queryTokens):
            penalty = token.penalty if token.penalty else defaultPenalty
            searchResult.dataQuality *= 1 - penalty
            searchResult.addDataQualityComponentDebugInfo("token '%s' in title but not query" % token.text, penalty)
            anyMatches = True
    return anyMatches


############################################################################################################
################################################    FILM    ################################################
############################################################################################################

# These are things we're so confident don't belong in TV titles that we're willing to strip them out wantonly.
# These aren't things that reflect badly on a movie for being in its title.
TV_THE_COMPLETE_REGEX_CONFIDENT = re.compile('[^:,\[\(-]\s*The Complete ', re.IGNORECASE)
TV_SEASON1_REGEX_CONFIDENT = re.compile('[:,\[\(-]\s*Seasons? ', re.IGNORECASE)
TV_SEASON2_REGEX_CONFIDENT = re.compile('[:,\[\(-]\s*The [0-9a-zA-Z-] Seasons?', re.IGNORECASE)
TV_BOXED_SET_REGEX_CONFIDENT = re.compile('[:,\[\(-]Box(ed)? Set[:,\]\) $-]', re.IGNORECASE)
TV_VOLUMES_REGEX_CONFIDENT = re.compile('[:,\[\(-]\s*Volumes? [0-9a-zA-Z-]{1,10}[\]) ]+$', re.IGNORECASE)
TV_BEST_OF_REGEX_CONFIDENT = re.compile('[^:,\[\(-]\s*The Best of ', re.IGNORECASE)

TV_TITLE_REMOVAL_REGEXPS = (
    TV_SEASON1_REGEX_CONFIDENT,
    TV_SEASON2_REGEX_CONFIDENT,
    TV_BOXED_SET_REGEX_CONFIDENT,
    TV_VOLUMES_REGEX_CONFIDENT,
    TV_BEST_OF_REGEX_CONFIDENT
)

def cleanTvTitle(tvTitle):
    return applyRemovalRegexps(TV_TITLE_REMOVAL_REGEXPS, tvTitle)

TV_TITLE_HIGH_CONFIDENCE_QUALITY_TESTS = (
    # I didn't quite feel confident enough to strip this one out.
    TitleDataQualityRegexpTest(TV_THE_COMPLETE_REGEX_CONFIDENT, "'the complete' prefix in title", 0.35,
        exceptionQueryRegexp=makeTokenRegexp('complete')),
)

TV_TITLE_BAD_TOKENS = (
    Token('season'), Token('seasons'),
    Token('episode'), Token('episodes'),
    Token('collector'), Token('collection'),
    Token('series'),
    Token('best of'),
    Token('volume'), Token('volumes')
)

def applyTvTitleDataQualityTests(searchResult, searchQuery):
    if applyTitleTests(TV_TITLE_HIGH_CONFIDENCE_QUALITY_TESTS, searchResult, searchQuery):
        # We've already found a severe problem and demoted heavily. Skip the token tests, which are weaker and may
        # be duplicative.
        return
    applyTokenTests(TV_TITLE_BAD_TOKENS, searchResult, searchQuery, defaultPenalty=0.2)


MOVIE_TITLE_YEAR_EXTRACTION_REGEXP = re.compile("\s*\((\d{4})\s*$")

# These are things we're so confident don't belong in movie titles that we're willing to strip them out wantonly.
# These aren't things that reflect badly on a movie for being in its title.
MOVIE_TITLE_REMOVAL_REGEXPS = (
    MOVIE_TITLE_YEAR_EXTRACTION_REGEXP,
    re.compile("[ ,:\[(-]+Director'?s Cut[ ,:\])-]*$", re.IGNORECASE),
    re.compile("[ ,:\[(-]+Blu-?Ray[ ,:\])-]*$", re.IGNORECASE),
    re.compile("[ ,:\[(-]+Box\s+Set[ ,:\])-]*$", re.IGNORECASE),
    re.compile("[ ,:\[(-]+HD[ ,:\])-]*$"),
    re.compile("[ ,:\[(-]+[a-zA-Z0-9']{3,15}\s+Edition[ ,:\])-]*$", re.IGNORECASE)
)

def cleanMovieTitle(movieTitle):
    return applyRemovalRegexps(MOVIE_TITLE_REMOVAL_REGEXPS, movieTitle)

def getMovieReleaseYearFromTitle(movieResolverObject):
    match = MOVIE_TITLE_YEAR_EXTRACTION_REGEXP.search(movieResolverObject.raw_name)
    if match:
        return int(match.group(1))

# These aren't things we expect, or things we remove. These are things that probably indicate that there's
# something wrong with a movie. Most likely, it's actually a TV show or a box set.
MOVIE_TITLE_HIGH_CONFIDENCE_QUALITY_TESTS = (
    TitleDataQualityRegexpTest(TV_THE_COMPLETE_REGEX_CONFIDENT, "'the complete' in title", 0.35,
                               exceptionQueryRegexp=makeTokenRegexp('complete')),
    TitleDataQualityRegexpTest(TV_SEASON1_REGEX_CONFIDENT, "season specification in title", 0.5,
                               exceptionQueryRegexp=makeTokenRegexp('season')),
    TitleDataQualityRegexpTest(TV_SEASON2_REGEX_CONFIDENT, "season specification in title", 0.5,
                               exceptionQueryRegexp=makeTokenRegexp('season')),
    TitleDataQualityRegexpTest(TV_BOXED_SET_REGEX_CONFIDENT, "box set in title", 0.5),
    TitleDataQualityRegexpTest(TV_VOLUMES_REGEX_CONFIDENT, "volume specification in title", 0.5,
                               exceptionQueryRegexp=makeTokenRegexp('volume')),
    TitleDataQualityRegexpTest(TV_BEST_OF_REGEX_CONFIDENT, "'best of' in title", 0.5,
                               exceptionQueryRegexp=makeTokenRegexp('best'))
)

MOVIE_TITLE_BAD_TOKENS = (
    Token('season'), Token('seasons'),
    Token('volume'), Token('volumes'),
    Token('box set', penalty=0.35), Token('boxed set', penalty=0.35),
    Token('trilogy', penalty=0.35),
    Token('collection'),
    Token('edition')
)

def applyMovieTitleDataQualityTests(searchResult, searchQuery):
    if applyTitleTests(MOVIE_TITLE_HIGH_CONFIDENCE_QUALITY_TESTS, searchResult, searchQuery):
        # We've already found a severe problem and demoted heavily. Skip the token tests, which are weaker and may
        # be duplicative.
        return
    applyTokenTests(MOVIE_TITLE_BAD_TOKENS, searchResult, searchQuery, defaultPenalty=0.2)


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

BOOK_TITLE_REMOVAL_REGEXPS = (
    makeDelimitedSectionRe('edition'),
    makeDelimitedSectionRe('version'),
    makeDelimitedSectionRe('series'),
    makeDelimitedSectionRe('vintage'),
    makeDelimitedSectionRe('classic'),
    makeDelimitedSectionRe('book'),
    makeDelimitedSectionRe('volume'),
)

def cleanBookTitle(bookTitle):
    return applyRemovalRegexps(BOOK_TITLE_REMOVAL_REGEXPS, bookTitle)

BOOK_TITLE_SUSPICIOUS_TESTS = (
    TitleDataQualityRegexpTest('\bbest of\b', "'best of' in title", 0.3,
                               exceptionQueryRegexp=makeTokenRegexp('best')),
    TitleDataQualityRegexpTest('\bbox(ed)? set\b', "'box set' in title", 0.3,
                               exceptionQueryRegexp=(makeTokenRegexp('box'), makeTokenRegexp('boxed'), makeTokenRegexp('set'))),
    TitleDataQualityRegexpTest('\bedition', "'edition' in title", 0.3,
                               exceptionQueryRegexp=makeTokenRegexp('edition')),
    TitleDataQualityRegexpTest('\bbook\s+\d', "'book #' in title", 0.3,
                               exceptionQueryRegexp=makeTokenRegexp('book')),
    TitleDataQualityRegexpTest('\bvolume\s+\d', "'volume #' in title", 0.3,
                               exceptionQueryRegexp=makeTokenRegexp('volume')),
)

def applyBookTitleDataQualityTests(searchResult, searchQuery):
    applyTitleTests(BOOK_TITLE_SUSPICIOUS_TESTS, searchResult, searchQuery)

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
