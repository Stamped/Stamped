#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import argparse
import inspect
import os
import pickle
import re
import sys
import tempfile
import traceback
import pprint

from api.MongoStampedAPI import globalMongoStampedAPI
from api.HTTPSchemas import HTTPEntitySearchResultsItem
from resolve import FullResolveContainer, EntityProxyContainer, EntityProxySource
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

FLAGS = None

class RunEvalResolutions(AStampedTestCase):
    @fixtureTest(useLocalDb=True)
    def test_run_app_resolution(self):
        self.__run_eval_for_category('app')

    @fixtureTest(useLocalDb=True)
    def test_run_book_resolution(self):
        self.__run_eval_for_category('book')

    @fixtureTest(useLocalDb=True)
    def test_run_film_resolution(self):
        self.__run_eval_for_category('film')

    @fixtureTest(useLocalDb=True)
    def test_run_music_resolution(self):
        self.__run_eval_for_category('music')

    @fixtureTest(useLocalDb=True)
    def test_run_place_resolution(self):
        self.__run_eval_for_category('place')

    @fixtureTest(useLocalDb=True)
    def test_run_all_resolution(self):
        self.__run_eval_for_category('all')

    def __get_search_ids_for_category(self, category):
        scriptDir = os.path.dirname(inspect.getfile(inspect.currentframe()))
        filename = os.path.join(scriptDir, category + '_search_ids')
        with open(filename) as fin:
            return filter(None, (line.strip() for line in fin))

    def __run_eval_for_category(self, category):
        if category == 'all':
            categories = ('app', 'book', 'film', 'music', 'place')
            searchIds = []
            for cat in categories:
                searchIds.extend(self.__get_search_ids_for_category(cat))
        else:
            searchIds = self.__get_search_ids_for_category(category)

        resolutionResult = {}
        formattedErrors = []
        resolver = FullResolveContainer.FullResolveContainer()
        for searchId in searchIds:
            try:
                entity, original = self.__convertSearchId(searchId, resolver)
                proxyList = self.__getResolverObjects(entity)
                resolutionResult[searchId] = (entity, original, proxyList)
            except Exception:
                formattedErrors.append(traceback.format_exc())

        printFunctionCounts()

        outputMessage = """
        /---------------------------------------------
        |    Resolution results for %s written to:
        |      %s
        \\---------------------------------------------
        """
        tmpPrefix = category + '-' + FLAGS.output_prefix
        with tempfile.NamedTemporaryFile(prefix=tmpPrefix, delete=False) as output:
            pickle.dump(resolutionResult, output)
            if formattedErrors:
                print('\n\nENCOUNTERED %i ERRORS\n\n' % len(formattedErrors))
                print('\n\n'.join([''.join(formattedError) for formattedError in formattedErrors]))
                print('\n\n')
            print outputMessage % (category, output.name)



    def __getResolverObjects(self, entity):
        result = []
        for sourceName, sourceObj in SOURCES.iteritems():
            sourceId = getattr(entity.sources, sourceName, None)
            if sourceId:
                result.append(sourceObj.entityProxyFromKey(sourceId))
        return result

    def __convertSearchId(self, searchId, fullResolver):
        temp_id_prefix = 'T_'
        id_components = searchId[len(temp_id_prefix):].split('____')
        sourceAndKeyRe = re.compile('^([A-Z]+)_([\w+-:/]+)$')
        sourcesAndKeys = []
        for component in id_components:
            match = sourceAndKeyRe.match(component)
            if not match:
                logs.warning('Unable to parse search ID component:' + component)
            else:
                sourcesAndKeys.append(match.groups())
        if not sourcesAndKeys:
            raise Exception('Unable to extract and third-party ID from composite search ID: ' + searchId)

        proxies = []
        seenSourceNames = set()
        entity_ids = []
        for sourceIdentifier, key in sourcesAndKeys:
            if sourceIdentifier in seenSourceNames:
                continue
            seenSourceNames.add(sourceIdentifier)

            source = SOURCES[sourceIdentifier.lower() + '_id']
            try:
                proxy = source.entityProxyFromKey(key)
                proxies.append(proxy)
            except KeyError:
                raise Exception('Failed to load key %s from source %s; exception body:\n%s' %
                             (key, sourceIdentifier, traceback.format_exc()))

        if not proxies:
            raise Exception('Completely unable to create entity from search ID: ' + searchId)

        entity = EntityProxyContainer.EntityProxyContainer().addAllProxies(proxies).buildEntity()
        entity.third_party_ids = id_components
        original = entity.dataExport()

        fullResolver.enrichEntity(entity, {})
        return entity, original


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prefix', action='store', default='tmp', dest='output_prefix')
    FLAGS, new_argv = parser.parse_known_args(sys.argv)
    sys.argv[:] = new_argv[:]

    main()
