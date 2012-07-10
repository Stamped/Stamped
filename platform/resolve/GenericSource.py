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
    from resolve.BasicSource                import BasicSource
    from utils                      import lazyProperty
    from gevent.pool                import Pool
    from pprint                     import pprint, pformat
    from abc                        import ABCMeta, abstractmethod
    from resolve.Resolver                   import *
    from resolve.ResolverObject             import *
    from resolve.ASourceController          import *
    from api.Schemas                import *
    from resolve.EntityGroups               import *
    from api.Entity                     import buildEntity
except Exception:
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
        while total > len(results):
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

        result = results[start:]
        return result
    return source

def listSource(items, **kwargs):
    return generatorSource(iter(items), **kwargs)

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
        from resolve import StampedSource
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

        albums = []
        for album in artist.albums:
            try:
                entityMini  = MediaCollectionEntityMini()
                entityMini.title = album['name']
                entityMini.types = ['album']
                if 'key' in album:
                    setattr(entityMini.sources, '%s_id' % artist.source, album['key'])
                    setattr(entityMini.sources, '%s_source' % artist.source, artist.source)
                if 'url' in album:
                    setattr(entityMini.sources, '%s_url' % artist.source, album['url'])
                albums.append(entityMini)
            except Exception:
                report()
                logs.info('Album import failure: %s for artist %s' % (album, artist))
        if len(albums) > 0:
            entity.albums = albums

    def __repopulateTracks(self, entity, artist, controller, decorations=None):
        if decorations is None:
            decorations = {}

        tracks = []
        for track in artist.tracks:
            try:
                entityMini  = MediaItemEntityMini()
                entityMini.title = track['name']
                entityMini.types = ['track']
                if 'key' in track:
                    setattr(entityMini.sources, '%s_id' % artist.source, track['key'])
                    setattr(entityMini.sources, '%s_source' % artist.source, artist.source)
                if 'url' in track:
                    setattr(entityMini.sources, '%s_url' % artist.source, track['url'])
                tracks.append(entityMini)
            except Exception:
                report()
                logs.info('Track import failure: %s for artist %s' % (track, artist))
        if len(tracks) > 0:
            entity.tracks = tracks
    
    def entityProxyFromKey(self, key, **kwargs):
        raise NotImplementedError(str(type(self)))
    
    def enrichEntityWithEntityProxy(self, proxy, entity, controller=None, decorations=None, timestamps=None):
        if controller is None:
            controller = AlwaysSourceController()
        if decorations is None:
            decorations = {}
        if timestamps is None:
            timestamps = {}

        timestamps[proxy.source] = controller.now
        
        def setAttribute(source, target):
            try:
                item = getattr(proxy, source)
                if item is not None and item != '':
                    setattr(entity, target, item)
                    timestamps[target] = controller.now
            except Exception as e:
                pass
        
        setAttribute('description',     'desc')
        setAttribute('phone',           'phone')
        setAttribute('email',           'email')
        setAttribute('url',             'site')

        images = []
        for image in proxy.images:
            if image is None or image == '':
                logs.warning('Caught an empty image from the proxy entity %s' % (proxy,))
                continue
            img = ImageSchema()
            size = ImageSizeSchema()
            size.url = image
            img.sizes = [size]
            images.append(img)
        if len(images) > 0:
            entity.images = images
            timestamps['images'] = controller.now
        
        ### Place
        if entity.kind == 'place' and proxy.kind == 'place':
            setAttribute('address_string', 'formatted_address')

            if proxy.coordinates is not None:
                coordinates = Coordinates()
                coordinates.lat = proxy.coordinates[0]
                coordinates.lng = proxy.coordinates[1]
                entity.coordinates = coordinates

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
                    if v is not None:
                        setattr(entity, 'address_%s' % k, v)
                timestamps['address'] = controller.now

            gallery = []
            for image in proxy.gallery:
                img             = ImageSchema()
                img.caption     = image['caption']
                size            = ImageSizeSchema()
                size.url        = image['url']
                size.height     = image['height']
                size.width      = image['width']
                img.sizes       = [size]
                gallery.append(img)
            if len(gallery) > 0:
                entity.gallery = gallery
                timestamps['gallery'] = controller.now
        
        ### Person
        if entity.kind == 'person' and proxy.kind == 'person':
            if len(proxy.genres) > 0:
                entity.genres = proxy.genres

            if controller.shouldEnrich('albums', self.sourceName, entity):
                self.__repopulateAlbums(entity, proxy, controller, decorations) 
                timestamps['albums'] = controller.now

            if controller.shouldEnrich('tracks', self.sourceName, entity):
                self.__repopulateTracks(entity, proxy, controller, decorations)
                timestamps['tracks'] = controller.now
        
        ### Media
        if entity.kind in set(['media_collection', 'media_item']) and entity.kind == proxy.kind:
            setAttribute('mpaa_rating',     'mpaa_rating')
            setAttribute('release_date',    'release_date')

            if proxy.length > 0:
                entity.length = int(proxy.length)
                timestamps['length'] = controller.now
            if len(proxy.genres) > 0:
                entity.genres = proxy.genres
                timestamps['genres'] = controller.now

            cast = []
            for actor in proxy.cast:
                entityMini = PersonEntityMini()
                entityMini.title = actor['name']
                cast.append(entityMini)
            if len(cast) > 0:
                entity.cast = cast
                timestamps['cast'] = controller.now

            directors = []
            for director in proxy.directors:
                entityMini = PersonEntityMini()
                entityMini.title = director['name']
                directors.append(entityMini)
            if len(directors) > 0:
                entity.directors = directors
                timestamps['directors'] = controller.now

            publishers = []
            for publisher in proxy.publishers:
                entityMini = PersonEntityMini()
                entityMini.title = publisher['name']
                publishers.append(entityMini)
            if len(publishers) > 0:
                entity.publishers = publishers
                timestamps['publishers'] = controller.now

            authors = []
            for author in proxy.authors:
                entityMini = PersonEntityMini()
                entityMini.title = author['name']
                authors.append(entityMini)
            if len(authors) > 0:
                entity.authors = authors
                timestamps['authors'] = controller.now

            artists = []
            for artist in proxy.artists:
                entityMini = PersonEntityMini()
                entityMini.title = artist['name']
                entityMini.types = ['artist']
                if 'key' in artist:
                    setattr(entityMini.sources, '%s_id' % proxy.source, artist['key'])
                    setattr(entityMini.sources, '%s_source' % proxy.source,  proxy.source)
                if 'url' in artist:
                    setattr(entityMini.sources, '%s_url' % proxy.source, artist['url'])
                artists.append(entityMini)
            if len(artists) > 0:
                entity.artists = artists
                timestamps['artists'] = controller.now
        
        ### Media Collection
        if entity.kind == 'media_collection' and proxy.kind == 'media_collection':
            if proxy.isType('album'):
                if controller.shouldEnrich('tracks', self.sourceName, entity):
                    self.__repopulateTracks(entity, proxy, controller)
                    timestamps['tracks'] = controller.now
        
        ### Media Item
        if entity.kind == 'media_item' and proxy.kind == 'media_item':
            albums = []
            for album in proxy.albums:
                entityMini = MediaCollectionEntityMini()
                entityMini.title = album['name']
                entityMini.types = ['album']
                if 'key' in album:
                    setattr(entityMini.sources, '%s_id' % proxy.source, album['key'])
                    setattr(entityMini.sources, '%s_source' % proxy.source, proxy.source)
                if 'url' in album:
                    setattr(entityMini.sources, '%s_url' % proxy.source, album['url'])
                albums.append(entityMini)
            if len(albums) > 0:
                entity.albums = albums
                timestamps['albums'] = controller.now

            if proxy.isbn is not None:
                entity.isbn = proxy.isbn
                timestamps['isbn'] = controller.now

            if proxy.sku_number is not None:
                entity.sku_number = proxy.sku_number
                timestamps['sku_number'] = controller.now

        ### Software
        if entity.kind == 'software' and proxy.kind == 'software':
            setAttribute('release_date', 'release_date')

            if len(proxy.genres) > 0:
                entity.genres = proxy.genres
                timestamps['genres'] = controller.now

            publishers = []
            for publisher in proxy.publishers:
                entityMini = PersonEntityMini()
                entityMini.title = publisher['name']
                publishers.append(entityMini)
            if len(publishers) > 0:
                entity.publishers = publishers
                timestamps['publishers'] = controller.now

            authors = []
            for author in proxy.authors:
                entityMini = PersonEntityMini()
                entityMini.title = author['name']
                authors.append(entityMini)
            if len(authors) > 0:
                entity.authors = authors
                timestamps['authors'] = controller.now

            screenshots = []
            for screenshot in proxy.screenshots:
                img = ImageSchema()
                size = ImageSizeSchema()
                size.url = screenshot
                img.sizes = [size]
                screenshots.append(img)
            if len(screenshots) > 0:
                entity.screenshots = screenshots
                timestamps['screenshots'] = controller.now
    
    @property
    def idField(self):
        return "%s_id" % self.idName
    
    @property
    def urlField(self):
        return "%s_url" % self.idName
    
    @property 
    def idName(self):
        return self.sourceName

    def getId(self, entity):
        return getattr(entity.sources, self.idField)

    def enrichEntity(self, entity, controller, decorations, timestamps):
        """

        """
        proxy = None
        results = None

        if self.getId(entity) is None and controller.shouldEnrich(self.idName, self.sourceName, entity):
            try:
                query = self.stamped.proxyFromEntity(entity)
                timestamps[self.idName] = controller.now
                results = self.resolver.resolve(query, self.matchSource(query))
                if len(results) != 0:
                    best = results[0]
                    if best[0]['resolved']:
                        setattr(entity.sources, self.idField, best[1].key)            
                        if self.urlField is not None and best[1].url is not None:
                            setattr(entity.sources, self.urlField, best[1].url)
                        proxy = best[1]
            except ValueError:
                logs.report()
                pass

        source_id = self.getId(entity)
        if source_id is not None:
            try:
                if proxy is None:
                    proxy = self.entityProxyFromKey(source_id, entity=entity)
                self.enrichEntityWithEntityProxy(proxy, entity, controller, decorations, timestamps)
            except Exception as e:
                report()

        # Haaaaaaaack.
        if results and self.sourceName != 'stamped':
            for result in results:
                if result[0]['resolved']:
                    entity.addThirdPartyId(self.sourceName, result[1].key)

        return True

