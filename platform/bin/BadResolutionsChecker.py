#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals
from pprint import pformat
import sys, traceback, string, random, pprint

from api.db.mongodb.MongoEntityCollection import MongoEntityCollection
from api.db.mongodb.MongoStampCollection import MongoStampCollection

from resolve.AmazonSource import AmazonSource
from resolve.FactualSource import FactualSource
from resolve.GooglePlacesSource import GooglePlacesSource
from resolve.iTunesSource import iTunesSource
from resolve.RdioSource import RdioSource
from resolve.SpotifySource import SpotifySource
from resolve.TMDBSource import TMDBSource
from resolve.TheTVDBSource import TheTVDBSource
from resolve.NetflixSource import NetflixSource
from resolve.StampedSource import *
from resolve.EntityProxyComparator import *

from optparse import OptionParser

def getAllEntityIds(stamped_only=False):
    if not stamped_only:
        return [result['_id'] for result in MongoEntityCollection()._collection.find({'sources.user_generated_id': {'$exists': False}, 'sources.userGenerated.generated_by': {'$exists': False}, 'kind': {'$ne': 'other'} }, fields={'_id':True})]
    else:
        stamped_entity_ids = [result['entity']['entity_id'] for result in MongoStampCollection()._collection.find()]
        return list(set(stamped_entity_ids))

import collections
sourceAttemptCounts = collections.defaultdict(int)
sourceFailureCounts = collections.defaultdict(int)

def entityToProxies(entity):
    sources = entity.sources
    id_fields_to_source_classes = {
        sources.amazon_id:       AmazonSource,
        sources.factual_id:      FactualSource,
        sources.googleplaces_reference: GooglePlacesSource,
        sources.itunes_id:       iTunesSource,
        sources.rdio_id:         RdioSource,
        sources.spotify_id:      SpotifySource,
        sources.tmdb_id:         TMDBSource,
        sources.thetvdb_id:      TheTVDBSource,
        sources.netflix_id:      NetflixSource,
        }
    proxies = [ StampedSource().proxyFromEntity(entity) ]
    for (id_field, source_class) in id_fields_to_source_classes.items():
        if id_field:
            try:
                sourceAttemptCounts[source_class().sourceName] += 1
                proxy = source_class().entityProxyFromKey(id_field)
                if not proxy:
                    print '\n\n\n\nFAILED TO LOAD PROXY FROM SOURCE %s WITH KEY %s\n\n\n\n' % (source_class().sourceName, id_field)
                else:
                    proxies.append(proxy)
            except Exception:
                sourceFailureCounts[source_class().sourceName] += 1
                #traceback.print_exc()
    return proxies

def getComparator(entity):
    entity_proxy = StampedSource().proxyFromEntity(entity)
    if isinstance(entity_proxy, EntityProxyArtist):
        return ArtistEntityProxyComparator
    if isinstance(entity_proxy, EntityProxyAlbum):
        return AlbumEntityProxyComparator
    if isinstance(entity_proxy, EntityProxyTrack):
        return TrackEntityProxyComparator
    if isinstance(entity_proxy, EntityProxyMovie):
        return MovieEntityProxyComparator
    if isinstance(entity_proxy, EntityProxyTV):
        return TvEntityProxyComparator
    if isinstance(entity_proxy, EntityProxyPlace):
        return PlaceEntityProxyComparator
    if isinstance(entity_proxy, EntityProxyBook):
        return BookEntityProxyComparator
    if isinstance(entity_proxy, EntityProxyApp):
        return AppEntityProxyComparator
    raise Exception('Unrecognized entity proxy type:' + str(type(entity_proxy)))

def log_entity_and_proxies(entity, proxies):
    logs.warning('\n\n' + pformat(entity) + '\n\n')
    logs.warning('\n\n'.join(map(str, proxies)) + '\n\n')

def entityIsWellResolved(entity):
    proxies = entityToProxies(entity)
    comparator = getComparator(entity)
    entity_proxy = proxies[0]
    component_proxies = proxies[1:]
    for component_proxy in component_proxies:
        if comparator.compare_proxies(entity_proxy, component_proxy).is_definitely_not_match():
            logs.warning('BAD RESOLUTION: Entity (%s, id:%s) disagrees with component_proxy (%s, id:%s:%s)' % (
              entity.title, entity.entity_id, component_proxy.name, component_proxy.source, component_proxy.key
            ))
            log_entity_and_proxies(entity, component_proxies)
            return False

    if not component_proxies:
        # TODO: Log how often this occurs.
        return True

    for i in range(len(component_proxies)):
        for j in range(i):
            if comparator.compare_proxies(component_proxies[i], component_proxies[j]).is_definitely_not_match():
                logs.warning('BAD RESOLUTION: For entity (%s, id:%s), component (%s, id:%s:%s) disagrees with component (%s, id:%s:%s)' % (
                    entity.title, entity.entity_id,
                    component_proxies[i].name, component_proxies[i].source, component_proxies[i].key,
                    component_proxies[j].name, component_proxies[j].source, component_proxies[j].key
                ))
                log_entity_and_proxies(entity, component_proxies)
                return False

    connected_components = set()
    newly_connected_components = set([component_proxies[0]])
    unconnected_components = set(component_proxies[1:])
    while newly_connected_components and unconnected_components:
        curr_component = newly_connected_components.pop()
        matches = []
        for unconnected_component in unconnected_components:
            if comparator.compare_proxies(curr_component, unconnected_component).is_match():
                matches.append(unconnected_component)
        for match in matches:
            unconnected_components.remove(match)
            newly_connected_components.add(match)

    if unconnected_components:
        logs.warning('BAD RESOLUTION: Entity (%s, id:%s) is not fully connected!' % (entity.title, entity.entity_id))
        log_entity_and_proxies(entity, component_proxies)
        return False

    return True

def main():
    usage = "Usage: %prog [options]"
    version = "%prog " + __version__
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('--dry_run', action='store_true', dest='dry_run', default=None)
    # TODO: Ability to limit by vertical
    parser.add_option('--max_checks', action='store', dest='max_checks', default=500)
    parser.add_option('--max_errors', action='store', dest='max_errors', default=20)
    parser.add_option('--stamped_only', action='store_true', dest='stamped_only', default=True)
    (options, args) = parser.parse_args()


    all_entity_ids = getAllEntityIds(options.stamped_only)
    random.shuffle(all_entity_ids)
    error_entity_ids = []
    entities_checked = 0
    entity_collection = MongoEntityCollection()
    for entity_id in all_entity_ids[:options.max_checks]:
        try:
            entities_checked += 1
            entity = entity_collection.getEntity(entity_id)
            well_resolved = entityIsWellResolved(entity)
            if not well_resolved:
                error_entity_ids.append(entity_id)
                if len(error_entity_ids) >= options.max_errors:
                    break
        except ValueError:
            pass

    print 'Of %d entities examined, %d were found to have errors!' % (entities_checked, len(error_entity_ids))
    print sourceAttemptCounts
    print sourceFailureCounts

if __name__ == '__main__':
    main()