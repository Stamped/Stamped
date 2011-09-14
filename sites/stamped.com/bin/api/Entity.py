#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

categories = set([
    'food', 
    'music', 
    'film', 
    'book', 
    'other'
])

subcategories = {
    # --------------------------
    #           food
    # --------------------------
    'restaurant'        : 'food', 
    'bar'               : 'food', 
    'bakery'            : 'food', 
    'cafe'              : 'food', 
    'market'            : 'food', 
    'food'              : 'food', 
    'night_club'        : 'food', 
    
    # --------------------------
    #           book
    # --------------------------
    'book'              : 'book', 
    
    # --------------------------
    #           film
    # --------------------------
    'movie'             : 'film', 
    'tv'                : 'film', 
    
    # --------------------------
    #           music
    # --------------------------
    'artist'            : 'music', 
    'song'              : 'music', 
    'album'             : 'music', 
    
    # --------------------------
    #           other
    # --------------------------
    'app'               : 'other', 
    'other'             : 'other', 
    
    # the following subcategories are from google places
    'amusement_park'    : 'other', 
    'aquarium'          : 'other', 
    'art_gallery'       : 'other', 
    'beauty_salon'      : 'other', 
    'book_store'        : 'other', 
    'bowling_alley'     : 'other', 
    'campground'        : 'other', 
    'casino'            : 'other', 
    'clothing_store'    : 'other', 
    'department_store'  : 'other', 
    'florist'           : 'other', 
    'gym'               : 'other', 
    'home_goods_store'  : 'other', 
    'jewelry_store'     : 'other', 
    'library'           : 'other', 
    'liquor_store'      : 'other', 
    'lodging'           : 'other', 
    'movie_theater'     : 'other', 
    'museum'            : 'other', 
    'park'              : 'other', 
    'school'            : 'other', 
    'shoe_store'        : 'other', 
    'shopping_mall'     : 'other', 
    'spa'               : 'other', 
    'stadium'           : 'other', 
    'store'             : 'other', 
    'university'        : 'other', 
    'zoo'               : 'other', 
    
    # the following subcategories are from amazon
    'video_game'        : 'other', 
}

def setSubtitle(entity):
    if entity.category == 'food':

        address = {}
        if len(entity.address_components) > 0:
            for component in entity.address_components:
                for i in component['types']:
                    address[i] = component['short_name']
        
        if 'locality' in address and 'administrative_area_level_1' in address:
            entity.subtitle = '%s, %s' % (address['locality'], \
                                        address['administrative_area_level_1'])
        else:
            entity.subtitle = str(entity.subcategory).title()

    elif entity.category == 'book':
        if entity.author != None:
            entity.subtitle = entity.author
        else:
            entity.subtitle = str(entity.subcategory).title()

    elif entity.category == 'film':
        if entity.subcategory == 'movie':
            if entity.original_release_date != None:
                entity.subtitle = entity.original_release_date
            else:
                entity.subtitle = 'Movie'
        elif entity.subcategory == 'tv':
            if entity.network_name != None:
                entity.subtitle = entity.network_name
            else:
                entity.subtitle = 'TV Show'

    elif entity.category == 'music' and entity.subcategory == 'artist':
        entity.subtitle = 'Artist'

    elif entity.category == 'music' and entity.subcategory == 'album':
        if entity.artist_display_name != None:
            entity.subtitle = "%s (Album)" % entity.artist_display_name
        else:
            entity.subtitle = 'Album'
            
    elif entity.category == 'music' and entity.subcategory == 'song':
        if entity.artist_display_name != None:
            entity.subtitle = "%s (Song)" % entity.artist_display_name
        else:
            entity.subtitle = 'Song'

    elif entity.category == 'other':
        entity.subtitle = str(entity.subcategory).replace('_', ' ').title()

    return entity

