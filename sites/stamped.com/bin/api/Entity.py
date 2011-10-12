#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import logs, re

from difflib    import SequenceMatcher

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

city_state_re = re.compile('.*,\s*([a-zA-Z .-]+)\s*,\s*([a-zA-Z][a-zA-Z]).*')

def setSubtitle(entity):
    entity.subtitle = str(entity.subcategory).replace('_', ' ').title()

def setFields(entity, detailed=False):
    global city_state_re

    try:
        entity.category = subcategories[entity.subcategory]
    except:
        entity.category = 'other'

    # Subtitle
    if entity.category == 'food':

        if detailed:
            if entity.address is not None:
                entity.subtitle = entity.address
            # elif entity.neighborhood is not None:
            #     entity.subtitle = entity.neighborhood
            else:
                setSubtitle(entity)
        else:
            # address = {}
            # if len(entity.address_components) > 0:
            #     for component in entity.address_components:
            #         for i in component['types']:
            #             address[str(i)] = component['short_name']
            
            # if 'locality' in address and 'administrative_area_level_1' in address:
            #     entity.subtitle = '%s, %s' % (address['locality'], \
            #                                   address['administrative_area_level_1'])
            # elif 'sublocality' in address and 'administrative_area_level_1' in address:
            #     entity.subtitle = '%s, %s' % (address['sublocality'], \
            #                                   address['administrative_area_level_1'])
            # elif entity.neighborhood is not None:
            #     entity.subtitle = entity.neighborhood
            # else:
            is_set = False
            
            if entity.address is not None:
                # attempt to parse the city, state from the address
                match = city_state_re.match(entity.address)
                
                if match is not None:
                    # city, state
                    entity.subtitle = "%s, %s" % match.groups()
                    is_set = True
            
            if not is_set:
                # else fall back to the generic subcategory
                setSubtitle(entity)
    
    elif entity.category == 'book':
        if entity.author != None:
            entity.subtitle = entity.author
        else:
            setSubtitle(entity)
    
    elif entity.category == 'film':
        if entity.subcategory == 'movie':
            if entity.original_release_date != None:
                entity.subtitle = 'Movie (%s)' % entity.original_release_date
            else:
                entity.subtitle = 'Movie'
        elif entity.subcategory == 'tv':
            if entity.network_name != None:
                entity.subtitle = 'TV Show (%s)' % entity.network_name
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
        if entity.subtitle:
            pass
        else:
            entity.subtitle = str(entity.subcategory).replace('_', ' ').title()
    
    if entity.subtitle is None or len(entity.subtitle) == 0:
        logs.warning('Invalid subtitle: %s' % entity)
        entity.subtitle = str(entity.subcategory).replace('_', ' ').title()
        
        if entity.subtitle is None or len(entity.subtitle) == 0:
            entity.subtitle = "Other"
    
    return entity

def isEqual(entity1, entity2):
    if entity1.subcategory != entity2.subcategory:
        return False
    
    if entity1.title.lower != entity2.title.lower():
        return False
    
    if entity1.lat is not None:
        if entity2.lat is None:
            return False
        
        earthRadius = 3959.0 # miles
        
        distance = utils.get_spherical_distance((entity1.lat, entity1.lng), 
                                                (entity2.lat, entity2.lng))
        distance = distance * earthRadius
        
        if distance > 0.8:
            return False
        
        """
        is_junk = " \t-,".__contains__ # characters for SequenceMatcher to disregard
        
        addr1 = entity1.address.lower()
        addr2 = entity2.address.lower()
        
        def _normalize_addr(addr):
            addr = addr.replace(' street ' ' st ')
            addr = addr.replace(' st. ' ' st ')
            addr = addr.replace(' boulevard ' ' st ')
            addr = addr.replace(' lane ' ' st ')
            addr = addr.replace(' highway ' ' st ')
            addr = addr.replace(' road ' ' st ')
            addr = addr.replace(',' ' ')
            return addr
        
        addr1 = _normalize_addr(addr1)
        addr2 = _normalize_addr(addr2)
        
        ratio = SequenceMatcher(is_junk, addr1, addr2).ratio()
        
        return (ratio >= 0.95)
        """
    
    elif entity2.lat is not None:
        return False
    
    return True

