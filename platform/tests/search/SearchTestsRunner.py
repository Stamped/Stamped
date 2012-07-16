#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import os, sys, re, functools
from gevent.pool import Pool
from search.EntitySearch import EntitySearch
from tests.search.SearchResultsScorer import ExpectedResults, SearchResultsScorer

class SearchTestCase(object):
    def __init__(self, category, query, *result_matchers):
        self.category = category
        if isinstance(query, basestring):
            self.query = query
            self.query_kwargs = {}
        else:
            assert(isinstance(query, dict))
            self.query = query.pop('query')
            self.query_kwargs = query
        self.expected_results = ExpectedResults(result_matchers)

    def simple_repr(self):
        return '(%s, %s, %s)' % (repr(self.category), repr(self.query), repr(self.query_kwargs))

    def __repr__(self):
        return '(%s, %s, %s, [%s])' % (
            repr(self.category),
            repr(self.query),
            repr(self.query_kwargs),
            ', '.join([repr(expected_result) for expected_result in self.expected_results])
        )


class TestResultsFile(object):
    def __init__(self, test_class, test_name):
        self.__test_class = test_class
        self.__test_name = test_name
        class_module_name = test_class.__module__
        if class_module_name == '__main__':
            class_filename = sys.argv[0]
        else:
            class_filename = os.path.abspath(sys.modules[class_module_name].__file__)
        self.__filename = '%s.%s.results' % (class_filename, test_name)

    def write_results(self, test_cases_and_scores):
        fout = open(self.__filename, 'w')
        for test_case, score in test_cases_and_scores:
            fout.write('%f --- %s\n' % (score, repr(test_case)))
        fout.close()

    RESULT_LINE_RE = re.compile('([0-9.-]+) --- (.+)\n$')
    def read_results_for_test_cases(self, test_cases):
        reprs_to_test_case_idxs = dict([(repr(test_case), idx) for idx, test_case in enumerate(test_cases)])
        results = [None] * len(test_cases)
        fin = open(self.__filename)
        lines = fin.readlines()
        old_unmatched = 0
        for line in lines:
            if not line.strip():
                continue
            match = RESULT_LINE_RE.match(line)
            if not match:
                raise Exception('Unrecognized line in test results file %s:%s' % (self.__filename, repr(line)))
            score = float(match.group(1))
            test_case_repr = match.group(2)
            idx = reprs_to_test_case_idxs.get(test_case_repr, None)
            if idx is None:
                old_unmatched += 1
            if results[idx] is not None:
                raise Exception('Received multiple entries for test case repr: ' + test_case_repr)
            results[idx] = score
        new_unmatched = len(result for result in results if result is None)
        if new_unmatched or old_unmatched:
            print 'For test %s.%s, unable to find matches for %d old tests and %d new tests.' % (
                self.__test_class, self.__test_name, old_unmatched, new_unmatched
            )
        return results



record_results = False

class SearchTestsRunner(object):
    def _run_tests(self, test_set_name, test_cases):
        test_case_outcomes = [None] * len(test_cases)
        search = EntitySearch()
        scorer = SearchResultsScorer()

        results_file = TestResultsFile(self.__class__, test_set_name)
        try:
            previous_scores = results_file.read_results_for_test_cases(test_cases)
        except Exception:
            previous_scores = None

        def run_test_case(test_case_idx):
            test_case = test_cases[test_case_idx]
            results = search.searchEntitiesAndClusters(test_case.category, test_case.query, **test_case.query_kwargs)
            score, errors = scorer.score_results(test_case.expected_results, results)
            test_case_outcomes[test_case_idx] = (score, errors)

        pool = Pool(3)
        for i in range(len(test_cases)):
            pool.spawn_link_exception(run_test_case, i)
        pool.join()

        print '\nRUNNING TEST SUITE: %s.%s\n' % (self.__class__.__name__, test_set_name)

        for i in range(len(test_cases)):
            previous_score = None if previous_scores is None else previous_scores[i]
            test_case = test_cases[i]
            score, errors = test_case_outcomes[i]
            if previous_score is None:
                status_string = 'NEW'
            elif abs(previous_score - score) < 0.00001:
                status_string = 'UNCHANGED'
            elif previous_score > score:
                status_string = 'REGRESSED'
            else:
                status_string = 'IMPROVED'
            if not errors:
                print '%s   :   %f (%s)  ...  PASS' % (test_case.simple_repr(), score, status_string)
            else:
                print '%s   :   %f (%s)  ...  %d ERRORS\n%s' % (
                    test_case.simple_repr(),
                    score,
                    status_string,
                    len(errors),
                    '\n'.join('    ' + error for error in errors)
                )