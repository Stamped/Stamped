#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'StampedSource', 'EntitySearchAll' ]

import Globals
from logs import report

try:
    import logs
    
    from Resolver                   import *
    from ResolverObject             import *
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    from pprint                     import pformat
    from libs.LibUtils              import parseDateString
    from Schemas                    import BasicEntity
    from datetime                   import datetime
    from bson                       import ObjectId
    from Entity                     import buildEntity
except:
    report()
    raise


class _EntityObject(object):
    """
    Abstract superclass (mixin) for Entity based objects.

    Creates a deepcopy of the entity, accessible via the 'entity' attribute.
    """

    def __init__(self, entity):
        self.__entity = buildEntity(entity.value)

    @property
    def entity(self):
        return self.__entity

    @lazyProperty
    def name(self):
        try:
            return self.entity['title']
        except Exception:
            return ''

    @lazyProperty
    def key(self):
        try:
            return self.entity['entity_id']
        except Exception:
            return ''

    @lazyProperty
    def types(self):
        try:
            return [ str(i) for i in self.entity.types ]
        except:
            return []

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
        return pformat( self.entity.value )


class EntityArtist(_EntityObject, ResolverPerson):
    """
    Entity artist wrapper
    """
    def __init__(self, entity):
        _EntityObject.__init__(self, entity)
        ResolverPerson.__init__(self)

    @lazyProperty
    def albums(self):
        try:
            return [ {'name' : album['title'] } for album in self.entity['albums'] ]
        except Exception:
            return []

    @lazyProperty
    def tracks(self):
        try:
            return [ {'name' : track['title'] } for track in self.entity['tracks'] ]
        except Exception:
            return []


class EntityAlbum(_EntityObject, ResolverMediaCollection):
    """
    Entity album wrapper
    """
    def __init__(self, entity):
        _EntityObject.__init__(self, entity)
        ResolverMediaCollection.__init__(self)

    @lazyProperty
    def artist(self):
        try:
            return { 'name' : self.entity['artists'][0]['title'] }
        except Exception:
            return { 'name' : '' }

    @lazyProperty
    def tracks(self):
        try:
            return [ {'name' : track['title'] } for track in self.entity['tracks'] ]
        except Exception:
            return []


class EntityTrack(_EntityObject, ResolverMediaItem):
    """
    Entity track wrapper
    """
    def __init__(self, entity):
        _EntityObject.__init__(self, entity)
        ResolverMediaItem.__init__(self)

    @lazyProperty
    def artist(self):
        try:
            return { 'name' : self.entity['artists'][0]['title'] }
        except Exception:
            return { 'name' : '' }

    @lazyProperty
    def album(self):
        try:
            return { 'name' : self.entity['collections'][0]['title'] }
        except Exception:
            return { 'name' : '' }

    @lazyProperty
    def length(self):
        try:
            return int(self.entity['length'])
        except Exception:
            return -1


class EntityMovie(_EntityObject, ResolverMediaItem):
    """
    Entity movie wrapper
    """
    def __init__(self, entity):
        _EntityObject.__init__(self, entity)
        ResolverMediaItem.__init__(self)

    @lazyProperty 
    def cast(self):
        try:
            return [ {'name' : item['title'] } for item in self.entity['cast'] ]
        except Exception:
            return []

    @lazyProperty 
    def director(self):
        try:
            return { 'name' : self.entity['directors'][0]['title'] }
        except Exception:
            return { 'name' : '' }

    @lazyProperty 
    def date(self):
        try:
            return self.entity['release_date']
        except Exception:
            return None

    @lazyProperty 
    def length(self):
        try:
            return int(self.entity['length'])
        except Exception:
            return -1

    @lazyProperty 
    def rating(self):
        try:
            return self.entity['mpaa_rating']
        except Exception:
            return None


class EntityBook(_EntityObject, ResolverMediaItem):
    """
    Entity book wrapper
    """
    def __init__(self, entity):
        _EntityObject.__init__(self, entity)
        ResolverMediaItem.__init__(self)

    @lazyProperty
    def author(self):
        try:
            return { 'name' : self.entity['authors'][0]['title'] }
        except Exception:
            return { 'name' : '' }

    @lazyProperty
    def publisher(self):
        try:
            return { 'name' : self.entity['publishers'][0]['title'] }
        except Exception:
            return { 'name' : '' }

    @lazyProperty
    def date(self):
        try:
            return self.entity['release_date']
        except Exception:
            return None

    @lazyProperty
    def length(self):
        try:
            return int(self.entity['length'])
        except Exception:
            return -1

    @lazyProperty
    def isbn(self):
        try:
            return self.entity['isbn']
        except:
            return ''

    @lazyProperty
    def eisbn(self):
        return None

class EntityPlace(_EntityObject, ResolverPlace):

    def __init__(self, entity):
        _EntityObject.__init__(self, entity)
        ResolverPlace.__init__(self)

    @lazyProperty
    def coordinates(self):
        try:
            return (self.entity['lat'], self.entity['lng'])
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
            return self.entity.formatAddress()
        except Exception:
            return ''


class EntitySearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, target):
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)

    @property
    def subtype(self):
        return self.target.type


class StampedSource(GenericSource):
    """
    """
    def __init__(self, stamped_api = None):
        GenericSource.__init__(self, 'stamped',
            groups=['tombstone']
        )
        self._stamped_api = stamped_api
    
    @property 
    def idName(self):
        return 'tombstone'

    @lazyProperty
    def __entityDB(self):
        if not self._stamped_api:
            from MongoStampedAPI import MongoStampedAPI
            self._stamped_api = MongoStampedAPI()
        
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
        return EntityArtist(entity)

    def albumFromEntity(self, entity):
        """
        ResolverAlbum factory method for entities.

        This method may or may not return a simple EntityAlbum or
        it could return a different implementation of ResolverAlbum.
        This method should be used optimistically with the hope that
        should an entity be deficient in some way, StampedSource may be
        able to safely enrich it.
        """
        return EntityAlbum(entity)

    def trackFromEntity(self, entity):
        """
        ResolverTrack factory method for entities.

        This method may or may not return a simple EntityTrack or
        it could return a different implementation of ResolverTrack.
        This method should be used optimistically with the hope that
        should an entity be deficient in some way, StampedSource may be
        able to safely enrich it.
        """
        return EntityTrack(entity)

    def movieFromEntity(self, entity):
        """
        ResolverMovie factory method for entities.

        This method may or may not return a simple EntityTrack or
        it could return a different implementation of ResolverTrack.
        This method should be used optimistically with the hope that
        should an entity be deficient in some way, StampedSource may be
        able to safely enrich it.
        """
        return EntityMovie(entity)

    def bookFromEntity(self, entity):
        """
        """
        return EntityBook(entity)

    def placeFromEntity(self, entity):
        return EntityPlace(entity)

    def wrapperFromEntity(self, entity):
        """
        Generic ResolverObject factory method for entities.

        This method will create a type specific ResolverObject
        based on the type of the given entity.
        """
        sub = entity.subcategory
        if sub == 'song':
            return self.trackFromEntity(entity)
        elif sub == 'album':
            return self.albumFromEntity(entity)
        elif sub == 'artist':
            return self.artistFromEntity(entity)
        elif sub == 'movie':
            return self.movieFromEntity(entity)
        elif sub == 'book':
            return self.bookFromEntity(entity)
        elif sub in set(['restaurant','bar','bakery','cafe','market','food','nightclub']):
            return self.placeFromEntity(entity)
        else:
            raise ValueError('Unrecognized subcategory %s for %s' % (sub, entity['title']))

    def matchSource(self, query):
        if query.kind == 'person':
            return self.artistSource(query)

        ### TODO: Finish this list
        elif query.type == 'album':
            return self.albumSource(query)
        elif query.type == 'track':
            return self.trackSource(query)
        elif query.type == 'movie':
            return self.movieSource(query)
        elif query.type == 'book':
            return self.bookSource(query)
        elif query.type == 'place':
            return self.placeSource(query)
        elif query.type == 'search_all':
            return self.searchAllSource(query)
        else:
            return self.emptySource

    def trackSource(self, query):
        def query_gen():
            try:
                yield {
                    '$and': [
                        {'titlel' : query.name.lower()},
                        {'$or': [
                            {'subcategory': 'song'},
                            {'types': 'song'}
                        ]}
                    ],
                }
                yield {
                    'mangled_title' : trackSimplify( query.name ),
                }
                yield {
                    'details.media.artist_display_title' : query.artist['name'],
                }
                yield {
                    'details.song.album.name': query.album['name'],
                }
            except GeneratorExit:
                pass
        return self.__querySource(query_gen(), query)

    def albumSource(self, query):
        def query_gen():
            try:
                yield {
                    'titlel' : query.name.lower(),
                }
                yield {
                    'mangled_title' : albumSimplify( query.name ),
                }
                yield {
                    'details.media.artist_display_title' : query.artist['name'],
                } 
                yield {
                    '$or': [
                        { 'details.album.tracks': track['name'] }
                            for track in query.tracks
                    ]
                }
            except GeneratorExit:
                pass
        return self.__querySource(query_gen(), query, subcategory='album')

    def artistSource(self, query):
        def query_gen():
            try:
                yield {
                    'titlel'        : query.name.lower(),
                    'types'         : 'artist',
                }
                yield {
                    'titlel'        : query.name.lower(),
                    'subcategory'   : 'artist',
                }
                # yield {
                #     'mangled_title' : artistSimplify( query.name ),
                # }
                yield {
                    '$or': [
                        { 'albums': {'$elemMatch':{ 'title': album['name'] } } }
                            for album in query.albums[20:]
                    ],
                    'types'         : 'artist',
                }
                yield {
                    '$or': [
                        { 'tracks': {'$elemMatch':{ 'title': track['name'] } } }
                            for track in query.tracks[20:]
                    ],
                    'types'         : 'artist',
                }
                yield {
                    '$or': [
                        { 'details.artist.albums': {'$elemMatch':{ 'album_name': album['name'] } } }
                            for album in query.albums[20:]
                    ],
                    'subcategory'   : 'artist',
                }
                yield {
                    '$or': [
                        { 'details.artist.songs': {'$elemMatch':{ 'song_name': track['name'] } } }
                            for track in query.tracks[20:]
                    ],
                    'subcategory'   : 'artist',
                }
            except GeneratorExit:
                pass
        return self.__querySource(query_gen(), query)

    def movieSource(self, query):
        def query_gen():
            try:
                yield {
                    'titlel' : query.name.lower(),
                }
                yield {
                    'mangled_title' : movieSimplify( query.name ),
                }
            except GeneratorExit:
                pass
        return self.__querySource(query_gen(), query, subcategory='movie')

    def bookSource(self, query):
        def query_gen():
            try:
                yield {
                    'titlel' : query.name.lower(),
                }
                yield {
                    'mangled_title' : bookSimplify( query.name ),
                }
                yield {
                    'details.book.author' : query.author['name'],
                }
            except GeneratorExit:
                pass
        return self.__querySource(query_gen(), query, subcategory='book')

    def placeSource(self, query):
        def query_gen():
            try:
                or_clause = [
                    {'subcategory' : 'bar'},
                    {'subcategory' : 'restaurant'},
                ]
                yield {
                    'titlel' : query.name.lower(),
                    '$or' : or_clause,
                }
                yield {
                    'mangled_title' : bookSimplify( query.name ),
                    '$or' : or_clause,
                }
                yield {
                    'details.book.author' : query.author['name'],
                    '$or' : or_clause,
                }
            except GeneratorExit:
                pass
        return self.__querySource(query_gen(), query)

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
        return self.__querySource(query_gen(), query, constructor_wrapper=EntitySearchAll)
    
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
        logs.info(str(mongo_query))
        return list(self.__entityDB._collection.find(mongo_query, fields=['_id'], limit=1000 ).sort('_id',pymongo.ASCENDING))

    def __querySource(self, query_gen, query_obj, constructor_wrapper=None, **kwargs):
        def gen():
            try:
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
                    logs.info('Found %d matches for query: %20s' % (len(matches), str(matches)))
                    #print(matches)
                    for match in matches:
                        entity_id = match['_id']
                        if entity_id not in id_set:
                            yield entity_id
                            id_set.add(entity_id)
            except GeneratorExit:
                pass
        generator = gen()
        
        def constructor(entity_id):
            return self.wrapperFromEntity(
                self.__entityDB.getEntity(
                    self.__entityDB._getStringFromObjectId(entity_id)
                )
            )
        
        if constructor_wrapper is not None:
            return self.generatorSource(generator, lambda x: constructor_wrapper(constructor(x)), unique=True, tolerant=True)
        else:
            return self.generatorSource(generator, constructor=constructor, unique=True, tolerant=True)
    
    @property
    def urlField(self):
        return None
    
    def resolve_fast(self, source, key):
        source_keys = {
            'amazon'            : 'sources.amazon_id', 
            'spotify'           : 'sources.spotify_id', 
            'rdio'              : 'sources.rdio_id', 
            'opentable'         : 'sources.opentable_id', 
            'tmdb'              : 'sources.tmdb_id', 
            'factual'           : 'sources.factual_id', 
            'singleplatform'    : 'sources.singleplatform_id', 
            'fandango'          : 'sources.fandango_id', 
            'googleplaces'      : 'sources.googleplaces_id', 
            'itunes'            : 'sources.itunes_id', 
            'netflix'           : 'sources.netflix.nid', 
            'thetvdb'           : 'sources.thetvdb.thetvdb_id', 
        }
        
        try:
            source_name = source.sourceName.lower().strip()
            mongo_key   = source_keys[source_name]
        except Exception:
            return None
        
        query       = { mongo_key : key }
        entity_id   = None
        logs.info(str(query))
        
        ret         = self.__entityDB._collection.find_one(query, fields=['_id'] )
        
        if ret:
            entity_id = str(ret['_id'])
            logs.info("Resolved '%s' key '%s' to existing entity_id '%s'" % (source_name, key, entity_id))
        
        return entity_id

if __name__ == '__main__':
    demo(StampedSource(), 'Katy Perry')

