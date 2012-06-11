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
        # inherit from ResolverObject.
        self.countLookupCall('base data')
        raw = globalAmazon().item_lookup(**self.__params)
        self.__data = xp(raw, 'ItemLookupResponse','Items','Item')

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
        self._properties = self._properties + ['salesRank']

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
            self._issueLookup()
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
        except Exception:
            report()
            return []


class AmazonTrack(_AmazonObject, ResolverMediaItem):

    def __init__(self, amazon_id, data=None, maxLookupCalls=None):
        _AmazonObject.__init__(self, amazon_id, data=data, ResponseGroup='Large,RelatedItems', RelationshipType='Tracks')
        ResolverMediaItem.__init__(self, types=['track'], maxLookupCalls=maxLookupCalls)
        self._properties = self._properties + ['salesRank']

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
            self._issueLookup()
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
        self._properties = self._properties + ['salesRank']

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
    
    def __init__(self, amazon_id, data=None, maxLookupCalls=None):
        _AmazonObject.__init__(self, amazon_id, data=data, ResponseGroup='Large')
        ResolverSoftware.__init__(self, types=['video_game'], maxLookupCalls=maxLookupCalls)
        self._properties = self._properties + ['salesRank']
    
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

    def __searchIndexLite(self, searchIndex, queryText, constructor, results, responseGroup='Medium,Reviews,Tracks'):
        searchResults = globalAmazon().item_search(SearchIndex=searchIndex,
            ResponseGroup=responseGroup, Keywords=queryText)
        # pprint(searchResults)
        items = xp(searchResults, 'ItemSearchResponse', 'Items')['c']

        if 'Item' in items:
            items = items['Item']
            indexResults = []
            for item in items:
                parsedItem = constructor(item, maxLookupCalls=0)
                if parsedItem:
                    indexResults.append(parsedItem)
            results[searchIndex] = indexResults

    def __searchIndexesLite(self, searchIndexes, queryText, constructors=None, constructor=None):
        """
        Issues searches for the given SearchIndexes and creates ResolverObjects from the types using the constructors.
        Callers can either pass a list with one constructor per searchIndex, or a single constructor to be used for
        all searches. The one ugly piece here right now is that constructor must take both the raw result and a
        'maxLookupCalls' kwarg. It was either this, or make a bunch of lambda functions for the callers since the
        constructors are mostly just Amazon_____ class constructors and for lite search we always want to pass
        maxLookupCalls=0.
        """
        if constructors is None and constructor is None:
            raise Exception("One of kwargs 'constructor' and 'constructors' must be passed to __searchIndexesLite!")
        if constructors is not None and constructor is not None:
            raise Exception("Only one of kwargs 'constructor' and 'constructors' can be passed to __searchIndexesLite!")
        if constructor is not None:
            constructors = [constructor] * len(searchIndexes)
        if len(constructors) != len(searchIndexes):
            raise Exception("__searchIndexesLite must have exactly one constructor per search index!")

        resultsBySearchIndex = {}
        pool = Pool(len(searchIndexes))
        for (searchIndex, constructor) in zip(searchIndexes, constructors):
            pool.spawn(self.__searchIndexLite, searchIndex, queryText, constructor, resultsBySearchIndex)
        pool.join()

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
        elif productTypeName in ['CONTRIBUTOR_AUTHORITY_SET', 'ABIS_DVD', 'VIDEO_VHS']:
            return None
        elif binding in ['Audio CD', 'Vinyl']:
            return AmazonAlbum(asin, data=rawResult, maxLookupCalls=maxLookupCalls)

        raise AmazonSource.UnknownTypeError('Unknown product type %s seen on result with ASIN %s!' % (productTypeName, asin))

    def __interleaveAndCombineDupesBasedOnAsin(self, scoredResultLists):
        """
        Takes in multiple lists of results of the same type and de-dupes based solely on ASIN. Note that the results of
        this function will not be sorted.
        """
        asinsToResults = {}
        for scoredResultList in scoredResultLists:
            for scoredResult in scoredResultList:
                if scoredResult.resolverObject.key not in asinsToResults:
                    asinsToResults[scoredResult.resolverObject.key] = [scoredResult]
                else:
                    asinsToResults[scoredResult.resolverObject.key].append(scoredResult)

        dedupedResults = []
        for asin, results in asinsToResults.items():
            if len(results) == 1:
                dedupedResults.append(results[0])
                continue
            scores = [ result.score for result in results ]
            scores.sort(reverse=True)
            # Flat sum would be too unbalancing.
            totalScore = scores[0] + (0.5 * sum(scores[1:]))
            results[0].score = totalScore
            dedupedResults.append(results[0])

        return dedupedResults

    def __scoreMusicResults(self, *unscoredResultsLists):
        if not unscoredResultsLists:
            return []

        scoredAlbums = []
        scoredTracks = []
        for unscoredResultList in unscoredResultsLists:
            scoredList = scoreResultsWithBasicDropoffScoring(unscoredResultList, sourceScore=0.6)
            albums = [scoredResult for scoredResult in scoredList if isinstance(scoredResult.resolverObject, AmazonAlbum)]
            tracks = [scoredResult for scoredResult in scoredList if isinstance(scoredResult.resolverObject, AmazonTrack)]

            scoredAlbums.append(albums)
            scoredTracks.append(tracks)

        print "scoredAlbums contains lengths:", [str(len(lst)) for lst in scoredAlbums]
        print "scoredTracks contains lengths:", [str(len(lst)) for lst in scoredTracks]

        # We don't really expect any album dupes, but it's very possible that a track will show up for both search
        # indexes. So we do a really simple combination based on ASIN, leaving full de-duping to the EntitySearch
        # object.
        albums = self.__interleaveAndCombineDupesBasedOnAsin(scoredAlbums)
        tracks = self.__interleaveAndCombineDupesBasedOnAsin(scoredTracks)

        for searchResult in albums + tracks:
            salesRank = searchResult.resolverObject.salesRank
            if salesRank:
                # TODO: TWEAK THIS MATH. This will be fucking ridiculous with something with salesRank=1. It needs to be
                # a lot smoother.
                searchResult.score *= (5000 / searchResult.resolverObject.salesRank) ** 0.2
            else:
                # Not a lot of trust in things without sales rank. (TODO: Is this justified?)
                searchResult.score *= 0.6
        self.__augmentAlbumResultsWithSongs(albums, tracks)

        return interleaveResultsByScore([albums, tracks])

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
            print "HANDLING", track.resolverObject.key
            if track.resolverObject.artists:
                simpleArtist = artistSimplify(track.resolverObject.artists[0])
            if (simpleTitle, simpleArtist) in seenTitlesAndArtists:
                continue
            seenTitlesAndArtists.add((simpleTitle, simpleArtist))

            try:
                largeImageUrl = xp(track.resolverObject.data, 'ImageSets', 'ImageSet', 'LargeImage', 'URL')['v']
                if largeImageUrl not in picUrlsToAlbums:
                    continue
                scoreBoost = track.score / 5
                album = picUrlsToAlbums[largeImageUrl]
                album.addScoreComponentDebugInfo('boost from song %s' % track.resolverObject.name, scoreBoost)
                album.score += scoreBoost

            except KeyError:
                pass

    def searchLite(self, queryCategory, queryText):
        if queryCategory == 'music':
            # We're not passing a constructor, so this will return the raw results. This is because we're not sure if
            # they're songs or albums yet, so there's no straightforward constructor we can pass.
            resultSets = self.__searchIndexesLite(['Music', 'DigitalMusic'], queryText,
                constructor=self.__constructMusicObjectFromResult)
            return self.__scoreMusicResults(resultSets.items())
        elif queryCategory == 'book':
            searchIndexes = [ 'Books' ]
        elif queryCategory == 'film':
            searchIndexes = [ 'Video' ] #TODO: Is this right?
    
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

