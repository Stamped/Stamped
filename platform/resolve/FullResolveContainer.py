#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'FullResolveContainer' ]

import Globals
from logs import report

try:
    from resolve.BasicSourceContainer   import BasicSourceContainer
    from resolve.ResolverSources        import *
    from pprint                 import pformat
    import logs

    import re
except:
    report()
    raise

class FullResolveContainer(BasicSourceContainer):
    """
    """

    def __init__(self):
        BasicSourceContainer.__init__(self)

        for source in allSources:
            self.addSource(source())
        
        self.setGlobalPriority('entity', -1)
        self.setGlobalPriority('thetvdb', 2)
        self.setGlobalPriority('itunes', 1)
        self.setGlobalPriority('netflix',0)

        self.setGroupPriority('tracks', 'amazon', -1)
        self.setGroupPriority('albums', 'amazon', -1)
        self.setGroupPriority('artists', 'amazon', -1)
        self.setGroupPriority('cast', 'netflix', 2)

        # Allow itunes and GooglePlaces to overwrite seed for for their own id, because they
        # deprecate sometimes.
        seedPriority = self.getGlobalPriority('seed')
        self.setGroupPriority('itunes', 'itunes', seedPriority + 1)
        self.setGroupPriority('googleplaces', 'googleplaces', seedPriority + 1)


def buildQueryFromArgs(args):
    title = args[0]
    subcategory = args[1] if len(args) > 1 else None

    query = {'titlel':title.lower()}
    if subcategory is not None:
        query['subcategory'] = subcategory

    return query


def getEntityFromSearchId(search_id):
    temp_id_prefix = 'T_'
    if not search_id.startswith(temp_id_prefix):
        # already a valid entity id
        return search_id

        # TODO: This code should be moved into a common location with BasicEntity.search_id
    id_components = search_id[len(temp_id_prefix):].split('____')

    sources = {
        'amazon':       AmazonSource,
        'factual':      FactualSource,
        'googleplaces': GooglePlacesSource,
        'itunes':       iTunesSource,
        'rdio':         RdioSource,
        'spotify':      SpotifySource,
        'tmdb':         TMDBSource,
        'thetvdb':      TheTVDBSource,
        'netflix':      NetflixSource,
        }

    sourceAndKeyRe = re.compile('^([A-Z]+)_([\w+-:/]+)$')
    proxies = []
    for component in id_components:
        match = sourceAndKeyRe.match(component)
        if not match:
            logs.warning('Unable to parse search ID component:' + component)
        else:
            sourceName, key = match.groups()
            if sourceName.lower() not in sources:
                logs.warning('Unable to recognize source:' + sourceName.lower())
            else:
                try:
                    proxies.append(sources[sourceName.lower()]().entityProxyFromKey(key))
                except Exception:
                    import traceback
                    logs.warning('ERROR while loading proxy:\n' + ''.join(traceback.format_exc()))

    if not proxies:
        logs.warning('Unable to extract and third-party ID from composite search ID: ' + search_id)
        raise StampedUnavailableError("Entity not found")

    from resolve.EntityProxyContainer import EntityProxyContainer
    from resolve.EntityProxySource import EntityProxySource
    return EntityProxyContainer().addAllProxies(proxies).buildEntity()


import sys
from optparse import OptionParser

def main():
    usage = "Usage: %prog --entity_id=<id>  OR  %prod --search_id=<id> OR %prod <query> <subcategory?> <index?>"
    version = "%prog " + __version__
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('--entity_id', action='store', dest='entity_id', default=None)
    parser.add_option('--search_id', action='store', dest='search_id', default=None)
    (options, args) = parser.parse_args()

    if options.entity_id and options.search_id:
        print '--entity_id and --search_id are mutually exclusive!'
    id_provided = options.entity_id or options.search_id
    if id_provided and len(args) > 1:
        print '--entity_id and --search_id cannot be used with query arguments!'

    if options.entity_id:
        from api.db.mongodb.MongoEntityCollection import MongoEntityCollection
        entity = MongoEntityCollection().getEntity(options.entity_id)
    elif options.search_id:
        entity = getEntityFromSearchId(options.search_id)
    else:
        query = buildQueryFromArgs(args)
        from api.MongoStampedAPI import MongoStampedAPI
        cursor = MongoStampedAPI()._entityDB._collection.find(query)
        if cursor.count() == 0:
            print("Could not find a matching entity for query: %s" % query)
            return

        entity =  MongoStampedAPI()._entityDB._convertFromMongo(cursor[0])


    print( "Before:\n%s" % pformat( entity.dataExport() ) )

    container = FullResolveContainer()

    decorations = {}
    container.enrichEntity( entity, decorations )

    print( "After:\n%s" % pformat( entity.dataExport() ) )
    if len(decorations) > 0:
        print( "With decorations:")

        for k,v in decorations.items():
            print( "%s decoration:" % k )

            try:
                print( "%s" % pformat(v.dataExport()) )
            except Exception:
                print( "%s" % pformat(v) )

    from libs.CountedFunction import printFunctionCounts
    printFunctionCounts()


if __name__ == "__main__":
    main()
