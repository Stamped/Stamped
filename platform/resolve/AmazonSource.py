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
    from TitleUtils                 import *
    from Resolver                   import *
    from ResolverObject             import *
    from datetime                   import datetime
    from libs.LibUtils              import months, parseDateString, xp
    from libs.AmazonAPI             import AmazonAPI
    from libs.Amazon                import Amazon, globalAmazon
    from utils                      import lazyProperty, basicNestedObjectToString
    from json                       import loads
    from pprint                     import pprint, pformat
    from search.ScoringUtils        import *
    from gevent.pool                import Pool
except:
    report()
    raise


class _AmazonObject(object):

    def __init__(self, amazon_id, data=None, **params):
        self.__data = data
        params['ItemId'] = amazon_id
        if 'ResponseGroup' not in params:
            params['ResponseGroup'] = 'Large'
        self.__params = params
        self.__amazon_id = amazon_id
    
    @lazyProperty
    def data(self):
        if self.__data is None:
            self._issueLookup()
        return self.__data

    def _issueLookup(self):
        # Slightly ugly -- calling ResolverObject method just because we know all _AmazonObject implementations also
        # inherit from ResolverObject. TODO: Get rid of multiple inheritance!
        # We don't catch the LookupRequiredError here because if you are initializing a capped-lookup object without
        # passing in initial data, you are doing it wrong.
        self.countLookupCall('base data')
        raw = globalAmazon().item_lookup(**self.__params)
        self.__data = xp(raw, 'ItemLookupResponse','Items','Item')

    @lazyProperty
    def raw_name(self):
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

    @property
    def salesRank(self):
        try:
            return int(xp(self.data, 'SalesRank')['v'])
        except KeyError:
            return None


class AmazonAlbum(_AmazonObject, ResolverMediaCollection):
    """
    """
    def __init__(self, amazon_id, data=None, maxLookupCalls=None):
        _AmazonObject.__init__(self, amazon_id, data=data, ResponseGroup='Large,RelatedItems', RelationshipType='Tracks')
        ResolverMediaCollection.__init__(self, types=['album'], maxLookupCalls=maxLookupCalls)
        self._properties.append('salesRank')

    def _cleanName(self, rawName):
        return cleanAlbumTitle(rawName)

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
        # We might be missing related items data entirely, in which case we start by issuing a lookup there.
        # TODO: This probably could be done as part of one lookup with the one about to be made.
        try:
            tracks = list(xp(self.data, 'RelatedItems')['c']['RelatedItem'])
        except KeyError:
            try:
                self._issueLookup()
            except LookupRequiredError:
                return []
        try:
            tracks = list(xp(self.data, 'RelatedItems')['c']['RelatedItem'])
            page_count = int(xp(self.data, 'RelatedItems', 'RelatedItemPageCount')['v'])
            for i in range(1,page_count):
                page = i+1
                self.countLookupCall('tracks')
                data = globalAmazon().item_lookup(ItemId=self.key, ResponseGroup='Large,RelatedItems', RelationshipType='Tracks', RelatedItemPage=str(page))
                tracks.extend( xp(data, 'ItemLookupResponse', 'Items', 'Item', 'RelatedItems')['c']['RelatedItem'] )
            track_d = {}
            for track in tracks:
                track_d[ int(xp(track, 'Item', 'ItemAttributes', 'TrackSequence')['v']) ] = {
                    'name' : xp(track, 'Item', 'ItemAttributes', 'Title')['v'],
                    'key' : xp(track, 'Item', 'ASIN')['v'],
                }
            return [ track_d[k] for k in sorted(track_d) ]
        except LookupRequiredException:
            return []
        except Exception:
            # TODO: It seems possible that only one of the requests failed; shouldn't we keep the results of the others?
            report()
            return []


class AmazonTrack(_AmazonObject, ResolverMediaItem):

    def __init__(self, amazon_id, data=None, maxLookupCalls=None):
        _AmazonObject.__init__(self, amazon_id, data=data, ResponseGroup='Large,RelatedItems', RelationshipType='Tracks')
        ResolverMediaItem.__init__(self, types=['track'], maxLookupCalls=maxLookupCalls)
        self._properties.append('salesRank')

    def _cleanName(self, rawName):
        return cleanTrackTitle(rawName)

    @lazyProperty
    def artists(self):
        try:
            return [ { 'name' : xp(self.attributes, 'Artist')['v'] } ]
        except Exception:
            pass

        try:
            return [ { 'name' : xp(self.attributes, 'Creator')['v'] } ]
        except Exception:
            pass

        try:
            album = xp(self.data, 'RelatedItems', 'RelatedItem', 'Item')
            key = xp(album,'ASIN')['v']
            attributes = xp(album, 'ItemAttributes')
            return [ { 'name' : xp(attributes, 'Creator')['v'] } ]
        except Exception:
            return []

    @lazyProperty
    def albums(self):
        try:
            album = xp(self.data, 'RelatedItems', 'RelatedItem', 'Item')
        except KeyError:
            try:
                self._issueLookup()
            except LookupRequiredError:
                return []
        try:
            album = xp(self.data, 'RelatedItems', 'RelatedItem', 'Item')
            key = xp(album, 'ASIN')['v']
            attributes = xp(album, 'ItemAttributes')
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

    def __init__(self, amazon_id, data=None, maxLookupCalls=None):
        _AmazonObject.__init__(self, amazon_id, data=data, ResponseGroup='AlternateVersions,Large')
        ResolverMediaItem.__init__(self, types=['book'], maxLookupCalls=maxLookupCalls)
        self._properties.append('salesRank')

    def _cleanName(self, rawName):
        return cleanBookTitle(rawName)

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
            return xp(self.data, 'EditorialReview', 'Content')['v']
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


class AmazonMovie(_AmazonObject, ResolverMediaItem):
    def __init__(self, amazon_id, data=None, maxLookupCalls=None):
        _AmazonObject.__init__(self, amazon_id, data=data, ResponseGroup='Medium,Reviews')
        ResolverMediaItem.__init__(self, types=['movie'], maxLookupCalls=maxLookupCalls)
        self._properties.append('salesRank')

    def _cleanName(self, rawName):
        return cleanMovieTitle(rawName)

    @lazyProperty
    def cast(self):
        # TODO: These functions are completely fucking repetitive, factor out common code.
        try:
            return [ {'name': actor['v']} for actor in self.attributes['c']['Actor'] ]
        except KeyError:
            return []

    @lazyProperty
    def directors(self):
        try:
            return [ { 'name': xp(self.attributes, 'Director')['v'] } ]
        except KeyError:
            return []

    @lazyProperty
    def studios(self):
        try:
            return [ { 'name': xp(self.attributes, 'Studio')['v'] } ]
        except KeyError:
            return []

    @lazyProperty
    def length(self):
        # Traditionally runtime is reported in minutes, but we want it in seconds.
        unitsConversion = 60
        try:
            units = xp(self.attributes, 'RunningTime')['a']['Units']
            if units != 'minutes':
                raise Exception('Unexpected units found on Amazon movie: (%s)' % units)
        except KeyError:
            pass
        try:
            return float(xp(self.attributes, 'RunningTime')['v']) * unitsConversion
        except KeyError:
            return None

    @lazyProperty
    def mpaa_rating(self):
        try:
            return xp(self.attributes, 'AudienceRating')['v']
        except KeyError:
            return None

    @lazyProperty
    def isbn(self):
        try:
            return xp(self.attributes, 'ISBN')['v']
        except KeyError:
            return None

    @lazyProperty
    def publishers(self):
        try:
            return [ { 'name' : xp(self.attributes, 'Publisher')['v'] } ]
        except KeyError:
            return []

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
    def release_date(self):
        try:
            return parseDateString(xp(self.attributes, 'ReleaseDate')['v'])
        except Exception:
            return ''

    @lazyProperty
    def description(self):
        # TODO: Many of these attributes are common between a bunch of Amazon types. Put them in _AmazonObject.
        try:
            return xp(self.attributes, 'EditorialReview', 'Content')['v']
        except KeyError:
            return ''

    @lazyProperty
    def genres(self):
        try:
            return [ xp(self.attributes, 'Genre')['v'] ]
        except KeyError:
            return []


class AmazonTvShow(_AmazonObject, ResolverMediaCollection):
    # TODO: GEt rid of the copious amount of redundancy between AmazonTvShow and AmazonMovie.
    def __init__(self, amazon_id, data=None, maxLookupCalls=None):
        _AmazonObject.__init__(self, amazon_id, data=data, ResponseGroup='Medium,Reviews')
        ResolverMediaCollection.__init__(self, types=['tv'], maxLookupCalls=maxLookupCalls)
        self._properties.append('salesRank')

    def _cleanName(self, rawName):
        return cleanTvTitle(rawName)

    @lazyProperty
    def cast(self):
        # TODO: These functions are completely fucking repetitive, factor out common code.
        try:
            return [ {'name': actor['v']} for actor in self.attributes['c']['Actor'] ]
        except KeyError:
            return []

    @lazyProperty
    def directors(self):
        try:
            return [ { 'name': xp(self.attributes, 'Director')['v'] } ]
        except KeyError:
            return []

    @lazyProperty
    def studios(self):
        try:
            return [ { 'name': xp(self.attributes, 'Studio')['v'] } ]
        except KeyError:
            return []

    @lazyProperty
    def length(self):
        # Traditionally runtime is reported in minutes, but we want it in seconds.
        unitsConversion = 60
        try:
            units = xp(self.attributes, 'RunningTime')['a']['Units']
            if units != 'minutes':
                raise Exception('Unexpected units found on Amazon movie: (%s)' % units)
        except KeyError:
            pass
        try:
            return float(xp(self.attributes, 'RunningTime')['v']) * unitsConversion
        except KeyError:
            return None

    @lazyProperty
    def mpaa_rating(self):
        try:
            return xp(self.attributes, 'AudienceRating')['v']
        except KeyError:
            return None

    @lazyProperty
    def isbn(self):
        try:
            return xp(self.attributes, 'ISBN')['v']
        except KeyError:
            return None

    @lazyProperty
    def publishers(self):
        try:
            return [ { 'name' : xp(self.attributes, 'Publisher')['v'] } ]
        except KeyError:
            return []

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
    def release_date(self):
        try:
            return parseDateString(xp(self.attributes, 'ReleaseDate')['v'])
        except Exception:
            return ''

    @lazyProperty
    def description(self):
        # TODO: Many of these attributes are common between a bunch of Amazon types. Put them in _AmazonObject.
        try:
            return xp(self.attributes, 'EditorialReview', 'Content')['v']
        except KeyError:
            return ''

    @lazyProperty
    def genres(self):
        try:
            return [ xp(self.attributes, 'Genre')['v'] ]
        except KeyError:
            return []


class AmazonVideoGame(_AmazonObject, ResolverSoftware):
    
    def __init__(self, amazon_id, data=None, maxLookupCalls=None):
        _AmazonObject.__init__(self, amazon_id, data=data, ResponseGroup='Large')
        ResolverSoftware.__init__(self, types=['video_game'], maxLookupCalls=maxLookupCalls)
        self._properties.append('salesRank')
    
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
            return xp(self.data, 'EditorialReview', 'Content')['v']
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

    class SearchIndexData(object):
        """
        Captures our handling of one Amazon search index: the name we have to pass in the search request, the
        ResponseGroups we want that are supported for a request against the index, and a function to create proxies
        for the results. The one ugly piece here right now is that constructor must take both the raw result and a
        'maxLookupCalls' kwarg. It was either this, or make a bunch of lambda functions for the callers since the
        constructors are mostly just Amazon_____ class constructors and for lite search we always want to pass
        maxLookupCalls=0.
        """
        def __init__(self, searchIndexName, responseGroups, proxyConstructor):
            self.searchIndexName = searchIndexName
            self.responseGroups = responseGroups
            self.proxyConstructor = proxyConstructor

    def __searchIndexLite(self, searchIndexData, queryText, results):
        searchResults = globalAmazon().item_search(SearchIndex=searchIndexData.searchIndexName,
            ResponseGroup=searchIndexData.responseGroups, Keywords=queryText, Count=25)
        #print "\n\n\n\nAMAZON\n\n\n\n\n"
        #pprint(searchResults)
        #print "\n\n\n\nENDMAZON\n\n\n\n\n"
        items = xp(searchResults, 'ItemSearchResponse', 'Items')['c']

        if 'Item' in items:
            items = items['Item']
            indexResults = []
            for item in items:
                parsedItem = searchIndexData.proxyConstructor(item, maxLookupCalls=0)
                if parsedItem:
                    indexResults.append(parsedItem)
            results[searchIndexData.searchIndexName] = indexResults

    def __searchIndexesLite(self, searchIndexes, queryText, timeout=None, logRawResults=False):
        """
        Issues searches for the given SearchIndexes and creates ResolverObjects from the results.
        """
        resultsBySearchIndex = {}
        pool = Pool(len(searchIndexes))
        for searchIndexData in searchIndexes:
            pool.spawn(self.__searchIndexLite, searchIndexData, queryText, resultsBySearchIndex)
        pool.join(timeout)
        if logRawResults:
            logComponents = ['\n\n\nAMAZON RAW RESULTS\nAMAZON RAW RESULTS\nAMAZON RAW RESULTS\n\n\n']
            for (searchIndexName, results) in resultsBySearchIndex.items():
                logComponents.append('\n\nAMAZON RESULTS FOR SEARCHINDEX %s\n\n' % searchIndexName)
                logComponents.extend(['\n\n%s\n\n' % pformat(result.data) for result in results])
            logComponents.append('\n\n\nEND AMAZON RAW RESULTS\n\n\n')
            logs.debug(''.join(logComponents))

        return resultsBySearchIndex

    class UnknownTypeError(Exception):
        def __init__(self, details):
            super(AmazonSource.UnknownTypeError, self).__init__(details)

    def __constructMusicObjectFromResult(self, rawResult, maxLookupCalls=None):
        """
        Determines whether the raw result is an album or a track and constructs an _AmazonObject appropriately.
        """
        productTypeName = xp(rawResult, 'ItemAttributes', 'ProductTypeName')['v']
        try:
            binding = xp(rawResult, 'ItemAttributes', 'Binding')['v']
        except KeyError:
            binding = None

        asin = xp(rawResult, 'ASIN')['v']
        if productTypeName == 'DOWNLOADABLE_MUSIC_TRACK':
            return AmazonTrack(asin, data=rawResult, maxLookupCalls=maxLookupCalls)
        elif productTypeName == 'DOWNLOADABLE_MUSIC_ALBUM':
            return AmazonAlbum(asin, data=rawResult, maxLookupCalls=maxLookupCalls)
        elif productTypeName in ['CONTRIBUTOR_AUTHORITY_SET', 'ABIS_DVD', 'VIDEO_VHS', 'DOWNLOADABLE_MUSIC_ARTIST']:
            return None
        elif binding in ['Audio CD', 'Vinyl']:
            return AmazonAlbum(asin, data=rawResult, maxLookupCalls=maxLookupCalls)

        raise AmazonSource.UnknownTypeError('Unknown product type %s seen on result with ASIN %s!' % (productTypeName, asin))

    def __constructVideoObjectFromResult(self, rawResult, maxLookupCalls=None):
        """
        Determines what the raw result is describing. Return AmazonTvShow for TV shows, AmazonMovie for movies, and
        None for things that are neither TV shows nor movies (for instance, TV episodes, movie collections.)
        """

        # TODO: This shit needs some work. It's fairly functional right now but is not to the point of being a clear
        # improvement over video search without Amazon. What we need to do is:
        # 1. Have a standard library for clipping out title nonsense but only when we're really sure -- like when it's
        #    preceded by punctuation.
        # 2. Have a standard library for detecting TV-ness and collection-ness using title nonsense & other attribute.s
        # 3. Have a standard library for detecting things in titles that are likely bullshit, but possibly not.
        # 4. Severely demote or mark as match-only things that either (a) are ambiguous TV-vs-movie, (b) are ambiguous
        #    movie-vs-movie-colleciton, or (b) likely have title bullshit.
        raise NotImplementedError()

        """
        print "CONSTRUCTING FROM RAW OBJECT\n\n"
        pprint(rawResult)
        print "\n\n"

        # TODO: Eliminate code duplication with __constructMusicObjectFromResult!
        productTypeName = xp(rawResult, 'ItemAttributes', 'ProductTypeName')['v']
        try:
            binding = xp(rawResult, 'ItemAttributes', 'Binding')['v']
        except KeyError:
            binding = None
        asin = xp(rawResult, 'ASIN')['v']

        movieLikeliness = 0
        tvShowLikeliness = 0

        if productTypeName == 'DOWNLOADABLE_MOVIE':
            movieLikeliness += 6
        elif productTypeName == 'DOWNLOADABLE_TV_EPISODE':
            pass
        elif productTypeName in ['ABIS_DVD', 'VIDEO_DVD'] and binding in ['DVD', 'Blu-ray']:
            pass
        else:
            logs.warning("Failed to recognize Amazon result with productTypeName " + productTypeName +
                         " binding " + binding)
            return None

        print "AFTER TYPES, WE HAVE:", "movie=", movieLikeliness, "tv=", tvShowLikeliness

        # Look for clues in the title.
        title = xp(rawResult, 'ItemAttributes', 'Title')['v']
        titleWords = title.lower().split()
        if 'complete' in titleWords:
            tvShowLikeliness += 2
        if 'collection' in titleWords:
            tvShowLikeliness += 4
        if 'gift set' in titleWords:
            tvShowLikeliness += 4
        if 'double feature' in titleWords:
            tvShowLikeliness += 4
        if 'season' in titleWords:
            tvShowLikeliness += 4
        if 'episodes' in titleWords:
            tvShowLikeliness += 4
        if 'trilogy' in titleWords:
            tvShowLikeliness += 4
            movieLikeliness += 4
        if 'volume' in titleWords:
            tvShowLikeliness += 4
        if 'the best of' in titleWords:
            tvShowLikeliness += 4

        print "AFTER TITLE HITS, WE HAVE:", "movie=", movieLikeliness, "tv=", tvShowLikeliness

        # Look for clues in the number of discs.
        try:
            numDiscs = int(xp(rawResult, 'ItemAttributes', 'NumberOfDiscs')['v'])
            if numDiscs in (1, 2):
                movieLikeliness += 2
            else:
                tvShowLikeliness += min(4, numDiscs - 3)
        except KeyError:
            pass

        print "AFTER NUM DISCS, WE HAVE:", "movie=", movieLikeliness, "tv=", tvShowLikeliness

        # Look for clues in the running time.
        try:
            runtime = float(xp(rawResult, 'ItemAttributes', 'RunningTime')['v'])
            # Runtime is in minutes.
            if runtime >= 60 and runtime < 120:
                movieLikeliness += 2
            if runtime > 200:
                tvShowLikeliness += 3
            # 2-3h could be a long movie or a short TV show. Probably the former.
            if runtime >= 120 and runtime < 180:
                movieLikeliness += 1
        except KeyError:
            pass

        print "AFTER RUNTIME, WE HAVE:", "movie=", movieLikeliness, "tv=", tvShowLikeliness

        # Look for clues in the pricing.
        try:
            currency = xp(rawResult, 'ItemAttributes', 'ListPrice', 'CurrencyCode')['v']
            if currency == 'USD':
                price = int(xp(rawResult, 'ItemAttributes', 'ListPrice', 'Amount')['v']) / 100.0
                if price > 30:
                    tvShowLikeliness += 3
                elif price < 20:
                    movieLikeliness += 3
        except KeyError:
            pass

        print "AFTER PRICE, WE HAVE:", "movie=", movieLikeliness, "tv=", tvShowLikeliness

        # Look for clues in the rating.
        try:
            rating = xp(rawResult, 'ItemAttributes', 'AudienceRating')['v']
            if rating.find('NR') == 0 or 'Not Rated' in rating or 'Unrated' in rating:
                tvShowLikeliness += 3
            elif tvShowLikeliness > 3:
                # This has a rating, but has all the properties of a collection. It's probably a collection of
                # movies. Drop it.
                print "Probably a collection! Dropping."
                return None
            else:
                movieLikeliness += 5
        except KeyError:
            tvShowLikeliness += 2

        print "AFTER RATING, WE HAVE:", "movie=", movieLikeliness, "tv=", tvShowLikeliness

        if movieLikeliness > 3 and tvShowLikeliness > 3:
            print "CONFLICT! Dropping."
            return None

        if movieLikeliness > tvShowLikeliness:
            result = AmazonMovie(asin, data=rawResult, maxLookupCalls=maxLookupCalls)
            return result
        else:
            result = AmazonTvShow(asin, data=rawResult, maxLookupCalls=maxLookupCalls)
            return result
        """


    def __interleaveAndCombineDupesBasedOnAsin(self, searchResultLists):
        """
        Takes in multiple lists of results of the same type and de-dupes based solely on ASIN. Note that the results of
        this function will not be sorted.
        """
        asinsToResults = {}
        for searchResultList in searchResultLists:
            for searchResult in searchResultList:
                if searchResult.resolverObject.key not in asinsToResults:
                    asinsToResults[searchResult.resolverObject.key] = [searchResult]
                else:
                    asinsToResults[searchResult.resolverObject.key].append(searchResult)

        dedupedResults = []
        for asin, results in asinsToResults.items():
            if len(results) == 1:
                dedupedResults.append(results[0])
                continue
            scores = [ result.relevance for result in results ]
            scores.sort(reverse=True)
            # Flat sum would be too unbalancing.
            totalScore = scores[0] + (0.5 * sum(scores[1:]))
            results[0].relevance = totalScore
            dedupedResults.append(results[0])

        return dedupedResults

    def __adjustScoresBySalesRank(self, resultList):
        """Adjusts the relevance scores of each result based on the sales rank from Amazon.

        The gist of the algorithm is this:
          - Take the log of all sales ranks. These range from 1 to ~1300000 at the time of writing,
            so we end up with ranks in roughly [1, 6].
          - Find mean and stddev of the log of ranks.
          - The relevance adjustment for each result is then how many stddevs is the log of its
            sales rank lower than the mean. Being three stddevs lower will give a boost factor of
            2.0, whereas three stddevs higher will nerf the relevance to 0.
        """
        if len(resultList) < 2:
            return

        # The max rank across a sample was around 1300000 at the time of writing.
        defaultSalesRank = 2000000
        salesRanks = (searchResult.resolverObject.salesRank or defaultSalesRank
                for searchResult in resultList)
        logSalesRanks = [math.log(rank, 10) for rank in salesRanks]
        # TODO(geoff): Use numpy for these computations
        rankMean = float(sum(logSalesRanks)) / len(logSalesRanks)
        rankStdDev = math.sqrt(sum((r - rankMean) ** 2 for r in logSalesRanks) / len(logSalesRanks))
        
        for logRank, searchResult in zip(logSalesRanks, resultList):
            factor = max((rankMean - logRank) / rankStdDev / 3 + 1, 0)
            searchResult.addRelevanceComponentDebugInfo('Amazon salesRank factor', factor)
            searchResult.relevance *= factor

    def __scoreFilmResults(self, resolverObjectsLists):
        scoredTvShows = []
        scoredMovies = []
        for resolverObjectList in resolverObjectsLists:
            scoredList = scoreResultsWithBasicDropoffScoring(resolverObjectList, sourceScore=1.0)
            tvShows = [searchResult for searchResult in scoredList if isinstance(searchResult.resolverObject, AmazonTvShow)]
            movies = [searchResult for searchResult in scoredList if isinstance(searchResult.resolverObject, AmazonMovie)]
            if len(tvShows) + len(movies) != len(scoredList):
                raise Exception('%d of %d elements in Amazon result list unrecognized!' % (
                    len(scoredList), len(scoredList) - len(tvShows) - len(movies)
                ))
            scoredTvShows.append(tvShows)
            scoredMovies.append(movies)

        tvShows = self.__interleaveAndCombineDupesBasedOnAsin(scoredTvShows)
        movies = self.__interleaveAndCombineDupesBasedOnAsin(scoredMovies)

        self.__adjustScoresBySalesRank(tvShows)
        self.__adjustScoresBySalesRank(movies)

        return interleaveResultsByRelevance([tvShows, movies])

    def __scoreMusicResults(self, resolverObjectsLists):
        # TODO: Clean up code duplication with __scoreFilmResults!
        if not resolverObjectsLists:
            return []

        scoredAlbums = []
        scoredTracks = []
        for resolverObjectList in resolverObjectsLists:
            scoredList = scoreResultsWithBasicDropoffScoring(resolverObjectList, sourceScore=0.6)
            albums = [searchResult for searchResult in scoredList if isinstance(searchResult.resolverObject, AmazonAlbum)]
            tracks = [searchResult for searchResult in scoredList if isinstance(searchResult.resolverObject, AmazonTrack)]
            if len(albums) + len(tracks) != len(scoredList):
                raise Exception('%d of %d elements in Amazon result list unrecognized!' % (
                    len(scoredList), len(scoredList) - len(albums) - len(tracks)
                ))

            scoredAlbums.append(albums)
            scoredTracks.append(tracks)

        # We don't really expect any album dupes, but it's very possible that a track will show up for both search
        # indexes. So we do a really simple combination based on ASIN, leaving full de-duping to the EntitySearch
        # object.
        albums = self.__interleaveAndCombineDupesBasedOnAsin(scoredAlbums)
        tracks = self.__interleaveAndCombineDupesBasedOnAsin(scoredTracks)

        self.__adjustScoresBySalesRank(albums)
        self.__adjustScoresBySalesRank(tracks)

        self.__augmentAlbumResultsWithSongs(albums, tracks)

        return interleaveResultsByRelevance([albums, tracks])

    def __scoreBookResults(self, resolverObjectsLists, queryText):
        assert len(resolverObjectsLists) <= 1 
        if len(resolverObjectsLists) == 0:
            return []
        # I use dramatically less dropoff and a huge penalty for missing authors because I'm occasionally getting these
        # complete shit results that I want to drop off the bottom.
        searchResults = scoreResultsWithBasicDropoffScoring(resolverObjectsLists['Books'], dropoffFactor=0.9)
        self.__adjustScoresBySalesRank(searchResults)
        for searchResult in searchResults:
            adjustBookRelevanceByQueryMatch(searchResult, queryText)
            applyBookTitleDataQualityTests(searchResult, queryText)
            if not searchResult.resolverObject.authors:
                penaltyFactor = 0.2
                searchResult.dataQuality *= penaltyFactor
                searchResult.addDataQualityComponentDebugInfo('penalty factor for missing author', penaltyFactor)

            miscComponentsToCheck = ['isbn', 'publishers', 'release_date', 'length', 'sku_number', 'images']
            componentsMissing = [c for c in miscComponentsToCheck if not getattr(searchResult.resolverObject, c)]
            if componentsMissing:
                penalty = 0.8 ** len(componentsMissing)
                searchResult.dataQuality *= penalty
                searchResult.addDataQualityComponentDebugInfo(
                        'penalty factor for missing components: %s' % str(componentsMissing), penalty)
        return searchResults

    def __augmentAlbumResultsWithSongs(self, albums, tracks):
        """
        Boosts the ranks of albums in search if we also see tracks from those albums in the same search results.
        This part is admittedly pretty heinous. Unlike, say, iTunes, Amazon does not tell us the ID or even the name
        of the album for a track, but we can get it through comparing cover art URLs. Ugh.

        Note that albums and tracks are both SearchResult objects. TODO: Should probably change naming to reflect that.

        TODO: We can get tracks now! Use tracks instead.
        """
        picUrlsToAlbums = {}
        for album in albums:
            try:
                largeImageUrl = xp(album.resolverObject.data, 'ImageSets', 'ImageSet', 'LargeImage', 'URL')['v']
                if largeImageUrl in picUrlsToAlbums:
                    logs.warning('Found multiple albums in Amazon results with identical cover art!')
                picUrlsToAlbums[largeImageUrl] = album
            except KeyError:
                pass

        # If there are dupes in the tracks side, we don't want to double-increment artist scores on that basis.
        seenTitlesAndArtists = set()
        for track in tracks:
            simpleTitle = trackSimplify(track.resolverObject.name)
            simpleArtist = ''
            if track.resolverObject.artists:
                simpleArtist = artistSimplify(track.resolverObject.artists[0])
            if (simpleTitle, simpleArtist) in seenTitlesAndArtists:
                continue
            seenTitlesAndArtists.add((simpleTitle, simpleArtist))

            try:
                largeImageUrl = xp(track.resolverObject.data, 'ImageSets', 'ImageSet', 'LargeImage', 'URL')['v']
                if largeImageUrl not in picUrlsToAlbums:
                    continue
                scoreBoost = track.relevance / 5
                album = picUrlsToAlbums[largeImageUrl]
                album.addRelevanceComponentDebugInfo('boost from song %s' % track.resolverObject.name, scoreBoost)
                album.relevance += scoreBoost

            except KeyError:
                pass

    def searchLite(self, queryCategory, queryText, timeout=None, coords=None, logRawResults=False):
        if queryCategory == 'music':
            # We're not passing a constructor, so this will return the raw results. This is because we're not sure if
            # they're songs or albums yet, so there's no straightforward constructor we can pass.
            searchIndexes = (
                AmazonSource.SearchIndexData('Music', 'Medium,Tracks,Reviews', self.__constructMusicObjectFromResult),
                AmazonSource.SearchIndexData('DigitalMusic', 'Medium,Reviews', self.__constructMusicObjectFromResult)
            )
            resultSets = self.__searchIndexesLite(searchIndexes, queryText, timeout=timeout, logRawResults=logRawResults)
            return self.__scoreMusicResults(resultSets.values())
        elif queryCategory == 'book':
            def createBook(rawResult, maxLookupCalls):
                asin = xp(rawResult, 'ASIN')['v']
                return AmazonBook(asin, data=rawResult, maxLookupCalls=maxLookupCalls)
            searchIndexes = (
                    AmazonSource.SearchIndexData('Books', 'Medium,Reviews', createBook),
                )
            resultSets = self.__searchIndexesLite(searchIndexes, queryText, timeout=timeout, logRawResults=logRawResults)
            return self.__scoreBookResults(resultSets, queryText)
        #elif queryCategory == 'film':
        #    searchIndexes = (
        #        AmazonSource.SearchIndexData('Video', 'Medium,Reviews', self.__constructVideoObjectFromResult),
        #        AmazonSource.SearchIndexData('DVD', 'Medium,Reviews', self.__constructVideoObjectFromResult)
        #    )
        #    resultSets = self.__searchIndexesLite(searchIndexes, queryText)
        #    return self.__scoreFilmResults(resultSets.values())
        else:
            raise NotImplementedError('AmazonSource.searchLite() does not handle category (%s)' % queryCategory)

    
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
            lookupData = globalAmazon().item_lookup(ResponseGroup='Large', ItemId=key)
            kind = xp(lookupData, 'ItemLookupResponse','Items','Item','ItemAttributes','ProductGroup')['v'].lower()
            logs.debug(kind)

            # TODO: Avoid additional API calls here.
            
            if kind == 'book':
                return AmazonBook(key)
            if kind == 'digital music album':
                return AmazonAlbum(key)
            if kind == 'digital music track':
                return AmazonTrack(key)
            if kind == 'video games':
                return AmazonVideoGame(key)
            
            raise Exception("unsupported amazon product type: %s" % kind)
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

