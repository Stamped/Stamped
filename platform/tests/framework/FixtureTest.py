#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import argparse, os, sys
from utils import AttributeDict, Singleton, get_db_config
from bson import json_util
import json
from api.db.mongodb.AMongoCollection import MongoDBConfig
from libs import MongoCache
import functools
from tests.StampedTestUtils import *

__fixture_test_flags = None

def defaultFixtureFilename(testCaseInstance, testFn, fixtureType):
    testClassModuleName = testCaseInstance.__class__.__module__
    if testClassModuleName == '__main__':
        # The test class was declared in the Python file we're running, so we can get it from sys.argv[0].
        testClassFilename = sys.argv[0]
    else:
        testClassModule = sys.modules[testClassModuleName]
        testClassFilename = os.path.abspath(testClassModule.__file__)
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

def fixtureTest(useLocalDb=False,
                generateLocalDbFn=None,
                generateLocalDbQueries=None,
                fixtureText=None):
    totalFixtureSources = ((generateLocalDbFn is not None) +
                           (generateLocalDbQueries is not None) +
                           (fixtureText is not None))
    if totalFixtureSources > 1:
        raise Exception('generateLocalDbFn, generateLocalDbQueries, and fixtureText are mutually exclusive!')
    if useLocalDb and totalFixtureSources:
        raise Exception('useLocalDb is set to True, but you also provided a fixture source.')

    def decoratorFn(testFn):
        @functools.wraps(testFn)
        def runTest(self, *args, **kwargs):
            useDbFixture = __fixture_test_flags.use_db_fixture
            useCacheFixture = __fixture_test_flags.use_cache_fixture
            writeFixtureFiles = __fixture_test_flags.write_fixture_files

            dbFixtureFilename = defaultFixtureFilename(self, testFn, 'dbfixture')
            cacheFixtureFilename = defaultFixtureFilename(self, testFn, 'cachefixture')

            if not useLocalDb:
                MongoDBConfig.getInstance().database_name = 'stamped_fixtures'
                from api.db.mongodb.AMongoCollection import MongoDBConfig as MongoDBConfig2
                MongoDBConfig2.getInstance().database_name = 'stamped_fixtures'
                MongoCache.disableStaleness = True
                MongoCache.cacheTableName = 'cache_fixture'

            db = getattr(MongoDBConfig.getInstance().connection, MongoDBConfig.getInstance().database_name)
            dbDict = {}

            if not useLocalDb:
                # Some functions may want a fixture literally so simple that they can specify it as inline text -- it doesn't come
                # from the database, it doesn't need to be updated, it's just something quick and hand-written. In that case, even
                # when we're doing runs of tests that regenerate the fixtures of the test suite, for these tests we still need to
                # load fixtures as normal.
                useDbFixture = useDbFixture or (generateLocalDbFn is None and generateLocalDbQueries is None)

                # Clear out the whole test DB before running the test.
                [getattr(db, tableName).drop() for tableName in db.collection_names() if tableName != 'system.indexes']

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
            if not useDbFixture and not useLocalDb:
                [getattr(db, tableName).drop() for tableName in db.collection_names()
                 if tableName not in [MongoCache.cacheTableName, 'system.indexes']]
                pass
            if not useCacheFixture:
                getattr(db, MongoCache.cacheTableName).drop()

            # Generate the DB objects anew if we're not loading them from file.
            if not useDbFixture and not useLocalDb:
                if generateLocalDbFn is not None:
                    generateLocalDbFn()
                elif generateLocalDbQueries is not None:
                    issueQueries(generateLocalDbQueries)

            if useCacheFixture:
                MongoCache.exceptionOnCacheMiss = not __fixture_test_flags.live_calls_on_cache_miss

            # The actual DB fixtures we want to snapshot before the function runs, because we don't want to incorporate
            # anything written during the function. But the third-party calls cache we want to snapshot after the
            # function runs.
            if writeFixtureFiles and not useLocalDb:
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
                    if getattr(db, MongoCache.cacheTableName).count():
                        dumpDbDictToFilename({MongoCache.cacheTableName: list(getattr(db, MongoCache.cacheTableName).find())}, cacheFixtureFilename)

                MongoDBConfig.getInstance().database_name = 'stamped'
                from api.db.mongodb.AMongoCollection import MongoDBConfig as MongoDBConfig2
                MongoDBConfig2.getInstance().database_name = 'stamped'
                MongoCache.disableStaleness = False
                if MongoCache.cacheTableName == 'cache_fixture':
                    MongoCache.cacheTableName = 'cache'
                    db.cache_fixture.drop()

            return testResult

        return runTest

    return decoratorFn


def main():
    # Here's the awkward part -- we want to parse options from the command-line, but there's also option parsing done
    # in unittest2.main(). So we need to do something unobtrusive here.

    parser = argparse.ArgumentParser()
    parser.add_argument('--use_live_db_results', action='store_false', default=True, dest='use_db_fixture')
    parser.add_argument('--use_live_api_calls', action='store_false', default=True, dest='use_cache_fixture')
    parser.add_argument('--write_fixture_files', action='store_true', default=False)
    parser.add_argument('--live_calls_on_cache_miss',action='store_true', default=False)

    global __fixture_test_flags
    __fixture_test_flags, new_argv = parser.parse_known_args(sys.argv)
    sys.argv[:] = new_argv[:]

    StampedTestRunner().run()


# TODO: Option to do per-class fixtures rather than per-methods.
