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
        for resultList in searchResults.itervalues():
            # TODO(geoff): dedupe the entities before resolve
            for entity, _ in resultList[:5]:
                item = HTTPEntitySearchResultsItem()
                item.importEntity(entity)
                converted = self.__convertSearchId(item.search_id, resolver)
                if converted:
                    resolutionResult[item.search_id] = (item,) + converted

        outputMessage = """
        /---------------------------------------------
        |    Resolution results written to:
        |      %s
        \\---------------------------------------------
        """
        with tempfile.NamedTemporaryFile(delete=False) as output:
            pickle.dump(resolutionResult, output)
            print outputMessage % output.name

        printFunctionCounts()


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
