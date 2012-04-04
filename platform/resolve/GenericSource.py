#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'GenericSource', 'generatorSource', 'listSource', 'multipleSource' ]

import Globals
from logs import report

try:
    from BasicSource                import BasicSource
    from utils                      import lazyProperty
    from gevent.pool                import Pool
    import logs
    from pprint                     import pprint, pformat
    import sys
    from Resolver                   import *
    from abc                        import ABCMeta, abstractmethod
    from ASourceController          import *
    from Schemas                    import *
except:
    report()
    raise


def generatorSource(generator, constructor=None, unique=False, tolerant=False):
    if constructor is None:
        constructor = lambda x: x
    results = []
    if unique:
        value_set = set()
    def source(start, count):
        total = start + count
        while total - len(results) > 0:
            try:
                value = None
                if tolerant:
                    try:
                        value = constructor(generator.next())
                    except StopIteration:
                        raise
                    except Exception:
                        pass
                else:
                    value = constructor(generator.next())
                if value is not None:
                    if unique:
                        if value not in value_set:
                            results.append(value)
                            value_set.add(value)
                    else:
                        results.append(value)
            except StopIteration:
                break

        if start + count <= len(results):
            result = results[start:start+count]
        elif start < len(results):
            result = results[start:]
        else:
            result = []
        return result
    return source

def listSource(items, **kwargs):
    def gen():
        try:
            for item in items:
                yield item
        except Exception:
            pass
    return generatorSource(gen(), **kwargs)

def multipleSource(source_functions, initial_timeout=None, final_timeout=None, **kwargs):
    def gen():
        try:
            pool = Pool(len(source_functions))
            sources = []
            def helper(source_function):
                source = source_function()
                if source is not None:
                    sources.append(source)
            for source_function in source_functions:
                pool.spawn(helper, source_function)
            pool.join(timeout=initial_timeout)

            offset = 0
            found = True
            while found:
                found = False
                for source in sources:
                    cur = source(offset,1)
                    for item in cur:
                        found = True
                        yield item
                offset += 1
        except GeneratorExit:
            pass
    return generatorSource(gen(),  **kwargs)

class GenericSource(BasicSource):
    """
    """
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        BasicSource.__init__(self, *args, **kwargs)
        self.addGroup(self.sourceName)

    @lazyProperty
    def resolver(self):
        return Resolver()

    @lazyProperty
    def stamped(self):
        import StampedSource
        return StampedSource.StampedSource()

    @abstractmethod
    def matchSource(self, query):
        pass

    def emptySource(self, start, count):
        return []

    def resolve(self, query, **options):
        return self.resolver.resolve(query, self.matchSource(query), **options)
    
    def generatorSource(self, generator, constructor=None, unique=False, tolerant=False):
        return generatorSource(generator, constructor=constructor, unique=unique, tolerant=tolerant)

    def __repopulateAlbums(self, entity, artist, controller, decorations=None):
        if decorations is None:
            decorations = {}

        for album in artist.albums:
            try:
                entityMini  = MediaCollectionEntityMini()
                entityMini.title = album['name']
                if 'key' in album:
                    entityMini.sources['%s_id' % artist.source] = album['key']
                    entityMini.sources['%s_source' % artist.source] = artist.source
                if 'url' in album:
                    entityMini.sources['%s_url' % artist.source] = album['url']
                entity.albums.append(entityMini)
            except Exception:
                report()
                logs.info('Album import failure: %s for artist %s' % (album, artist))

    def __repopulateSongs(self, entity, artist, controller, decorations=None):
        if decorations is None:
            decorations = {}
        for track in artist.tracks:
            try:
                entityMini  = MediaItemEntityMini()
                entityMini.title = track['name']
                entityMini.types.append('song')
                entityMini.types.append('track')
                if 'key' in track:
                    entityMini.sources['%s_id' % artist.source] = track['key']
                    entityMini.sources['%s_source' % artist.source] = artist.source
                if 'url' in track:
                    entityMini.sources['%s_url' % artist.source] = track['url']

                    # Attempt fast resolve
                    # entity_id = self.stamped.resolve_fast(artist.source, track['key'])
                    # to_enrich = decorations.setdefault('track_ids', [])
                    # if entity_id is not None:
                    #     to_enrich.append(('stamped', entity_id))
                    # else:
                    #     to_enrich.append((artist.source, track['key']))

                entity.tracks.append(entityMini)
            except Exception:
                report()
                logs.info('Track import failure: %s for artist %s' % (track, artist))
    
    def wrapperFromKey(self, key, type=None):
        raise NotImplementedError
        return None

    def buildEntityFromWrapper(self, wrapper, controller=None, decorations=None, timestamps=None):
        if wrapper.type == 'place':
            entity = PlaceEntity()
        elif wrapper.type == 'artist':
            entity = PersonEntity()
        elif wrapper.type in set(['album', 'tv']):
            entity = MediaCollectionEntity()
        elif wrapper.type in set(['book', 'movie', 'track']):
            entity = MediaItemEntity()
        elif wrapper.type == 'app':
            entity = SoftwareEntity()
        else:
            entity = BasicEntity()
        
        entity.types = [ wrapper.type ]
        self.enrichEntityWithWrapper(wrapper, entity, controller, decorations, timestamps)
        
        return entity

    def enrichEntityWithWrapper(self, wrapper, entity, controller=None, decorations=None, timestamps=None):
        if controller is None:
            controller = AlwaysSourceController()
        if decorations is None:
            decorations = {}
        if timestamps is None:
            timestamps = {}

        if wrapper.source == 'stamped':
            entity.entity_id = wrapper.key 
        else:
            entity.entity_id = 'T_%s_%s' % (wrapper.source.upper(), wrapper.key)

        def setAttribute(source, target):
            try:
                if wrapper[source] is not None and wrapper[source] != '':
                    entity[target] = wrapper[source]
            except:
                pass

        ### General
        entity.title = wrapper.name 
        if wrapper.description != '':
            entity.desc = wrapper.description
        if wrapper.image != '':
            img = ImageSchema()
            img.image = wrapper.image
            entity.images.append(img)

        setAttribute('phone',   'phone')
        setAttribute('email',   'email')
        setAttribute('url',     'site')

        try:
            if not isType(wrapper.subcategory):
                entity.types.append(wrapper.subcategory)
        except:
            pass

        ### Place
        if entity.kind == 'place':
            try:
                if wrapper.coordinates is not None:
                    entity.coordinates.lat = wrapper.coordinates[0]
                    entity.coordinates.lng = wrapper.coordinates[1]
            except:
                pass

            if len(wrapper.address) > 0:
                address_set = set([
                    'street',
                    'street_ext',
                    'locality',
                    'region',
                    'postcode',
                    'country',
                ])
                for k in address_set:
                    v = None
                    if k in wrapper.address:
                        v = wrapper.address[k]
                    entity['address_%s' % k] = v

            setAttribute('address_string', 'formatted_address')

        ### Person
        if entity.kind == 'person':
            try:
                if len(wrapper.genres) > 0:
                    entity.genres = wrapper.genres
            except:
                pass

            if controller.shouldEnrich('album_list', self.sourceName, entity):
                self.__repopulateAlbums(entity, wrapper, controller, decorations) 

            if controller.shouldEnrich('track_list', self.sourceName, entity):
                self.__repopulateSongs(entity, wrapper, controller, decorations)

        ### Media
        if entity.kind in set(['media_collection', 'media_item']):
            setAttribute('rating', 'mpaa_rating')
            setAttribute('date', 'release_date')

            try:
                if wrapper.length > 0:
                    entity.length = int(wrapper.length)
            except:
                pass

            try:
                if len(wrapper.genres) > 0:
                    entity.genres = wrapper.genres
            except:
                pass

            try:
                if len(wrapper.cast) > 0:
                    for actor in wrapper.cast:
                        entityMini = PersonEntityMini()
                        entityMini.title = actor['name']
                        entity.cast.append(entityMini)
            except:
                pass

            try:
                if wrapper.director['name'] != '':
                    entityMini = PersonEntityMini()
                    entityMini.title = wrapper.director['name']
                    entity.directors.append(entityMini)
            except AttributeError:
                pass

            try:
                if wrapper.publisher['name'] != '':
                    entityMini = PersonEntityMini()
                    entityMini.title = wrapper.publisher['name']
                    entity.publishers.append(entityMini)
            except AttributeError:
                pass

            try:
                if wrapper.author['name'] != '':
                    entityMini = PersonEntityMini()
                    entityMini.title = wrapper.author['name']
                    entity.authors.append(entityMini)
            except AttributeError:
                pass

            try:
                if wrapper.artist['name'] != '':
                    entityMini = PersonEntityMini()
                    entityMini.title = wrapper.artist['name']
                    entityMini.types.append('artist')
                    if 'key' in wrapper.artist:
                        entityMini.sources['%s_id' % wrapper.source] = wrapper.artist['key']
                        entityMini.sources['%s_source' % wrapper.source] = wrapper.source
                    if 'url' in wrapper.artist:
                        entityMini.sources['%s_url' % wrapper.source] = wrapper.artist['url']
                    entity.artists.append(entityMini)
            except AttributeError:
                pass

        ### Media Collection
        if entity.kind == 'media_collection':
            if wrapper.type == 'album' and controller.shouldEnrich('tracks', self.sourceName, entity):
                self.__repopulateSongs(entity, wrapper, controller)

        ### Media Item
        if entity.kind == 'media_item':
            try:
                if wrapper.album['name'] != '':
                    entityMini = MediaCollectionEntityMini()
                    entityMini.title = wrapper.album['name']
                    entityMini.types.append('album')
                    if 'key' in wrapper.album:
                        entityMini.sources['%s_id' % wrapper.source] = wrapper.album['key']
                        entityMini.sources['%s_source' % wrapper.source] = wrapper.source
                    if 'url' in wrapper.album:
                        entityMini.sources['%s_url' % wrapper.source] = wrapper.album['url']
                    entity.collections.append(entityMini)
            except AttributeError:
                pass

            try:
                if wrapper.eisbn is not None:
                    entity.isbn = wrapper.eisbn
                elif wrapper.isbn is not None:
                    entity.isbn = wrapper.isbn
            except AttributeError:
                pass

            try:
                if wrapper.sku is not None:
                    entity.sku_number = wrapper.sku
            except AttributeError:
                pass

        ### Software
        if entity.kind == 'software':
            setAttribute('date', 'release_date')

            try:
                if len(wrapper.genres) > 0:
                    for genre in wrapper.genres:
                        entity.genres.append(genre)
            except:
                pass

            try:
                if wrapper.publisher['name'] != '':
                    entityMini = PersonEntityMini()
                    entityMini.title = wrapper.publisher['name']
                    entity.authors.append(entityMini)
            except:
                pass

            try:
                if len(wrapper.screenshots) > 0:
                    for screenshot in wrapper.screenshots:
                        img = ImageSchema()
                        img.image = screenshot
                        entity.screenshots.append(img)
            except:
                pass

    @property
    def idField(self):
        return "%s_id" % self.idName

    @property
    def urlField(self):
        return "%s_url" % self.idName

    @property 
    def idName(self):
        return self.sourceName

    def enrichEntity(self, entity, controller, decorations, timestamps):
        if controller.shouldEnrich(self.idName, self.sourceName, entity):
            try:
                query = self.stamped.wrapperFromEntity(entity)
                timestamps[self.idName] = controller.now
                results = self.resolver.resolve(query, self.matchSource(query))
                if len(results) != 0:
                    best = results[0]
                    if best[0]['resolved']:
                        entity[self.idField] = best[1].key
                        if self.urlField is not None and best[1].url is not None:
                            entity[self.urlField] = best[1].url
            except ValueError:
                pass
        source_id = entity[self.idField]
        if source_id is not None:
            try:
                wrapper = self.wrapperFromKey(source_id)
                self.enrichEntityWithWrapper(wrapper, entity, controller, decorations, timestamps)
            except Exception:
                print 'Whoops'
        return True

