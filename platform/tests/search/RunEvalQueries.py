#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import pickle
import tempfile

from search.EntitySearch import EntitySearch
from tests.framework.FixtureTest import *

class RunEvalQueries(AStampedFixtureTestCase):
    @fixtureTest()
    def test_run_quries(self):
        queries = [
                'book i robot',
                ]

        searcher = EntitySearch()
        searchResults = {}
        for query in queries:
            searchResults[query] = self.__runSearch(query, searcher)

        outputMessage = """
        /---------------------------------------------
        |    Search results written to:
        |      %s
        \\---------------------------------------------
        """
        with tempfile.NamedTemporaryFile(delete=False) as fout:
            pickle.dump(searchResults, fout)
            print outputMessage % fout.name

    def __runSearch(self, query, searcher):
        tokens = query.split()
        assert len(tokens) > 1
        results = searcher.searchEntitiesAndClusters(tokens[0], tokens[1:])
        return [(entity.dataExport(), cluster) for entity, cluster in results]


if __name__ == '__main__':
    main()
