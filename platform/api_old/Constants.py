#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


kinds = set([
    'place',
    'person',
    'media_collection',
    'media_item',
    'software',
    'other',
    ])

types = set([
    # PEOPLE
    'artist',

    # MEDIA COLLECTIONS
    'tv',
    'album',

    # MEDIA ITEMS
    'track',
    'movie',
    'book',

    # SOFTWARE
    'app',

    # PLACES
    'restaurant',
    'bar',
    'bakery',
    'cafe',
    'market',
    'food',
    'night_club',
    'amusement_park',
    'aquarium',
    'art_gallery',
    'beauty_salon',
    'book_store',
    'bowling_alley',
    'campground',
    'casino',
    'clothing_store',
    'department_store',
    'establishment',
    'florist',
    'gym',
    'home_goods_store',
    'jewelry_store',
    'library',
    'liquor_store',
    'lodging',
    'movie_theater',
    'museum',
    'park',
    'school',
    'shoe_store',
    'shopping_mall',
    'spa',
    'stadium',
    'store',
    'university',
    'zoo',
    ])

categories = set([
    'place',
    'music',
    'film',
    'book',
    'app',
    'other',
    ])

subcategoryData = {
    # Subcategory           Category        Kind                        Type
    'restaurant'        : ( 'place',        [ 'place' ],                [ 'restaurant' ] ),
    'bar'               : ( 'place',        [ 'place' ],                [ 'bar' ] ),
    'bakery'            : ( 'place',        [ 'place' ],                [ 'bakery' ] ),
    'cafe'              : ( 'place',        [ 'place' ],                [ 'cafe' ] ),
    'market'            : ( 'place',        [ 'place' ],                [ 'market' ] ),
    'food'              : ( 'place',        [ 'place' ],                [ 'food' ] ),
    'night_club'        : ( 'place',        [ 'place' ],                [ 'night_club' ] ),
    'amusement_park'    : ( 'place',        [ 'place' ],                [ 'amusement_park' ] ),
    'aquarium'          : ( 'place',        [ 'place' ],                [ 'aquarium' ] ),
    'art_gallery'       : ( 'place',        [ 'place' ],                [ 'art_gallery' ] ),
    'beauty_salon'      : ( 'place',        [ 'place' ],                [ 'beauty_salon' ] ),
    'book_store'        : ( 'place',        [ 'place' ],                [ 'book_store' ] ),
    'bowling_alley'     : ( 'place',        [ 'place' ],                [ 'bowling_alley' ] ),
    'campground'        : ( 'place',        [ 'place' ],                [ 'campground' ] ),
    'casino'            : ( 'place',        [ 'place' ],                [ 'casino' ] ),
    'clothing_store'    : ( 'place',        [ 'place' ],                [ 'clothing_store' ] ),
    'department_store'  : ( 'place',        [ 'place' ],                [ 'department_store' ] ),
    'establishment'     : ( 'place',        [ 'place' ],                [ 'establishment' ] ),
    'florist'           : ( 'place',        [ 'place' ],                [ 'florist' ] ),
    'gym'               : ( 'place',        [ 'place' ],                [ 'gym' ] ),
    'home_goods_store'  : ( 'place',        [ 'place' ],                [ 'home_goods_store' ] ),
    'jewelry_store'     : ( 'place',        [ 'place' ],                [ 'jewelry_store' ] ),
    'library'           : ( 'place',        [ 'place' ],                [ 'library' ] ),
    'liquor_store'      : ( 'place',        [ 'place' ],                [ 'liquor_store' ] ),
    'lodging'           : ( 'place',        [ 'place' ],                [ 'lodging' ] ),
    'movie_theater'     : ( 'place',        [ 'place' ],                [ 'movie_theater' ] ),
    'museum'            : ( 'place',        [ 'place' ],                [ 'museum' ] ),
    'park'              : ( 'place',        [ 'place' ],                [ 'park' ] ),
    'school'            : ( 'place',        [ 'place' ],                [ 'school' ] ),
    'shoe_store'        : ( 'place',        [ 'place' ],                [ 'shoe_store' ] ),
    'shopping_mall'     : ( 'place',        [ 'place' ],                [ 'shopping_mall' ] ),
    'spa'               : ( 'place',        [ 'place' ],                [ 'spa' ] ),
    'stadium'           : ( 'place',        [ 'place' ],                [ 'stadium' ] ),
    'store'             : ( 'place',        [ 'place' ],                [ 'store' ] ),
    'university'        : ( 'place',        [ 'place' ],                [ 'university' ] ),
    'zoo'               : ( 'place',        [ 'place' ],                [ 'zoo' ] ),

    # Subcategory           Category        Kind                        Type
    'book'              : ( 'book',         [ 'media_item' ],           [ 'book' ] ),

    # Subcategory           Category        Kind                        Type
    'movie'             : ( 'film',         [ 'media_item' ],           [ 'movie' ] ),
    'tv'                : ( 'film',         [ 'media_collection' ],     [ 'tv' ] ),

    # Subcategory           Category        Kind                        Type
    'artist'            : ( 'music',        [ 'person' ],               [ 'artist' ] ),
    'album'             : ( 'music',        [ 'media_collection' ],     [ 'album' ] ),
    'track'             : ( 'music',        [ 'media_item' ],           [ 'track' ] ),
    'song'              : ( 'music',        [ 'media_item' ],           [ 'track' ] ),

    # Subcategory           Category        Kind                        Type
    'app'               : ( 'app',          [ 'software' ],             [ 'app' ] ),

    # Subcategory           Category        Kind                        Type
    'other'             : ( 'other',        [ 'other' ],                [ 'other' ] ),
    'video_game'        : ( 'other',        [ 'software' ],             [ 'video_game' ] ),
    }

subcategories = set(subcategoryData.keys())

