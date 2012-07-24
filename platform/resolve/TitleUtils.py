#!/usr/bin/env python

from __future__ import division

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import math
import re
from resolve.StringNormalizationUtils import format
from collections import namedtuple

# TODO: Merge with search/DataQualityUtils.py somewhere common (to avoid dependency loop)

############################################################################################################
################################################   UTILS    ################################################
############################################################################################################

Penalty = namedtuple('Penalty', ['description', 'score'])

# Tools for fixing up titles.

def applyRemovalRegexps(regexps, title):
    modified = True
    while modified:
        modified = False
        for removalRegexp in regexps:
            if removalRegexp.search(title):
                title = removalRegexp.sub('', title)
                modified = True
    return format(title)


# Tools for demoting based on regepx title matches.

class TitleDataQualityRegexpTest(object):
    """
    Encapsulates a test, in the form of a regular expression, for potential data quality issues in a search result
    based on its title. When the regular expression matches the result title, we apply the score penalty and attach
    the message to the data quality score debug information.

    If rawName==True, we apply the regular expression to the raw_name ResolverObject field instead of the processed
    name property.
    """
    def __init__(self, penalizedTitleRegexp, message, penalty, exceptionQueryRegexps=None, rawName=False):
        self.titleRegexp = penalizedTitleRegexp
        if isinstance(self.titleRegexp, basestring):
            self.titleRegexp = re.compile(self.titleRegexp, re.IGNORECASE)
        self.exceptionQueryRegexps = exceptionQueryRegexps
        self.message = message
        self.penalty = penalty
        self.rawName = rawName

    def __matchesException(self, query):
        if not self.exceptionQueryRegexps:
            return False
        try:
            return self.exceptionQueryRegexps.search(query)
        except:
            return any(regexp.search(query) for regexp in self.exceptionQueryRegexps)

    def matchesTitle(self, title, query=None):
        return self.titleRegexp.search(title) and not (query and self.__matchesException(query))

    def runTest(self, title, searchQuery):
        if self.matchesTitle(title, searchQuery):
            return [Penalty(self.message, self.penalty)]
        return []

    def applyTest(self, searchResult, searchQuery):
        title = searchResult.resolverObject.raw_name if self.rawName else searchResult.resolverObject.name
        penalties = self.runTest(title, searchQuery)
        for penalty in penalties:
            searchResult.dataQuality *= 1 - penalty.score
            searchResult.addDataQualityComponentDebugInfo(penalty.description, penalty.score)
        return bool(penalties)


def applyTitleTests(titleTests, searchResult, searchQuery):
    modified = [titleTest.applyTest(searchResult, searchQuery) for titleTest in titleTests]
    return any(modified)


def runTitleTests(titleTests, title, searchQuery):
    penalties = []
    for titleTest in titleTests:
        penalties.extend(titleTest.runTest(searchResult, searchQuery))
    return penalties


def makeTokenRegexp(token):
    """Returns a simple regular expression testing whether or not the word appears as a single token in the text."""
    return re.compile("(^|[ ,-:\[(])%s($|[ ,-:\])])" % token, re.IGNORECASE)


def makeTokensRegexp(*tokens):
    """Returns a simple regular expression testing whether or not the word appears as a single token in the text."""
    return re.compile("(^|[ ,-:\[(])(%s)($|[ ,-:\])])" % '|'.join(tokens), re.IGNORECASE)


def makeDelimitedSectionRe(pattern):
    """Returns a regex that matches an entire delimited section (by () or []) if the
    section contains the given pattern.
    """
    return re.compile("[(\[].*?\\b%s\\b.*?[)\]]" % pattern, re.IGNORECASE)


ROMAN_NUMERAL_RE = re.compile(
    r'\b(?P<numeral>(ix|iv|v?i{1,3}))\s*(:|$)', re.IGNORECASE)
REPLACEMENTS = {
    'x' : 10,
    'ix' : 9,
    'v' : 5,
    'iv' : 4,
    'i' : 1,
}
def convertRomanNumerals(title):
    """Convert roman numerals in special places of the title to their decimal representation.

    This function is conservative, in that the roman numerals will only be replaced if it occurs at
    the end of the title or right before a ":". This avoids false positives, for example, whenever
    the word "I" is used.
    """
    def romanToInt(numeral):
        numeral = numeral.lower()
        total = 0
        while numeral:
            step = 2 if numeral[:2] in REPLACEMENTS else 1
            total += REPLACEMENTS[numeral[:step]]
            numeral = numeral[step:]
        return str(total)

    match = ROMAN_NUMERAL_RE.search(title)
    if match:
        matchStart, matchEnd = match.span()
        modifiedTail = convertRomanNumerals(title[matchEnd:])
        numeral = match.group('numeral')
        numeralInt = romanToInt(numeral)
        title = title[:matchStart] + title[matchStart:matchEnd].replace(numeral, numeralInt, 1) + modifiedTail
    return title


def __stripPrefix(a, b):
    longer, shorter = (a, b) if len(a) > len(b) else (b, a)
    if longer.startswith(shorter):
        return longer[len(shorter):].strip()


def isDelimitedPrefix(a, b):
    """Returns true if one string is a prefix of the other, and the remaining string is separated by
    a delimiter

    Currently a delimiter is one of :-,([. This is to cluster titles like "Twilight" and "Twilight:
    Book 1 of the Corny Overused Vampire Themed Series Special Edition"
    """
    remainder = __stripPrefix(a, b)
    delimiters = ':-,(['
    return remainder and remainder[0] in delimiters


POSSESSIVE_RE = re.compile('\'s($|\s)', re.IGNORECASE)
NON_CHAR_LETTER_RE = re.compile('[ (\[)\]/.,:;"\'&-]')
def tokenizeString(string):
    withoutPossessives = POSSESSIVE_RE.sub(' ', string)
    withoutPunctuation = NON_CHAR_LETTER_RE.sub(' ', withoutPossessives)
    return withoutPunctuation.lower().split()


# Tools for demoting based on title token matches.
class Token(object):
    def __init__(self, text, penalty=None, rawName=False):
        self.text = text
        self.penalty = penalty
        self.useRawName = rawName

    def isIn(self, tokenList):
        if ' ' not in self.text:
            return self.text in tokenList
        else:
            # This is actually multiple words. So we'll hack a little.
            return self.text in ' '.join(tokenList)


def runTokenTests(tokens, title, query, defaultPenalty=0.1):
    queryTokens = tokenizeString(query)
    # TODO: Should I use raw_name?
    titleTokens = tokenizeString(title)
    penalties = []
    for token in tokens:
        if token.isIn(titleTokens) and not token.isIn(queryTokens):
            penalties.append(Penalty("token hit '%s'" % token.text, token.penalty or defaultPenalty))
    return penalties


def applyTokenTests(tokens, searchResult, searchQuery, defaultPenalty=0.1):
    queryTokens = tokenizeString(searchQuery)
    # TODO: Should I use raw_name?
    titleTokens = tokenizeString(searchResult.resolverObject.name)
    rawTitleTokens = tokenizeString(searchResult.resolverObject.raw_name)
    anyMatches = False
    for token in tokens:
        currTitleTokens = rawTitleTokens if token.useRawName else titleTokens
        if token.isIn(currTitleTokens) and not token.isIn(queryTokens):
            penalty = token.penalty or defaultPenalty
            searchResult.dataQuality *= 1 - penalty
            searchResult.addDataQualityComponentDebugInfo("token '%s' in title but not query" % token.text, penalty)
            anyMatches = True
    return anyMatches


############################################################################################################
################################################    FILM    ################################################
############################################################################################################

# These are things we're so confident don't belong in TV titles that we're willing to strip them out wantonly.
# These aren't things that reflect badly on a movie for being in its title.
TV_SEASON1_REGEX_CONFIDENT = re.compile(r'\s*[:,\[\(-]\s*Seasons?\s*\d+', re.IGNORECASE)
TV_SEASON2_REGEX_CONFIDENT = re.compile(r'\s*[:,\[\(-]\s*The [0-9a-zA-Z-] Seasons?', re.IGNORECASE)
TV_BOXED_SET_REGEX_CONFIDENT = re.compile(r'\s*[:,\[\(-]\s*Box(ed)? Set([:,\]\) -]|$)', re.IGNORECASE)
TV_VOLUMES_REGEX_CONFIDENT = re.compile(r'\s*[:,\[\(-]\s*Volumes? [0-9a-zA-Z-]{1,10}([\])]|\\b)$', re.IGNORECASE)
TV_BEST_OF_REGEX_CONFIDENT = re.compile(r'\s*(^|[:,\[\(-])\s*(The )?Best of ', re.IGNORECASE)
TV_UNCENSORED_REGEX_CONFIDENT = re.compile(r'\s*(^|[:,\[\(-])\s*uncensored\\b', re.IGNORECASE)
# TODO: Occasionally it is best to keep this in the title, but it's hard to know when. Maybe when the search hits the
# text in it or something?
TV_PRESENTS_REGEX_CONFIDENT = re.compile(r'^(["\'a-zA-Z0-9]+\s+){1,3}Presents\s*:\s*', re.IGNORECASE)

TITLE_YEAR_EXTRACTION_REGEXP = re.compile("\s*\((\d{4})\)\s*$")

TV_TITLE_REMOVAL_REGEXPS = (
    TITLE_YEAR_EXTRACTION_REGEXP,
    TV_SEASON1_REGEX_CONFIDENT,
    TV_SEASON2_REGEX_CONFIDENT,
    TV_BOXED_SET_REGEX_CONFIDENT,
    TV_VOLUMES_REGEX_CONFIDENT,
    TV_BEST_OF_REGEX_CONFIDENT,
    TV_UNCENSORED_REGEX_CONFIDENT,
    TV_PRESENTS_REGEX_CONFIDENT,
)

def cleanTvTitle(tvTitle):
    return applyRemovalRegexps(TV_TITLE_REMOVAL_REGEXPS, tvTitle)

TV_THE_COMPLETE_REGEX_CONFIDENT = re.compile('\s*(^|[:,\[\(-])\s*The Complete ', re.IGNORECASE)
TV_TITLE_HIGH_CONFIDENCE_QUALITY_TESTS = (
    # I didn't quite feel confident enough to strip this one out.
    TitleDataQualityRegexpTest(TV_THE_COMPLETE_REGEX_CONFIDENT, "'the complete' prefix in title", 0.35,
        exceptionQueryRegexps=makeTokenRegexp('complete')),
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


# These are things we're so confident don't belong in movie titles that we're willing to strip them out wantonly.
# These aren't things that reflect badly on a movie for being in its title.
MOVIE_TITLE_REMOVAL_REGEXPS = (
    TITLE_YEAR_EXTRACTION_REGEXP,
    TV_PRESENTS_REGEX_CONFIDENT,
    re.compile("[ ,:\[(-]+\s*Director'?s Cut[ ,:\])-]*$", re.IGNORECASE),
    re.compile("[ ,:\[(-]+\s*Blu-?Ray[ ,:\])-]*$", re.IGNORECASE),
    re.compile("[ ,:\[(-]+\s*Box\s+Set[ ,:\])-]*$", re.IGNORECASE),
    re.compile("[ ,:\[(-]+\s*HD[ ,:\])-]*$"),
    re.compile("[,:\[(-]+\s*uncensored[ ,:\])-]*$", re.IGNORECASE),
    re.compile("[,:\[(-]+\s*([a-zA-Z0-9']{3,20}\s+){1,2}(Cut|Edition|Restoration|Version)[ ,:\])-]*$", re.IGNORECASE),
    re.compile("[,:\[(-]+\s*([a-zA-Z0-9']{3,20}\s+){0,2}remastered[ ,:\])-]*$", re.IGNORECASE),
    re.compile("[\[\(].*subtitle.*[\)\]]\s*$", re.IGNORECASE),
    re.compile("\((Unrated|NR|Not Rated|Uncut)( Edition)?\)\s*$", re.IGNORECASE)
)

def cleanMovieTitle(movieTitle):
    return applyRemovalRegexps(MOVIE_TITLE_REMOVAL_REGEXPS, movieTitle)

def getFilmReleaseYearFromTitle(rawTitle):
    match = TITLE_YEAR_EXTRACTION_REGEXP.search(rawTitle)
    if match:
        return int(match.group(1))

# These aren't things we expect, or things we remove. These are things that probably indicate that there's
# something wrong with a movie. Most likely, it's actually a TV show or a box set.
MOVIE_TITLE_HIGH_CONFIDENCE_QUALITY_TESTS = (
    TitleDataQualityRegexpTest(TV_THE_COMPLETE_REGEX_CONFIDENT, "'the complete' in title", 0.35,
                               exceptionQueryRegexps=makeTokenRegexp('complete'), rawName=True),
    TitleDataQualityRegexpTest(TV_SEASON1_REGEX_CONFIDENT, "season specification in title", 0.5,
                               exceptionQueryRegexps=makeTokenRegexp('season'), rawName=True),
    TitleDataQualityRegexpTest(TV_SEASON2_REGEX_CONFIDENT, "season specification in title", 0.5,
                               exceptionQueryRegexps=makeTokenRegexp('season'), rawName=True),
    TitleDataQualityRegexpTest(TV_BOXED_SET_REGEX_CONFIDENT, "box set in title", 0.5, rawName=True),
    TitleDataQualityRegexpTest(TV_VOLUMES_REGEX_CONFIDENT, "volume specification in title", 0.5,
                               exceptionQueryRegexps=makeTokenRegexp('volume'), rawName=True),
    TitleDataQualityRegexpTest(TV_BEST_OF_REGEX_CONFIDENT, "'best of' in title", 0.5,
                               exceptionQueryRegexps=makeTokenRegexp('best'), rawName=True)
)

MOVIE_TITLE_BAD_TOKENS = (
    # Raw name tests -- these are things that, if they are in the raw name, indicate that this may not be a single
    # movie, it may be a collection, or a TV show.
    Token('season', rawName=True), Token('seasons', rawName=True),
    Token('volume', rawName=True), Token('volumes', rawName=True),
    Token('box set', penalty=0.35, rawName=True), Token('boxed set', penalty=0.35, rawName=True),
    Token('trilogy', penalty=0.35, rawName=True),
    Token('collection', rawName=True),
    # Processed name tests -- these aren't things that indicate that this isn't a movie, but they're things that
    # indicate we weren't able to fix the title completely.
    Token('edition', rawName=False, penalty=0.15),
    Token('remastered', rawName=False, penalty=0.15),
    Token('re-mastered', rawName=False, penalty=0.15),
    Token('version', rawName=False, penalty=0.15),
    Token('HD', rawName=False, penalty=0.15),
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

ARTIST_TITLE_BAD_TOKENS = (
    Token('karaoke', penalty=0.4, rawName=True),
    Token('tribute', penalty=0.4, rawName=True),
    Token('cover', penalty=0.4, rawName=True),
    Token('featuring', penalty=0.4, rawName=True)
    )
# Artist titles don't really have problems, either.
def cleanArtistTitle(artistTitle):
    return artistTitle

def applyArtistTitleDataQualityTests(searchResult, searchQuery):
    applyTokenTests(ARTIST_TITLE_BAD_TOKENS, searchResult, searchQuery)

# These are things we're so confident don't belong in track/album titles that we're willing to strip them out wantonly.
# These aren't things that reflect badly on a movie for being in its title.
ALBUM_AND_TRACK_TITLE_REMOVAL_REGEXPS = (
    re.compile("\s*[,:\[(-]+\s*([a-zA-Z0-9']{3,20}\s+){0,2}remastered[ ,:\])-]*$", re.IGNORECASE),
    re.compile("\s*[,:\[(-]+\s*(uncensored|explicit|single|vinyl|album|ep|lp)[ ,:\])-]*$", re.IGNORECASE),
)

TRACK_TITLE_SUSPICIOUS_TESTS = (
    TitleDataQualityRegexpTest(r'\s*[,:\[(-]+\s*([a-zA-Z0-9\']{3,20}\s+){1,2}(Mix|Remix|Re-mix|Remixed|Re-Mixed)[ ,:\])-]*$', 'mix in title', 0.5,
        exceptionQueryRegexps=makeTokensRegexp('mix', 'remix'), rawName=True),
    TitleDataQualityRegexpTest(r'\s*[,:\[(-]+\s*([a-zA-Z0-9\']{3,20}\s+){1,2}(Cut|Edit|Version)[ ,:\])-]*$', 'version info in title', 0.5,
        exceptionQueryRegexps=makeTokensRegexp('cut', 'edit', 'version'), rawName=True),
    TitleDataQualityRegexpTest(r'\s*[,:\[(-]+\s*(Instrumental)[ ,:\])-]*$', 'instrumental in title', 0.5,
        exceptionQueryRegexps=makeTokenRegexp('instrumental'), rawName=True)
)
def cleanTrackTitle(trackTitle):
    return applyRemovalRegexps(ALBUM_AND_TRACK_TITLE_REMOVAL_REGEXPS, trackTitle)

TRACK_TITLE_BAD_TOKENS = (
    Token('mix', rawName=True), Token('remix', rawName=True),
    Token('re-mix', rawName=True), Token('remixed', rawName=True), Token('re-mixed', rawName=True),
    Token('cut', rawName=True), Token('edit', rawName=True), Token('instrumental', rawName=True),
    Token('inst', rawName=True), Token('cover', rawName=True),
    Token('tribute', rawName=True), Token('karaoke', rawName=True, penalty=0.4),
    Token('remastered', rawName=False, penalty=0.15),
    Token('re-mastered', rawName=False, penalty=0.15),
    Token('version', rawName=False),
    Token('LP', rawName=False),
)
def applyTrackTitleDataQualityTests(searchResult, searchQuery):
    # Even though we cut this mix/edit/etc. bullshit out of the title we want to demote results that had these terms
    # in their raw names in order to favor the non-mixed/edited/whatever versions.
    if not applyTitleTests(TRACK_TITLE_SUSPICIOUS_TESTS, searchResult, searchQuery):
        applyTokenTests(TRACK_TITLE_BAD_TOKENS, searchResult, searchQuery, defaultPenalty=0.25)

    if searchResult.resolverObject.artists:
        try:
            artistName = searchResult.resolverObject.artists[0]['name']
            artistPenalties = runTokenTests(ARTIST_TITLE_BAD_TOKENS, artistName, searchQuery)
            for artistPenalty in artistPenalties:
                searchResult.dataQuality *= (1 - artistPenalty.score) ** 0.5
                searchResult.addDataQualityComponentDebugInfo('Artist title penalty: %s' % repr(artistPenalty.description), artistPenalty.score)
        except KeyError:
            pass

# Album titles don't really have problems.
def cleanAlbumTitle(albumTitle):
    return applyRemovalRegexps(ALBUM_AND_TRACK_TITLE_REMOVAL_REGEXPS, albumTitle)

ALBUM_TITLE_BAD_TOKENS = (
    Token('ep', penalty=0.25),
    Token('karaoke', penalty=0.4, rawName=True),
    Token('cover', penalty=0.4, rawName=True),
    Token('tribute', penalty=0.3, rawName=True),
)
def applyAlbumTitleDataQualityTests(searchResult, searchQuery):
    applyTokenTests(ALBUM_TITLE_BAD_TOKENS, searchResult, searchQuery, defaultPenalty=0.2)

    if searchResult.resolverObject.artists:
        try:
            artistName = searchResult.resolverObject.artists[0]['name']
            artistPenalties = runTokenTests(ARTIST_TITLE_BAD_TOKENS, artistName, searchQuery)
            for artistPenalty in artistPenalties:
                searchResult.dataQuality *= (1 - artistPenalty.score) ** 0.5
                searchResult.addDataQualityComponentDebugInfo('Artist title penalty: %s' % repr(artistPenalty.description), artistPenalty.score)
        except KeyError:
            pass

############################################################################################################
################################################   BOOKS    ################################################
############################################################################################################

BOOK_TITLE_REMOVAL_REGEXPS = (
    makeDelimitedSectionRe('bargain'),
    makeDelimitedSectionRe('books?'),
    makeDelimitedSectionRe('classics?'),
    makeDelimitedSectionRe('editions?'),
    makeDelimitedSectionRe('hardcover'),
    makeDelimitedSectionRe('paperback'),
    makeDelimitedSectionRe('series'),
    makeDelimitedSectionRe('signet'),
    makeDelimitedSectionRe('translations?'),
    makeDelimitedSectionRe('version'),
    makeDelimitedSectionRe('vintage'),
    makeDelimitedSectionRe('volume'),
    re.compile(':\s*a\s+novel\s*$', re.IGNORECASE),
)

def cleanBookTitle(bookTitle):
    return applyRemovalRegexps(BOOK_TITLE_REMOVAL_REGEXPS, bookTitle)


def _makeSingleTokenSuspiciousTest(token, weight):
    return TitleDataQualityRegexpTest('\\b%s\\b' % token, '"%s" in title' % token, weight,
            exceptionQueryRegexps=makeTokenRegexp(token))

BOOK_TITLE_SUSPICIOUS_TESTS = (
    TitleDataQualityRegexpTest(r'\bbest of\b', '"best of" in title', 0.25,
        exceptionQueryRegexps=makeTokenRegexp('best')),
    TitleDataQualityRegexpTest(r'\bbooks?\s+\d', '"book #" in title', 0.25,
        exceptionQueryRegexps=makeTokenRegexp('book')),
    TitleDataQualityRegexpTest(r'\bvolumes?\s+\d', '"volume #" in title', 0.25,
        exceptionQueryRegexps=makeTokenRegexp('volume')),
    TitleDataQualityRegexpTest(r'\bvol\.?\s+\d', '"vol #" in title', 0.25,
        exceptionQueryRegexps=makeTokenRegexp('vol')),
    TitleDataQualityRegexpTest('\(', 'parenthesis in title', 0.1),
    TitleDataQualityRegexpTest('\[', 'bracket in title', 0.1),

    _makeSingleTokenSuspiciousTest('audiobook', 0.4),

    _makeSingleTokenSuspiciousTest('audio', 0.25),
    _makeSingleTokenSuspiciousTest('box', 0.25),
    _makeSingleTokenSuspiciousTest('boxed', 0.25),
    _makeSingleTokenSuspiciousTest('edition', 0.25),
    _makeSingleTokenSuspiciousTest('set', 0.25),
    _makeSingleTokenSuspiciousTest('bundle', 0.25),
    _makeSingleTokenSuspiciousTest('collection', 0.25),
    _makeSingleTokenSuspiciousTest('series', 0.25),

    _makeSingleTokenSuspiciousTest('abridged', 0.1),
    _makeSingleTokenSuspiciousTest('complete', 0.1),
    _makeSingleTokenSuspiciousTest('trilogy', 0.1),
    _makeSingleTokenSuspiciousTest('unabridged', 0.1),

    # TODO(geoff): this is a hacky way to demote the study guides. There are just so many of them...
    TitleDataQualityRegexpTest(r'\bCliffs? ?Notes?\b', '"cliffs notes" in title', 0.4,
        exceptionQueryRegexps=(makeTokenRegexp('cliff'), makeTokenRegexp('note'))),
    TitleDataQualityRegexpTest('(literature made easy)', '"literature made easy" in title', 0.4,
        exceptionQueryRegexps=(makeTokenRegexp('literature'), makeTokenRegexp('made'), makeTokenRegexp('easy'))),
    TitleDataQualityRegexpTest(r'\bstudy guide\b', '"study guide" in title', 0.4,
        exceptionQueryRegexps=(makeTokenRegexp('study'), makeTokenRegexp('guide'))),
)

def applyBookDataQualityTests(searchResult, searchQuery):
    for author in searchResult.resolverObject.authors:
        if author['name'].lower().strip() == 'shmoop':
            searchResult.dataQuality *= 0.5
            searchResult.addDataQualityComponentDebugInfo('"shmoop" in author', 0.5)
            return
    applyTitleTests(BOOK_TITLE_SUSPICIOUS_TESTS, searchResult, searchQuery)

    # Penalize for long author names. Penalty starts at 30 chars, reaches 0.4 (the cutoff for
    # dropping item from cluster) at 100 chars.
    if searchResult.resolverObject.authors:
        maxAuthorLength = max(len(author['name']) for author in searchResult.resolverObject.authors)
        if maxAuthorLength > 30:
            authorLengthPenalty = math.log(maxAuthorLength - 29) / 10.656
            searchResult.dataQuality *= 1 - authorLengthPenalty
            searchResult.addDataQualityComponentDebugInfo('author name with length %d' % maxAuthorLength, authorLengthPenalty)


def isSuspiciousPrefixBookTitle(a, b):
    """Returns true if one string is a prefix of the other, and the reminder is suspicious.

    That is, if the remainder contains words like "edition," "collection," etc. This would cluster
    together titles like "The Help" and "The Help Duluxe Edition."""
    remainer = __stripPrefix(a, b)
    if remainer:
        return any(test.matchesTitle(remainer) for test in BOOK_TITLE_SUSPICIOUS_TESTS)


############################################################################################################
################################################    APPS    ################################################
############################################################################################################

def cleanAppTitle(appTitle):
    return appTitle

def applyAppTitleDataQualityTests(searchResult, searchQuery):
    pass

############################################################################################################
################################################   PLACES   ################################################
############################################################################################################

def cleanPlaceTitle(placeTitle):
    return placeTitle

def applyPlaceTitleDataQualityTests(searchResult, searchQuery):
    pass
