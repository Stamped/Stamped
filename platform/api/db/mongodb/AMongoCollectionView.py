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
from AMongoCollection   import AMongoCollection
from Entity             import *

class AMongoCollectionView(AMongoCollection):
    
    def _getTimeSlice(self, query, timeSlice):
        # initialize params
        # -----------------
        sort        = [('timestamp.stamped', pymongo.DESCENDING), ('timestamp.created', pymongo.DESCENDING)] # Legacy support
        viewport    = (timeSlice.viewport and timeSlice.viewport.lower_right is not None)
        
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
            add_or_query ([
                {'timestamp.stamped': { '$lt': timeSlice.before }},
                {'timestamp.created': { '$lt': timeSlice.before }} # Legacy support
            ])

        # handle category / subcategory filters
        # -------------------------------------
        ### TODO: Allow for both kinds and types (once we don't need backwards compatbility for category / subcategory)
        if timeSlice.types is not None and len(timeSlice.types) > 0:
            subcategories = list(timeSlice.types)
            if 'track' in timeSlice.types:
                subcategories.append('song')
            add_or_query([  {'entity.types': {'$in': list(timeSlice.types)}},
                            {'entity.subcategory': {'$in': subcategories}} ])

        elif timeSlice.kinds is not None and len(timeSlice.kinds) > 0:
            query["entity.kind"] = {'$in': list(timeSlice.kinds)}
        
        # handle viewport filter
        # ----------------------
        if viewport:
            query["entity.coordinates.lat"] = {
                "$gte" : timeSlice.viewport.lower_right.lat, 
                "$lte" : timeSlice.viewport.upper_left.lat, 
            }
            
            if timeSlice.viewport.upper_left.lng <= timeSlice.viewport.lower_right.lng:
                query["entity.coordinates.lng"] = { 
                    "$gte" : timeSlice.viewport.upper_left.lng, 
                    "$lte" : timeSlice.viewport.lower_right.lng, 
                }
            else:
                # handle special case where the viewport crosses the +180 / -180 mark
                add_or_query([  {
                        "entity.coordinates.lng" : {
                            "$gte" : timeSlice.viewport.upper_left.lng, 
                        }, 
                    }, 
                    {
                        "entity.coordinates.lng" : {
                            "$lte" : timeSlice.viewport.lower_right.lng, 
                        }, 
                    }, 
                ])

        logs.debug("QUERY: %s" % query)
        logs.debug("SLICE: %s" % timeSlice.dataExport())
        
        # find, sort, and truncate results
        results = self._collection.find(query) \
                      .sort(sort) \
                      .skip(timeSlice.offset) \
                      .limit(timeSlice.limit)

        return map(self._convertFromMongo, results)
    
    def _getSearchSlice(self, query, searchSlice):
        # initialize params
        # -----------------
        viewport    = (searchSlice.viewport and searchSlice.viewport.lower_right is not None)
        
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
        if timeSlice.types is not None and len(timeSlice.types) > 0:
            subcategories = list(timeSlice.types)
            if 'track' in timeSlice.types:
                subcategories.append('song')
            add_or_query([  {'entity.types': {'$in': list(timeSlice.types)}},
                            {'entity.subcategory': {'$in': subcategories}} ])

        elif timeSlice.kinds is not None and len(timeSlice.kinds) > 0:
            query["entity.kind"] = {'$in': list(timeSlice.kinds)}

        # Query
        if searchSlice.query is not None:
            # TODO: make query regex better / safeguarded
            user_query = searchSlice.query.lower().strip()
            try:
                user_query = unicodedata.normalize('NFKD', user_query).encode('ascii','ignore')
            except Exception:
                logs.warning("Unable to normalize query to ascii: %s" % user_query)
            
            ### TODO: check multiple blurbs
            add_or_query([ { "blurb"            : { "$regex" : user_query, "$options" : 'i', } }, 
                           { "contents.blurb"   : { "$regex" : user_query, "$options" : 'i', } },
                           { "entity.title"     : { "$regex" : user_query, "$options" : 'i', } } ])
        
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

        logs.debug("QUERY: %s" % query)
        logs.debug("SLICE: %s" % searchSlice.dataExport())
        
        # find, sort, and truncate results
        ### TODO: Change ranking
        results = self._collection.find(query) \
                      .sort([('timestamp.created', pymongo.DESCENDING)]) \
                      .limit(searchSlice.limit)

        return map(self._convertFromMongo, results)








    def _getSlice(self, query, genericCollectionSlice):
        # initialize params
        # -----------------
        time_filter = 'timestamp.created'
        sort        = None
        complexSort = None
        reverse     = genericCollectionSlice.reverse
        user_query  = genericCollectionSlice.query
        viewport    = (genericCollectionSlice.viewport and genericCollectionSlice.viewport.lower_right.lat is not None)
        relaxed     = (viewport and genericCollectionSlice.query is not None and genericCollectionSlice.sort == 'relevance')
        orig_coords = True
        
        if genericCollectionSlice.limit is None:
            genericCollectionSlice.limit = 0
        
        if relaxed:
            center = {
                'lat' : (genericCollectionSlice.viewport.upper_left.lat + genericCollectionSlice.viewport.lower_right.lat) / 2.0,
                'lng' : (genericCollectionSlice.viewport.upper_left.lng + genericCollectionSlice.viewport.lower_right.lng) / 2.0,
            }
        
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
        
        # handle setup for sorting
        # ------------------------
        if genericCollectionSlice.sort == 'modified' or genericCollectionSlice.sort == 'created':
            sort = 'timestamp.%s' % genericCollectionSlice.sort
            time_filter = sort
        elif genericCollectionSlice.sort == 'alphabetical':
            sort = 'entity.title'
            
            reverse = not reverse
        elif genericCollectionSlice.sort == 'proximity':
            if genericCollectionSlice.coordinates.lat is None or genericCollectionSlice.coordinates.lng is None:
                raise StampedInputError("proximity sort requires a valid center parameter")
            
            query["entity.coordinates.lat"] = { "$exists" : True}
            query["entity.coordinates.lng"] = { "$exists" : True}
            
            reverse = not reverse

        elif genericCollectionSlice.sort == 'stamped':
            complexSort = [('timestamp.stamped', pymongo.DESCENDING), ('timestamp.created', pymongo.DESCENDING)]
        
        if genericCollectionSlice.sort != 'relevance' and genericCollectionSlice.query is not None:
            raise StampedInputError("non-empty search query is only compatible with sort set to \"relevance\"")
        
        # handle before / since filters
        # -----------------------------
        since  = genericCollectionSlice.since
        before = genericCollectionSlice.before
        
        if since is not None and before is not None:
            query[time_filter] = { '$gte': since, '$lte': before }
        elif since is not None:
            query[time_filter] = { '$gte': since }
        elif before is not None:
            query[time_filter] = { '$lte': before }
        
        # handle category / subcategory filters
        # -------------------------------------
        if genericCollectionSlice.category is not None:
            # kinds           = deriveKindFromCategory(genericCollectionSlice.category) 
            # types           = deriveTypesFromCategory(genericCollectionSlice.category)
            # subcategories   = deriveSubcategoriesFromCategory(genericCollectionSlice.category)
            kinds           = mapCategoryToKinds(genericCollectionSlice.category) 
            types           = mapCategoryToTypes(genericCollectionSlice.category)
            subcategories   = mapCategoryToSubcategories(genericCollectionSlice.category)
            
            kinds_and_types = []
            if len(kinds) > 0:
                kinds_and_types.append({'entity.kind': {'$in': list(kinds)}})
            if len(types) > 0:
                kinds_and_types.append({'entity.types': {'$in': list(types)}})
            
            if len(kinds_and_types) > 0:
                add_or_query([ { "entity.category" : str(genericCollectionSlice.category).lower() }, 
                               { "entity.subcategory" : {"$in": list(subcategories)} },
                               { "$and" : kinds_and_types } ])
            else:
                add_or_query([ { "entity.category" : str(genericCollectionSlice.category).lower() }, 
                               { "entity.subcategory" : {"$in": list(subcategories)} } ])
        
        if genericCollectionSlice.subcategory is not None:
            query['entity.subcategory'] = str(genericCollectionSlice.subcategory).lower()
        
        # handle search query filter
        # --------------------------
        if user_query is not None:
            # TODO: make query regex better / safeguarded
            user_query = user_query.lower().strip()
            try:
                user_query = unicodedata.normalize('NFKD', user_query).encode('ascii','ignore')
            except Exception:
                logs.warning("Unable to normalize query to ascii: %s" % user_query)
            
            # process 'in' or 'near' location hint
            result = libs.worldcities.try_get_region(user_query)
            
            if result is not None:
                user_query, coords, region_name = result
                utils.log("using region %s at %s" % (region_name, coords))
                
                # disregard original viewport in favor of using the region's 
                # coordinates as a ranking hint
                orig_coords = False
                relaxed     = True
                viewport    = False
                center      = {
                    'lat' : coords[0], 
                    'lng' : coords[1], 
                }
            else:
                utils.log("using default coordinates")
            
            add_or_query([ { "blurb"        : { "$regex" : user_query, "$options" : 'i', } }, 
                           { "entity.title" : { "$regex" : user_query, "$options" : 'i', } } ])
        
        # handle viewport filter
        # ----------------------
        if relaxed:
            query["entity.coordinates.lat"] = { "$exists" : True}
            query["entity.coordinates.lng"] = { "$exists" : True}
        elif viewport:
            query["entity.coordinates.lat"] = {
                "$gte" : genericCollectionSlice.viewport.lower_right.lat, 
                "$lte" : genericCollectionSlice.viewport.upper_left.lat, 
            }
            
            if genericCollectionSlice.viewport.upper_left.lng <= genericCollectionSlice.viewport.lower_right.lng:
                query["entity.coordinates.lng"] = { 
                    "$gte" : genericCollectionSlice.viewport.upper_left.lng, 
                    "$lte" : genericCollectionSlice.viewport.lower_right.lng, 
                }
            else:
                # handle special case where the viewport crosses the +180 / -180 mark
                add_or_query([  {
                        "entity.coordinates.lng" : {
                            "$gte" : genericCollectionSlice.viewport.upper_left.lng, 
                        }, 
                    }, 
                    {
                        "entity.coordinates.lng" : {
                            "$lte" : genericCollectionSlice.viewport.lower_right.lng, 
                        }, 
                    }, 
                ])

        #utils.log(pprint.pformat(query))
        #utils.log(pprint.pformat(genericCollectionSlice))
        
        # find, sort, and truncate results
        # --------------------------------
        if sort is not None:
            # fast-path which uses built-in sorting
            # -------------------------------------

            # order in which to return sorted results
            order   = pymongo.ASCENDING if reverse else pymongo.DESCENDING
            
            results = self._collection.find(query) \
                      .sort(sort, order) \
                      .skip(genericCollectionSlice.offset) \
                      .limit(genericCollectionSlice.limit)

        elif complexSort is not None:
            results = self._collection.find(query) \
                      .sort(complexSort) \
                      .skip(genericCollectionSlice.offset) \
                      .limit(genericCollectionSlice.limit)


        else:
            # slow-path which uses custom map-reduce for sorting
            # --------------------------------------------------
            scope = {
                'query'         : user_query, 
                'limit'         : genericCollectionSlice.limit, 
                'offset'        : genericCollectionSlice.offset, 
                'orig_coords'   : orig_coords, 
            }
            
            if viewport:
                if relaxed:
                    earthRadius = 3959.0 # miles
                    _viewport   = genericCollectionSlice.viewport
                    ll0         = (_viewport.upper_left.lat,  _viewport.upper_left.lng)
                    ll1         = (_viewport.lower_right.lat, _viewport.lower_right.lng)
                    
                    # expand viewport filter by 5%
                    lat_diff    = (ll0[0] - ll1[0]) * 0.05
                    lng_diff    = (ll0[1] - ll1[1]) * 0.05
                    
                    ll2_lat     = max(-90,  ll0[0] + lat_diff)
                    ll2_lng     = max(-180, ll0[1] + lng_diff)
                    
                    ll3_lat     = min(90,   ll1[0] - lat_diff)
                    ll3_lng     = min(180,  ll1[1] - lng_diff)
                    
                    scope['viewport'] = {
                        'upper_left' : {
                            'lat' : ll2_lat, 
                            'lng' : ll2_lng, 
                        }, 
                        'lower_right' : {
                            'lat' : ll3_lat, 
                            'lng' : ll3_lng, 
                        }, 
                    }
                else:
                    scope['viewport'] = genericCollectionSlice.viewport.dataExport()
            
            logs.debug("js scope: %s" % pprint.pformat(scope))
            
            if genericCollectionSlice.sort == 'proximity':
                # handle proximity-based sort
                # ---------------------------
                scope['center'] = genericCollectionSlice.coordinates.dataExport()
                
                # TODO: handle +180 / -180 meridian special case 
                _map = bson.code.Code("""function ()
                {
                    var diff0 = (this.entity.coordinates.lat - center.lat);
                    var diff1 = (this.entity.coordinates.lng - center.lng);
                    var score = Math.sqrt(diff0 * diff0 + diff1 * diff1);
                    
                    emit('query', { obj : this, score : score });
                }""")
            elif genericCollectionSlice.sort == 'popularity' or \
                (genericCollectionSlice.sort == 'relevance' and genericCollectionSlice.query is None):
                # handle popularity-based sort
                # ----------------------------
                _map = bson.code.Code("""function () {
                    var score = 0.0;
                    
                    try {
                        if (this.stats.num_credit > 0)
                            score += 10 * this.stats.num_credit;
                    } catch(err) {}
                    
                    try {
                        if (this.stats.num_likes > 0)
                            score += 3 * this.stats.num_likes;
                    } catch(err) {}
                    
                    try {
                        if (this.stats.num_comments > 0)
                            score += this.stats.num_comments;
                    } catch(err) {}
                    
                    emit('query', { obj : this, score : score });
                }""")
            elif genericCollectionSlice.sort == 'relevance':
                # handle relevancy-based sort
                # ---------------------------
                
                if relaxed:
                    scope['center'] = center
                
                # TODO: incorporate more complicated relevancy metrics into this 
                # weighting function, including possibly:
                #     * recency
                #     * popularity
                #     * other metadata sources (e.g., tags, menu, etc.)
                # NOTE: blurb & entity title matching already occurs at regex query level!
                # these scores are then completely redundant since levenshtein will never 
                # be taken into account.
                _map = bson.code.Code("""function () {
                    var title_value = 0.0, dist_value = 0.0;
                    var blurb, title;
                    
                    try {
                        title = this.entity.title.toLowerCase();
                    } catch(e) {
                        title = "";
                    }
                    
                    try {
                        blurb = this.blurb.toLowerCase();
                    } catch(e) {
                        blurb = "";
                    }
                    
                    if (title.length > 0 && title.match(query)) {
                        title_value = 1.0;
                    } else if (blurb.length > 0 && blurb.match(query)) {
                        title_value = 0.5;
                    } else {
                        title_value = 0.1;
                    }
                    
                    try {
                        var inside = false;
                        
                        try {
                            if (this.entity.coordinates.lat >= viewport.lower_right.lat && this.entity.coordinates.lat <= viewport.upper_left.lat) {
                                if (viewport.upper_left.lng <= viewport.lower_right.lng) {
                                    if (this.entity.coordinates.lng >= viewport.upper_left.lng && this.entity.coordinates.lng <= viewport.lower_right.lng) {
                                        inside = true;
                                    }
                                } else {
                                    if (this.entity.coordinates.lng >= viewport.upper_left.lng || this.entity.coordinates.lng <= viewport.lower_right.lng) {
                                        inside = true;
                                    }
                                }
                            }
                        } catch (e) { }
                        
                        if (inside) {
                            dist_value = 10000.0;
                        } else {
                            var diff0 = (this.entity.coordinates.lat - center.lat);
                            var diff1 = (this.entity.coordinates.lng - center.lng);
                            var dist  = Math.sqrt(diff0 * diff0 + diff1 * diff1);
                            
                            if (dist < 0) {
                                dist_value = 0;
                            } else {
                                var x = (dist - 50);
                                var a = -0.4;
                                var b = 2.8;
                                var c = -6.3;
                                var d = 4.0;
                                
                                var x2 = x * x;
                                var x3 = x2 * x;
                                
                                var value = a * x3 + b * x2 + c * x + d;
                                
                                if (value > 0) {
                                    value = Math.log(1 + value);
                                } else {
                                    value = -Math.log(1 - value);
                                }
                                
                                dist_value = value;
                            }
                            
                            if (!orig_coords) {
                                var earthRadius = 3959.0;
                                var dist2 = dist * earthRadius;
                                
                                if (dist2 >= 500) {
                                    dist_value = 0;
                                    return;
                                }
                            }
                        }
                    }
                    catch (e) {
                        dist_value = 0;
                    }
                    
                    var title_weight = 1.0;
                    var dist_weight  = 1.0;
                    
                    var score = title_value * title_weight + \
                                dist_value  * dist_weight;
                    
                    emit('query', { obj : this, score : score });
                }""")
            
            # TODO: optimize reduce for offset / limit
            _reduce = bson.code.Code("""function(key, values) {
                var min = 0.0;
                var out = [];
                
                function sortOut(a, b) {
                    if (a.score > 0) { scoreA = a.score } else { scoreA = 0 }
                    if (b.score > 0) { scoreB = b.score } else { scoreB = 0 }
                    return scoreB - scoreA;
                }
                values.forEach(function(v) {
                    if (out.length < offset + limit) {
                        out[out.length] = { score : v.score, obj : v.obj }
                        if (v.score < min) { min = v.score; }
                    } else {
                        if (v.score > min) {
                            out[out.length] = { score : v.score, obj : v.obj }
                            out.sort(sortOut);
                            out.pop();
                        }
                    }
                });
                
                out.sort(sortOut);
                var obj = new Object();
                obj.data = out;
                
                return obj;
            }""")
            
            logs.debug('Query: %s' % query)
            
            try:
                result = self._collection.inline_map_reduce(_map, _reduce, query=query, scope=scope, limit=1000)
            except Exception as e:
                logs.warning('Map/Reduce failed: %s' % e)
                logs.debug('Query: %s' % query)
                logs.debug('Scope: %s' % scope)
                logs.debug('Map: %s' % _map)
                logs.debug('Reduce: %s' % _reduce)
                raise
            
            try:
                value = result[-1]['value'] 
                if 'data' in value:
                    data = value['data']
                else:
                    data = [value]
                
                assert(isinstance(data, list))
            except Exception:
                logs.debug(utils.getFormattedException())
                return []
            
            results = map(lambda d: d['obj'], data)
            if reverse:
                results = list(reversed(results))
            
            if viewport and relaxed:
                scope = AttributeDict(scope)
                
                def _within_viewport(result):
                    result = AttributeDict(result)
                    if result.entity.coordinates.lat >= scope.viewport.lower_right.lat and \
                        result.entity.coordinates.lat <= scope.viewport.upper_left.lat:
                        
                        if scope.viewport.upper_left.lng <= scope.viewport.lower_right.lng:
                            if result.entity.coordinates.lng >= scope.viewport.upper_left.lng and \
                                result.entity.coordinates.lng <= scope.viewport.lower_right.lng:
                                return True
                        else:
                            # handle special case where the viewport crosses the +180 / -180 mark
                            if result.entity.coordinates.lng >= scope.viewport.upper_left.lng or \
                                result.entity.coordinates.lng <= scope.viewport.lower_right.lng:
                                return True
                    
                    return False
                
                inside = filter(_within_viewport, results)
                
                if len(inside) > 0:
                    logs.debug("%d results inside viewport; pruning %d results outside" % 
                               (len(inside), len(results) - len(inside)))
                    results = inside
                else:
                    logs.debug("no results inside viewport; %d results outside" % (len(results), ))
            
            results = results[genericCollectionSlice.offset : genericCollectionSlice.offset + genericCollectionSlice.limit]
        
        results = map(self._convertFromMongo, results)
        
        # condense results to remove duplicate entities across stamps
        if genericCollectionSlice.unique:
            seen = set()
            ret  = []
            
            for result in results:
                try:
                    entity_id = result.entity_id
                    
                    if entity_id in seen:
                        continue
                    
                    seen.add(entity_id)
                except Exception:
                    logs.warn(utils.getFormattedException())
                
                ret.append(result)
            
            results = ret
        
        return results

