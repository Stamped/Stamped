#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import logs, re
import unicodedata, utils
import libs.CountryData

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
    'establishment'     : 'other', 
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

countries = libs.CountryData.countries

city_state_re = re.compile('.*,\s*([a-zA-Z .-]+)\s*,\s*([a-zA-Z]+).*')
year_re = re.compile(r'([0-9]{4})')

def formatReleaseDate(date):
    try:
        return date.strftime("%h %d, %Y")
    except:
        return None

def formatAddress(entity, extendStreet=False, breakLines=False):

    street      = entity.address_street
    street_ext  = entity.address_street_ext
    locality    = entity.address_locality
    region      = entity.address_region
    postcode    = entity.address_postcode
    country     = entity.address_country

    delimiter = '\n' if breakLines else ', '

    if street is not None and locality is not None and country is not None:

        # Expand street 
        if extendStreet == True and street_ext is not None:
            street = '%s %s' % (street, street_ext)

        # Use state if in US
        if country == 'US':
            if region is not None and postcode is not None:
                return '%s%s%s, %s %s' % (street, delimiter, locality, region, postcode)
            elif region is not None:
                return '%s%s%s, %s' % (street, delimiter, locality, postcode)
            elif postcode is not None:
                return '%s%s%s, %s' % (street, delimiter, locality, region)

        # Use country if outside US
        else:
            if country in countries:
                return '%s%s%s, %s' % (street, delimiter, locality, countries[country])
            else:
                return '%s%s%s, %s' % (street, delimiter, locality, country)

    if entity.address is not None:
        return entity.address
        
    if entity.neighborhood is not None:
        return entity.neighborhood

    return None

def formatSubcategory(subcategory):
    if subcategory == 'tv':
        return 'TV'
    return subcategory.title()

def formatFilmLength(seconds):
    try:
        seconds = int(seconds)
        m = (seconds % 3600) / 60
        h = (seconds - (seconds % 3600)) / 3600
        if h > 0:
            return '%s hr %s min' % (h, m)
        else:
            return '%s min' % m
    except Exception:
        return None

def getGenericSubtitle(entity):
    return str(entity.subcategory).replace('_', ' ').title()

def getLocationSubtitle(entity, detailed=False):
    # Return detailed address data if requested
    if detailed:
        
        address = formatAddress(entity)
        if address is not None:
            return address
        
        return getGenericSubtitle(entity)
    
    # Check if address components exist
    if entity.address_country is not None and entity.address_locality is not None:
        if entity.address_country == 'US':
            if entity.address_region is not None:
                return "%s, %s" % (entity.address_locality, entity.address_region)
        else:
            country = entity.address_country
            if entity.address_country in countries:
                country = countries[entity.address_country]
            return "%s, %s" % (entity.address_locality, country)
    
    # Extract city / state with regex as fallback
    if entity.address is not None:
        match = city_state_re.match(entity.address)
        
        if match is not None:
            # city, state
            return "%s, %s" % match.groups()
    
    # Use generic subtitle as last resort
    return getGenericSubtitle(entity)

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
        entity.subtitle = getLocationSubtitle(entity, detailed)
    
    elif entity.category == 'book':
        if entity.author is not None:
            entity.subtitle = entity.author
        else:
            setSubtitle(entity)
    
    elif entity.category == 'film':
        if entity.subcategory == 'movie':
            try:
                year = year_re.search(entity.original_release_date).groups()[0]
                entity.subtitle = 'Movie (%s)' % year
            except:
                entity.subtitle = 'Movie'
        elif entity.subcategory == 'tv':
            if entity.network_name is not None:
                entity.subtitle = 'TV Show (%s)' % entity.network_name
            else:
                entity.subtitle = 'TV Show'
    
    elif entity.category == 'music':
        if entity.subcategory == 'artist':
            entity.subtitle = 'Artist'
        elif entity.subcategory == 'album':
            if entity.artist_display_name is not None:
                entity.subtitle = "Album by %s" % entity.artist_display_name
            else:
                entity.subtitle = 'Album'
        elif entity.subcategory == 'song':
            if entity.artist_display_name is not None:
                entity.subtitle = "Song by %s" % entity.artist_display_name
            else:
                entity.subtitle = 'Song'
    
    elif entity.category == 'other':
        if entity.subcategory == 'app' and entity.artist_display_name is not None:
            entity.subtitle = 'App (%s)' % entity.artist_display_name
        elif entity.address is not None:
            entity.subtitle = getLocationSubtitle(entity, detailed)
        elif entity.subtitle is None:
            setSubtitle(entity)
    
    if entity.subtitle is None or len(entity.subtitle) == 0:
        logs.warning('Invalid subtitle: %s' % entity)
        setSubtitle(entity)
        
        if entity.subtitle is None or len(entity.subtitle) == 0:
            entity.subtitle = "Other"
    
    return entity

def isEqual(entity1, entity2, prefix=False):
    """
    # note: useful for debugging search dupes
    from pprint import pformat
    utils.log("-" * 40)
    utils.log(pformat(entity1.value))
    utils.log(pformat(entity2.value))
    utils.log("-" * 40)
    """
    
    try:
        is_google_places_special_case = \
            ((entity1.subcategory == 'other' and entity1.googleLocal is not None) or \
             (entity2.subcategory == 'other' and entity2.googleLocal is not None))
        
        if not prefix and entity1.subcategory != entity2.subcategory:
            # if either entity came from google autosuggest, disregard subcategories not matching
            if not is_google_places_special_case:
                return False
        
        if entity1.simplified_title != entity2.simplified_title:
            return False
        elif prefix or is_google_places_special_case:
            return True
        
        if entity1.lat is not None:
            if entity2.lat is None:
                return False
            
            earthRadius = 3959.0 # miles
            
            distance = utils.get_spherical_distance((entity1.lat, entity1.lng), 
                                                    (entity2.lat, entity2.lng))
            
            distance = distance * earthRadius
            
            if distance > 0.8 or distance < 0:
                return False
            
            # TODO: investigate libraries to determine similarity between two 
            # addresses (e.g., converting to some standardized form and then 
            # comparing)
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
    except:
        return False

def getSimplifiedTitle(title):
    title = unicodedata.normalize('NFKD', unicode(title)).encode('ascii', 'ignore')
    title = title.lower().strip()
    
    return title

