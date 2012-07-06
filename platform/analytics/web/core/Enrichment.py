#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from MongoStampedAPI import MongoStampedAPI
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
        output.append('%s %s enrich success rate: %s' % (src, ent, float(enriched)/total*100))
        cumulative['sources.'+src+'_id'] = {'$exists': False}
    non_enriched = collection.find(cumulative).count()
    output.append('%% of %s entities with some enrichment: %s' % (ent,float(total - non_enriched)/total*100))
    return output


#Comprises the queries for a kind and array of enrichment sources
def kindEnrichRate(kind, enrich_srcs,collection):
    output = []
    total = collection.find({'kind': kind}).count()
    output.append('Total number of %s entities: %s' % (kind,total))
    cumulative = {'kind': kind}
    for src in enrich_srcs:
        enriched = collection.find({'kind': kind, 'sources.'+src+'_id': {'$exists': True}}).count()
        output.append('%s %s enrich success rate: %s' % (src, kind, float(enriched)/total*100))
        cumulative['sources.'+src+'_id'] = {'$exists': False}
    non_enriched = collection.find(cumulative).count()
    output.append('%% of %s entities with some enrichment: %s' % (kind,float(total - non_enriched)/total*100))
    return output


def getEnrichmentStats(collection):
    
    #Media items
    media_items = 'Total Media Items: %s' % (collection.find({'kind': 'media_item'}).count())
    songs = typeEnrichRate('track',['itunes','spotify','rdio','amazon'],collection)
    movies = typeEnrichRate('movie',['itunes','netflix','tmdb','amazon'],collection)
    books = typeEnrichRate('book',['itunes','amazon'],collection)


    #Media Collections
    media_colls = 'Total Media Collections: %s' % (collection.find({'kind': 'media_collection'}).count())
    shows = typeEnrichRate('tv',['itunes','amazon','netflix',],collection)
    albums = typeEnrichRate('album',['itunes','spotify','rdio','amazon'],collection)


    #Places
    places = kindEnrichRate('place',['opentable','foursquare','instagram','googleplaces','factual','singleplatform'],collection)

    
    #Special Request via landon
    single_factual = collection.find({'kind': 'place', 'sources.singleplatform_id': {'$exists': True}, 'sources.factual_id': {'$exists': True}}).count()
    factual = collection.find({'kind': 'place','sources.factual_id': {'$exists': True}}).count()
    percentSingle = '%% of factual ids with singleplatform ids: %s' % (float(single_factual)/factual*100)
    

    #People
    artists = typeEnrichRate('artist',['itunes','rdio','spotify'],collection)

    #Software    
    app = typeEnrichRate('app',['itunes'],collection)


    return media_items,songs,movies,books,media_colls,shows,albums,places,percentSingle,artists,app


