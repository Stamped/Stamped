#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'StampedSource',
            'EntityProxyArtist', 'EntityProxyAlbum', 'EntityProxyTrack', 'EntityProxyMovie', 'EntityProxyTV',
            'EntityProxyBook', 'EntityProxyPlace', 'EntityProxyApp', 'EntitySearchAll']

import Globals
from logs import report
import re

try:
    import logs
    
    from resolve.Resolver                   import *
    from resolve.ResolverObject             import *
    from resolve.GenericSource              import GenericSource
    from utils                      import lazyProperty
    from pprint                     import pformat
    from libs.LibUtils              import parseDateString
    from api.Schemas                import BasicEntity
    from api.Schemas                    import BasicEntityMini as BasicEntityMini1
    from api.Schemas                import BasicEntityMini as BasicEntityMini2
    from datetime                   import datetime
    from bson                       import ObjectId
    from api.Entity                     import buildEntity

    # TODO GET RID OF SEARCH IMPORTS
    from search.SearchResult import SearchResult
    from search.ScoringUtils import *
    from api.db.mongodb.MongoEntityStatsCollection import MongoEntityStatsCollection

    from libs.SearchUtils import formatSearchQuery
except:
    report()
    raise


class _EntityProxyObject(object):
    """
    Abstract superclass (mixin) for Entity based objects.

    Creates a deepcopy of the entity, accessible via the 'entity' attribute.
    """

    def __init__(self, entity):
        self.__entity = buildEntity(entity.dataExport())

    @property
    def entity(self):
        return self.__entity

    @lazyProperty
    def raw_name(self):
        try:
            return self.entity.title
        except Exception:
            return ''

    @lazyProperty
    def key(self):
        try:
            return self.entity.entity_id
        except Exception:
            return None

    @property 
    def source(self):
        return "stamped"

    @lazyProperty
    def subcategory(self):
        try:
            return self.entity.subcategory
        except Exception:
            return 'other'

    def __repr__(self):
        return pformat( self.entity )


class EntityProxyArtist(_EntityProxyObject, ResolverPerson):
    """
    Entity artist proxy
    """
    def __init__(self, entity):
        _EntityProxyObject.__init__(self, entity)
        ResolverPerson.__init__(self, types=entity.types)

    def _cleanName(self, rawName):
        # No processing happens after it's already become an entity.
        return rawName

    @lazyProperty
    def albums(self):
        try:
            return [ { 'name' : item.title } for item in self.entity.albums ]
        except Exception:
            return []

    @lazyProperty
    def tracks(self):
        try:
            return [ { 'name' : item.title } for item in self.entity.tracks ]
        except Exception:
            return []


class EntityProxyAlbum(_EntityProxyObject, ResolverMediaCollection):
    """
    Entity album proxy
    """
    def __init__(self, entity):
        _EntityProxyObject.__init__(self, entity)
        ResolverMediaCollection.__init__(self, types=entity.types)

    def _cleanName(self, rawName):
        # No processing happens after it's already become an entity.
        return rawName

    @lazyProperty
    def artists(self):
        try:
            return [ { 'name' : item.title } for item in self.entity.artists ]
        except Exception:
            return []

    @lazyProperty
    def tracks(self):
        try:
            return [ { 'name' : item.title } for item in self.entity.tracks ]
        except Exception:
            return []


class EntityProxyTrack(_EntityProxyObject, ResolverMediaItem):
    """
    Entity track proxy
    """
    def __init__(self, entity):
        _EntityProxyObject.__init__(self, entity)
        ResolverMediaItem.__init__(self, types=entity.types)

    def _cleanName(self, rawName):
        # No processing happens after it's already become an entity.
        return rawName

    @property # @lazyProperty
    def artists(self):
        try:
            return [ { 'name' : item.title } for item in self.entity.artists ]
        except Exception:
            return []

    @lazyProperty
    def albums(self):
        try:
            return [ { 'name' : item.title } for item in self.entity.albums ]
        except Exception:
            return []

    @lazyProperty
    def length(self):
        try:
            return int(self.entity.length)
        except Exception:
            return -1

def _fixCast(cast):
    newcast = []
    if not cast:
        return newcast
    try:
        if (isinstance(cast, list) or isinstance(cast, tuple)) and \
           (isinstance(cast[0], BasicEntityMini1) or isinstance(cast[0], BasicEntityMini2)):
            return [{'name': person.title} for person in cast]
        # if it's just a string, construct a list of dictionaries with 'title' keys
        if isinstance(cast, basestring):
            print('converting cast from string')
            names = cast.split(',')
            cast = list()
            for name in names:
                cast.append( {'name': name} )
            print('converted cast: %s' % cast)
        for item in cast:
            name = item.get('title', None)
            character = item.get('character', None)
            if name is None:
                continue
            m = re.match(r'(.+) as (.+)', name)
            if m is not None:
                name = m.group(1)
                character = m.group(2)
            newitem = dict()
            newitem['name'] = name
            if character is not None:
                newitem['character'] = character
            newcast.append(newitem)
    except Exception as e:
        print('FIXCAST ERROR: %s' % e)
        import traceback
        traceback.print_stack()
    return newcast


class EntityProxyMovie(_EntityProxyObject, ResolverMediaItem):
    """
    Entity movie proxy
    """
    def __init__(self, entity):
        _EntityProxyObject.__init__(self, entity)
        ResolverMediaItem.__init__(self, types=entity.types)

    def _cleanName(self, rawName):
        # No processing happens after it's already become an entity.
        return rawName

    @lazyProperty 
    def cast(self):
        try:
            return _fixCast(self.entity.cast)#[ { 'name' : item.title } for item in self.entity.cast ]
        except Exception:
            return []

    @lazyProperty 
    def directors(self):
        try:
            return [ { 'name' : item.title } for item in self.entity.directors ]
        except Exception:
            return []

    @lazyProperty 
    def release_date(self):
        try:
            return self.entity.release_date
        except Exception:
            return None

    @lazyProperty 
    def length(self):
        try:
            return int(self.entity.length)
        except Exception:
            return -1

    @lazyProperty 
    def mpaa_rating(self):
        try:
            return self.entity.mpaa_rating
        except Exception:
            return None


class EntityProxyTV(_EntityProxyObject, ResolverMediaCollection):
    """
    Entity tv proxy
    """
    def __init__(self, entity):
        _EntityProxyObject.__init__(self, entity)
        ResolverMediaCollection.__init__(self, types=entity.types)

    def _cleanName(self, rawName):
        # No processing happens after it's already become an entity.
        return rawName

    @lazyProperty
    def cast(self):
        try:
            return _fixCast(self.entity.cast)# [ { 'name' : item.title } for item in self.entity.cast ]
        except Exception:
            return []

    @lazyProperty 
    def directors(self):
        try:
            return [ { 'name' : item.title } for item in self.entity.directors ]
        except Exception:
            return []

    @lazyProperty 
    def length(self):
        try:
            return int(self.entity.length)
        except Exception:
            return -1

    @lazyProperty 
    def rating(self):
        try:
            return self.entity.mpaa_rating
        except Exception:
            return None


class EntityProxyBook(_EntityProxyObject, ResolverMediaItem):
    """
    Entity book proxy
    """
    def __init__(self, entity):
        _EntityProxyObject.__init__(self, entity)
        ResolverMediaItem.__init__(self, types=entity.types)

    def _cleanName(self, rawName):
        # No processing happens after it's already become an entity.
        return rawName

    @lazyProperty
    def authors(self):
        try:
            return [ { 'name' : item.title } for item in self.entity.authors ]
        except Exception:
            return []

    @lazyProperty 
    def publishers(self):
        try:
            return [ { 'name' : item.title } for item in self.entity.publishers ]
        except Exception:
            return []

    @lazyProperty
    def release_date(self):
        try:
            return self.entity.release_date
        except Exception:
            return None

    @lazyProperty
    def length(self):
        try:
            return int(self.entity.length)
        except Exception:
            return -1

    @lazyProperty
    def isbn(self):
        try:
            return self.entity.isbn
        except:
            return ''

class EntityProxyPlace(_EntityProxyObject, ResolverPlace):

    def __init__(self, entity):
        _EntityProxyObject.__init__(self, entity)
        ResolverPlace.__init__(self, types=entity.types)

    def _cleanName(self, rawName):
        # No processing happens after it's already become an entity.
        return rawName

    @lazyProperty
    def coordinates(self):
        try:
            return (self.entity.coordinates.lat, self.entity.coordinates.lng)
        except Exception:
            return None

    @lazyProperty
    def address(self):
        try:
            return {
                'address':  self.entity.address_street,
                'locality': self.entity.address_locality,
                'region':   self.entity.address_region,
                'postcode': self.entity.address_postcode,
                'country':  self.entity.address_country,
            }
        except Exception:
            return ''

    @lazyProperty
    def address_string(self):
        try:
            return self.entity.formatAddress()
        except Exception:
            return ''

    @lazyProperty
    def phone(self):
        return self.entity.phone


class EntityProxyApp(_EntityProxyObject, ResolverSoftware):
    """
    Entity app proxy
    """
    def __init__(self, entity):
        _EntityProxyObject.__init__(self, entity)
        ResolverSoftware.__init__(self, types=entity.types)

    def _cleanName(self, rawName):
        # No processing happens after it's already become an entity.
        return rawName

    @lazyProperty
    def release_date(self):
        try:
            return self.entity.release_date
        except Exception:
            return None

    @lazyProperty 
    def authors(self):
        try:
            return [ { 'name' : item.title } for item in self.entity.authors ]
        except Exception:
            return []


class EntitySearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, target):
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)


class StampedSource(GenericSource):
    def __init__(self, stamped_api = None):
        GenericSource.__init__(self, 'stamped', 
            groups=['tombstone'],
            kinds=[
                'person',
                'place',
                'media_collection',
                'media_item',
                'software',
            ]
        )
        
        self._stamped_api = stamped_api
    
    @property 
    def idName(self):
        return 'tombstone'

    @lazyProperty
    def __entityDB(self):
        if not self._stamped_api:
            from api import MongoStampedAPI
            self._stamped_api = MongoStampedAPI.globalMongoStampedAPI()
        
        return self._stamped_api._entityDB
    
    def artistFromEntity(self, entity):
        """
        ResolverArtist factory method for entities.

        This method may or may not return a simple EntityArtist or
        it could return a different implementation of ResolverArtist.
        This method should be used optimistically with the hope that
        should an entity be deficient in some way, StampedSource may be
        able to safely enrich it.
        """
        return EntityProxyArtist(entity)

    def albumFromEntity(self, entity):
        """
        ResolverAlbum factory method for entities.

        This method may or may not return a simple EntityAlbum or
        it could return a different implementation of ResolverAlbum.
        This method should be used optimistically with the hope that
        should an entity be deficient in some way, StampedSource may be
        able to safely enrich it.
        """
        return EntityProxyAlbum(entity)

    def trackFromEntity(self, entity):
        """
        ResolverTrack factory method for entities.

        This method may or may not return a simple EntityTrack or
        it could return a different implementation of ResolverTrack.
        This method should be used optimistically with the hope that
        should an entity be deficient in some way, StampedSource may be
        able to safely enrich it.
        """
        return EntityProxyTrack(entity)

    def movieFromEntity(self, entity):
        """
        ResolverMovie factory method for entities.

        This method may or may not return a simple EntityTrack or
        it could return a different implementation of ResolverTrack.
        This method should be used optimistically with the hope that
        should an entity be deficient in some way, StampedSource may be
        able to safely enrich it.
        """
        return EntityProxyMovie(entity)

    def tvFromEntity(self, entity):
        """
        ResolverMovie factory method for entities.

        This method may or may not return a simple EntityTrack or
        it could return a different implementation of ResolverTrack.
        This method should be used optimistically with the hope that
        should an entity be deficient in some way, StampedSource may be
        able to safely enrich it.
        """
        return EntityProxyTV(entity)

    def bookFromEntity(self, entity):
        """
        """
        return EntityProxyBook(entity)

    def placeFromEntity(self, entity):
        return EntityProxyPlace(entity)

    def appFromEntity(self, entity):
        return EntityProxyApp(entity)

    def proxyFromEntity(self, entity):
        """
        Generic ResolverObject factory method for entities.

        This method will create a type specific ResolverObject
        based on the type of the given entity.
        """
        if entity.kind == 'person':
            if entity.isType('artist'):
                return self.artistFromEntity(entity)

        if entity.kind == 'place':
            return self.placeFromEntity(entity)

        if entity.kind == 'media_collection':
            if entity.isType('album'):
                return self.albumFromEntity(entity)
            if entity.isType('tv'):
                return self.tvFromEntity(entity)

        if entity.kind == 'media_item':
            if entity.isType('track'):
                return self.trackFromEntity(entity)
            if entity.isType('movie'):
                return self.movieFromEntity(entity)
            if entity.isType('book'):
                return self.bookFromEntity(entity)

        if entity.kind == 'software':
            if entity.isType('app'):
                return self.appFromEntity(entity)

        raise ValueError('Unrecognized entity %s (%s)' % (entity.title, entity))
    
    def matchSource(self, query):
        if query.kind == 'search':
            return self.searchAllSource(query)

        if query.kind == 'person':
            return self.artistSource(query)
        if query.kind == 'place':
            return self.placeSource(query)
        if query.kind == 'media_collection':
            if query.isType('album'):
                return self.albumSource(query)
            if query.isType('tv'):
                return self.tvSource(query)
        if query.kind == 'media_item':
            if query.isType('track'):
                return self.trackSource(query)
            if query.isType('movie'):
                return self.movieSource(query)
            if query.isType('book'):
                return self.bookSource(query)
        if query.kind == 'software':
            if query.isType('app'):
                return self.appSource(query)

        return self.emptySource

    def trackSource(self, query):
        def query_gen():
            yield {
                'titlel'        : query.name.lower(),
                'types'         : 'track',
            }
            yield {
                'titlel'        : query.name.lower(),
                'subcategory'   : 'song',
            }
            yield {
                'albums.title': {'$in': [album['name'] for album in query.albums[:20]]},
                'types'         : 'track',
            }
            yield {
                'artists.title': {'$in': [artist['name'] for artist in query.artists[:20]]},
                'types'         : 'track',
            }
        return self.__querySource(query_gen(), query)

    def albumSource(self, query):
        def query_gen():
            yield {
                'titlel'        : query.name.lower(),
                'types'         : 'album',
            }
            yield {
                'titlel'        : query.name.lower(),
                'subcategory'   : 'album',
            }
            yield {
                'artists.title': {'$in': [artist['name'] for artist in query.artists[:20]]},
                'types'         : 'album',
            }
            yield {
                'tracks.title': {'$in': [track['name'] for track in query.tracks[:20]]},
                'types'         : 'album',
            }
        return self.__querySource(query_gen(), query)

    def artistSource(self, query):
        def query_gen():
            yield {
                'titlel'        : query.name.lower(),
                'types'         : 'artist',
            }
            yield {
                'titlel'        : query.name.lower(),
                'subcategory'   : 'artist',
            }
            yield {
                'albums.title': {'$in': [album['name'] for album in query.albums[:20]]},
                'types'         : 'artist',
            }
            yield {
                'tracks.title': {'$in': [track['name'] for track in query.tracks[:20]]},
                'types'         : 'artist',
            }
        return self.__querySource(query_gen(), query)

    def movieSource(self, query):
        def query_gen():
            yield {
                'titlel'        : query.name.lower(),
                'types'         : 'movie',
            }
            yield {
                'titlel'        : query.name.lower(),
                'subcategory'   : 'movie',
            }
        return self.__querySource(query_gen(), query)

    def tvSource(self, query):
        def query_gen():
            yield {
                'titlel'        : query.name.lower(),
                'types'         : 'tv',
            }
            yield {
                'titlel'        : query.name.lower(),
                'subcategory'   : 'tv',
            }
        return self.__querySource(query_gen(), query)

    def bookSource(self, query):
        def query_gen():
            yield {
                'titlel'        : query.name.lower(),
                'types'         : 'book',
            }
            yield {
                'titlel'        : query.name.lower(),
                'subcategory'   : 'book',
            }
            yield {
                'authors.title': {'$in': [author['name'] for author in query.authors[:20]]},
                'types'         : 'book',
            }
        return self.__querySource(query_gen(), query)

    def appSource(self, query):
        def query_gen():
            yield {
                'titlel'        : query.name.lower(),
                'types'         : 'app',
            }
            yield {
                'titlel'        : query.name.lower(),
                'subcategory'   : 'app',
            }
        return self.__querySource(query_gen(), query)

    def placeSource(self, query):
        def query_gen():
            yield {
                'titlel'        : query.name.lower(),
                'kind'          : 'place',
            }
            yield {
                'titlel'        : query.name.lower(),
                'subcategory'   : {'$in' : ['bar', 'restaurant']},
            }
        return self.__querySource(query_gen(), query)

    def searchLite(self, queryCategory, queryText, timeout=None, coords=None, logRawResults=False):
        tokenQueries = formatSearchQuery(queryText)
        if queryCategory == 'film':
            query = {
                '$and' : tokenQueries + [ {
                    '$or' : [
                        { 'types' : { '$in' : [ 'tv', 'movie' ] } },
                        { 'subcategory' : { '$in' : [ 'tv', 'movie' ] } },
                    ]
                } ],
            }
        elif queryCategory == 'music':
            query = {
                '$and' : tokenQueries + [ {
                    '$or' : [
                            { 'types' : { '$in' : [ 'artist', 'album', 'track' ] } },
                            { 'subcategory' : { '$in' : [ 'artist', 'album', 'song' ] } },
                    ]
                } ],
            }
        elif queryCategory == 'place':
            query = {
                '$and' : tokenQueries + [ {
                    '$or' : [
                            { 'kind' : 'place' },
                            { 'subcategory' : { '$in' : [ 'bar', 'restaurant' ] } },
                    ]
                } ],
            }
        elif queryCategory == 'app':
            query = {
                '$and' : tokenQueries + [ {
                    '$or' : [
                            { 'types' : 'app' },
                            { 'subcategory' : 'app' },
                    ]
                } ],
            }
        elif queryCategory == 'book':
            query = {
                '$and' : tokenQueries + [ {
                    '$or' : [
                            { 'types' : 'book' },
                            { 'subcategory' : 'book' },
                    ]
                } ],
            }
        else:
            raise NotImplementedError()
        # Exclude tombstoned listings.
        and_list = query.setdefault('$and',[])
        and_list.append( {
            '$or' : [
                    {'sources.tombstone_id' : { '$exists':False }},
                    {'sources.tombstone_id' : None},
            ]
        } )
        matches = list(self.__id_query(query))
        entityIds = [ match['_id'] for match in matches ]
        # TODO: Should just retrieve all of this from the initial query!
        entityProxies = [ self.entityProxyFromKey(entityId) for entityId in entityIds ]
        if logRawResults:
            logComponents = ['\n\n\nSTAMPED RAW RESULTS\nSTAMPED RAW RESULTS\nSTAMPED RAW RESULTS\n\n\n']
            logComponents.extend(['\n\n%s\n\n' % str(proxy.entity) for proxy in entityProxies])
            logComponents.append('\n\n\nEND STAMPED RAW RESULTS\n\n\n')
            logs.debug(''.join(logComponents))
        entityStats = MongoEntityStatsCollection().getStatsForEntities(entityIds)
        statsByEntityId = dict([(stats.entity_id, stats) for stats in entityStats])
        results = []
        for entityProxy in entityProxies:
            stats = statsByEntityId.get(entityProxy.key, None)
            # Use fairly conservative scoring now for StampedSource on the assumption that it will probably cluster
            # with other stuff.
            num_stamps = 0 if stats is None else stats.num_stamps
            result = SearchResult(entityProxy)
            result.relevance = 0.3 + 0.2 * (num_stamps ** 0.5)
            result.addRelevanceComponentDebugInfo('Initial score based on Entity with %d stamps' % num_stamps,
                                                  result.relevance)
            results.append(result)
        sortByRelevance(results)
        return results


    def searchAllSource(self, query, timeout=None):
        def query_gen():
            try:
                # Exact match
                yield {
                    'titlel' : query.query_string.lower(),
                }

                words = query.query_string.lower().split()
                if len(words) == 1:
                    return

                # Pair prefix
                yield {
                    '$or' : [
                        {
                            'titlel' : {
                                '$regex' : r"^%s %s( .*)?$" % (words[i], words[i+1])
                            }
                        }
                            for i in xrange(len(words) - 1)
                    ]
                }

                blacklist = set([
                    'the',
                    'a',
                    'an',
                ])

                yield {
                    '$or' : [
                        {
                            'titlel' : {
                                '$regex' : r"^%s( .*)?$" % (word)
                            }
                        }
                            for word in words if word not in blacklist
                    ]
                }

                # Pair regex
                yield {
                    '$or' : [
                        {
                            'titlel' : {
                                '$regex' : r"^(.* )?%s %s( .*)?$" % (words[i], words[i+1])
                            }
                        }
                            for i in xrange(len(words) - 1)
                    ]
                }
                """
                blacklist = set([
                    'and',
                    'or',
                    'in',
                    'the',
                    'a',
                    'an',
                    'of',
                    'on',
                    'movie',
                ])

                # Word regex
                yield {
                    '$or' : [
                        {
                            'titlel' : {
                                '$regex' : r"^(.* )?%s( .*)?$" % word
                            }
                        }
                            for word in simplify(query.query_string).split()
                                if word not in blacklist
                    ]
                }
                """
            except GeneratorExit:
                pass
        return self.__querySource(query_gen(), query, constructor_proxy=EntitySearchAll)

    """
    def enrichEntity(self, entity, controller, decorations, timestamps):
        if controller.shouldEnrich('tombstone', self.sourceName, entity):
            try:
                query = self.wrapperFromEntity(entity)
                timestamps['tombstone'] = controller.now
                mins = None
                if query.type == 'artist':
                    mins = {
                        'name':.1,
                        'albums':.1,
                        'tracks':-1,
                        'total':-1,
                    }
                results = self.resolver.resolve(query, self.matchSource(query), mins=mins)
                if len(results) != 0:
                    best = results[0]
                    if best[0]['resolved']:
                        entity[self.idField] = best[1].key
                        if self.urlField is not None and best[1].url is not None:
                            entity[self.urlField] = best[1].url
            except ValueError:
                pass
        return True
        """
    
    def __id_query(self, mongo_query):
        import pymongo
        #print(pformat(mongo_query))
        logs.debug(str(mongo_query))
        return list(self.__entityDB._collection.find(mongo_query, fields=['_id'], limit=1000).sort('_id',pymongo.ASCENDING))

    def __querySource(self, query_gen, query_obj, constructor_proxy=None, **kwargs):
        def gen():
            id_set = set()
            for query in query_gen:
                for k,v in kwargs.items():
                    query[k] = v
                
                and_list = query.setdefault('$and',[])
                and_list.append( {
                    '$or' : [
                        {'sources.tombstone_id' : { '$exists':False }},
                        {'sources.tombstone_id' : None},
                    ]
                } )
                if query_obj.source == 'stamped' and query_obj.key != '':
                    query['_id'] = { '$lt' : ObjectId(query_obj.key) }
                matches = self.__id_query(query)
                logs.debug('Found %d matches for query: %20s' % (len(matches), str(matches)))
                #print(matches)
                for match in matches:
                    entity_id = match['_id']
                    if entity_id not in id_set:
                        yield entity_id
                        id_set.add(entity_id)
        generator = gen()
        
        def constructor(entity_id):
            return self.proxyFromEntity(
                self.__entityDB.getEntity(
                    self.__entityDB._getStringFromObjectId(entity_id)
                )
            )
        
        if constructor_proxy is not None:
            return self.generatorSource(generator, lambda x: constructor_proxy(constructor(x)), unique=True, tolerant=True)
        else:
            return self.generatorSource(generator, constructor=constructor, unique=True, tolerant=True)

    def entityProxyFromKey(self, entity_id, **kwargs):
        return self.proxyFromEntity(self.__entityDB.getEntity(entity_id))

    @property
    def urlField(self):
        return None
    
    def resolve_fast_batch(self, sourcesAndKeys):
        SOURCES = set(['amazon', 'spotify', 'rdio', 'opentable', 'tmdb', 'factual', 'instagram',
                'singleplatform', 'foursquare', 'fandango', 'googleplaces', 'itunes', 'netflix',
                'thetvdb'])
        mongoQueries = []
        queryPairs = []
        for source, key in sourcesAndKeys:
            source_name = source.lower().strip()
            sourceIdField = source_name + '_id'
            queryPairs.append((sourceIdField, key))
            if source_name in SOURCES:
                mongoQueries.append({'sources.' + sourceIdField : key})
        
        query = mongoQueries[0] if len(mongoQueries) == 1 else {'$or' : mongoQueries}
        results = self.__entityDB._collection.find(query, fields=['sources'])

        # TODO PRELAUNCH FUCK FUCK FUCK CHECK FOR TOMBSTONE IDS
        sourceIdsToEntityId = {}
        for result in results:
            sourceIds = result['sources']
            for k, v in sourceIds.iteritems():
                if k.endswith('_id'):
                    sourceIdsToEntityId[k,v] = str(result['_id'])

        return [sourceIdsToEntityId.get(query, None) for query in queryPairs]

    def resolve_fast(self, source, key):
        return self.resolve_fast_batch([(source, key)])[0]

if __name__ == '__main__':
    demo(StampedSource(), 'Katy Perry')

