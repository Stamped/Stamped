#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import bson, logs, pprint, pymongo
import libs.worldcities, unicodedata

from errors             import *
from utils              import AttributeDict
from db.mongodb.AMongoCollection   import AMongoCollection
from api_old.Entity             import *

class AMongoCollectionView(AMongoCollection):
    
    def _getTimeSlice(self, query, timeSlice, objType=None):
        # initialize params
        # -----------------
        if objType == 'todo':
            sort = [('timestamp.created', pymongo.DESCENDING)]
        else:
            sort = [('timestamp.stamped', pymongo.DESCENDING)] 
        
        if timeSlice.limit is None:
            timeSlice.limit = 0
        if timeSlice.offset is None:
            timeSlice.offset = 0
        
        def add_or_query(args):
            if "$or" not in query:
                query["$or"] = args
            else:
                result = []
                for item in query.pop("$and", []) + [{"$or": query.pop("$or")}] + [{"$or": args}]:
                    if item not in result:
                        result.append(item)

                query["$and"] = result
                # query["$and"] = query["$and"] + [ { "$or" : existing }, { "$or" : args } ]
        
        
        # handle before / since filters
        # -----------------------------
        if timeSlice.before is not None:
            if objType == 'todo':
                query['timestamp.created'] = { '$lt': timeSlice.before }
            else:
                query['timestamp.stamped'] = { '$lt': timeSlice.before }

        # handle category / subcategory filters
        # -------------------------------------
        ### TODO: Allow for both kinds and types (once we don't need backwards compatbility for category / subcategory)
        if timeSlice.types is not None and len(timeSlice.types) > 0:
            subcategories = list(timeSlice.types)
            if 'track' in timeSlice.types:
                subcategories.append('song')
            query['entity.types'] = {'$in': list(timeSlice.types)}
        

        # logs.debug("QUERY: %s" % query)
        # logs.debug("SLICE: %s" % timeSlice.dataExport())
        
        # find, sort, and truncate results
        results = self._collection.find(query) \
                      .sort(sort) \
                      .skip(timeSlice.offset) \
                      .limit(timeSlice.limit)

        return map(self._convertFromMongo, results)
    
    def _getSearchSlice(self, query, searchSlice, objType=None):
        # initialize params
        # -----------------
        viewport    = (searchSlice.viewport and searchSlice.viewport.lower_right is not None)

        if objType == 'todo':
            sort = [('timestamp.created', pymongo.DESCENDING)]
        else:
            sort = [('timestamp.stamped', pymongo.DESCENDING)] 
        
        if searchSlice.limit is None:
            searchSlice.limit = 0
        
        def add_or_query(args):
            if "$or" not in query:
                query["$or"] = args
            else:
                result = []
                for item in query.pop("$and", []) + [{"$or": query.pop("$or")}] + [{"$or": args}]:
                    if item not in result:
                        result.append(item)

                query["$and"] = result
                # query["$and"] = query["$and"] + [ { "$or" : existing }, { "$or" : args } ]
        
        # handle category / subcategory filters
        # -------------------------------------
        ### TODO: Allow for both kinds and types (once we don't need backwards compatbility for category / subcategory)
        if searchSlice.types is not None and len(searchSlice.types) > 0:
            subcategories = list(searchSlice.types)
            if 'track' in searchSlice.types:
                subcategories.append('song')
            query['entity.types'] = {'$in': list(searchSlice.types)}

        # Query
        if searchSlice.query is not None:
            # TODO: make query regex better / safeguarded
            user_query = searchSlice.query.lower().strip()
            try:
                user_query = unicodedata.normalize('NFKD', user_query).encode('ascii','ignore')
            except Exception:
                logs.warning("Unable to normalize query to ascii: %s" % user_query)
            
            query["search_blurb"] = { "$regex" : user_query, "$options" : 'i' }
        
        # handle viewport filter
        # ----------------------
        if viewport:
            query["entity.coordinates.lat"] = {
                "$gte" : searchSlice.viewport.lower_right.lat, 
                "$lte" : searchSlice.viewport.upper_left.lat, 
            }
            
            if searchSlice.viewport.upper_left.lng <= searchSlice.viewport.lower_right.lng:
                query["entity.coordinates.lng"] = { 
                    "$gte" : searchSlice.viewport.upper_left.lng, 
                    "$lte" : searchSlice.viewport.lower_right.lng, 
                }
            else:
                # handle special case where the viewport crosses the +180 / -180 mark
                add_or_query([  {
                        "entity.coordinates.lng" : {
                            "$gte" : searchSlice.viewport.upper_left.lng, 
                        }, 
                    }, 
                    {
                        "entity.coordinates.lng" : {
                            "$lte" : searchSlice.viewport.lower_right.lng, 
                        }, 
                    }, 
                ])

        # logs.debug("QUERY: %s" % query)
        # logs.debug("SLICE: %s" % searchSlice.dataExport())
        
        # find, sort, and truncate results
        ### TODO: Change ranking
        results = self._collection.find(query).sort(sort).limit(searchSlice.limit)

        return map(self._convertFromMongo, results)


