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
                resolutionResult[item.search_id] = (item,) + self.__convertSearchId(item.search_id, resolver)

        outputMessage = """
        /---------------------------------------------
        |    Resolution results written to:
        |      %s
        \\---------------------------------------------
        """
        with tempfile.NamedTemporaryFile(delete=False) as output:
            pickle.dump(resolutionResult, output)
            print outputMessage % output.name

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
            logs.warning('Source not found: %s (%s)' % (source_name, search_id))
            raise StampedUnavailableError

        source = sources[source_name.lower()]()
        try:
            proxy = source.entityProxyFromKey(source_id)
        except KeyError:
            raise StampedUnavailableError("Entity not found")

        entityProxy = EntityProxyContainer.EntityProxyContainer(proxy)
        entity = entityProxy.buildEntity()
        fullResolver.enrichEntity(entity, {})
        return entity, proxy


if __name__ == '__main__':
    main()
