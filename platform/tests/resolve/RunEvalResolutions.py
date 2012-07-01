#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import pickle
import sys
import tempfile
import pprint

from resolve.FullResolveContainer import FullResolveContainer

from tests.framework.FixtureTest import *

class RunEvalResolutions(AStampedFixtureTestCase):
    @fixtureTest()
    def test_run_eval(self):
        def entityIdGen():
            index = 0
            while True:
                yield 'geoffs_entity_%d' % index
                index += 1

        with open('/tmp/resolution_eval_input') as input:
            searchResults = pickle.load(input)

        # First fill in entity ids for any entity without them. We will be matching using these ids.
        idGen = entityIdGen()
        for resultList in searchResults.itervalues():
            for entity, _ in resultList:
                if entity.entity_id is None:
                    entity.entity_id = next(idGen)
        with open('/tmp/resolution_eval_input', 'w') as output:
            pickle.dump(searchResults, output)

        fullResolver = FullResolveContainer()
        resolutionResult = {}
        for resultList in searchResults.itervalues():
            # TODO(geoff): dedupe the entities before resolve
            for entity, _ in resultList:
                originalData = entity.dataExport()
                fullResolver.enrichEntity(entity, {}, max_iterations=4)
                resolutionResult[entity.entity_id] = (originalData, entity)

        outputMessage = """
        /---------------------------------------------
        |    Resolution results written to:
        |      %s
        \\---------------------------------------------
        """
        with tempfile.NamedTemporaryFile(delete=False) as output:
            pickle.dump(resolutionResult, output)
            print outputMessage % output.name


if __name__ == '__main__':
    main()
