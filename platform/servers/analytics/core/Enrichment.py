#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from api.MongoStampedAPI import MongoStampedAPI
from gevent.pool import Pool


kindsMap = {
    # PEOPLE
    'artist' : 'person',

    # MEDIA COLLECTIONS
    'tv' : 'media_collection',
    'album' : 'media_collection',

    # MEDIA ITEMS
    'track' : 'media_item',
    'movie' : 'media_item',
    'book' : 'media_item',

    # SOFTWARE
    'app' : 'software',

    # PLACES
    'restaurant' : 'place',
    'bar' : 'place',
    'bakery' : 'place',
    'cafe' : 'place',
    'market' : 'place',
    'food' : 'place',
    'night_club' : 'place',
    'amusement_park' : 'place',
    'aquarium' : 'place',
    'art_gallery' : 'place',
    'beauty_salon' : 'place',
    'book_store' : 'place',
    'bowling_alley' : 'place',
    'campground' : 'place',
    'casino' : 'place',
    'clothing_store' : 'place',
    'department_store' : 'place',
    'establishment' : 'place',
    'florist' : 'place',
    'gym' : 'place',
    'home_goods_store' : 'place',
    'jewelry_store' : 'place',
    'library' : 'place',
    'liquor_store' : 'place',
    'lodging' : 'place',
    'movie_theater' : 'place',
    'museum' : 'place',
    'park' : 'place',
    'school' : 'place',
    'shoe_store' : 'place',
    'shopping_mall' : 'place',
    'spa' : 'place',
    'stadium' : 'place',
    'store' : 'place',
    'university' : 'place',
    'zoo' : 'place'
}

def typeToKind(typ):
    return kindsMap[typ]
    
#Comprises the queries for a type and array of enrichment sources
def typeEnrichRate(ent, enrich_srcs,collection):
    output = []
    total = collection.find({'types': ent}).count()
    output.append('Total number of %s entities: %s' % (ent,total))
    cumulative = {'types': ent}
    for src in enrich_srcs:
        enriched = collection.find({'types': ent, 'sources.'+src+'_id': {'$exists': True}}).count()
        output.append('%s %s enrich success rate: %.2f%%' % (src, ent, float(enriched)/total*100))
        cumulative['sources.'+src+'_id'] = {'$exists': False}
    non_enriched = collection.find(cumulative).count()
    output.append('%% of %s entities with some enrichment: %.2f%%' % (ent,float(total - non_enriched)/total*100))
    return output


#Comprises the queries for a kind and array of enrichment sources
def kindEnrichRate(kind, enrich_srcs,collection):
    output = []
    total = collection.find({'kind': kind}).count()
    output.append('Total number of %s entities: %s' % (kind,total))
    cumulative = {'kind': kind}
    for src in enrich_srcs:
        enriched = collection.find({'kind': kind, 'sources.'+src+'_id': {'$exists': True}}).count()
        output.append('%s %s enrich success rate: %.2f%%' % (src, kind, float(enriched)/total*100))
        cumulative['sources.'+src+'_id'] = {'$exists': False}
    non_enriched = collection.find(cumulative).count()
    output.append('%% of %s entities with some enrichment: %.2f%%' % (kind,float(total - non_enriched)/total*100))
    return output


def getEnrichmentStats(collection,subset):
    
    #Media items
    if subset == 'media_items':
        unattempted = collection.find({'subcategory': {'$in': ['book','track','movie']}}).count()
        attempted = collection.find({'kind': 'media_item'}).count()
        breakdown = []
        breakdown.append(typeEnrichRate('track',['itunes','spotify','rdio','amazon'],collection))
        breakdown.append(typeEnrichRate('movie',['itunes','netflix','tmdb','amazon'],collection))
        breakdown.append(typeEnrichRate('book',['itunes','amazon'],collection))
                 
        return unattempted, attempted, breakdown

    #Media Collections
    elif subset == 'media_colls':
        unattempted = collection.find({'subcategory': {'$in': ['tv','album']}}).count()
        attempted = collection.find({'kind': 'media_collection'}).count()
        breakdown=[]
        breakdown.append(typeEnrichRate('tv',['itunes','amazon','netflix',],collection))
        breakdown.append(typeEnrichRate('album',['itunes','spotify','rdio','amazon'],collection))

        return unattempted, attempted, breakdown

    #Places
    elif subset == "places":
        unattempted = collection.find({'category': 'food'}).count()
        unattempted += collection.find({'category': 'other','subcategory': {'$nin': ['app','other']}}).count()
        attempted = collection.find({'kind': 'place'}).count()
        breakdown = []
        breakdown.append(kindEnrichRate('place',['opentable','foursquare','instagram','googleplaces','factual','singleplatform'],collection))
    
        #Special Request via landon
        single_factual = collection.find({'kind': 'place', 'sources.singleplatform_id': {'$exists': True}, 'sources.factual_id': {'$exists': True}}).count()
        factual = collection.find({'kind': 'place','sources.factual_id': {'$exists': True}}).count()
        breakdown.append(['%% of factual ids with singleplatform ids: %s%%' % (float(single_factual)/factual*100)])
    
        return unattempted, attempted, breakdown

    #People
    elif subset == 'people':
        unattempted = collection.find({'subcategory': 'artist'}).count()
        attempted = collection.find({'kind': 'person'}).count()
        breakdown = [typeEnrichRate('artist',['itunes','rdio','spotify'],collection)]

        return unattempted, attempted, breakdown
    
    #Software
    elif subset == 'software':    
        unattempted = collection.find({'subcategory': 'app'}).count()
        attempted = collection.find({'kind': 'software'}).count()
        breakdown=[typeEnrichRate('app',['itunes'],collection)]

        return unattempted, attempted, breakdown

    else:
        print "input error"
        return 


