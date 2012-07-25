#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import report

try:
    import logs, pprint, urllib2, traceback, re, sys, time, datetime, math
    from resolve.GenericSource import GenericSource
    from utils import lazyProperty
    from gevent.pool import Pool
    from resolve.TitleUtils import *
    from resolve.ResolverObject import *
    from BeautifulSoup import BeautifulSoup, NavigableString
except:
    report()
    raise


def crawl_with_retries(url, num_attempts=3):
    time.sleep(0.1)
    attempts_remaining = 3
    while attempts_remaining:
        try:
            f = urllib2.urlopen(url)
            data = f.read()
            f.close()
            return data
        except Exception as e:
            attempts_remaining -= 1
            print 'Failed once, sleeping and retrying'
            time.sleep(1)
            if not attempts_remaining:
                traceback.print_exc()
                return None


class ImdbTvSeries(ResolverMediaCollection):
    def __init__(self, url, rank=None):
        ResolverMediaItem.__init__(self, types=['movie'], maxLookupCalls=0)
        self.__url = url
        crawl_data = crawl_with_retries(url)
        self.__data = BeautifulSoup(crawl_data)
        self.__rank = rank

    @property
    def key(self):
        return self.__url

    @property
    def source(self):
        return 'imdb'

    def __unquote(self, string):
        string = string.strip()
        if string[0] == '"' and string[-1] == '"':
            string = string[1:-1]
        return string.strip()

    def __clean(self, string):
        whitespace_re = re.compile('\s+')
        return whitespace_re.sub(' ', string)

    @lazyProperty
    def raw_name(self):
        main_details = check_exactly_one(self.__data('div', id='maindetails_center_top'))
        header = check_exactly_one(main_details('h1', {'class':'header', 'itemprop':'name'}))
        return self.__clean(' '.join(map(self.__unquote, [item for item in header.contents if isinstance(item, NavigableString)])))

    def _cleanName(self, rawName):
        return cleanTvTitle(rawName)

    @lazyProperty
    def release_date(self):
        main_details = check_exactly_one(self.__data('div', id='maindetails_center_top'))
        header = check_exactly_one(main_details('h1', {'class':'header', 'itemprop':'name'}))
        year = header('span', 'nobr').string.strip()
        assert len(year) == 6 and year[1] == '(' and year[5] == ')'
        year = int(year[1:-1])
        return datetime.datetime(year, 1, 1)

    @lazyProperty
    def last_popular(self):
        years_section = self.__data('div', id='maindetails_center_bottom')('div', 'article')[0]('div', 'txt-block')[1]
        assert check_exactly_one(years_section('h4', 'inline')).string == 'Year:'
        years_span = years_section('span')[0]
        years = []
        for link in years_span('a'):
            if link.string.strip().isdigit():
                years.append(int(link.string.strip()))
        last_year = max(years)
        return datetime.datetime(last_year, 1, 1)

    @property
    def popularity_score(self):
        if self.__rank is None:
            return 0
        return 2000.0 / ((10 + self.__rank) ** 0.7)

    @lazyProperty
    def cast(self):
        



def check_exactly_one(matches):
    assert len(matches) == 1
    return matches[0]


def crawl_url(url, results_to_process):
    data = crawl_with_retries(url)
    soup = BeautifulSoup(data)
    main_div = soup.find('div', id='root').find('div', id='pagecontent').find('div', id='main')\
    table_body = main_div.find('table', id='result').find('tbody')
    rows = main_div.findAll('tr')[1:]
    assert(len(rows) == 50)
    for row in rows[:results_to_process]:
        details_section = check_exactly_one(row('td', 'title'))
        #title = check_exactly_one(details_section('a')).string.strip()
        #description = check_exactly_one(details_section('span', 'outline')).string.strip()
        #if description and description[0] == '"' and description[-1] == '"':
        #    description = description[1:-1]
        relative_url = check_exactly_one(details_section('a'))['href']
        absolute_url = 'http://www.imdb.com' + relative_url
        # TODO: Should pull out actual ID.
        resolver_object = ImdbTvSeries(absolute_url)
        print '\n\n'
        print resolver_object
        print '\n\n'


def crawl_period(year_start, year_end, num_results):
    results_remaining = num_results
    start = 1
    while results_remaining < 0:
        url = 'http://www.imdb.com/search/title?sort=moviemeter,asc&start=%d&title_type=tv_series&year=%d,%d' % (
            start, year_start, year_end
        )
        crawl_url(url, results_remaining)
        start += 50
        results_remaining -= 50


def crawl(num_decades_to_crawl, results_per_decade):
    for i in range(1, num_decades_to_crawl+1):
        decade_start = 2012 - (10*i) + 1
        decade_end = 2012 - (10*i) + 10
        crawl_period(decade_start, decade_end, results_per_decade)


def main():
    assert len(sys.argv) == 3
    num_decades = int(sys.argv[1])
    results_per_decade = int(sys.argv[2])
    crawl(num_decades, results_per_decade)


if __name__ == '__main__':
    main()