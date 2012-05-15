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

def demo(default_title='Katy Perry', object_id=None):
    import bson, sys
    
    title = default_title.lower()
    subcategory = None
    index = 0
    
    print(sys.argv)
    if len(sys.argv) > 1:
        title = sys.argv[1]
    if len(sys.argv) > 2:
        subcategory = sys.argv[2]
    if len(sys.argv) > 3:
        index = int(sys.argv[3])
    
    from MongoStampedAPI import MongoStampedAPI
    api = MongoStampedAPI()
    db  = api._entityDB
    if object_id is not None:
        query = {'_id':  bson.ObjectId(object_id)}
    else:
        query = {'titlel':title}
    
    if subcategory is not None:
        query['subcategory'] = subcategory
    
    print("Query: %s" % query)
    cursor = db._collection.find(query)
    
    if cursor.count() == 0:
        print("Could not find a matching entity for %s" % title)
        return
    
    result = cursor[index]
    entity = db._convertFromMongo(result)
    print( "Before:\n%s" % pformat( entity.value ) )
    
    container = FullResolveContainer()
    
    decorations = {}
    container.enrichEntity( entity, decorations )
    
    print( "After:\n%s" % pformat( entity.value ) )
    if len(decorations) > 0:
        print( "With decorations:")
        
        for k,v in decorations.items():
            print( "%s decoration:" % k )
            
            try:
                print( "%s" % pformat(v.value) )
            except Exception:
                print( "%s" % pformat(v) )

if __name__ == "__main__":
    import sys
    params = {}
    if len(sys.argv) == 2 and sys.argv[1].find('=') == -1:
        params['default_title'] = sys.argv[1]
    else:
        for arg in sys.argv[1:]:
            pair = arg.split('=')
            params[pair[0]] = pair[1]
    demo(**params)
