#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from whoosh.analysis import *
from whoosh.support.charset import accent_map

# Tokenizer and filter for text processing. For detailed explanation of each of these fields, see
# Whoosh documentation at: http://packages.python.org/Whoosh/api/analysis.html
# 
# The gist here is that the RegexTokenizer will break the input string into tokens based on default
# regex, which as far as I can tell splits on words and common punctuations. Then the tokens are
# piped into each filter (the | operator is overloaded to behave like the unix pipe):
#       CharsetFilter - removes common diacritics, e.g. é -> e
#       LowercaseFilter - puts tokens into lowercase
#       StopFilter - removes common stop words in English
TOKENIZER = RegexTokenizer() | CharsetFilter(accent_map) | LowercaseFilter() | StopFilter() 

# The TeeFilter passes the input stream to each of the filters passed in constructor, and merges the
# outputs. The PassFilter just returns the input token, and the StemFilter removes usual word
# endings in English, e.g. economical -> economic. The net effect of the normalizer is that for each
# input word, we return the word itself plus a canonical version of that word.
# TODO also add common spell correction?
NORMALIZER = TeeFilter(PassFilter(), StemFilter())

def generateSearchTokens(entity):
    components = []
    if entity.title is not None:
        components.append(entity.title)

    def addSubfieldTitles(field):
        subfield = getattr(entity, field, None)
        if subfield is not None:
            for subdoc in subfield:
                if getattr(subdoc, 'title', None) is not None:
                    components.append(subdoc.title)
    subfields = ('authors', 'albums', 'artists', 'tracks', 'directors', 'cast')
    for field in subfields:
        addSubfieldTitles(field)
        
    return getTokensForIndexing(components)

def toUnicode(string):
    if isinstance(string, unicode):
        return string
    elif isinstance(string, str):
        return string.decode('utf-8')
    else:
        raise TypeError('Invalid type for toUnicode: ' + str(type(string)))

def getTokensForIndexing(components):
    fullDoc = ' '.join(toUnicode(c) for c in components)
    tokens = (token for token in TOKENIZER(fullDoc))
    return list(set(token.text for token in NORMALIZER(tokens)))

def formatSearchQuery(queryText):
    tokens = (token for token in TOKENIZER(queryText))
    components = []
    for token in tokens:
        normalized = set([normalized.text for normalized in NORMALIZER([token])])
        query = next(iter(normalized)) if len(normalized) == 1 else {'$in' : list(normalized)}
        components.append({'search_tokens' : query})
    return components


if __name__ == '__main__':
    from sys import argv
    print getTokensForIndexing(argv[1:])

