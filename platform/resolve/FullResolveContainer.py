#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'FullResolveContainer' ]

import Globals
from logs import report

try:
    from BasicSourceContainer   import BasicSourceContainer
    from EntityGroups           import *
    from ResolverSources        import *
    from pprint                 import pformat
except:
    report()
    raise

seedPriority = 100

class FullResolveContainer(BasicSourceContainer):
    """
    """

    def __init__(self):
        BasicSourceContainer.__init__(self)

        for group in allGroups:
            self.addGroup(group())
        for source in allSources:
            self.addSource(source())
        
        self.setGlobalPriority('seed', seedPriority)
        self.setGlobalPriority('entity', -1)
        self.setGlobalPriority('thetvdb', 2)
        self.setGlobalPriority('itunes', 1)
        self.setGlobalPriority('netflix',0)

        self.setGroupPriority('amazon', 'tracks', -1)
        self.setGroupPriority('amazon', 'albums', -1)
        self.setGroupPriority('amazon', 'artists', -1)

        # Allow itunes to overwrite seed for iTunes id (necessary because ids can deprecate)
        self.setGroupPriority('itunes', 'itunes', seedPriority + 1)

def buildQueryFromArgs(args):
    title = args[0]
    subcategory = args[1] if len(args) > 1 else None

    query = {'titlel':title.lower()}
    if subcategory is not None:
        query['subcategory'] = subcategory

    return query


def getEntityFromSearchId(searchId):
    import re
    source_name, source_id = re.match(r'^T_([A-Z]*)_([\w+-:]*)', searchId).groups()

    sources = {
        'amazon':       AmazonSource,
        'factual':      FactualSource,
        'googleplaces': GooglePlacesSource,
        'itunes':       iTunesSource,
        'rdio':         RdioSource,
        'spotify':      SpotifySource,
        'tmdb':         TMDBSource,
        'thetvdb':      TheTVDBSource,
    }

    if source_name.lower() not in sources:
        raise Exception('Source not found: %s (%s)' % (source_name, searchId))

    source = sources[source_name.lower()]()
    proxy = source.entityProxyFromKey(source_id)

    from EntityProxyContainer import EntityProxyContainer
    return EntityProxyContainer(proxy).buildEntity()


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


if __name__ == "__main__":
    main()
