#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from mock import Mock
from resolve.TitleUtils import *
from tests.StampedTestUtils import *

class TitleUtilsTest(AStampedTestCase):
    def test_convert_ending_roman_numerals(self):
        self.assertEqual(convertRomanNumerals("Godfather III"), "Godfather 3")
        self.assertEqual(convertRomanNumerals("Godfather III: the movie"), "Godfather 3: the movie")
        self.assertEqual(convertRomanNumerals("Godfather III the movie"), "Godfather III the movie")
        self.assertEqual(convertRomanNumerals("Godfather iii  : the movie"), "Godfather 3  : the movie")
        self.assertEqual(convertRomanNumerals("Godfather iv"), "Godfather 4")
        self.assertEqual(convertRomanNumerals("Godfather iv: part vii"), "Godfather 4: part 7")

    def test_clean_book_title(self):
        self.assertEqual(cleanBookTitle("Kate Spade (limited edition)"), "Kate Spade")
        self.assertEqual(cleanBookTitle("Kate Spade [limited edition]"), "Kate Spade")
        self.assertEqual(cleanBookTitle("Edition edition (limited edition)"), "Edition edition")
        self.assertEqual(cleanBookTitle("Kate Spade (book 1)"), "Kate Spade")
        self.assertEqual(cleanBookTitle("Kate Spade (signet books)"), "Kate Spade")
        self.assertEqual(cleanBookTitle("Kate Spade (paperback)"), "Kate Spade")
        self.assertEqual(cleanBookTitle("Kate Spade (3-volume set)"), "Kate Spade")
        self.assertEqual(cleanBookTitle("Kate Spade [book 1] (volume 2) (keep this)"), "Kate Spade (keep this)")

    def test_clean_movie_title(self):
        self.assertEqual(cleanMovieTitle("2012 (2010)"), "2012")
        self.assertEqual(cleanMovieTitle("2012 HD"), "2012")
        self.assertEqual(cleanMovieTitle("2012: BluRay Version HD BluRay"), "2012")
        self.assertEqual(cleanMovieTitle("The Godfather: the something restoration"), "The Godfather")
        self.assertEqual(cleanMovieTitle("Spirited Away, Digitally Remastered"), "Spirited Away")

    def test_clean_tv_title(self):
        # self.assertEqual(cleanTvTitle("Lost : Season 2"), "Lost")
        # self.assertEqual(cleanTvTitle("The Complete Lost"), "Lost")
        self.assertEqual(cleanTvTitle("Completely Lost"), "Completely Lost")
        # self.assertEqual(cleanTvTitle("Lost, Volumn 2"), "Lost")

    def __check_quality_tests_applied(self, title, query, testFn, score):
        mockResolver = Mock()
        mockResolver.name = title
        mockResult = Mock()
        mockResult.resolverObject = mockResolver
        mockResult.dataQuality = 1.0
        testFn(mockResult, query)
        self.assertAlmostEqual(mockResult.dataQuality, score)

    def test_book_title_quality(self):
        self.__check_quality_tests_applied(
                'Stamped: super edition book 2 of something trilogy',
                'stamped',
                applyBookTitleDataQualityTests,
                0.75 * 0.75 * 0.9)
        self.__check_quality_tests_applied(
                'Stamped: super edition book 2 of something trilogy',
                'trilogy',
                applyBookTitleDataQualityTests,
                0.75 * 0.75)
        self.__check_quality_tests_applied(
                'Stamped: super edition book 2 of something trilogy',
                'book 2 trilogy',
                applyBookTitleDataQualityTests,
                0.75)
        self.__check_quality_tests_applied(
                'Stamped: the complete book collection',
                'book 2 trilogy',
                applyBookTitleDataQualityTests,
                0.75 * 0.9)
        self.__check_quality_tests_applied(
                'Stamped: boxed set',
                'stamped',
                applyBookTitleDataQualityTests,
                0.75 * 0.75)
        self.__check_quality_tests_applied(
                'Stamped: boxed set',
                'boxed',
                applyBookTitleDataQualityTests,
                0.75)

    def test_movie_title_quality(self):
        self.__check_quality_tests_applied(
                'The complete stamped story season 3',
                'stamped',
                applyMovieTitleDataQualityTests,
                0.65 * 0.5)
        self.__check_quality_tests_applied(
                'The complete stamped story season 3',
                'season',
                applyMovieTitleDataQualityTests,
                0.65)
 
if __name__ == '__main__':
    StampedTestRunner().run()

