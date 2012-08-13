#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import pickle
import re
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from collections import namedtuple
from contextlib import closing
from datetime import datetime, timedelta
from tempfile import TemporaryFile
from whoosh.analysis import *
from whoosh.support.charset import accent_map

import keys.aws
from api.db.mongodb.MongoEntityCollection import MongoEntityCollection
from libs import ec2_utils
from errors import StampedDocumentNotFoundError
from search.AutoCompleteTrie import AutoCompleteTrie

EntityTuple = namedtuple('EntityTuple', ['entity_id', 'title', 'last_popular', 'types', 'num_stamps'])

# The tokenizer breaks input text into tokens by spaces and common punctuations. The CharsetFilter
# removes any accent marks on letters, and the LowercaseFilter puts all letters to lowercase.
TOKENIZER = RegexTokenizer() | CharsetFilter(accent_map) | LowercaseFilter()

def buildAutoCompleteIndex():
    entityDb = MongoEntityCollection()
    query = {
        'sources.tombstone_id' : { '$exists':False },
        'sources.user_generated_id' : { '$exists':False },
        'schema_version' : 0,
    }
    allEntities = (convertEntity(entity, entityDb) for entity in entityDb._collection.find(
        query, fields=['title', 'last_popular', 'types']))
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
        trie.pruneAndCompress(entityScoringFn, lambda x: x.title.strip(), 5, 50)
    return categoryMapping


def convertEntity(entityDict, entityDb):
    entityId = str(entityDict.pop('_id'))
    if 'last_popular' not in entityDict:
        entityDict['last_popular'] = datetime(1, 1, 1)
    entityDict['entity_id'] = entityId
    entityDict['types'] = tuple(entityDict['types'])
    try:
        entityDict['num_stamps'] = entityDb.entity_stats.getEntityStats(entityId).num_stamps
    except (StampedDocumentNotFoundError, KeyError):
        entityDict['num_stamps'] = 0
    return EntityTuple(**entityDict)


def normalizeTitle(title):
    return ' '.join(tokenizeTitleAndNormalize(title))


def tokenizeTitleAndNormalize(title):
    # Remove apostrophes, so contractions don't get broken into two separate words.
    title = u''.join(c for c in title if c != "'")
    return [token.text for token in TOKENIZER(title)]


def entityScoringFn(entity):
    # Get a boost if it was popular in the last 30 days.
    # TODO(geoff): Need a much better ranking function
    return datetime.now() - entity.last_popular < timedelta(30), entity.num_stamps


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


def getS3Key(stack_name=None):
    stack_name = stack_name or ec2_utils.get_stack().instance.stack
    BUCKET_NAME = 'stamped.com.static.images'
    FILE_NAME = 'search/v2/autocomplete/' + stack_name

    conn = S3Connection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
    bucket = conn.create_bucket(BUCKET_NAME)
    key = bucket.get_key(FILE_NAME)
    if key is None:
        key = bucket.new_key(FILE_NAME)
    return key


def saveIndexToS3(index, stack_name=None):
    with TemporaryFile() as tmpFile:
        pickle.dump(index, tmpFile)
        tmpFile.seek(0)
        with closing(getS3Key(stack_name)) as key:
            key.set_contents_from_file(tmpFile)
            key.set_acl('private')


def pushNewIndexToS3():
    saveIndexToS3(buildAutoCompleteIndex())


def loadIndexFromS3(stack_name=None):
    with TemporaryFile() as tmpFile:
        with closing(getS3Key(stack_name)) as key:
            key.get_contents_to_file(tmpFile)
        tmpFile.seek(0)
        return pickle.load(tmpFile)


if __name__ == '__main__':
    from sys import argv
    usageString = """
    USAGE:
        AutoCompleteIndex.py build indexFileOutput
        AutoCompleteIndex.py search indexFile category searchTerm ...
        If the index filename given is "<stackname>.S3" then the index stored in S3 is used.
    """

    s3_pattern = re.compile(r'(.*)\.S3')
    if argv[1] == 'build':
        match = s3_pattern.match(argv[2])
        if match:
            saveIndexToS3(buildAutoCompleteIndex(), match.group(1))
        else:
            with open(argv[2], 'w') as fileOut:
                pickle.dump(buildAutoCompleteIndex(), fileOut)
    elif argv[1] == 'search':
        match = s3_pattern.match(argv[2])
        if match:
            categoryMapping = loadIndexFromS3(match.group(1))
        else:
            with open(argv[2]) as fileIn:
                categoryMapping = pickle.load(fileIn)
        trie = categoryMapping[argv[3]]
        for query in argv[4:]:
            print 'Suggestion results for query', query
            print trie[query]
    else:
        print usageString
