#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'MusicSource' ]

import Globals
from logs import report

try:
    from libs.Spotify               import globalSpotify
    from BasicSource                import BasicSource
    from utils                      import lazyProperty
    import logs
    from pprint                     import pprint, pformat
    import sys
    from Resolver                   import Resolver, SpotifyArtist, SpotifyAlbum, SpotifyTrack
    from abc                        import ABCMeta, abstractmethod
except:
    report()
    raise

_verbose = False
_very_verbose = False

class MusicSource(BasicSource):
    """
    """
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        BasicSource.__init__(self, *args, **kwargs)
        self.addGroup(self.sourceName)

    def matchSource(self, query):
        if query.type == 'artist':
            return self.artistSource(query)
        elif query.type == 'album':
            return self.albumSource(query)
        elif query.type == 'track':
            return self.trackSource(query)
        else:
            return self.emptySource

    @abstractmethod
    def artistSource(self, query):
        pass

    @abstractmethod
    def albumSource(self, query):
        pass

    @abstractmethod
    def trackSource(self, query):
        pass

    def enrichEntity(self, entity, controller, decorations, timestamps):
        if controller.shouldEnrich(self.sourceName, self.sourceName, entity):
            timestamps[self.sourceName] = controller.now
            subcategory = entity['subcategory']
            results = []
            if subcategory == 'song':
                results = self.resolveTrack(entity)
            elif subcategory == 'album':
                results = self.resolveAlbum(entity)
            elif subcategory == 'artist':
                results = self.resolveArtist(entity)

            if len(results) != 0:
                best = results[0]
                if best['resolved']:
                    entity[self.sourceName] = best['key']
        return True
    
    def resolveTrack(self, entity):
        query = self.resolver.trackFromEntity(entity)
        return self.resolver.resolve( query, self.trackSource(query))
    
    def resolveAlbum(self, entity, **options):
        query = self.resolver.albumFromEntity(entity)
        return self.resolver.resolve( query, self.albumSource(query), **options)


    def resolveArtist(self, entity):
        query = self.resolver.artistFromEntity(entity)
        return self.resolver.resolve( query, self.artistSource(query))


    def demo(self):
        import Resolver
        import sys

        title = 'Katy Perry'
        subcategory = None
        count = 1

        print(sys.argv)
        if len(sys.argv) > 1:
            title = sys.argv[1]
        if len(sys.argv) > 2:
            subcategory = sys.argv[2]
        if len(sys.argv) > 3:
            count = int(sys.argv[3])

        Resolver._verbose = True
        from MongoStampedAPI import MongoStampedAPI
        api = MongoStampedAPI()
        db = api._entityDB
        query = {'title':title}
        if subcategory is not None:
            query['subcategory'] = subcategory
        cursor = db._collection.find(query)
        if cursor.count() == 0:
            print("Could not find a matching entity for %s" % title)
            return
        result = cursor[0]
        entity = db._convertFromMongo(result)
        rdio_id = None
        if entity['subcategory'] == 'artist':
            rdio_id = self.resolveArtist(entity)
        elif entity['subcategory'] == 'album':
            rdio_id = self.resolveAlbum(entity)
        elif entity['subcategory'] == 'song':
            rdio_id = self.resolveTrack(entity)
        print("Resolved %s to" % (entity['title']))
        pprint(rdio_id)

