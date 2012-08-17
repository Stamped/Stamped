#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from servers.analytics.core.mongoQuery  import mongoQuery

class EnrichmentReport(object):
    
    def __init__(self, mongoQuery=mongoQuery()):
        self.mongoQ = mongoQuery
        
    #Comprises the queries for a type and array of enrichment sources
    def typeEnrichRate(self, type, enrich_srcs):
        output = []
        total = self.mongoQ.entity_collection.find({'types': type}).count()
        output.append('Total number of %s entities: %s' % (type, total))
        cumulative = {'types': type}
        for src in enrich_srcs:
            enriched = self.mongoQ.entity_collection.find({'types': type, ('sources.%s_id' % (src)) : {'$exists': True}}).count()
            output.append('%s %s enrich success rate: %.2f%%' % (src, type, float(enriched) / total * 100))
            cumulative['sources.%s_id' % src] = {'$exists': False}
        non_enriched = self.mongoQ.entity_collection.find(cumulative).count()
        output.append('%% of %s entities with some enrichment: %.2f%%' % (type,float(total - non_enriched) / total * 100))
        return output


    #Comprises the queries for a kind and array of enrichment sources
    def kindEnrichRate(self, kind, enrich_srcs):
        output = []
        total = self.mongoQ.entity_collection.find({'kind': kind}).count()
        output.append('Total number of %s entities: %s' % (kind, total))
        cumulative = {'kind': kind}
        for src in enrich_srcs:
            enriched = self.mongoQ.entity_collection.find({'kind': kind, ('sources.%s_id' % src): {'$exists': True}}).count()
            output.append('%s %s enrich success rate: %.2f%%' % (src, kind, float(enriched) / total * 100))
            cumulative['sources.%s_id' % src] = {'$exists': False}
        non_enriched = self.mongoQ.entity_collection.find(cumulative).count()
        output.append('%% of %s entities with some enrichment: %.2f%%' % (kind,float(total - non_enriched) / total * 100))
        return output


    def getEnrichmentStats(self, subset):
        
        #Media items
        if subset == 'media_items':
            unattempted = self.mongoQ.entity_collection.find({'subcategory': {'$in': ['book','track','movie']}}).count()
            attempted = self.mongoQ.entity_collection.find({'kind': 'media_item'}).count()
            breakdown = []
            breakdown.append(self.typeEnrichRate('track', ['itunes', 'spotify', 'rdio', 'amazon']))
            breakdown.append(self.typeEnrichRate('movie', ['itunes', 'netflix', 'tmdb', 'amazon']))
            breakdown.append(self.typeEnrichRate('book', ['itunes', 'amazon']))
                     
            return unattempted, attempted, breakdown
    
        #Media Collections
        elif subset == 'media_colls':
            unattempted = self.mongoQ.entity_collection.find({'subcategory': {'$in': ['tv', 'album']}}).count()
            attempted = self.mongoQ.entity_collection.find({'kind': 'media_collection'}).count()
            breakdown=[]
            breakdown.append(self.typeEnrichRate('tv', ['itunes', 'amazon', 'netflix']))
            breakdown.append(self.typeEnrichRate('album', ['itunes', 'spotify', 'rdio', 'amazon']))
    
            return unattempted, attempted, breakdown
    
        #Places
        elif subset == "places":
            unattempted = self.mongoQ.entity_collection.find({'category': 'food'}).count()
            unattempted += self.mongoQ.entity_collection.find({'category': 'other','subcategory': {'$nin': ['app','other']}}).count()
            attempted = self.mongoQ.entity_collection.find({'kind': 'place'}).count()
            breakdown = []
            breakdown.append(self.kindEnrichRate('place', ['opentable', 'foursquare', 'instagram', 'googleplaces', 'factual', 'singleplatform']))
        
            #Special Request via landon
            single_factual = self.mongoQ.entity_collection.find({'kind': 'place', 'sources.singleplatform_id': {'$exists': True}, 'sources.factual_id': {'$exists': True}}).count()
            factual = self.mongoQ.entity_collection.find({'kind': 'place','sources.factual_id': {'$exists': True}}).count()
            breakdown.append(['%% of factual ids with singleplatform ids: %s%%' % (float(single_factual) / factual * 100)])
        
            return unattempted, attempted, breakdown
    
        #People
        elif subset == 'people':
            unattempted = self.mongoQ.entity_collection.find({'subcategory': 'artist'}).count()
            attempted = self.mongoQ.entity_collection.find({'kind': 'person'}).count()
            breakdown = [self.typeEnrichRate('artist', ['itunes', 'rdio', 'spotify'])]
    
            return unattempted, attempted, breakdown
        
        #Software
        elif subset == 'software':    
            unattempted = self.mongoQ.entity_collection.find({'subcategory': 'app'}).count()
            attempted = self.mongoQ.entity_collection.find({'kind': 'software'}).count()
            breakdown=[self.typeEnrichRate('app', ['itunes'])]
    
            return unattempted, attempted, breakdown
    
        else:
            return None


