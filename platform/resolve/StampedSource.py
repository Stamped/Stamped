#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'StampedSource' ]

import Globals
from logs import report

try:
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    import logs
    from Resolver                   import Resolver, demo
except:
    report()
    raise

class StampedSource(GenericSource):
    """
    """
    def __init__(self):
        GenericSource.__init__(self, 'stamped')

    @lazyProperty
    def __entityDB(self):
        import MongoStampedAPI
        api = MongoStampedAPI.MongoStampedAPI()
        return api._entityDB

    def matchSource(self, query):
        if query.type == 'artist':
            return self.artistSource(query)
        elif query.type == 'album':
            return self.albumSource(query)
        elif query.type == 'track':
            return self.trackSource(query)
        else:
            return self.emptySource

    def trackSource(self, query):
        tracks = list(self.__entityDB._collection.find({
            'subcategory':'song',
            '$or': [
                { 'title':query.name },
                { 'details.media.artist_display_title':query.artist['name'] },
                { 'details.song.album.name': query.album['name'] },
            ]
        }, {'_id':1} ))
        def source(start, count):
            if start + count <= len(tracks):
                result = tracks[start:start+count]
            elif start < len(tracks):
                result = tracks[start:]
            else:
                result = []
            return [ self.resolver.trackFromEntity( self.__entityDB.getEntity( self.__entityDB._getStringFromObjectId(entry['_id']) ) ) for entry in result ]
        return source
    
    def albumSource(self, query):
        options = [
            { 'title':query.name },
            { 'details.media.artist_display_title':query.artist['name'] },
        ]
        for track in query.tracks:
            options.append( {
                'details.album.tracks': track['name'],
            })
        albums = list(self.__entityDB._collection.find({
            'subcategory':'album',
            '$or': options,
        }, {'_id':1} ))
        def source(start, count):
            if start + count <= len(albums):
                result = albums[start:start+count]
            elif start < len(albums):
                result = albums[start:]
            else:
                result = []
            return [ self.resolver.albumFromEntity( self.__entityDB.getEntity( self.__entityDB._getStringFromObjectId(entry['_id']) )  ) for entry in result ]
        return source


    def artistSource(self, query):
        options = [
            { 'title':query.name },
        ]
        for track in query.tracks:
            options.append( {
                'details.artist.songs': track['name'],
            })
        for album in query.albums:
            options.append( {
                'details.artist.albums': album['name'],
            })
        artists = list(self.__entityDB._collection.find({
            'subcategory':'artist',
            '$or': options,
        }, {'_id':1} ))
        def source(start, count):
            if start + count <= len(artists):
                result = artists[start:start+count]
            elif start < len(artists):
                result = artists[start:]
            else:
                result = []
            return [ self.resolver.artistFromEntity( self.__entityDB.getEntity( self.__entityDB._getStringFromObjectId(entry['_id']) )  ) for entry in result ]
        return source

if __name__ == '__main__':
    demo(StampedSource(), 'Katy Perry')
