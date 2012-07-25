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
    import logs, pprint, urllib2, traceback, re, sys, time, datetime
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


class BoxOfficeMojoMovie(ResolverMediaItem):
    def __init__(self, url):
        ResolverMediaItem.__init__(self, types=['movie'], maxLookupCalls=0)
        self.__url = url
        crawl_data = crawl_with_retries(url)
        self.__data = BeautifulSoup(crawl_data)

    @property
    def key(self):
        return self.__url

    @property
    def source(self):
        return 'boxofficemojo'

    @lazyProperty
    def raw_name(self):
        title_matches = self.__data('font', face='Verdana', size='6')
        if not title_matches:
            title_matches = self.__data('font', face='Verdana', size='5')
        assert(len(title_matches) == 1)
        bold_section = title_matches[0]('b')[0]
        if bold_section.string:
            return bold_section.string.strip()
        return ' '.join([item for item in bold_section.contents if isinstance(item, NavigableString)])

    def _cleanName(self, rawName):
        return cleanMovieTitle(rawName)

    def __find_singular_navstring_match(self, text, required=False):
        matches = self.__data.findAll(text=re.compile(text))
        if len(matches) > 1 or (required and not matches):
            raise Exception('Found wrong # matches for text: %s for BoxOfficeMojo movie at: %s' % (
                repr(text), repr(self.__url)
            ))
        if not matches:
            return None
        return matches[0]

    @lazyProperty
    def box_office_total(self):
        domestic_total_navstring = self.__find_singular_navstring_match('Domestic Total.*:')
        section = domestic_total_navstring.parent
        price_navstring_matches = section(text=re.compile('\$[0-9,]+'))
        if not price_navstring_matches:
            section = section.parent
            price_navstring_matches = section(text=re.compile('\$[0-9,]+'))

        max_price = 0
        for match in price_navstring_matches:
            max_price = max(max_price, int(match.strip()[1:].replace(',', '')))

        return max_price

        #print section
        #assert(section.name == 'font' and section['size'] == '4')
        #total_as_string = section.parent.parent('b')[0].string
        #if total_as_string[0] != '$':
        #    raise Exception('Unrecognized total_as_string %s for BoxOfficeMojo movie at %s' % (
        #        repr(total_as_string), repr(self.__url)
        #    ))

    @lazyProperty
    def release_date(self):
        release_date_navstring = self.__find_singular_navstring_match('Release Date:')
        section = release_date_navstring.parent
        print section
        assert(section.name == 'td')
        try:
            date_string = section('b')[0]('a')[0].string.strip()
        except Exception:
            try:
                date_string = section('b')[0]('nobr')[0].string.strip()
            except Exception:
                date_string = section('b')[0].string.strip()
        return datetime.datetime.strptime(date_string, '%B %d, %Y')

    @lazyProperty
    def mpaa_rating(self):
        mpaa_rating_navstring = self.__find_singular_navstring_match('MPAA Rating:', required=False)
        if not mpaa_rating_navstring:
            return None
        return mpaa_rating_navstring.parent('b')[0].string.strip()

    RUNTIME_RE = re.compile('^\s*(([0,1,2,3])\s+(hrs?\.?|hours?)\s+)?(\d{1,2})\s+(mins?\.?|minutes?)\s*$')
    @lazyProperty
    def length(self):
        runtime_navstring = self.__find_singular_navstring_match('Runtime:')
        runtime_string = runtime_navstring.parent('b')[0].string
        print 'RUNTIME STRING:', runtime_string
        match = self.RUNTIME_RE.match(runtime_string)
        if not match:
            raise Exception('Unrecognized runtime %s for BoxOfficeMojo movie at %s' % (
                repr(runtime_string), repr(self.__url)
            ))
        hours, minutes = int(match.group(2)), int(match.group(4))
        return (minutes*60) + (hours*3600)

    @lazyProperty
    def cast(self):
        cast_navstring = self.__find_singular_navstring_match('Actors:', required=False)
        if cast_navstring is None:
            return []
        possible_cast_members = cast_navstring.parent.parent.parent.parent('font')[1].contents
        cast = []
        for possible_cast_member in possible_cast_members:
            is_cast_member = possible_cast_member.__class__.__name__ == 'NavigableString'
            if (possible_cast_member.__class__.__name__ == 'Tag' and
                possible_cast_member.name == 'a' and
                '/people/chart/' in possible_cast_member['href']):
                is_cast_member = True

            if is_cast_member:
                cast.append({u'name': possible_cast_member.string.strip()})

        return cast

    @lazyProperty
    def directors(self):
        directors_navstring = self.__find_singular_navstring_match('Directors?:', required=False)
        if directors_navstring is None:
            return []
        possible_directors = directors_navstring.parent.parent.parent.parent('font')[1].contents
        directors = []
        for possible_director in possible_directors:
            is_director = possible_director.__class__.__name__ == 'NavigableString'
            if (possible_director.__class__.__name__ == 'Tag' and
                possible_director.name == 'a' and
                '/people/chart/' in possible_director['href']):
                is_director = True

            if is_director and possible_director.string.strip():
                directors.append({u'name': possible_director.string.strip()})

        return directors

    @property
    def last_popular(self):
        return self.release_date

    @lazyProperty
    def popularity_score(self):
        return correct_for_inflation(self.box_office_total, self.release_date.year) / 3000000.0



raw_inflation_numbers = """
2012	2.93 %	2.87 %	2.65 %	2.30 %	1.70 %	1.66 %
2011	1.63 %	2.11 %	2.68 %	3.16 %	3.57 %	3.56 %	3.63 %	3.77 %	3.87 %	3.53 %	3.39 %	2.96 %	3.16 %
2010	2.63 %	2.14 %	2.31 %	2.24 %	2.02 %	1.05 %	1.24 %	1.15 %	1.14 %	1.17 %	1.14 %	1.50 %	1.64 %
2009	0.03 %	0.24 %	-0.38 %	-0.74 %	-1.28 %	-1.43 %	-2.10 %	-1.48 %	-1.29 %	-0.18 %	1.84 %	2.72 %	-0.34 %
2008	4.28 %	4.03 %	3.98 %	3.94 %	4.18 %	5.02 %	5.60 %	5.37 %	4.94 %	3.66 %	1.07 %	0.09 %	3.85 %
2007	2.08 %	2.42 %	2.78 %	2.57 %	2.69 %	2.69 %	2.36 %	1.97 %	2.76 %	3.54 %	4.31 %	4.08 %	2.85 %
2006	3.99 %	3.60 %	3.36 %	3.55 %	4.17 %	4.32 %	4.15 %	3.82 %	2.06 %	1.31 %	1.97 %	2.54 %	3.24 %
2005	2.97 %	3.01 %	3.15 %	3.51 %	2.80 %	2.53 %	3.17 %	3.64 %	4.69 %	4.35 %	3.46 %	3.42 %	3.39 %
2004	1.93 %	1.69 %	1.74 %	2.29 %	3.05 %	3.27 %	2.99 %	2.65 %	2.54 %	3.19 %	3.52 %	3.26 %	2.68 %
2003	2.60 %	2.98 %	3.02 %	2.22 %	2.06 %	2.11 %	2.11 %	2.16 %	2.32 %	2.04 %	1.77 %	1.88 %	2.27 %
2002	1.14 %	1.14 %	1.48 %	1.64 %	1.18 %	1.07 %	1.46 %	1.80 %	1.51 %	2.03 %	2.20 %	2.38 %	1.59 %
2001	3.73 %	3.53 %	2.92 %	3.27 %	3.62 %	3.25 %	2.72 %	2.72 %	2.65 %	2.13 %	1.90 %	1.55 %	2.83 %
2000	2.74 %	3.22 %	3.76 %	3.07 %	3.19 %	3.73 %	3.66 %	3.41 %	3.45 %	3.45 %	3.45 %	3.39 %	3.38 %
1999	1.67 %	1.61 %	1.73 %	2.28 %	2.09 %	1.96 %	2.14 %	2.26 %	2.63 %	2.56 %	2.62 %	2.68 %	2.19 %
1998	1.57 %	1.44 %	1.37 %	1.44 %	1.69 %	1.68 %	1.68 %	1.62 %	1.49 %	1.49 %	1.55 %	1.61 %	1.55 %
1997	3.04 %	3.03 %	2.76 %	2.50 %	2.23 %	2.30 %	2.23 %	2.23 %	2.15 %	2.08 %	1.83 %	1.70 %	2.34 %
1996	2.73 %	2.65 %	2.84 %	2.90 %	2.89 %	2.75 %	2.95 %	2.88 %	3.00 %	2.99 %	3.26 %	3.32 %	2.93 %
1995	2.80 %	2.86 %	2.85 %	3.05 %	3.19 %	3.04 %	2.76 %	2.62 %	2.54 %	2.81 %	2.61 %	2.54 %	2.81 %
1994	2.52 %	2.52 %	2.51 %	2.36 %	2.29 %	2.49 %	2.77 %	2.90 %	2.96 %	2.61 %	2.67 %	2.67 %	2.61 %
1993	3.26 %	3.25 %	3.09 %	3.23 %	3.22 %	3.00 %	2.78 %	2.77 %	2.69 %	2.75 %	2.68 %	2.75 %	2.96 %
1992	2.60 %	2.82 %	3.19 %	3.18 %	3.02 %	3.09 %	3.16 %	3.15 %	2.99 %	3.20 %	3.05 %	2.90 %	3.03 %
1991	5.65 %	5.31 %	4.90 %	4.89 %	4.95 %	4.70 %	4.45 %	3.80 %	3.39 %	2.92 %	2.99 %	3.06 %	4.25 %
1990	5.20 %	5.26 %	5.23 %	4.71 %	4.36 %	4.67 %	4.82 %	5.62 %	6.16 %	6.29 %	6.27 %	6.11 %	5.39 %
1989	4.67 %	4.83 %	4.98 %	5.12 %	5.36 %	5.17 %	4.98 %	4.71 %	4.34 %	4.49 %	4.66 %	4.65 %	4.83 %
1988	4.05 %	3.94 %	3.93 %	3.90 %	3.89 %	3.96 %	4.13 %	4.02 %	4.17 %	4.25 %	4.25 %	4.42 %	4.08 %
1987	1.46 %	2.10 %	3.03 %	3.78 %	3.86 %	3.65 %	3.93 %	4.28 %	4.36 %	4.53 %	4.53 %	4.43 %	3.66 %
1986	3.89 %	3.11 %	2.26 %	1.59 %	1.49 %	1.77 %	1.58 %	1.57 %	1.75 %	1.47 %	1.28 %	1.10 %	1.91 %
1985	3.53 %	3.52 %	3.70 %	3.69 %	3.77 %	3.76 %	3.55 %	3.35 %	3.14 %	3.23 %	3.51 %	3.80 %	3.55 %
1984	4.19 %	4.60 %	4.80 %	4.56 %	4.23 %	4.22 %	4.20 %	4.29 %	4.27 %	4.26 %	4.05 %	3.95 %	4.30 %
1983	3.71 %	3.49 %	3.60 %	3.90 %	3.55 %	2.58 %	2.46 %	2.56 %	2.86 %	2.85 %	3.27 %	3.79 %	3.22 %
1982	8.39 %	7.62 %	6.78 %	6.51 %	6.68 %	7.06 %	6.44 %	5.85 %	5.04 %	5.14 %	4.59 %	3.83 %	6.16 %
1981	11.83 %	11.41 %	10.49 %	10.00 %	9.78 %	9.55 %	10.76 %	10.80 %	10.95 %	10.14 %	9.59 %	8.92 %	10.35 %
1980	13.91 %	14.18 %	14.76 %	14.73 %	14.41 %	14.38 %	13.13 %	12.87 %	12.60 %	12.77 %	12.65 %	12.52 %	13.58 %
1979	9.28 %	9.86 %	10.09 %	10.49 %	10.85 %	10.89 %	11.26 %	11.82 %	12.18 %	12.07 %	12.61 %	13.29 %	11.22 %
1978	6.84 %	6.43 %	6.55 %	6.50 %	6.97 %	7.41 %	7.70 %	7.84 %	8.31 %	8.93 %	8.89 %	9.02 %	7.62 %
1977	5.22 %	5.91 %	6.44 %	6.95 %	6.73 %	6.87 %	6.83 %	6.62 %	6.60 %	6.39 %	6.72 %	6.70 %	6.50 %
1976	6.72 %	6.29 %	6.07 %	6.05 %	6.20 %	5.97 %	5.35 %	5.71 %	5.49 %	5.46 %	4.88 %	4.86 %	5.75 %
1975	11.80 %	11.23 %	10.25 %	10.21 %	9.47 %	9.39 %	9.72 %	8.60 %	7.91 %	7.44 %	7.38 %	6.94 %	9.20 %
1974	9.39 %	10.02 %	10.39 %	10.09 %	10.71 %	10.86 %	11.51 %	10.86 %	11.95 %	12.06 %	12.20 %	12.34 %	11.03 %
1973	3.65 %	3.87 %	4.59 %	5.06 %	5.53 %	6.00 %	5.73 %	7.38 %	7.36 %	7.80 %	8.25 %	8.71 %	6.16 %
1972	3.27 %	3.51 %	3.50 %	3.49 %	3.23 %	2.71 %	2.95 %	2.94 %	3.19 %	3.42 %	3.67 %	3.41 %	3.27 %
1971	5.29 %	5.00 %	4.71 %	4.16 %	4.40 %	4.64 %	4.36 %	4.62 %	4.08 %	3.81 %	3.28 %	3.27 %	4.30 %
1970	6.18 %	6.15 %	5.82 %	6.06 %	6.04 %	6.01 %	5.98 %	5.41 %	5.66 %	5.63 %	5.60 %	5.57 %	5.84 %
1969	4.40 %	4.68 %	5.25 %	5.52 %	5.51 %	5.48 %	5.44 %	5.71 %	5.70 %	5.67 %	5.93 %	6.20 %	5.46 %
1968	3.65 %	3.95 %	3.94 %	3.93 %	3.92 %	4.20 %	4.49 %	4.48 %	4.46 %	4.75 %	4.73 %	4.72 %	4.27 %
1967	3.46 %	2.81 %	2.80 %	2.48 %	2.79 %	2.78 %	2.77 %	2.45 %	2.75 %	2.43 %	2.74 %	3.04 %	2.78 %
1966	1.92 %	2.56 %	2.56 %	2.87 %	2.87 %	2.53 %	2.85 %	3.48 %	3.48 %	3.79 %	3.79 %	3.46 %	3.01 %
1965	0.97 %	0.97 %	1.29 %	1.62 %	1.62 %	1.94 %	1.61 %	1.94 %	1.61 %	1.93 %	1.60 %	1.92 %	1.59 %
1964	1.64 %	1.64 %	1.31 %	1.31 %	1.31 %	1.31 %	1.30 %	0.98 %	1.30 %	0.97 %	1.30 %	0.97 %	1.28 %
1963	1.33 %	1.00 %	1.33 %	0.99 %	0.99 %	1.32 %	1.32 %	1.32 %	0.99 %	1.32 %	1.32 %	1.64 %	1.24 %
1962	0.67 %	1.01 %	1.01 %	1.34 %	1.34 %	1.34 %	1.00 %	1.34 %	1.33 %	1.33 %	1.33 %	1.33 %	1.20 %
1961	1.71 %	1.36 %	1.36 %	1.02 %	1.02 %	0.68 %	1.35 %	1.01 %	1.35 %	0.67 %	0.67 %	0.67 %	1.07 %
1960	1.03 %	1.73 %	1.73 %	1.72 %	1.72 %	1.72 %	1.37 %	1.37 %	1.02 %	1.36 %	1.36 %	1.36 %	1.46 %
1959	1.40 %	1.05 %	0.35 %	0.35 %	0.35 %	0.69 %	0.69 %	1.04 %	1.38 %	1.73 %	1.38 %	1.73 %	1.01 %
1958	3.62 %	3.25 %	3.60 %	3.58 %	3.21 %	2.85 %	2.47 %	2.12 %	2.12 %	2.12 %	2.11 %	1.76 %	2.73 %
1957	2.99 %	3.36 %	3.73 %	3.72 %	3.70 %	3.31 %	3.28 %	3.66 %	3.28 %	2.91 %	3.27 %	2.90 %	3.34 %
1956	0.37 %	0.37 %	0.37 %	0.75 %	1.12 %	1.87 %	2.24 %	1.87 %	1.86 %	2.23 %	2.23 %	2.99 %	1.52 %
1955	-0.74 %	-0.74 %	-0.74 %	-0.37 %	-0.74 %	-0.74 %	-0.37 %	-0.37 %	0.37 %	0.37 %	0.37 %	0.37 %	-0.28 %
1954	1.13 %	1.51 %	1.13 %	0.75 %	0.75 %	0.37 %	0.37 %	0.00 %	-0.37 %	-0.74 %	-0.37 %	-0.74 %	0.32 %
1953	0.38 %	0.76 %	1.14 %	0.76 %	1.14 %	1.13 %	0.37 %	0.75 %	0.75 %	1.12 %	0.75 %	0.75 %	0.82 %
1952	4.33 %	2.33 %	1.94 %	2.33 %	1.93 %	2.32 %	3.09 %	3.09 %	2.30 %	1.91 %	1.14 %	0.75 %	2.29 %
1951	8.09 %	9.36 %	9.32 %	9.32 %	9.28 %	8.82 %	7.47 %	6.58 %	6.97 %	6.50 %	6.88 %	6.00 %	7.88 %
1950	-2.08 %	-1.26 %	-0.84 %	-1.26 %	-0.42 %	-0.42 %	1.69 %	2.10 %	2.09 %	3.80 %	3.78 %	5.93 %	1.09 %
1949	1.27 %	1.28 %	1.71 %	0.42 %	-0.42 %	-0.83 %	-2.87 %	-2.86 %	-2.45 %	-2.87 %	-1.65 %	-2.07 %	-0.95 %
1948	10.23 %	9.30 %	6.85 %	8.68 %	9.13 %	9.55 %	9.91 %	8.89 %	6.52 %	6.09 %	4.76 %	2.99 %	7.74 %
1947	18.13 %	18.78 %	19.67 %	19.02 %	18.38 %	17.65 %	12.12 %	11.39 %	12.75 %	10.58 %	8.45 %	8.84 %	14.65 %
1946	2.25 %	1.69 %	2.81 %	3.37 %	3.35 %	3.31 %	9.39 %	11.60 %	12.71 %	14.92 %	17.68 %	18.13 %	8.43 %
1945	2.30 %	2.30 %	2.30 %	1.71 %	2.29 %	2.84 %	2.26 %	2.26 %	2.26 %	2.26 %	2.26 %	2.25 %	2.27 %
1944	2.96 %	2.96 %	1.16 %	0.57 %	0.00 %	0.57 %	1.72 %	2.31 %	1.72 %	1.72 %	1.72 %	2.30 %	1.64 %
1943	7.64 %	6.96 %	7.50 %	8.07 %	7.36 %	7.36 %	6.10 %	4.85 %	5.45 %	4.19 %	3.57 %	2.96 %	6.00 %
1942	11.35 %	12.06 %	12.68 %	12.59 %	13.19 %	10.88 %	11.56 %	10.74 %	9.27 %	9.15 %	9.09 %	9.03 %	10.97 %
1941	1.44 %	0.71 %	1.43 %	2.14 %	2.86 %	4.26 %	5.00 %	6.43 %	7.86 %	9.29 %	10.00 %	9.93 %	5.11 %
1940	-0.71 %	0.72 %	0.72 %	1.45 %	1.45 %	2.17 %	1.45 %	1.45 %	-0.71 %	0.00 %	0.00 %	0.71 %	0.73 %
1939	-1.41 %	-1.42 %	-1.42 %	-2.82 %	-2.13 %	-2.13 %	-2.13 %	-2.13 %	0.00 %	0.00 %	0.00 %	0.00 %	-1.30 %
1938	0.71 %	0.00 %	-0.70 %	-0.70 %	-2.08 %	-2.08 %	-2.76 %	-2.76 %	-3.42 %	-4.11 %	-3.45 %	-2.78 %	-2.01 %
1937	2.17 %	2.17 %	3.65 %	4.38 %	5.11 %	4.35 %	4.32 %	3.57 %	4.29 %	4.29 %	3.57 %	2.86 %	3.73 %
1936	1.47 %	0.73 %	0.00 %	-0.72 %	-0.72 %	0.73 %	1.46 %	2.19 %	2.19 %	2.19 %	1.45 %	1.45 %	1.04 %
1935	3.03 %	3.01 %	3.01 %	3.76 %	3.76 %	2.24 %	2.24 %	2.24 %	0.74 %	1.48 %	2.22 %	2.99 %	2.56 %
1934	2.33 %	4.72 %	5.56 %	5.56 %	5.56 %	5.51 %	2.29 %	1.52 %	3.03 %	2.27 %	2.27 %	1.52 %	3.51 %
1933	-9.79 %	-9.93 %	-10.00 %	-9.35 %	-8.03 %	-6.62 %	-3.68 %	-2.22 %	-1.49 %	-0.75 %	0.00 %	0.76 %	-5.09 %
1932	-10.06 %	-10.19 %	-10.26 %	-10.32 %	-10.46 %	-9.93 %	-9.93 %	-10.60 %	-10.67 %	-10.74 %	-10.20 %	-10.27 %	-10.30 %
1931	-7.02 %	-7.65 %	-7.69 %	-8.82 %	-9.47 %	-10.12 %	-9.04 %	-8.48 %	-9.64 %	-9.70 %	-10.37 %	-9.32 %	-8.94 %
1930	0.00 %	-0.58 %	-0.59 %	0.59 %	-0.59 %	-1.75 %	-4.05 %	-4.62 %	-4.05 %	-4.62 %	-5.20 %	-6.40 %	-2.66 %
1929	-1.16 %	0.00 %	-0.58 %	-1.17 %	-1.16 %	0.00 %	1.17 %	1.17 %	0.00 %	0.58 %	0.58 %	0.58 %	0.00 %
1928	-1.14 %	-1.72 %	-1.16 %	-1.16 %	-1.15 %	-2.84 %	-1.16 %	-0.58 %	0.00 %	-1.15 %	-0.58 %	-1.16 %	-1.15 %
1927	-2.23 %	-2.79 %	-2.81 %	-3.35 %	-2.25 %	-0.56 %	-1.14 %	-1.15 %	-1.14 %	-1.14 %	-2.26 %	-2.26 %	-1.92 %
1926	3.47 %	4.07 %	2.89 %	4.07 %	2.89 %	1.14 %	-1.13 %	-1.69 %	-1.13 %	-0.56 %	-1.67 %	-1.12 %	0.94 %
1925	0.00 %	0.00 %	1.17 %	1.18 %	1.76 %	2.94 %	3.51 %	4.12 %	3.51 %	2.91 %	4.65 %	3.47 %	2.44 %
1924	2.98 %	2.38 %	1.79 %	0.59 %	0.59 %	0.00 %	-0.58 %	-0.58 %	-0.58 %	-0.58 %	-0.58 %	0.00 %	0.45 %
1923	-0.59 %	-0.59 %	0.60 %	1.20 %	1.20 %	1.80 %	2.38 %	3.01 %	3.61 %	3.59 %	2.98 %	2.37 %	1.80 %
1922	-11.05 %	-8.15 %	-8.74 %	-7.73 %	-5.65 %	-5.11 %	-5.08 %	-6.21 %	-5.14 %	-4.57 %	-3.45 %	-2.31 %	-6.10 %
1921	-1.55 %	-5.64 %	-7.11 %	-10.84 %	-14.08 %	-15.79 %	-14.90 %	-12.81 %	-12.50 %	-12.06 %	-12.12 %	-10.82 %	-10.85 %
1920	16.97 %	20.37 %	20.12 %	21.56 %	21.89 %	23.67 %	19.54 %	14.69 %	12.36 %	9.94 %	7.03 %	2.65 %	15.90 %
1919	17.86 %	14.89 %	17.14 %	17.61 %	16.55 %	14.97 %	15.23 %	14.94 %	13.38 %	13.13 %	13.50 %	14.55 %	15.31 %
1918	19.66 %	17.50 %	16.67 %	12.70 %	13.28 %	13.08 %	17.97 %	18.46 %	18.05 %	18.52 %	20.74 %	20.44 %	17.26 %
1917	12.50 %	15.38 %	14.29 %	18.87 %	19.63 %	20.37 %	18.52 %	19.27 %	19.82 %	19.47 %	17.39 %	18.10 %	17.80 %
1916	2.97 %	4.00 %	6.06 %	6.00 %	5.94 %	6.93 %	6.93 %	7.92 %	9.90 %	10.78 %	11.65 %	12.62 %	7.64 %
1915	1.00 %	1.01 %	0.00 %	2.04 %	2.02 %	2.02 %	1.00 %	-0.98 %	-0.98 %	0.99 %	0.98 %	1.98 %	0.92 %
1914	2.04 %	1.02 %	1.02 %	0.00 %	2.06 %	1.02 %	1.01 %	3.03 %	2.00 %	1.00 %	0.99 %	1.00 %	1.35 %
"""

jan_data_by_year = {}

def load_inflation_information():
    lines = [line.strip() for line in raw_inflation_numbers.split('\n') if line.strip()]
    for line in lines:
        year = int(line.split()[0])
        january_rate = float(line.split()[1])
        jan_data_by_year[year] = january_rate


def correct_for_inflation(price, year):
    for i in range(year+1, 2012+1):
        price *= 1 + (jan_data_by_year[i]*0.01)
    return price

def write_page_url(page_num):
    return 'http://boxofficemojo.com/alltime/domestic.htm?page=%d&p=.htm' % page_num


def create_movie_from_url(url):
    pass

ID_IN_URL_RE=re.compile('[?&]id=([A-Za-z0-9_-]+)\.htm')

def crawl(pages_to_crawl):
    for page_num in range(1, pages_to_crawl + 1):
        page_data = crawl_with_retries(write_page_url(page_num))
        page_soup = BeautifulSoup(page_data)

        def handle_table_row(row_object):
            relative_url = row_object('td')[1]('a')[0]['href']
            match = ID_IN_URL_RE.search(relative_url)
            if match is None:
                for i in range(50):
                    print 'NO MATCH FOR ROW', row_object
                return

            absolute_url = 'http://boxofficemojo.com/movies/?page=main&id=%s.htm' % match.group(1)
            print "CRAWLING", absolute_url
            movie = BoxOfficeMojoMovie(absolute_url)
            print '\n\n\n'
            print movie
            print '\n\n\n'

        rows_handled = 0
        for row in page_soup('tr', bgcolor='#ffff99'):
            handle_table_row(row)
            rows_handled += 1
        for row in page_soup('tr', bgcolor='#f4f4ff'):
            handle_table_row(row)
            rows_handled += 1
        for row in page_soup('tr', bgcolor='#ffffff'):
            handle_table_row(row)
            rows_handled += 1

        for i in range(50):
            print('ON PAGE %d, HANDLED %d ROWS' % (page_num, rows_handled))

def main():
    load_inflation_information()
    if sys.argv[1] == 'crawl' and len(sys.argv) == 3 and sys.argv[2].isdigit():
        crawl(int(sys.argv[2]))
    elif sys.argv[1] == 'lookup' and len(sys.argv) == 3:
        resolver_object = BoxOfficeMojoMovie(sys.argv[2])
        print str(resolver_object)


if __name__ == '__main__':
    main()