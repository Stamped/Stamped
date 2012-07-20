#!/usr/bin/env python

from __future__ import division

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import report

try:
    import utils, re, string, traceback
    import logs
    import unicodedata
    from difflib                    import SequenceMatcher
except:
    report()
    raise


#generally applicable removal patterns
_general_regex_removals = [
    (re.compile(r'.*(\(.*\)).*')    , 1),     # a name ( with parens ) anywhere
    (re.compile(r'.*(\[.*]).*')     , 1),     # a name [ with brackets ] anywhere
    (re.compile(r'.*(\(.*)')        , 1),     # a name ( bad parathetical
    (re.compile(r'.*(\[.*)')        , 1),     # a name [ bad brackets
    (re.compile(r'.*(\.\.\.).*')    , 1),     # ellipsis ... anywhere
    (re.compile(r".*(').*")         , 1),
    (re.compile(r'.*(").*')         , 1),
    (re.compile(r'^(the ).*$')      , 1),
    (re.compile(r'.*\w(-)\w.*$')    , 1, ' '),
    # TODO PRELAUNCH FUCK FUCK FUCK: Clear out -:;/., and all sorts of other gratuitous punctuation. Run SxS!
                                                ]

#generally applicable replacements
_general_replacements = [
    ('&', ' and '),                             # canonicalize synonyms
]

# track-specific removal patterns
_track_removals = [
    (re.compile(r'.*[^-](-+.* (remix|mix|version|edit|dub|tribute|cover|bpm|single|\w+ [vV]ersion)$)'), 1),
    (re.compile(r'.*( *[\(\[]\w* *\w* *[vV]ersion[\)\]]$)'), 1),
]

# album-specific removal patterns
_album_removals = [
    (re.compile(r'^(the ).*$'), 1),
    (re.compile(r'.*((-|,)( the)? remixes.*$)'), 1),
    (re.compile(r'.*(- ep$)'), 1),
    (re.compile(r'.*( the (\w+ )?remixes$)'), 1),
    (re.compile(r'.*(- remix ep)'), 1),
    (re.compile(r'.*(- single$)'), 1),
]

# artist-specific removal patterns
_artist_removals = [
    (re.compile(r'^(the ).*$'), 1),
    (re.compile(r'^.*( band)'), 1),
]

# movie-specific removal patterns
_movie_removals = [
    # TODO - unimplemented and unused
]

def regexRemoval(string, patterns):

    """
    Modification-loop pattern removal

    Given a list of (pattern,groups) tuples, attempts to remove any match
    until no pattern matches for a full cycle.

    Multipass safe and partially optimized
    """
    modified = True
    while modified:
        modified = False

        for case in patterns:

            if len(case) == 2:
                pattern, group = case
                replacement = ''
            elif len(case) == 3:
                pattern, group, replacement = case
            else:
                raise Exception('Invalid case: ' + repr(case))

            while True:
                match = pattern.match(string)

                if match:
                    string = string[:match.start(group)] + replacement + string[match.end(group):]
                    modified = True
                else:
                    break

    return string

_whitespace_regexp = re.compile("\s+")

def format(string):
    """
    Whitespace unification
    Replaces all non-space whitespace with spaces.
    Removes any double-spacing or leading or trailing whitespace.
    """
    return _whitespace_regexp.sub(" ", string).strip()

def simplify(string):
    """
    General purpose string simplification

    Maps unicode characters to simplified ascii versions.
    Removes parenthesized strings, bracked stings, and ellipsis
    Performs whitespace unification.

    Multipass safe and partially optimized
    """

    string = unicodedata.normalize('NFKD', unicode(string)).encode('ascii', 'ignore')
    string = format(string.lower().strip())
    string = regexRemoval(string, _general_regex_removals)

    for find, replacement in _general_replacements:
        string = string.replace(find, replacement)

    return format(string)

def trackSimplify(name, artist=None):
    string = simplify(name)
    string = regexRemoval(string, _track_removals)

    # occasionally track names have their artist's name embedded within them,
    # so attempt to canonicalize track names by removing their artist's name
    # if present.
    # TODO: Do this in TrackEntityProxyComparator!
    if artist:
        artist = artist.lower().strip()

        artist_names = [
            artist,
            simplify(artist),
            artistSimplify(artist),
            ]

        for name in artist_names:
            if len(name) > 3:
                n = string.find(name)

                if n >= 0:
                    s2 = "%s %s" % (string[:n].strip(), string[n + len(name):].strip())

                    if len(s2) > 3:
                        string = s2
                        break

    return format(string)

def albumSimplify(string):
    # TODO: Work this into the regexRemoval call!
    string = re.compile('[ (\[:,-]+EP[)\]:, -]*$').sub(' ', string)
    string = simplify(string)
    string = regexRemoval(string, _album_removals)
    return format(string)

def artistSimplify(string):
    string = simplify(string)
    string = regexRemoval(string, _artist_removals)
    return format(string)

def movieSimplify(movie_name):
    # TODO: Do this in a more organized way!
    movie_name = re.compile('(^|\s)the(\s|$)', re.IGNORECASE).sub(' ', movie_name)
    movie_name = re.compile('(-\s|\s-)').sub(' ', movie_name)
    movie_name = re.compile('\s+').sub(' ', movie_name)
    movie_name = movie_name.strip()
    return format(simplify(movie_name))

def bookSimplify(string):
    return format(simplify(string))

def nameSimplify(string):
    """
    Name (person) specific simplification for fuzzy comparisons.
    """
    return format(simplify(string))

def videoGameSimplify(string):
    return format(simplify(string))

def stringComparison(a, b, strict=False):
    """
    Generic fuzzy string comparison.

    Returns a comparison decimal [0,1]
    """
    if not strict:
        a = simplify(a)
        b = simplify(b)

    if a == b:
        return 1.0
    else:
        junk_to_ignore = "\t-.;&".__contains__ # characters for SequenceMatcher to disregard
        v = SequenceMatcher(junk_to_ignore, a, b).ratio()

        #utils.log("DEBUG: %s vs %s (%f)" % (a, b, v))
        return v