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
    import logs, sys
    from BasicSource                import BasicSource
    from utils                      import lazyProperty
    from gevent.pool                import Pool
    from pprint                     import pprint, pformat
    from abc                        import ABCMeta, abstractmethod
    from Resolver                   import *
    from ResolverObject             import *
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
            
            def _helper(source_function):
                source = source_function()
                if source is not None:
                    sources.append(source)
            
            for source_function in source_functions:
                pool.spawn(_helper, source_function)
            
            pool.join(timeout=initial_timeout)
            
            offset = 0
            found  = True
            
            while found:
                found = False
                
                for source in sources:
                    cur = source(offset, 1)
                    
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
                entity.tracks.append(entityMini)
            except Exception:
                report()
                logs.info('Track import failure: %s for artist %s' % (track, artist))
    
    def entityProxyFromKey(self, key, type=None):
        raise NotImplementedError
    
    def buildEntityFromEntityProxy(self, proxy, controller=None, decorations=None, timestamps=None):
        if proxy.kind == 'place':
            entity = PlaceEntity()
        elif proxy.kind == 'person':
            entity = PersonEntity()
        elif proxy.kind == 'media_collection':
            entity = MediaCollectionEntity()
        elif proxy.kind == 'media_item':
            entity = MediaItemEntity()
        elif proxy.kind == 'software':
            entity = SoftwareEntity()
        else:
            entity = BasicEntity()
        
        self.enrichEntityWithEntityProxy(proxy, entity, controller, decorations, timestamps)
        
        return entity
    
    def enrichEntityWithEntityProxy(self, proxy, entity, controller=None, decorations=None, timestamps=None):
        if controller is None:
            controller = AlwaysSourceController()
        if decorations is None:
            decorations = {}
        if timestamps is None:
            timestamps = {}
        
        if proxy.source == 'stamped':
            entity.entity_id = proxy.key 
        else:
            entity.entity_id = 'T_%s_%s' % (proxy.source.upper(), proxy.key)
        
        def setAttribute(source, target):
            try:
                if proxy[source] is not None and proxy[source] != '':
                    entity[target] = proxy[source]
            except:
                pass
        
        ### General
        entity.title = proxy.name 
        if proxy.description != '':
            entity.desc = proxy.description
        if proxy.image != '':
            img = ImageSchema()
            img.image = proxy.image
            entity.images.append(img)
        
        setAttribute('phone',   'phone')
        setAttribute('email',   'email')
        setAttribute('url',     'site')
        
        entity.types = proxy.types

        
        ### Place
        if entity.kind == 'place':
            try:
                if proxy.coordinates is not None:
                    entity.coordinates.lat = proxy.coordinates[0]
                    entity.coordinates.lng = proxy.coordinates[1]
            except:
                pass

            if len(proxy.address) > 0:
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
                    if k in proxy.address:
                        v = proxy.address[k]
                    entity['address_%s' % k] = v

            setAttribute('address_string', 'formatted_address')
        
        ### Person
        if entity.kind == 'person':
            try:
                if len(proxy.genres) > 0:
                    entity.genres = proxy.genres
            except:
                pass

            if controller.shouldEnrich('album_list', self.sourceName, entity):
                self.__repopulateAlbums(entity, proxy, controller, decorations) 

            if controller.shouldEnrich('track_list', self.sourceName, entity):
                self.__repopulateSongs(entity, proxy, controller, decorations)
        
        ### Media
        if entity.kind in set(['media_collection', 'media_item']):
            setAttribute('rating', 'mpaa_rating')
            setAttribute('date', 'release_date')

            try:
                if proxy.length > 0:
                    entity.length = int(proxy.length)
            except:
                pass

            try:
                if len(proxy.genres) > 0:
                    entity.genres = proxy.genres
            except:
                pass

            try:
                if len(proxy.cast) > 0:
                    for actor in proxy.cast:
                        entityMini = PersonEntityMini()
                        entityMini.title = actor['name']
                        entity.cast.append(entityMini)
            except:
                pass

            try:
                if proxy.director['name'] != '':
                    entityMini = PersonEntityMini()
                    entityMini.title = proxy.director['name']
                    entity.directors.append(entityMini)
            except AttributeError:
                pass

            try:
                if proxy.publisher['name'] != '':
                    entityMini = PersonEntityMini()
                    entityMini.title = proxy.publisher['name']
                    entity.publishers.append(entityMini)
            except AttributeError:
                pass

            try:
                if proxy.author['name'] != '':
                    entityMini = PersonEntityMini()
                    entityMini.title = proxy.author['name']
                    entity.authors.append(entityMini)
            except AttributeError:
                pass

            try:
                if proxy.artist['name'] != '':
                    entityMini = PersonEntityMini()
                    entityMini.title = proxy.artist['name']
                    entityMini.types.append('artist')
                    if 'key' in proxy.artist:
                        entityMini.sources['%s_id' % proxy.source] = proxy.artist['key']
                        entityMini.sources['%s_source' % proxy.source] = proxy.source
                    if 'url' in proxy.artist:
                        entityMini.sources['%s_url' % proxy.source] = proxy.artist['url']
                    entity.artists.append(entityMini)
            except AttributeError:
                pass
        
        ### Media Collection
        if entity.kind == 'media_collection':
            if proxy.isType('album') and controller.shouldEnrich('tracks', self.sourceName, entity):
                self.__repopulateSongs(entity, proxy, controller)
        
        ### Media Item
        if entity.kind == 'media_item':
            try:
                if proxy.album['name'] != '':
                    entityMini = MediaCollectionEntityMini()
                    entityMini.title = proxy.album['name']
                    entityMini.types.append('album')
                    if 'key' in proxy.album:
                        entityMini.sources['%s_id' % proxy.source] = proxy.album['key']
                        entityMini.sources['%s_source' % proxy.source] = proxy.source
                    if 'url' in proxy.album:
                        entityMini.sources['%s_url' % proxy.source] = proxy.album['url']
                    entity.collections.append(entityMini)
            except AttributeError:
                pass

            try:
                if proxy.eisbn is not None:
                    entity.isbn = proxy.eisbn
                elif proxy.isbn is not None:
                    entity.isbn = proxy.isbn
            except AttributeError:
                pass

            try:
                if proxy.sku is not None:
                    entity.sku_number = proxy.sku
            except AttributeError:
                pass
        
        ### Software
        if entity.kind == 'software':
            setAttribute('date', 'release_date')

            try:
                if len(proxy.genres) > 0:
                    for genre in proxy.genres:
                        entity.genres.append(genre)
            except:
                pass

            try:
                if proxy.publisher['name'] != '':
                    entityMini = PersonEntityMini()
                    entityMini.title = proxy.publisher['name']
                    entity.authors.append(entityMini)
            except:
                pass

            try:
                if len(proxy.screenshots) > 0:
                    for screenshot in proxy.screenshots:
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
                query = self.stamped.proxyFromEntity(entity)
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
                proxy = self.entityProxyFromKey(source_id)
                self.enrichEntityWithEntityProxy(proxy, entity, controller, decorations, timestamps)
            except Exception as e:
                print 'Error: %s' % e
        
        return True

