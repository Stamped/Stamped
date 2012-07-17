#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import pickle
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from collections import namedtuple
from contextlib import closing
from datetime import datetime
from tempfile import TemporaryFile
from whoosh.analysis import *
from whoosh.support.charset import accent_map

import keys.aws
from api.db.mongodb.MongoEntityCollection import MongoEntityCollection
from search.AutoCompleteTrie import AutoCompleteTrie

EntityTuple = namedtuple('EntityTuple', ['entity_id', 'title', 'last_popular', 'types'])
TOKENIZER = RegexTokenizer() | CharsetFilter(accent_map) | LowercaseFilter()

def normalizeTitle(title):
    return ' '.join(tokenizeTitleAndNormalize(title))

def tokenizeTitleAndNormalize(title):
    tokens = [token.text for token in TOKENIZER(title)]
    while True:
        try:
            index = tokens.index('s', 1)
        except ValueError:
            break
        tokens[index-1] = tokens[index-1] + 's'
        del tokens[index]
    return tokens

def entityScoringFn(entity, prefix):
    # TODO(geoff): factor in how many stamps are on the entity
    return entity.last_popular

def convertEntity(entityDict):
    if 'last_popular' not in entityDict:
        entityDict['last_popular'] = datetime(1, 1, 1)
    entityDict['entity_id'] = str(entityDict.pop('_id'))
    entityDict['types'] = tuple(entityDict['types'])
    return EntityTuple(**entityDict)


def categorizeEntity(entity):
    if 'album' in entity.types or 'track' in entity.types or 'artist' in entity.types:
        return 'music'
    if 'book' in entity.types:
        return 'book'
    if 'movie' in entity.types or 'tv' in entity.types:
        return 'film'
    if 'app' in entity.types:
        return 'app'


def emptyIndex():
    return dict([(category, AutoCompleteTrie()) for category in ('music', 'book', 'film', 'app')])


def buildAutoCompleteIndex():
    entityDb = MongoEntityCollection()
    allEntities = (convertEntity(entity) for entity in entityDb._collection.find(
        fields=['title', 'last_popular', 'types']))
    categoryMapping = emptyIndex()
    for entity in allEntities:
        category = categorizeEntity(entity)
        if not category:
            continue
        tokens = tokenizeTitleAndNormalize(entity.title)
        trie = categoryMapping[category]
        while tokens:
            trie.addBinding(' '.join(tokens), entity)
            if tokens[0] in STOP_WORDS:
                tokens = tokens[1:]
            else:
                break
    for trie in categoryMapping.itervalues():
        trie.pruneAndCompress(entityScoringFn, 5, 50)
        trie.modify(lambda x: x.title)
    return categoryMapping


def getS3Key():
    BUCKET_NAME = 'stamped.com.static.images'
    FILE_NAME = 'search/v2/autocomplete'

    conn = S3Connection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
    bucket = conn.create_bucket(BUCKET_NAME)
    key = bucket.get_key(FILE_NAME)
    if key is None:
        key = bucket.new_key(FILE_NAME)
    return key


def saveIndexToS3(index):
    with TemporaryFile() as tmpFile:
        pickle.dump(index, tmpFile)
        tmpFile.seek(0)
        with closing(getS3Key()) as key:
            key.set_contents_from_file(tmpFile)
            key.set_acl('private')


def loadIndexFromS3():
    with TemporaryFile() as tmpFile:
        with closing(getS3Key()) as key:
            key.get_contents_to_file(tmpFile)
        tmpFile.seek(0)
        return pickle.load(tmpFile)


if __name__ == '__main__':
    from sys import argv
    usageString = """
    USAGE:
        AutoCompleteIndex.py build indexFileOutput
        AutoCompleteIndex.py search indexFile category searchTerm ...
        If the index filename given is "S3" then the index stored in S3 is used.
    """

    if argv[1] == 'build':
        if argv[2] == 'S3':
            saveIndexToS3(buildAutoCompleteIndex())
        else:
            with open(argv[2], 'w') as fileOut:
                pickle.dump(buildAutoCompleteIndex(), fileOut)
    elif argv[1] == 'search':
        if argv[2] == 'S3':
            categoryMapping = loadIndexFromS3()
        else:
            with open(argv[2]) as fileIn:
                categoryMapping = pickle.load(fileIn)
        trie = categoryMapping[argv[3]]
        for query in argv[4:]:
            print 'Suggestion results for query', query
            print trie[query]
    else:
        print usageString
