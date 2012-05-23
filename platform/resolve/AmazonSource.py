#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'AmazonSource' ]

import Globals
from logs import report

try:
    import logs, re
    from GenericSource              import GenericSource, multipleSource
    from Resolver                   import *
    from ResolverObject             import *
    from datetime                   import datetime
    from libs.LibUtils              import months, parseDateString, xp
    from libs.AmazonAPI             import AmazonAPI
    from libs.Amazon                import Amazon, globalAmazon
    from utils                      import lazyProperty
    from json                       import loads
    from pprint                     import pprint, pformat
except:
    report()
    raise


class _AmazonObject(object):

    def __init__(self, amazon_id, **params):
        params['ItemId'] = amazon_id
        if 'ResponseGroup' not in params:
            params['ResponseGroup'] = 'Large'
        self.__params = params
        self.__amazon_id = amazon_id
    
    @lazyProperty
    def data(self):
        raw = globalAmazon().item_lookup(**self.__params)
        
        return xp(raw, 'ItemLookupResponse','Items','Item')
    
    @lazyProperty
    def name(self):
        return xp(self.attributes, 'Title')['v']

    @lazyProperty
    def attributes(self):
        return xp(self.data, 'ItemAttributes')

    @property 
    def key(self):
        return self.__amazon_id

    @property 
    def source(self):
        return 'amazon'

    def __repr__(self):
        return pformat( self.attributes )

    @property 
    def underlying(self):
        return self


class AmazonAlbum(_AmazonObject, ResolverMediaCollection):
    """
    """
    def __init__(self, amazon_id):
        _AmazonObject.__init__(self, amazon_id, ResponseGroup='Large,RelatedItems', RelationshipType='Tracks')
        ResolverMediaCollection.__init__(self, types=['album'])

    @lazyProperty
    def artists(self):
        try:
            return [ { 'name' : xp(self.attributes, 'Artist')['v'] } ]
        except Exception:
            try:
                return [ { 'name' : xp(self.attributes, 'Creator')['v'] } ]
            except Exception:
                return []

    @lazyProperty
    def tracks(self):
        try:
            tracks = list(xp(self.data, 'RelatedItems')['c']['RelatedItem'])
            page_count = int(xp(self.data, 'RelatedItems', 'RelatedItemPageCount')['v'])
            for i in range(1,page_count):
                page = i+1
                data = globalAmazon().item_lookup(ItemId=self.key, ResponseGroup='Large,RelatedItems', RelationshipType='Tracks', RelatedItemPage=str(page))
                tracks.extend( xp(data, 'ItemLookupResponse', 'Items', 'Item', 'RelatedItems')['c']['RelatedItem'] )
            track_d = {}
            for track in tracks:
                track_d[ int(xp(track, 'Item', 'ItemAttributes', 'TrackSequence')['v']) ] = {
                    'name' : xp(track, 'Item', 'ItemAttributes', 'Title')['v'],
                    'key' : xp(track, 'Item', 'ASIN')['v'],
                }
            return [ track_d[k] for k in sorted(track_d) ]
        except Exception:
            report()
            return []


class AmazonTrack(_AmazonObject, ResolverMediaItem):

    def __init__(self, amazon_id):
        _AmazonObject.__init__(self, amazon_id, ResponseGroup='Large,RelatedItems', RelationshipType='Tracks')
        ResolverMediaItem.__init__(self, types=['track'])

    @lazyProperty
    def artists(self):
        album = xp(self.data, 'RelatedItems', 'RelatedItem', 'Item')
        key = xp(album,'ASIN')['v']
        attributes = xp(album, 'ItemAttributes')
        try:
            return [ { 'name' : xp(attributes, 'Creator')['v'] } ]
        except Exception:
            return []

    @lazyProperty
    def albums(self):
        album = xp(self.data, 'RelatedItems', 'RelatedItem', 'Item')
        key = xp(album, 'ASIN')['v']
        attributes = xp(album, 'ItemAttributes')
        try:
            return [{
                'name' : xp(attributes, 'Title')['v'],
                'source' : 'amazon',
                'key' : key,
            }]
        except Exception:
            return []

    @lazyProperty
    def length(self):
        try:
            return float(xp(self.attributes,'RunningTime')['v'])
        except Exception:
            logs.warning("no RunningTime for Amazon track %s (%s)" % (self.name, self.key))
            return -1

    @lazyProperty
    def genres(self):
        ### TODO: Convert these into readable English
        # try:
        #     return [ xp(self.attributes, 'Genre')['v'] ]
        # except Exception:
        #     return []
        return []

    @lazyProperty
    def release_date(self):
        try:
            return parseDateString(xp(self.attributes, 'ReleaseDate')['v'])
        except Exception:
            return None

class AmazonBook(_AmazonObject, ResolverMediaItem):

    def __init__(self, amazon_id):
        _AmazonObject.__init__(self, amazon_id,  ResponseGroup='AlternateVersions,Large')
        ResolverMediaItem.__init__(self, types=['book'])

    @lazyProperty
    def authors(self):
        try:
            return [{
                'name': xp(self.attributes, 'Author')['v']
            }]
        except Exception:
            return []

    @lazyProperty
    def publishers(self):
        try:
            return [{
                'name': xp(self.attributes, 'Publisher')['v']
            }]
        except Exception:
            return []

    @lazyProperty
    def release_date(self):
        try:
            return parseDateString( xp(self.attributes, 'PublicationDate')['v'] )
        except Exception:
            return None

    @lazyProperty
    def length(self):
        try:
            return float(xp(self.attributes, "NumberOfPages")['v'])
        except Exception:
            return -1

    @lazyProperty
    def isbn(self):
        try:
            return xp(self.attributes, 'ISBN')['v']
        except Exception:
            return None

    @lazyProperty
    def sku_number(self):
        try:
            return xp(self.attributes, 'SKU')['v']
        except Exception:
            return None

    @lazyProperty
    def description(self):
        try:
            review = xp(self.data, 'EditorialReview', 'Content')['v']
        except Exception:
            return ""

    @lazyProperty
    def link(self):
        try:
            return xp(self.data, 'ItemLinks', 'ItemLink', 'URL')['v']
        except Exception:
            return None

    @lazyProperty
    def ebookVersion(self):
        if xp(self.underlying.attributes, 'Binding')['v'] == 'Kindle Edition':
            return self.underlying
        return None

    @lazyProperty
    def images(self):
        try:
            image_set = xp(self.underlying.data, 'ImageSets','ImageSet')
            image = xp(image_set,'LargeImage','URL')['v']
            if image is not None:
                return [image]
        except Exception:
            pass
        return []

    @lazyProperty
    def url(self):
        try:
            if self.ebookVersion is not None and self.ebookVersion.link is not None:
                return self.ebookVersion.link
        except Exception:
            pass
        return None

    @lazyProperty 
    def underlying(self):
        try:
            versions = xp(self.data, 'AlternateVersions')['c']['AlternateVersion']
            priorities = [
                'Kindle Edition',
                'Hardcover',
                'Paperback',
                'Audio CD',
            ]
            self_kind = xp(self.attributes, 'Binding')['v']
            for kind in priorities:
                if self_kind == kind:
                    return self
                for version in versions:
                    if xp(version, 'Binding')['v'] == kind:
                        return AmazonBook(xp(version, 'ASIN')['v'])
        except Exception:
            pass
        return self

class AmazonVideoGame(_AmazonObject, ResolverSoftware):
    
    def __init__(self, amazon_id):
        _AmazonObject.__init__(self, amazon_id,  ResponseGroup='Large')
        ResolverSoftware.__init__(self, types=['video_game'])
    
    @lazyProperty
    def authors(self):
        try:
            return [ { 'name': xp(self.attributes, 'Author')['v'] } ]
        except Exception:
            return []
    
    @lazyProperty
    def publishers(self):
        try:
            return [ { 'name': xp(self.attributes, 'Publisher')['v'] } ]
        except Exception:
            return []
    
    @lazyProperty
    def platform(self):
        try:
            return { 'name': xp(self.attributes, 'Platform')['v'] }
        except Exception:
            return { 'name':'' }
    
    @lazyProperty
    def release_date(self):
        try:
            return parseDateString( xp(self.attributes, 'PublicationDate')['v'] )
        except Exception:
            return None
    
    @lazyProperty
    def sku_number(self):
        try:
            return xp(self.attributes, 'SKU')['v']
        except Exception:
            return None
    
    @lazyProperty
    def genres(self):
        try:
            return [ xp(self.attributes, 'Genre')['v'] ]
        except Exception:
            return []
    
    @lazyProperty
    def description(self):
        try:
            review = xp(self.data, 'EditorialReview', 'Content')['v']
        except Exception:
            return ""
    
    @lazyProperty
    def link(self):
        try:
            return xp(self.data, 'ItemLinks', 'ItemLink', 'URL')['v']
        except Exception:
            return None

class AmazonSearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, target):
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)

class AmazonSource(GenericSource):
    """
    Amazon entities
    """
    def __init__(self):
        GenericSource.__init__(self, 'amazon',
            groups=[
                'artists',
                # 'genres',
                'length',
                'albums',
                'release_date',
                'authors',
                'publishers',
                'isbn',
                'desc',
                'sku_number',
                'images',
            ],
            kinds=[
                'media_collection',
                'media_item',
                'software',
            ],
            types=[
                'album',
                'track',
                'book',
                'video_game',
            ]
        )

    def getGroups(self, entity=None):
        groups = GenericSource.getGroups(self, entity)
        if entity.isType('album') or entity.isType('track'):
            groups.remove('desc')
        if entity.isType('artist'):
            groups.remove('images')
        return groups

    def matchSource(self, query):
        if query.kind == 'search':
            return self.searchAllSource(query)

        if query.isType('album'):
            return self.albumSource(query)
        if query.isType('track'):
            return self.trackSource(query)
        if query.isType('book'):
            return self.bookSource(query)
        if query.isType('video_game'):
            return self.videoGameSource(query)

        return self.emptySource

    def __searchGen(self, proxy, *queries):
        def gen():
            try:
                for params in queries:
                    test = params.pop('test', lambda x: True)
                    if 'SearchIndex' not in params:
                        params['SearchIndex'] = 'All'
                    if 'ResponseGroup' not in params:
                        params['ResponseGroup'] = "ItemAttributes"
                    results = globalAmazon().item_search(**params)
                    items = xp(results, 'ItemSearchResponse', 'Items')['c']
                    
                    if 'Item' in items:
                        items = items['Item']
                        
                        for item in items:
                            try:
                                if test == None or test(item):
                                    yield xp(item, 'ASIN')['v']
                            except Exception:
                                pass
            except GeneratorExit:
                pass
        
        return self.generatorSource(gen(), constructor=lambda x: proxy( x ), unique=True)
    
    def albumSource(self, query=None, query_string=None):
        if query_string is None:
            query_string = ' '.join([
                query.name
            ])
        
        return self.__searchGen(AmazonAlbum, {
            'test':lambda item:  xp(item, 'ItemAttributes', 'ProductTypeName')['v'] == "DOWNLOADABLE_MUSIC_ALBUM",
            'Keywords':query_string
        })
    
    def trackSource(self, query=None, query_string=None):
        if query_string is None:
            query_string = ' '.join([
                query.name
            ])
        
        return self.__searchGen(AmazonTrack, {
            'test':lambda item:  xp(item, 'ItemAttributes', 'ProductTypeName')['v'] == "DOWNLOADABLE_MUSIC_TRACK",
            'Keywords':query_string
        })
    
    def bookSource(self, query=None, query_string=None):
        if query_string is None:
            query_string = ' '.join([
                query.name
            ])
        
        return self.__searchGen(AmazonBook,
            {
                'Keywords':query_string,
                'SearchIndex':'Books',
                'test': lambda item: xp(item, 'ItemAttributes', 'Binding')['v'] == 'Kindle Edition',
            },
            {
                'Keywords':query_string,
                'SearchIndex':'Books',
            }
        )
    
    def videoGameSource(self, query=None, query_string=None):
        if query_string is None:
            query_string = ' '.join([
                query.name
            ])
        
        def _is_video_game(item):
            try:
                if xp(item, 'ItemAttributes', 'ProductGroup')['v'].lower() == "video games":
                    return True
            except Exception:
                pass
            
            try:
               if xp(item, 'ItemAttributes', 'ProductTypeName')['v'].lower() == "console_video_game":
                   return True
            except Exception:
                pass
            
            return False
        
        return self.__searchGen(AmazonVideoGame, {
            'test'      : _is_video_game,
            'Keywords'  : query_string, 
        })
    
    def searchAllSource(self, query, timeout=None):
        if query.kinds is not None and len(query.kinds) > 0 and len(self.kinds.intersection(query.kinds)) == 0:
            logs.debug('Skipping %s (kinds: %s)' % (self.sourceName, query.kinds))
            return self.emptySource

        if query.types is not None and len(query.types) > 0 and len(self.types.intersection(query.types)) == 0:
            logs.debug('Skipping %s (types: %s)' % (self.sourceName, query.types))
            return self.emptySource

        logs.debug('Searching %s...' % self.sourceName)
        
        q = query.query_string

        sources = []

        if query.types is None or query.isType('album'):
            sources.append(lambda : self.albumSource(query_string=q))
        if query.types is None or query.isType('book'):
            sources.append(lambda : self.bookSource(query_string=q))
        if query.types is None or query.isType('track'):
            sources.append(lambda : self.trackSource(query_string=q))
        if query.types is None or query.isType('video_game'):
            sources.append(lambda : self.videoGameSource(query_string=q))

        if len(sources) == 0:
            return self.emptySource 

        return multipleSource(
            sources,
            constructor=AmazonSearchAll
        )
    
    @lazyProperty
    def __amazon_api(self):
        return AmazonAPI()
    
    @lazyProperty
    def __amazon(self):
        return self.__amazon_api.amazon
    
    # def __enrichSong(self, entity, asin):
    #     track = AmazonTrack(asin)
    #     if track.artist['name'] != '':
    #         entity['artist_display_name'] = track.artist['name']
    #     if track.album['name'] != '':
    #         entity['album_name'] = track.album['name']
    #     if len(track.genres) > 0:
    #         entity['genre'] = track.genres[0]
    #     if track.date != None:
    #         entity['release_date'] = track.date
    #     if track.length > 0:
    #         entity['track_length'] = track.length
    
    # def __enrichBook(self, entity, asin):
    #     book = AmazonBook(asin)
    #     if book.author['name'] != '':
    #         entity['author'] = book.author['name']
    #     if book.publisher['name'] != '':
    #         entity['publisher'] = book.publisher['name']
    #     if book.date != None:
    #         entity['release_date'] = book.date
    #     if book.description != '':
    #         entity['desc'] = book.description
    #     if book.length > 0:
    #         entity['num_pages'] = int(book.length)
    #     if book.isbn != None:
    #         entity['isbn'] = book.isbn
    #     if book.sku != None:
    #         entity['sku_number'] = book.sku
    #     if book.ebookVersion is not None and book.ebookVersion.link is not None:
    #         entity['amazon_link'] = book.ebookVersion.link
    #     elif book.link != None:
    #         entity['amazon_link'] = book.link
    #     entity['amazon_underlying'] = book.underlying.key
    #     try:
    #         image_set = xp(book.underlying.data, 'ImageSets','ImageSet')
    #         entity['images']['large'] = xp(image_set,'LargeImage','URL')['v']
    #         entity['images']['small'] = xp(image_set,'MediumImage','URL')['v']
    #         entity['images']['tiny']  = xp(image_set,'SmallImage','URL')['v']
    #     except Exception:
    #         logs.warning("no image set for %s" % book.underlying.key)
    
    # def __enrichVideoGame(self, entity, asin):
    #     game = AmazonVideoGame(asin)
        
    #     if game.artist['name'] != '':
    #         entity['artist_display_name'] = game.artist['name']
    #     if len(game.genres) > 0:
    #         entity['genre'] = game.genres[0]
    #     if game.date != None:
    #         entity['release_date'] = game.date
    #     if game.description != '':
    #         entity['desc'] = game.description
    #     if game.sku != None:
    #         entity['sku_number'] = game.sku
    #     if game.platform != '':
    #         entity['platform'] = game.platform
        
    #     try:
    #         image_set = xp('.//ImageSets','ImageSet')
    #         entity['images']['large'] = xp(image_set,'LargeImage','URL')['v']
    #         entity['images']['small'] = xp(image_set,'MediumImage','URL')['v']
    #         entity['images']['tiny']  = xp(image_set,'SmallImage','URL')['v']
    #     except Exception:
    #         logs.warning("no image set for %s" % asin)
    
    def entityProxyFromKey(self, key, **kwargs):
        try:
            item = _AmazonObject(amazon_id=key)
            kind = xp(item.attributes, 'ProductGroup')['v'].lower()
            logs.debug(kind)
            
            # TODO: Avoid additional API calls here?
            
            if kind == 'book':
                return AmazonBook(key)
            if kind == 'digital music album':
                return AmazonAlbum(key)
            if kind == 'digital music track':
                return AmazonTrack(key)
            if kind == 'video games':
                return AmazonVideoGame(key)
            
            raise Exception("unsupported amazon product type")
        except KeyError:
            pass
        return None
    
    def enrichEntityWithEntityProxy(self, proxy, entity, controller=None, decorations=None, timestamps=None):
        GenericSource.enrichEntityWithEntityProxy(self, proxy, entity, controller, decorations, timestamps)
        entity.sources.amazon_id = proxy.key
        try:
            if entity.isType('book'):
                entity.sources.amazon_underlying = proxy.underlying.key
        except Exception:
            pass
        return True

if __name__ == '__main__':
    demo(AmazonSource(), "Don't Speak")

