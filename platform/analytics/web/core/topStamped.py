#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


import Globals
import keys.aws, logs, utils

from MongoStampedAPI        import MongoStampedAPI
from boto.sdb.connection    import SDBConnection
from boto.exception         import SDBResponseError
from bson.code              import Code



def getTopStamped(kinds,date,collection):
    
    if kinds == None:
        query = """function () {
                       if (this.timestamp.created > ISODate("%s")){
                           emit(this.entity.title, 1);
                       }
                  } """ % (date)
    else:
        query = """function () {
                       if (this.timestamp.created > ISODate("%s") && (this.entity.types == "%s" """ % (date,kinds[0])
                       
        for kind in kinds [1:]:
            query = """ %s || this.entity.types == "%s" """ % (query,kind)
        
        query = """%s)){
                           emit(this.entity.title, 1);
                       }
                  } """ % (query)
    
    map = Code(query)
    
    reduce = Code("function (key, values) {"
                  "  var total = 0;"
                  "  for (var i = 0; i < values.length; i++) {"
                  "    total += values[i];"
                  "  }"
                  "  return total;"
                  "}")
    
    result = collection.inline_map_reduce(map, reduce)
    
    sortedResult = sorted(result, key=lambda k: k['value'],reverse=True) 
    
    return sortedResult
    
        
        

