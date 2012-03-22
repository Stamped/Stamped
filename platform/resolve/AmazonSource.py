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
    from GenericSource    import GenericSource
    import logs
    import re
    from Resolver           import *
    from datetime       import datetime
    from libs.LibUtils           import months, parseDateString, xp
    from libs.AmazonAPI         import AmazonAPI
    from libs.Amazon            import Amazon, globalAmazon
    from utils          import lazyProperty
    from json           import loads
    from pprint         import pprint, pformat
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


class AmazonAlbum(_AmazonObject, ResolverAlbum):
    """
    """
    def __init__(self, amazon_id):
        _AmazonObject.__init__(self, amazon_id, ResponseGroup='Large,RelatedItems', RelationshipType='Tracks')
        ResolverAlbum.__init__(self)

    @lazyProperty
    def artist(self):
        try:
            return {'name' : xp(self.attributes, 'Artist')['v'] }
        except Exception:
            try:
                return {'name' : xp(self.attributes, 'Creator')['v'] }
            except Exception:
                return {'name' :''}

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


class AmazonTrack(_AmazonObject, ResolverTrack):

    def __init__(self, amazon_id):
        _AmazonObject.__init__(self, amazon_id, ResponseGroup='Large,RelatedItems', RelationshipType='Tracks')
        ResolverTrack.__init__(self)

    @lazyProperty
    def artist(self):
        album = xp(self.data, 'RelatedItems', 'RelatedItem', 'Item')
        key = xp(album,'ASIN')['v']
        attributes = xp(album, 'ItemAttributes')
        try:
            return {'name' : xp(attributes, 'Creator')['v'] }
        except Exception:
            return {'name' : ''}

    @lazyProperty
    def album(self):
        album = xp(self.data, 'RelatedItems', 'RelatedItem', 'Item')
        key = xp(album, 'ASIN')['v']
        attributes = xp(album, 'ItemAttributes')
        try:
            return {
                'name' : xp(attributes, 'Title')['v'],
                'source' : 'amazon',
                'key' : key,
            }
        except Exception:
            return {'name' : ''}

    @lazyProperty
    def length(self):
        try:
            return float(xp(self.attributes,'RunningTime')['v'])
        except Exception:
            logs.warning("no RunningTime for Amazon track %s (%s)" % (self.name, self.key))
            return -1

    @lazyProperty
    def genres(self):
        try:
            return [ xp(self.attributes, 'Genre')['v'] ]
        except Exception:
            return []

    @lazyProperty
    def date(self):
        try:
            return parseDateString(xp(self.attributes, 'ReleaseDate')['v'])
        except Exception:
            return None

class AmazonBook(_AmazonObject, ResolverBook):

    def __init__(self, amazon_id):
        _AmazonObject.__init__(self, amazon_id,  ResponseGroup='AlternateVersions,Large')
        ResolverBook.__init__(self)

    @lazyProperty
    def author(self):
        try:
            return {
                'name': xp(self.attributes, 'Author')['v']
            }
        except Exception:
            return { 'name':'' }

    @lazyProperty
    def publisher(self):
        try:
            return {
                'name': xp(self.attributes, 'Publisher')['v']
            }
        except Exception:
            return { 'name':'' }

    @lazyProperty
    def date(self):
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
    def sku(self):
        try:
            return xp(self.attributes, 'SKU')['v']
        except Exception:
            return None

    @lazyProperty
    def eisbn(self):
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

class AmazonSearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, target):
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)

    @property
    def subtype(self):
        return self.target.type

class AmazonSource(GenericSource):
    """
    Amazon entities
    """
    def __init__(self):
        GenericSource.__init__(self, 'amazon',
            'amazon',

            'artist_display_name',
            'genre',
            'track_length',
            'album_name',
            'release_date',
            'author',
            'publisher',
            'num_pages',
            'isbn',
            'desc',
            'sku_number',
            'amazon_link',
            'amazon_underlying',
            'images',
        )

    def matchSource(self, query):
        if query.type == 'album':
            return self.albumSource(query)
        elif query.type == 'track':
            return self.trackSource(query)
        elif query.type == 'book':
            return self.bookSource(query)
        elif query.type == 'search_all':
            return self.searchAllSource(query)
        return self.emptySource

    def __searchGen(self, wrapper, *queries):
        def gen():
            try:
                for params in queries:
                    test = params.pop('test', lambda x: True)
                    if 'SearchIndex' not in params:
                        params['SearchIndex'] = 'All'
                    if 'ResponseGroup' not in params:
                        params['ResponseGroup'] = "ItemAttributes"
                    results = globalAmazon().item_search(**params)
                    items = xp(results, 'ItemSearchResponse', 'Items')['c']['Item']
                    for item in items:
                        try:
                            if test == None or test(item):
                                yield xp(item, 'ASIN')['v']
                        except Exception:
                            pass

            except GeneratorExit:
                pass
        return self.generatorSource(gen(), constructor=lambda x: wrapper( x ), unique=True)

    def albumSource(self, query):
        keywords = ' '.join([
            query.name
        ])
        return self.__searchGen(AmazonAlbum, {
            'test':lambda item:  xp(item, 'ItemAttributes', 'ProductTypeName')['v'] == "DOWNLOADABLE_MUSIC_ALBUM",
            'Keywords':keywords
        })

    def trackSource(self, query):
        keywords = ' '.join([
            query.name
        ])
        return self.__searchGen(AmazonTrack, {
            'test':lambda item:  xp(item, 'ItemAttributes', 'ProductTypeName')['v'] == "DOWNLOADABLE_MUSIC_TRACK",
            'Keywords':keywords
        })

    def bookSource(self, query):
        keywords = ' '.join([
            query.name
        ])
        return self.__searchGen(AmazonBook,
            {
                'Keywords':keywords,
                'SearchIndex':'Books',
                'test': lambda item: xp(item, 'ItemAttributes', 'Binding')['v'] == 'Kindle Edition',
            },
            {
                'Keywords':keywords,
                'SearchIndex':'Books',
            }
        )

    @lazyProperty
    def __amazon_api(self):
        return AmazonAPI()

    @lazyProperty
    def __amazon(self):
        return self.__amazon_api.amazon

    def __enrichSong(self, entity, asin):
        track = AmazonTrack(asin)
        if track.artist['name'] != '':
            entity['artist_display_name'] = track.artist['name']
        if track.album['name'] != '':
            entity['album_name'] = track.album['name']
        if len(track.genres) > 0:
            entity['genre'] = track.genres[0]
        if track.date != None:
            entity['release_date'] = track.date
        if track.length > 0:
            entity['track_length'] = track.length

    def __enrichBook(self, entity, asin):
        book = AmazonBook(asin)
        if book.author['name'] != '':
            entity['author'] = book.author['name']
        if book.publisher['name'] != '':
            entity['publisher'] = book.publisher['name']
        if book.date != None:
            entity['release_date'] = book.date
        if book.description != '':
            entity['desc'] = book.description
        if book.length > 0:
            entity['num_pages'] = int(book.length)
        if book.isbn != None:
            entity['isbn'] = book.isbn
        if book.sku != None:
            entity['sku_number'] = book.sku
        if book.ebookVersion is not None and book.ebookVersion.link is not None:
            entity['amazon_link'] = book.ebookVersion.link
        elif book.link != None:
            entity['amazon_link'] = book.link
        entity['amazon_underlying'] = book.underlying.key
        try:
            image_set =  xp(book.underlying.data, 'ImageSets','ImageSet')
            entity['images']['large'] = xp(image_set,'LargeImage','URL')['v']
            entity['images']['small'] = xp(image_set,'MediumImage','URL')['v']
            entity['images']['tiny'] = xp(image_set,'SmallImage','URL')['v']
        except Exception:
            logs.warning("no image set for %s" % book.underlying.key)

    def enrichEntity(self, entity, controller, decorations, timestamps):
        asin = entity['asin']
        if asin is not None and asin != '':
            entity['amazon_id'] = asin
        else:
            GenericSource.enrichEntity(self, entity, controller, decorations, timestamps)
        if entity['amazon_id'] != None:
            asin = entity['amazon_id']
            if entity['subcategory'] == 'song':
                self.__enrichSong(entity, asin)
            if entity['subcategory'] == 'book':
                self.__enrichBook(entity, asin)
        return True

if __name__ == '__main__':
    demo(AmazonSource(), "Don't Speak")
