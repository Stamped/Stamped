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
from resolve.RdioSource import RdioSource
from resolve.SpotifySource import SpotifySource
from resolve.TMDBSource import TMDBSource
from resolve.TheTVDBSource import TheTVDBSource
from libs.CountedFunction import printFunctionCounts

from tests.framework.FixtureTest import *

class RunEvalResolutions(AStampedFixtureTestCase):
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
        with tempfile.NamedTemporaryFile(delete=False) as output:
            pickle.dump(resolutionResult, output)
            if formattedErrors:
                print('\n\nENCOUNTERED %i ERRORS\n\n' % len(formattedErrors))
                print('\n\n'.join([''.join(formattedError) for formattedError in formattedErrors]))
                print('\n\n')
            print outputMessage % output.name

        printFunctionCounts()


    def __getResolverObjects(self, entity):
        sources = {
            'amazon_id':       AmazonSource(),
            'factual_id':      FactualSource(),
            'googleplaces_id': GooglePlacesSource(),
            'itunes_id':       iTunesSource(),
            'rdio_id':         RdioSource(),
            'spotify_id':      SpotifySource(),
            'tmdb_id':         TMDBSource(),
            'thetvdb_id':      TheTVDBSource(),
        }
        result = []
        for sourceName, sourceObj in sources.iteritems():
            sourceId = getattr(entity.sources, sourceName, None)
            if sourceId:
                result.append(sourceObj.entityProxyFromKey(sourceId))
        return result


    def __convertSearchId(self, searchId, fullResolver):
        source_name, source_id = re.match(r'^T_([A-Z]*)_([\w+-:]*)', searchId).groups()

        sources = {
            'amazon':       AmazonSource,
            'factual':      FactualSource,
            'googleplaces': GooglePlacesSource,
            'itunes':       iTunesSource,
            'rdio':         RdioSource,
            'spotify':      SpotifySource,
            'tmdb':         TMDBSource,
            'thetvdb':      TheTVDBSource,
        }

        if source_name.lower() not in sources:
            raise Exception('Unknow source: ' + source_name.lower())

        source = sources[source_name.lower()]()
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
    main()
