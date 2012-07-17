#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from tests.StampedTestUtils       import *
from tests.framework.FixtureTest  import fixtureTest
from tests.search.SearchTestsRunner import SearchTestCase, SearchTestsRunner, main
from tests.search.SearchResultMatcher import *
from tests.search.SearchResultsScorer import *

Matcher = BookResultMatcher

def makeTestCase(query, *expected_results):
    return SearchTestCase('book', query, *expected_results)

def makeSimpleTestCase(query, author=None, author_contains=None, consistent=True):
    assert (not author) or (not author_contains)
    if author is None and author_contains is None:
        return makeTestCase(query, Matcher(title=Equals(query)))
    elif author is not None:
        return makeTestCase(query, Matcher(title=Equals(query), author=Equals(author), consistent=consistent))
    else:
        return makeTestCase(query, Matcher(title=Equals(query), author=Contains(author_contains), consistent=consistent))

class BookSearchTests(SearchTestsRunner):
    
    def test_basic(self):
        """ Test basic book searches """
        
        test_cases = (
            makeTestCase('freedom', Matcher(title=Equals('freedom: a novel'))),
            makeTestCase('freedom by jonathon franzen', Matcher(title=Equals('freedom: a novel'), author=Contains('franzen'))),
            makeSimpleTestCase('of mice and men', author_contains='steinbeck', consistent=False),
            makeSimpleTestCase('1Q84', author_contains='Murakami'),
            makeTestCase('1Q84 book', Matcher(title=Equals('1Q84'), author=Contains('Murakami'))),
            makeTestCase('steve jobs biography', Matcher(title=Equals('Steve Jobs'), author=Contains('isaacson'))),
            makeTestCase('embassytown china', Matcher(title=Equals('embassytown'), author=Contains('china'))),
            makeSimpleTestCase('baking made easy', author_contains='pascale'),
            makeSimpleTestCase('bossypants', author='tina fey'),
            makeSimpleTestCase('the immortal life of henrietta lacks', author_contains='skloot'),
            makeTestCase('henrietta lacks',
                Matcher(title=Equals('the immortal life of henrietta lacks'), author=Contains('skloot'))),
            makeTestCase('immortal henrietta',
                Matcher(title=Equals('the immortal life of henrietta lacks'), author=Contains('skloot'))),
            makeTestCase('the girl who kicked the hornet\'s nest',
                Matcher(title=LooselyEquals('the girl who kicked the hornet\'s nest'), author=Equals('stieg larsson'))),
            makeTestCase('girl kicks hornets nest',
                Matcher(title=LooselyEquals('the girl who kicked the hornet\'s nest'), author=Equals('stieg larsson'))),
            makeTestCase('girl kicks hornets nest',
                Matcher(title=LooselyEquals('the girl who kicked the hornet\'s nest'), author=Equals('stieg larsson'))),
            makeSimpleTestCase('the boy who harnessed the wind', author_contains='Kamkwamba'),
            makeSimpleTestCase('the girl who played with fire', author='stieg larsson'),
            makeSimpleTestCase('the help', author_contains='stockett'),
            makeSimpleTestCase('the fault in our starts', author='john green'),
            makeTestCase('lord of flies', Matcher(title=Equals('lord of the flies'), author=Contains('golding'))),
            makeTestCase('amrar', Matcher(title=Equals('amrar va lukhar'), author=Contains('kaziev'))),
            makeSimpleTestCase('freakonomics'),
            makeSimpleTestCase('hamlet'),
        )

        self._run_tests('book_tests', test_cases[7:])

if __name__ == '__main__':
    main()
