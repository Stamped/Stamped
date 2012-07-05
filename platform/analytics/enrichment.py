#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from api.MongoStampedAPI import MongoStampedAPI
from pprint import pprint

api = MongoStampedAPI()
collection = api._entityDB._collection



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
def typeEnrichRate(ent, enrich_srcs):
    total = collection.find({'kind': typeToKind(ent), 'types': ent}).count()
    output =  '\nTotal number of '+ent+ ' entities: '+str(total)+'\n'
    cumulative = {'kind': typeToKind(ent), 'types': ent}
    for src in enrich_srcs:
        enriched = collection.find({'kind': typeToKind(ent), 'types': ent, 'sources.'+src+'_id': {'$exists': True}}).count()
        output = output +src+' '+ent+' enrich success rate: ' + str(float(enriched)/total*100) +'\n'
        cumulative['sources.'+src+'_id'] = {'$exists': False}
    non_enriched = collection.find(cumulative).count()
    output = output + '% of '+ent+' entities with some enrichment: ' + str(float(total - non_enriched)/total*100) +'\n'
    return output


#Comprises the queries for a kind and array of enrichment sources
def kindEnrichRate(kind, enrich_srcs):
    total = collection.find({'kind': kind}).count()
    output =  '\nTotal number of '+kind+ ' entities: '+str(total)+'\n'
    cumulative = {'kind': kind}
    for src in enrich_srcs:
        enriched = collection.find({'kind': kind, 'sources.'+src+'_id': {'$exists': True}}).count()
        output = output +src+' '+kind+' enrich success rate: ' + str(float(enriched)/total*100) +'\n'
        cumulative['sources.'+src+'_id'] = {'$exists': False}
    non_enriched = collection.find(cumulative).count()
    output = output + '% of '+kind+' entities with some enrichment: ' + str(float(total - non_enriched)/total*100) +'\n'
    return output

#################
###Media items###
#################

media_items = collection.find({'kind': 'media_item'}).count()
print '\n'+'Number of media items: '+str(media_items) +'\n'


#Songs
songs = typeEnrichRate('track',['itunes','spotify','rdio','amazon'])
print songs


#Movies
movies = typeEnrichRate('movie',['itunes','netflix','tmdb','amazon'])
print movies


#Books
books = typeEnrichRate('book',['itunes','amazon'])
print books


###################
#Media Collections#
###################

media_colls = collection.find({'kind': 'media_collection'}).count()
print '\n'+'Number of media collections: '+str(media_colls) +'\n'

#Tv Shows
shows = typeEnrichRate('tv',['itunes','amazon','netflix',])
print shows


#Albums
albums = typeEnrichRate('album',['itunes','spotify','rdio','amazon'])
print albums


########
#Places#
########

#There were a shitload of types for places so default diagnostics only show overall places.

places = kindEnrichRate('place',['opentable','foursquare','instagram','googleplaces','factual','singleplatform'])
print places

#Special Request via landon
single_factual = collection.find({'kind': 'place', 'sources.singleplatform_id': {'$exists': True}, 'sources.factual_id': {'$exists': True}}).count()
factual = collection.find({'kind': 'place','sources.factual_id': {'$exists': True}}).count()
print '% of factual_ids with singleplatform_ids '+ str(float(single_factual)/factual*100)


##########
##People##
##########

artists = typeEnrichRate('artist',['itunes','rdio','spotify'])
print artists


############
##Software##
############

app = typeEnrichRate('app',['itunes'])
print app


