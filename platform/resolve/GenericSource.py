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
    from ASourceController          import ASourceController
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

    def __repopulateAlbums(self, entity, artist, controller):
        new_albums = []
        for album in artist.albums:
            try:
                info = {
                    'album_name'    : album['name'],
                    'source'        : self.sourceName,
                    'timestamp'     : controller.now,
                    'album_mangled' : albumSimplify(album['name']),
                }
                if 'key' in album:
                    info['id'] = album['key']
                new_albums.append(info)
            except:
                logs.info('Album import failure: %s for artist %s' % (track, artist))
        entity['albums'] = new_albums

    def __repopulateSongs(self, entity, artist, controller):
        new_songs = []
        for track in artist.tracks:
            try:
                info = {
                    'song_name'     : track['name'],
                    'source'        : self.sourceName,
                    'timestamp'     : controller.now,
                    'song_mangled'  : trackSimplify(track['name']),
                }
                if 'key' in track:
                    info['id'] = track['key']
                new_songs.append(info)
            except Exception:
                logs.info('Track import failure: %s for artist %s' % (track, artist))
        entity['songs'] = new_songs

    def wrapperFromKey(self, key, type=None):
        return None

    def enrichEntityWithWrapper(self, wrapper, entity, controller=None, decorations=None, timestamps=None):
        if controller is None:
            controller = AlwaysSourceController()
        if decorations is None:
            decorations = {}
        if timestamps is None:
            timestamps = {}

        if wrapper.source == 'stamped':
            entity['entity_id'] = wrapper.key 
        else:
            entity['entity_id'] = 'T_%s_%s' % (wrapper.source.upper(), wrapper.key)

        if wrapper.type == 'place':
            subcategory = wrapper.subcategory
            if subcategory is not None:
                entity['subcategory'] = subcategory
        else:
            subcategory = typeToSubcategory(wrapper.type)
            if subcategory is not None:
                entity['subcategory'] = subcategory
        entity['title'] = wrapper.name
        if wrapper.description != '':
            entity['desc'] = wrapper.description

        if wrapper.type == 'movie':
            if wrapper.rating is not None:
                entity['mpaa_rating'] = wrapper.rating
        if wrapper.type == 'artist':
            if controller.shouldEnrich('albums', self.sourceName, entity):
                self.__repopulateAlbums(entity, wrapper, controller) 
            if controller.shouldEnrich('songs', self.sourceName, entity):
                self.__repopulateSongs(entity, wrapper, controller)

        if wrapper.type == 'album':
            if len(wrapper.tracks) > 0:
                entity['tracks'] = [
                    track['name'] for track in wrapper.tracks
                ]

        if wrapper.type == 'track':
            if wrapper.album['name'] != '':
                entity['album_name'] = wrapper.album['name']

        if wrapper.type == 'book':
            if wrapper.author['name'] != '':
                entity['author'] = wrapper.author['name']
            if wrapper.eisbn is not None:
                entity['isbn'] = wrapper.eisbn
            if wrapper.isbn is not None:
                entity['isbn'] = wrapper.isbn
            if wrapper.sku is not None:
                entity['sku_number'] = wrapper.sku
            if wrapper.publisher['name'] != '':
                entity['publisher'] = wrapper.publisher['name']
            if wrapper.length > 0:
                entity['num_pages'] = int(wrapper.length)

        if wrapper.type == 'place':
            if wrapper.coordinates is not None:
                entity['coordinates'] = {
                    'lat': wrapper.coordinates[0],
                    'lng': wrapper.coordinates[1],
                }

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

            if wrapper.address_string is not None:
                entity['address'] = wrapper.address_string
            if wrapper.phone is not None:
                entity['phone'] = wrapper.phone
            if wrapper.url is not None:
                entity['site'] = wrapper.url
            if wrapper.email is not None:
                entity['email'] = wrapper.email

        if wrapper.type in set(['track','album','artist','movie','book']):
            if len(wrapper.genres) > 0:
                entity['genre'] = wrapper.genres[0]
        if wrapper.type in set(['track','album']):
            if wrapper.artist['name'] != '':
                entity['artist_display_name'] = wrapper.artist['name']
        if wrapper.type in set(['track', 'album', 'movie', 'book']):
            if wrapper.date is not None:
                entity['release_date'] = wrapper.date
        if wrapper.type in set(['track', 'movie']):
            if wrapper.length > 0:
                entity['track_length'] = str(int(wrapper.length))
        if wrapper.type in set(['movie', 'tv']):
            if len(wrapper.cast) > 0:
                cast = [
                    actor['name'] for actor in wrapper.cast
                ]
                entity['cast'] = ', '.join(cast)
            if wrapper.director['name'] != '':
                entity['director'] = wrapper.director['name']
        if wrapper.type in set(['app']):
            if wrapper.publisher['name'] != '':
                entity['artist_display_name'] = wrapper.publisher['name']
        return True

    @property
    def idField(self):
        return "%s_id" % self.sourceName

    @property
    def urlField(self):
        return "%s_url" % self.sourceName

    def enrichEntity(self, entity, controller, decorations, timestamps):
        if controller.shouldEnrich(self.sourceName, self.sourceName, entity):
            try:
                query = self.stamped.wrapperFromEntity(entity)
                timestamps[self.sourceName] = controller.now
                results = self.resolver.resolve(query, self.matchSource(query))
                if len(results) != 0:
                    best = results[0]
                    if best[0]['resolved']:
                        entity[self.idField] = best[1].key
                        if self.urlField is not None and best[1].url is not None:
                            entity[self.urlField] = best[1].url
            except ValueError:
                pass
        return True

