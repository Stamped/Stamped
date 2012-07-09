#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import sys
print 'hi'
sys.stdout.flush()
import Globals
print 'try again'
from logs import report

try:
    from resolve.FullResolveContainer   import FullResolveContainer
    from tests.AStampedAPIHttpTestCase            import *
    from api.Schemas                    import Entity
    from pprint                         import pformat
    from datetime                       import datetime
except:
    report()
    raise

_verbose = False

_now = datetime.utcnow()

_cases = [
    (
        {
            "subcategory" : "restaurant",
            "title" : "Olives",
            "coordinates" : {
                "lat" : 40.736623,
                "lng" : -73.988658
            },
        },
        {'category': 'place',
         'coordinates': {'lat': 40.736623, 'lng': -73.988658},
         'details': {'contact': {'phone': u'(212) 353-8345',
                                 'phone_source': 'factual',
                                 'phone_timestamp': _now,
                                 'site': u'http://www.toddenglish.com/',
                                 'site_source': 'googleplaces',
                                 'site_timestamp': _now},
                     'place': {'address_country': u'US',
                               'address_locality': u'New York',
                               'address_postcode': u'10003',
                               'address_region': u'NY',
                               'address_source': 'factual',
                               'address_street': u'201 Park Ave S',
                               'address_timestamp': _now}},
         'sources': {'factual': {'factual_id': u'dde8bf50-d829-012e-561a-003048cad9da',
                                 'factual_source': 'factual',
                                 'factual_timestamp': _now},
                     'singleplatform': {'singleplatform_id': u'olives-18',
                                        'singleplatform_source': 'factual',
                                        'singleplatform_timestamp': _now}},
         'subcategory': 'restaurant',
         'title': 'Olives'},
    ),
    (
        {
            "subcategory" : "restaurant",
            "title" : "Peter Luger Steak House",
            "coordinates" : {
                "lat" : 40.709982,
                "lng" : -73.962501
            },
        },
        {'category': 'place',
         'coordinates': {'lat': 40.709982, 'lng': -73.962501},
         'details': {'contact': {'phone': u'(718) 387-7400',
                                 'phone_source': 'factual',
                                 'phone_timestamp': _now,
                                 'site': u'http://www.peterluger.com/',
                                 'site_source': 'factual',
                                 'site_timestamp': _now},
                     'place': {'address_country': u'US',
                               'address_locality': u'Brooklyn',
                               'address_postcode': u'11211',
                               'address_region': u'NY',
                               'address_source': 'factual',
                               'address_street': u'178 Broadway',
                               'address_timestamp': _now},
                     'restaurant': {'cuisine': u'Steak, American',
                                    'cuisine_source': 'factual',
                                    'cuisine_timestamp': _now,
                                    'price_range': 4,
                                    'price_range_source': 'factual',
                                    'price_range_timestamp': _now}},
         'sources': {'factual': {'factual_id': u'5af9664f-8307-4964-98b9-bce2a55c5c3f',
                                 'factual_source': 'factual',
                                 'factual_timestamp': _now},
                     'singleplatform': {'singleplatform_id': u'peter-luger-steakhouse-2',
                                        'singleplatform_source': 'factual',
                                        'singleplatform_timestamp': _now}},
         'subcategory': 'restaurant',
         'title': 'Peter Luger Steak House'}
    ),
    (
        {
            "subcategory" : "movie",
            "title" : "Up",
            "sources" : {
            },
            "details" : {
                "media" : {
                    "original_release_date" : "2009-05-29T07:00:00Z",
                    "copyright" : "Disney",
                    "artist_display_name" : "Pixar",
                    "mpaa_rating" : "PG",
                    "genre" : "Kids & Family",
                },
            },
        },
        {'category': 'film',
         'details': {'media': {'artist_display_name': 'Pixar',
                               'copyright': 'Disney',
                               'genre': 'Kids & Family',
                               'mpaa_rating': 'PG',
                               'original_release_date': '2009-05-29T07:00:00Z',
                               'release_date': datetime(2009, 5, 29, 0, 0),
                               'release_date_source': 'format',
                               'release_date_timestamp': _now}},
         'sources': {'tmdb': {'tmdb_id': '14160',
                              'tmdb_source': 'tmdb',
                              'tmdb_timestamp': _now}},
         'subcategory': 'movie',
         'title': 'Up'}
    ),
    (
        {
            "category" : "music",
            "details" : {
                "media" : {
                    "artist_display_name" : "Breathe Carolina",
                    "genre" : "Alternative",
                    "original_release_date" : "2011-07-12T07:00:00Z",
                    "track_length" : 231
                },
                "song" : {
                    "album_name" : "Hell Is What You Make It",
                }
            },
            "subcategory" : "song",
            "title" : "Sweat It Out",
        },
        {
            "category" : "music",
            "details" : {
                "media" : {
                    "artist_display_name" : "Breathe Carolina",
                    "genre" : "Alternative",
                    "original_release_date" : "2011-07-12T07:00:00Z",
                    'release_date': datetime(2011, 7, 12, 0, 0),
                    'release_date_source': 'format',
                    'release_date_timestamp': _now,
                    "track_length" : '231'
                },
                "song" : {
                    "album_name" : "Hell Is What You Make It",
                }
            },
            'sources': {
                'rdio':
                {
                    'rdio_id': 't9664977',
                    'rdio_source': 'rdio',
                    'rdio_timestamp': _now,
                }
            },
            "subcategory" : "song",
            "title" : "Sweat It Out",
        },
    ),
    (
        {
            "details" : {
                "album" : {
                    "tracks" : [
                        "Once",
                        "Even Flow",
                        "Alive",
                        "Why Go",
                        "Black",
                        "Jeremy",
                        "Oceans",
                        "Porch",
                        "Garden",
                        "Deep",
                        "Release"
                    ],
                    "track_count" : 11
                },
                "media" : {
                    "genre" : "Rock",
                    "artist_id" : 467464,
                    "original_release_date" : "1992-01-13T08:00:00Z",
                    "copyright" : "1991 Sony Music Entertainment Inc.",
                    "artist_display_name" : "Pearl Jam"
                }
            },
            "subcategory" : "album",
            "title" : "Ten",
        },
        {
            "details" : {
                "album" : {
                    "tracks" : [
                        "Once",
                        "Even Flow",
                        "Alive",
                        "Why Go",
                        "Black",
                        "Jeremy",
                        "Oceans",
                        "Porch",
                        "Garden",
                        "Deep",
                        "Release"
                    ],
                    "track_count" : 11
                },
                "media" : {
                    "genre" : "Rock",
                    "artist_id" : '467464',
                    "original_release_date" : "1992-01-13T08:00:00Z",
                    "copyright" : "1991 Sony Music Entertainment Inc.",
                    "artist_display_name" : "Pearl Jam"
                }
            },
             'sources': {'rdio': {'rdio_id': u'a237673',
                      'rdio_source': 'rdio',
                      'rdio_timestamp': _now}},
            "subcategory" : "album",
            "title" : "Ten",
        },

    ),
]

class AResolveHttpTest(AStampedAPIHttpTestCase):

    def setUp(self):
        self.container = FullResolveContainer()
        self.cases = []
        for case in _cases:
            before = Entity()
            before.importData(case[0])
            self.cases.append((before,case[1]))

    def tearDown(self):
        pass
    
    def compare(self, result, after):
        if type(after) is dict:
            for k,v in after.items():
                self.assertEqual(k in result, True, "%s not in %s should be %s" % (k, result, v) )
                if type(v) is dict:
                    self.compare( result[k] , v )
                else:
                    self.assertEqual( result[k] , v , "%s should be %s; is %s in %s" % (k, v, result[k], result) )
        else:
            self.assertEqual(result,after)

class ResolveCasesTest(AResolveHttpTest):

    def test_cases_resolve(self):
        now = _now
        for before, after in self.cases:
            decorations = {}
            if _verbose:
                before_string = 'Before:\n%s' % (pformat(before),)
            modified = self.container.enrichEntity(before,decorations,timestamp=_now)
            if _verbose:
                print(before_string)
                print('After\n%s' % (pformat(before),))
                print(pformat(decorations))
            self.compare(before, after)

if __name__ == '__main__':
    _verbose = True
    main()

