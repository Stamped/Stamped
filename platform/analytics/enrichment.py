import Globals
from MongoStampedAPI import MongoStampedAPI
from pprint import pprint

api = MongoStampedAPI();
collection = api._entityDB._collection;

kinds = {'track' : 'media_item', 'movie' : 'media_item', 'book' : 'media_item', 'tv' : 'media_collection', 'album' : 'media_collection',
         'bar' : 'place', 'restaurant' : 'place','establishment' : 'place','point_of_interest' : 'place','cafe' : 'place','market' : 'place',
         'park' : 'place','store' : 'place','bakery' : 'place','beauty_salon' : 'place','lodging' : 'place','night_club' : 'place',
         'museum' : 'place','clothing_store' : 'place','shopping_mall' : 'place','shoe_store' : 'place', 'artist' : 'person'}


#Comprises the queries for a type and array of enrichment sources
def type_enrich_rate(ent, enrich_srcs):
    total = collection.find({'kind': kinds[ent], 'types': ent}).count();
    output =  '\nTotal number of '+ent+ ' entities: '+str(total)+'\n';
    cumulative = {'kind': kinds[ent], 'types': ent};
    for src in enrich_srcs:
        enriched = collection.find({'kind': kinds[ent], 'types': ent, 'sources.'+src+'_id': {'$exists': True}}).count();
        output = output +src+' '+ent+' enrich success rate: ' + str(float(enriched)/total*100) +'\n'
        cumulative['sources.'+src+'_id'] = {'$exists': False};
    non_enriched = collection.find(cumulative).count();
    output = output + '% of '+ent+' entities with some enrichment: ' + str(float(total - non_enriched)/total*100) +'\n'
    return output


#Comprises the queries for a kind and array of enrichment sources
def kind_enrich_rate(kind, enrich_srcs):
    total = collection.find({'kind': kind}).count();
    output =  '\nTotal number of '+kind+ ' entities: '+str(total)+'\n';
    cumulative = {'kind': kind};
    for src in enrich_srcs:
        enriched = collection.find({'kind': kind, 'sources.'+src+'_id': {'$exists': True}}).count();
        output = output +src+' '+kind+' enrich success rate: ' + str(float(enriched)/total*100) +'\n'
        cumulative['sources.'+src+'_id'] = {'$exists': False};
    non_enriched = collection.find(cumulative).count();
    output = output + '% of '+kind+' entities with some enrichment: ' + str(float(total - non_enriched)/total*100) +'\n'
    return output

#################
###Media items###
#################

media_items = collection.find({'kind': 'media_item'}).count();
print '\n'+'Number of media items: '+str(media_items) +'\n'


#Songs
songs = type_enrich_rate('track',['itunes','spotify','rdio','amazon']);
print songs


#Movies
movies = type_enrich_rate('movie',['itunes','netflix','tmdb','amazon']);
print movies


#Books
books = type_enrich_rate('book',['itunes','amazon']);
print books


###################
#Media Collections#
###################

media_colls = collection.find({'kind': 'media_collection'}).count();
print '\n'+'Number of media collections: '+str(media_colls) +'\n'

#Tv Shows
shows = type_enrich_rate('tv',['itunes','amazon','netflix',]);
print shows


#Albums
albums = type_enrich_rate('album',['itunes','spotify','rdio','amazon']);
print albums


########
#Places#
########

#There were a shitload of types for places so default diagnostics only show overall places.

places = kind_enrich_rate('place',['opentable','foursquare','instagram','googleplaces','factual','singleplatform']);
print places

#Special Request via landon
single_factual = collection.find({'kind': 'place', 'sources.singleplatform_id': {'$exists': True}, 'sources.factual_id': {'$exists': True}}).count()
factual = collection.find({'kind': 'place','sources.factual_id': {'$exists': True}}).count()
print '% of factual_ids with singleplatform_ids '+ str(float(single_factual)/factual)


##########
##People##
##########

artists = type_enrich_rate('artist',['itunes','rdio','spotify']);
print artists




