#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import log, report

try:
    from MongoStampedAPI                import MongoStampedAPI
    from AStampedAPIHttpTestCase            import *
    from api.Schemas                    import Entity
    from pprint                         import pprint
    from datetime                       import datetime
except:
    report()
    raise

_verbose = False

class AEnrichHttpTest(AStampedAPIHttpTestCase):

    def setUp(self):
        self.api = MongoStampedAPI()
        self.media1 = Entity()
        raw = {
            "category" : "film",
            "subtitle" : "film",
            "subcategory" : "movie",
            "title" : "Colombiana",
            "image" : "http://images.fandango.com/r85.9.2/ImageRenderer/375/375/images/no_image_375x375.jpg/140038/images/masterrepository/tms/105255/105255_aa.jpg",
            "titlel" : "colombiana",
            "sources" : {
                "fandango" : {
                    "fid" : "140038"
                }
            },
            "details" : {
                "media" : {
                    "track_length" : "6420",
                    "genre" : "Action/Adventure",
                    "original_release_date" : "August 26, 2011",
                    "mpaa_rating" : "PG-13"
                },
                "video" : {
                    "director" : "Olivier Megaton",
                    "cast" : "Zoe Saldana, Jordi Mollà, Lennie James, Amandla Stenberg, Michael Vartan"
                }
            },
            "desc" : "A young woman, after witnessing her parents' murder as a child in Bogota, grows up to be a stone-cold assassin. \n\n  Release Date:8/26/2011"
        }
        self.media1.importData(raw)

    def tearDown(self):
        pass

class EnrichMovieTest(AEnrichHttpTest):

    def test_enrich_movie(self):
        modified = self.api._entityDB.enrichEntity(self.media1)
        if _verbose:
            pprint(self.media1)
        self.assertEqual(modified,True)
        release_date = datetime(2011,8,26)
        self.assertEqual(self.media1.release_date,release_date)
        self.assertEqual(self.media1.release_date_source,'cleaner')

if __name__ == '__main__':
    _verbose = True
    main()

