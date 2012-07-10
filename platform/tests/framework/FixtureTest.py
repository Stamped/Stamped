#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import os, sys
from utils import AttributeDict, Singleton, get_db_config
from bson import json_util
import json
from api.db.mongodb.AMongoCollection import MongoDBConfig
from tests.StampedTestUtils import *
from libs import MongoCache
import functools


class AStampedFixtureTestCase(AStampedTestCase):
    """
    Base class for tests intending to use test fixtures.
    """

    @classmethod
    def setUpClass(cls):
        MongoDBConfig.getInstance().database_name = 'stamped_fixtures'
        from api.db.mongodb.AMongoCollection import MongoDBConfig as MongoDBConfig2
        MongoDBConfig2.getInstance().database_name = 'stamped_fixtures'
        MongoCache.disableStaleness = True
        
        db = getattr(MongoDBConfig.getInstance().connection, MongoDBConfig.getInstance().database_name)
        [getattr(db, tableName).drop() for tableName in db.collection_names() if tableName != 'system.indexes']

    @classmethod
    def tearDownClass(cls):
        # Put things back the way they were in case another test needs to hit the real database.
        MongoDBConfig.getInstance().database_name = 'stamped'
        from api.db.mongodb.AMongoCollection import MongoDBConfig as MongoDBConfig2
        MongoDBConfig2.getInstance().database_name = 'stamped'
        MongoCache.disableStaleness = False


class FixtureTestRuntimeSettings(Singleton):
    def __init__(self):
        self.useDbFixture = True
        self.useCacheFixture = True
        self.writeFixtureFiles = False
        self.liveCallsOnCacheMiss = False


def defaultFixtureFilename(testCaseInstance, testFn, fixtureType):
    testClassModuleName = testCaseInstance.__class__.__module__
    if testClassModuleName == '__main__':
        # The test class was declared in the Python file we're running, so we can get it from sys.argv[0].
        testClassFilename = sys.argv[0]
    else:
        testClassModule = sys.modules[testClassModuleName]
        testClassFilename = os.path.abspath(sys.modules[testClassModule].__file__)
    fixtureFilenameBase = testClassFilename[:testClassFilename.rfind(".")]
    funcName = testFn.func_name
    result = '%s.%s.%s.json' % (fixtureFilenameBase, funcName, fixtureType)
    return result

def loadTestDbDataFromText(text):
    db = getattr(MongoDBConfig.getInstance().connection, MongoDBConfig.getInstance().database_name)
    dbDict = json.loads(text, object_hook=json_util.object_hook)
    for (tableName, tableContents) in dbDict.items():
        if tableContents:
            batchSize = 20
            curr = 0
            while curr < len(tableContents):
                nextCurr = curr + batchSize
                currBatch = tableContents[curr:nextCurr]
                getattr(db, tableName).insert(currBatch)
                curr = nextCurr

def loadTestDbDataFromFilename(filename):
    fileHandle = open(filename)
    contents = fileHandle.read()
    fileHandle.close()
    loadTestDbDataFromText(contents)

def issueQueries(queries):
    # TODO: Pull this out to a named constant somewhere, or be more intelligent about this, or something.
    config = { 'mongodb' : { 'hosts': [get_db_config('peach.db3')] } }
    devDbConfig = MongoDBConfig()
    devDbConfig.config = AttributeDict(config)
    devDb = devDbConfig.connection.stamped
    # TODO: This whole "stamped_fixtures" thing really needs to be a constant.
    localDb = MongoDBConfig.getInstance().connection.stamped_fixtures
    for (collectionName, query) in queries:
        devCollection = getattr(devDb, collectionName)
        results = list(devCollection.find(query))
        localCollection = getattr(localDb, collectionName)
        localCollection.insert(results)

def dumpDbDictToFilename(dbDict, fileName):
    """
    Takes a dictionary mapping collection names to lists of collection objects and dumps it to a JSON file at the given
    filename.
    """
    dbAsJson = json.dumps(dbDict, default=json_util.default)
    fileOut = open(fileName, 'w')
    fileOut.write(dbAsJson)
    fileOut.close()

def fixtureTest(generateLocalDbFn=None,
                generateLocalDbQueries=None,
                fixtureText=None):
    totalFixtureSources = ((generateLocalDbFn is not None) +
                           (generateLocalDbQueries is not None) +
                           (fixtureText is not None))
    if totalFixtureSources > 1:
        raise Exception('generateLocalDbFn, generateLocalDbQueries, and fixtureText are mutually exclusive!')

    def decoratorFn(testFn):

        @functools.wraps(testFn)
        def runTest(self, *args, **kwargs):
            useDbFixture = FixtureTestRuntimeSettings.getInstance().useDbFixture
            useCacheFixture = FixtureTestRuntimeSettings.getInstance().useCacheFixture
            writeFixtureFiles = FixtureTestRuntimeSettings.getInstance().writeFixtureFiles

            db = getattr(MongoDBConfig.getInstance().connection, MongoDBConfig.getInstance().database_name)

            # Some functions may want a fixture literally so simple that they can specify it as inline text -- it doesn't come
            # from the database, it doesn't need to be updated, it's just something quick and hand-written. In that case, even
            # when we're doing runs of tests that regenerate the fixtures of the test suite, for these tests we still need to
            # load fixtures as normal.
            useDbFixture = useDbFixture or (generateLocalDbFn is None and generateLocalDbQueries is None)

            dbFixtureFilename = defaultFixtureFilename
            # Clear out the whole test DB before running the test.
            [getattr(db, tableName).drop() for tableName in db.collection_names() if tableName != 'system.indexes']

            dbDict = {}

            dbFixtureFilename = defaultFixtureFilename(self, testFn, 'dbfixture')
            cacheFixtureFilename = defaultFixtureFilename(self, testFn, 'cachefixture')

            if useDbFixture or useCacheFixture:
                if fixtureText is not None:
                    loadTestDbDataFromText(fixtureText)
                else:
                    try:
                        loadTestDbDataFromFilename(dbFixtureFilename)
                    except IOError:
                        # We wanted to use a fixture, but we didn't find one. In this case we just decide to fall back
                        # to generating data if either a function or query to do so is provided. If neither is provided,
                        # we assume that this function doesn't touch the database at all.
                        useDbFixture = False

            if useCacheFixture:
                try:
                    loadTestDbDataFromFilename(cacheFixtureFilename)
                except IOError:
                    useCacheFixture = False

            # Take anything out of the database that we don't want.
            if not useDbFixture:
                # TODO: 'cache' should really be a constant somewhere rather than being hard-coded all over the
                # place.
                [getattr(db, tableName).drop() for tableName in db.collection_names()
                 if tableName not in ['cache', 'system.indexes']]
                pass
            if not useCacheFixture:
                db.cache.drop()

            # Generate the DB objects anew if we're not loading them from file.
            if not useDbFixture:
                if generateLocalDbFn is not None:
                    generateLocalDbFn()
                elif generateLocalDbQueries is not None:
                    issueQueries(generateLocalDbQueries)

            if useCacheFixture:
                MongoCache.exceptionOnCacheMiss = not FixtureTestRuntimeSettings.getInstance().liveCallsOnCacheMiss

            # The actual DB fixtures we want to snapshot before the function runs, because we don't want to incorporate
            # anything written during the function. But the third-party calls cache we want to snapshot after the
            # function runs.
            if writeFixtureFiles:
                for tableName in db.collection_names():
                    if tableName not in ['cache', 'system.indexes']:
                        dbDict[tableName] = list(getattr(db, tableName).find())

            try:
                testResult = testFn(self, *args, **kwargs)
            finally:
                # Clean up after ourselves.
                MongoCache.exceptionOnCacheMiss = False
                if writeFixtureFiles:
                    dumpDbDictToFilename(dbDict, dbFixtureFilename)
                    if db.cache.count():
                        dumpDbDictToFilename({'cache': list(db.cache.find())}, cacheFixtureFilename)

            return testResult

        return runTest

    return decoratorFn


def main():
    # Here's the awkward part -- we want to parse options from the command-line, but there's also option parsing done
    # in unittest2.main(). So we need to do something unobtrusive here.

    argv = sys.argv

    # Generate live DB data rather than using saved fixtures.
    liveDbResultsFlag = '--use_live_db_results'
    if liveDbResultsFlag in argv:
        del argv[argv.index(liveDbResultsFlag)]
        print "Skipping DB fixture"
        FixtureTestRuntimeSettings.getInstance().useDbFixture = False

    # Get live results from third-party APIs rather than using saved fixtures.
    liveApiCallsFlag = "--use_live_api_calls"
    if liveApiCallsFlag in argv:
        del argv[argv.index(liveApiCallsFlag)]
        print "Skipping cache fixture"
        FixtureTestRuntimeSettings.getInstance().useCacheFixture = False

    # Regenerate fixture files.
    writeFixtureFilesFlag = '--write_fixture_files'
    if writeFixtureFilesFlag in argv:
        del argv[argv.index(writeFixtureFilesFlag)]
        FixtureTestRuntimeSettings.getInstance().writeFixtureFiles = True

    liveCallsOnCacheMissFlag = '--live_calls_on_cache_miss'
    if liveCallsOnCacheMissFlag in argv:
        del argv[argv.index(liveCallsOnCacheMissFlag)]
        FixtureTestRuntimeSettings.getInstance().liveCallsOnCacheMiss = True

    StampedTestRunner().run()


# TODO: Option to do per-class fixtures rather than per-methods.
