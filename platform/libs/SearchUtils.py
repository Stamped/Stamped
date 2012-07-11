#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from whoosh.analysis import *
from whoosh.support.charset import accent_map

TOKENIZER = RegexTokenizer() | CharsetFilter(accent_map) | LowercaseFilter() | StopFilter() 
# TODO add spell correction here?
NORMALIZER = TeeFilter(PassFilter(), StemFilter())

def addMatchCodesToMongoDocument(document):
    components = []
    if 'title' in document:
        components.append(document['title'])

    def addSubfieldTitles(field):
        if field in document:
            for subdoc in document[field]:
                components.append(subdoc['title'])
    subfields = ('authors', 'albums', 'artists', 'tracks', 'directors', 'cast', 'publishers')
    for field in subfields:
        addSubfieldTitles(field)
    document['match_codes'] = getTokensForIndexing(components)


def getTokensForIndexing(components):
    fullDoc = ' '.join(unicode(str(c), 'utf-8') for c in components)
    tokens = (token for token in TOKENIZER(fullDoc))
    return list(set(token.text for token in NORMALIZER(tokens)))


def formatSearchQuery(queryText):
    queryText = unicode(queryText, 'utf-8')
    tokens = (token for token in TOKENIZER(queryText))
    components = []
    for token in tokens:
        normalized = set([normalized.text for normalized in NORMALIZER([token])])
        components.append({'match_codes' : {'$in' : list(normalized)}})
    return components


if __name__ == '__main__':
    from sys import argv
    print getTokensForIndexing(argv[1:])

