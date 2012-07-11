#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import pickle
import re
import sys
import tempfile
import traceback
import pprint

from api.MongoStampedAPI import globalMongoStampedAPI
from api.HTTPSchemas import HTTPEntitySearchResultsItem
from resolve import FullResolveContainer, EntityProxyContainer
from resolve.AmazonSource import AmazonSource
from resolve.FactualSource import FactualSource
from resolve.GooglePlacesSource import GooglePlacesSource
from resolve.iTunesSource import iTunesSource
from resolve.NetflixSource import NetflixSource
from resolve.RdioSource import RdioSource
from resolve.SpotifySource import SpotifySource
from resolve.TMDBSource import TMDBSource
from resolve.TheTVDBSource import TheTVDBSource
from libs.CountedFunction import printFunctionCounts

from tests.StampedTestUtils import *
from tests.framework.FixtureTest import *

SOURCES = {
    'amazon_id' : AmazonSource(),
    'factual_id' : FactualSource(),
    'googleplaces_id' : GooglePlacesSource(),
    'itunes_id' : iTunesSource(),
    'rdio_id' : RdioSource(),
    'spotify_id' : SpotifySource(),
    'tmdb_id' : TMDBSource(),
    'thetvdb_id' : TheTVDBSource(),
    'netflix_id' : NetflixSource(),
}

OUTPUT_PREFIX = 'tmp'

class RunEvalResolutions(AStampedTestCase):
    @fixtureTest()
    def test_run_eval(self):
        with open('/tmp/resolution_eval_input') as input:
            searchResults = pickle.load(input)

        resolver = FullResolveContainer.FullResolveContainer()
        api = globalMongoStampedAPI()
        resolutionResult = {}

        formattedErrors = []

        for resultList in searchResults.itervalues():
            # TODO(geoff): dedupe the entities before resolve
            for entity, _ in resultList[:2]:
                try:
                    item = HTTPEntitySearchResultsItem()
                    item.importEntity(entity)
                    converted = self.__convertSearchId(item.search_id, resolver)
                    if converted:
                        entity, proxy = converted
                        proxyList = self.__getResolverObjects(entity)
                        resolutionResult[item.search_id] = (item, entity, proxy, proxyList)
                except Exception:
                    formattedErrors.append(traceback.format_exc())

        outputMessage = """
        /---------------------------------------------
        |    Resolution results written to:
        |      %s
        \\---------------------------------------------
        """
        with tempfile.NamedTemporaryFile(prefix=OUTPUT_PREFIX, delete=False) as output:
            pickle.dump(resolutionResult, output)
            if formattedErrors:
                print('\n\nENCOUNTERED %i ERRORS\n\n' % len(formattedErrors))
                print('\n\n'.join([''.join(formattedError) for formattedError in formattedErrors]))
                print('\n\n')
            print outputMessage % output.name

        printFunctionCounts()


    def __getResolverObjects(self, entity):
        result = []
        for sourceName, sourceObj in SOURCES.iteritems():
            sourceId = getattr(entity.sources, sourceName, None)
            if sourceId:
                result.append(sourceObj.entityProxyFromKey(sourceId))
        return result


    def __convertSearchId(self, searchId, fullResolver):
        source_name, source_id = re.match(r'^T_([A-Z]*)_([\w+-:]*)', searchId).groups()

        id_name = source_name.lower() + '_id'
        if id_name not in SOURCES:
            raise Exception('Unknow source: ' + id_name)

        source = SOURCES[id_name]
        try:
            proxy = source.entityProxyFromKey(source_id)
        except KeyError as e:
            print e
            return None

        if proxy is not None:
            entityProxy = EntityProxyContainer.EntityProxyContainer(proxy)
            entity = entityProxy.buildEntity()
            fullResolver.enrichEntity(entity, {})
            return entity, proxy


if __name__ == '__main__':
    # Hacky command line parsing. Modify argv in place, because main() will do its own parsing
    # later.
    global OUTPUT_PREFIX
    for i, arg in enumerate(sys.argv):
        if arg.startswith('--prefix'):
            if arg == '--prefix':
                OUTPUT_PREFIX = argv[i+1]
                del argv[i]
            elif arg.startswith('--prefix='):
                OUTPUT_PREFIX = arg[9:]
            del argv[i]
            break
    main()
