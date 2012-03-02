#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


import Globals
from logs   import report

try:
    from utils          import lazyProperty
    from pprint         import pprint, pformat
    from libs.iTunes    import iTunes
except:
    report()
    raise

class ArtistQuality():

    def __init__(self):
        pass

    @lazyProperty
    def api(self):
        import MongoStampedAPI
        return MongoStampedAPI.MongoStampedAPI()

    @lazyProperty
    def db(self):
        return self.api._entityDB

    def find(self,query):
        return (
            self.db._convertFromMongo( result )
                for result in self.db._collection.find(query)
        )

    def empty(self):
        query = {
            'subcategory':'artist',
            'sources.userGenerated':{ '$exists': False },
            '$and': [
                {
                    '$or': [
                        { 'details.artist.songs': { '$exists' : False } },
                        { 'details.artist.songs': { '$size' : 0 } },
                    ]
                },
                {
                    '$or': [
                        { 'details.artist.albums': { '$exists' : False } },
                        { 'details.artist.albums': { '$size' : 0 } },
                    ]
                }
            ]
        }
        return self.find(query)

    def demo(self):
        itunes = iTunes()
        empties = list(self.empty())
        print( "%s Empty artists:" % len(empties) )
        for artist in empties:
            #print(artist.title, artist.aid, artist.apple.view_url)
            info = itunes.method('lookup',id=artist.aid)
            pprint(info)

if __name__ == '__main__':
    ArtistQuality().demo()


