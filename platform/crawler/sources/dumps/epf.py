#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import mmap, os, re, utils

# generated by the following vim regex from:
#    http://www.apple.com/itunes/affiliates/resources/documentation/itunes-enterprise-partner-feed.html
# 
# :%s/^\([a-zA-Z0-9_]*\)[ \t]*\([a-zA-Z0-9_]*\)[ \t]*\([a-zA-Z0-9_]*\)[ \t]*\([A-Z].*\)/{\r'name' : "\1", \r'type' : "\2", \r'grouping' : "\3", \r'desc' : "\4", \r}, /g

files = [
    {
        'name' : "album_popularity_per_genre", 
        'type' : "Poplarity", 
        'grouping' : "popularity", 
        'desc' : "Assigns a ranking for the top music collections in a given storefront and genre.", 
    }, 
    {
        'name' : "application", 
        'type' : "Content", 
        'grouping' : "itunes", 
        'desc' : "Application metadata. Defines all iPhone and iPod touch applications in the App Store. Elements such as titles and descriptions default to English when available, otherwise the primary language of the application is used. For translations, see application_detail.", 
    }, 
    {
        'name' : "application_detail", 
        'type' : "Translation", 
        'grouping' : "itunes", 
        'desc' : "Defines the language-specific attributes of an application.", 
    }, 
    {
        'name' : "application_device_type", 
        'type' : "Join", 
        'grouping' : "itunes", 
        'desc' : "Many-to-many relationship between applications and device types. Associates applications with the devices with which they are compatible.", 
    }, 
    {
        'name' : "application_popularity_per_genre", 
        'type' : "Poplarity", 
        'grouping' : "poplarity", 
        'desc' : "Assigns a ranking for the top applications in a given storefront and genre", 
    }, 
    {
        'name' : "application_price", 
        'type' : "Content", 
        'grouping' : "pricing", 
        'desc' : "Retail price of an application.", 
    }, 
    {
        'name' : "artist", 
        'type' : "Content", 
        'grouping' : "itunes", 
        'desc' : "Artist metadata. Unlike other Content and Join tables, this artist table contains all the artists, regardless of availability of the artist's contents in any given country of interest.", 
    }, 
    {
        'name' : "artist_application", 
        'type' : "Join", 
        'grouping' : "itunes", 
        'desc' : "Associates applications with their artists (or authors). Every application has exactly one artist.", 
    }, 
    {
        'name' : "artist_collection", 
        'type' : "Join", 
        'grouping' : "itunes", 
        'desc' : "Many-to-many relationship between artists and collections. Only primary artists are included.", 
    }, 
    {
        'name' : "artist_match", 
        'type' : "Content", 
        'grouping' : "match", 
        'desc' : "Mappings from the iTunes internal identifier for artist to external identifiers.", 
    }, 
    {
        'name' : "artist_song", 
        'type' : "Join", 
        'grouping' : "itunes", 
        'desc' : "Many-to-many relationship between artists and songs. Only primary artists are included.", 
    }, 
    {
        'name' : "artist_translation", 
        'type' : "Translation", 
        'grouping' : "itunes", 
        'desc' : "The translation string for artist names for a specific language.", 
    }, 
    {
        'name' : "artist_type", 
        'type' : "Reference", 
        'grouping' : "itunes", 
        'desc' : "Artist type metadata. Defines all artist types; including musicians, TV shows, actors, iPhone developers, and authors.", 
    }, 
    {
        'name' : "artist_video", 
        'type' : "Join", 
        'grouping' : "itunes", 
        'desc' : "Many-to-many relationship between artists and videos. Only primary artists are included.", 
    }, 
    {
        'name' : "collection", 
        'type' : "Content", 
        'grouping' : "itunes", 
        'desc' : "A collection can contain multiple songs and videos, and can represent a music album, audiobook, or TV season.", 
    }, 
    {
        'name' : "collection_match", 
        'type' : "Content", 
        'grouping' : "match", 
        'desc' : "Mappings from the iTunes internal identifier for collection to external identifiers.", 
    }, 
    {
        'name' : "collection_price", 
        'type' : "Content", 
        'grouping' : "pricing", 
        'desc' : "The retail price of the collection.", 
    }, 
    {
        'name' : "collection_song", 
        'type' : "Join", 
        'grouping' : "itunes", 
        'desc' : "Many-to-many relationship between collections and songs. Most of the songs are included only in one collection.", 
    }, 
    {
        'name' : "collection_translation", 
        'type' : "Translation", 
        'grouping' : "itunes", 
        'desc' : "The translation string for collection names for a specific language.", 
    }, 
    {
        'name' : "collection_type", 
        'type' : "Reference", 
        'grouping' : "itunes", 
        'desc' : "The type of collection (TV season, album, and so on).", 
    }, 
    {
        'name' : "collection_video", 
        'type' : "Join", 
        'grouping' : "itunes", 
        'desc' : "Many-to-many relationship between collections and videos. Most of the videos are included only in one collection.", 
    }, 
    {
        'name' : "device_type", 
        'type' : "Reference", 
        'grouping' : "itunes", 
        'desc' : "Device type metadata. Specifies the types of devices currently available (for example, iPhone and iPod touch).", 
    }, 
    {
        'name' : "genre", 
        'type' : "Reference", 
        'grouping' : "itunes", 
        'desc' : "Genre name and its structure. All music genres are represented in hierarchical manner starting from genre 34 Music.", 
    }, 
    {
        'name' : "genre_application", 
        'type' : "Join", 
        'grouping' : "itunes", 
        'desc' : "Genre information for the application. Associates an application with one or more categories. There is only one primary genre for each application.", 
    }, 
    {
        'name' : "genre_artist", 
        'type' : "Join", 
        'grouping' : "itunes", 
        'desc' : "Genre information of artists. There is only one primary genre for each artist.", 
    }, 
    {
        'name' : "genre_collection", 
        'type' : "Join", 
        'grouping' : "itunes", 
        'desc' : "Genre information of a collection. There is only one primary genre for each collection.", 
    }, 
    {
        'name' : "genre_video", 
        'type' : "Join", 
        'grouping' : "itunes", 
        'desc' : "Genre information of video. There is only one primary genre for each video.", 
    }, 
    {
        'name' : "key_value", 
        'type' : "Meta", 
        'grouping' : "itunes", 
        'desc' : "Utility file to store metadata to the specific EPF export. Each record is a key-value pair. For example, the schema version number and date of the last full mode data dump are included.", 
    }, 
    {
        'name' : "imix", 
        'type' : "Content", 
        'grouping' : "itunes", 
        'desc' : "Metadata for mixes that are defined by iTunes users.", 
    }, 
    {
        'name' : "media_type", 
        'type' : "Reference", 
        'grouping' : "itunes", 
        'desc' : "Types of products.", 
    }, 
    {
        'name' : "mix", 
        'type' : "Content", 
        'grouping' : "itunes", 
        'desc' : "Metadata for mixes that are defined editorially by iTunes.", 
    }, 
    {
        'name' : "mix_collection", 
        'type' : "Content", 
        'grouping' : "itunes", 
        'desc' : "Metadata for collections of mixes.", 
    }, 
    {
        'name' : "mix_type", 
        'type' : "Reference", 
        'grouping' : "itunes", 
        'desc' : "Types of mixes.", 
    }, 
    {
        'name' : "parental_advisory", 
        'type' : "Reference", 
        'grouping' : "itunes", 
        'desc' : "The type of parental advisory status.", 
    }, 
    {
        'name' : "role", 
        'type' : "Reference", 
        'grouping' : "itunes", 
        'desc' : "The name of the artist role.", 
    }, 
    {
        'name' : "song", 
        'type' : "Content", 
        'grouping' : "itunes", 
        'desc' : "Song metadata. In most cases, one song is only contained in one collection. But in some cases, one song is shared by multiple collections.", 
    }, 
    {
        'name' : "song_match", 
        'type' : "Content", 
        'grouping' : "match", 
        'desc' : "Mappings from the iTunes internal identifier for song to external identifiers.", 
    }, 
    {
        'name' : "song_imix", 
        'type' : "Join", 
        'grouping' : "itunes", 
        'desc' : "Join table between imixes and songs.", 
    }, 
    {
        'name' : "song_mix", 
        'type' : "Join", 
        'grouping' : "itunes", 
        'desc' : "Join table between mixes and songs.", 
    }, 
    {
        'name' : "song_popularity_per_genre", 
        'type' : "Poplarity", 
        'grouping' : "poplarity", 
        'desc' : "Assigns a ranking to the top songs in a given storefront and genre", 
    }, 
    {
        'name' : "song_price", 
        'type' : "Content", 
        'grouping' : "pricing", 
        'desc' : "The retail price of the song.", 
    }, 
    {
        'name' : "song_translation", 
        'type' : "Translation", 
        'grouping' : "itunes", 
        'desc' : "The translation string for song names for a specific language.", 
    }, 
    {
        'name' : "storefront", 
        'type' : "Reference", 
        'grouping' : "itunes", 
        'desc' : "Identifier number of each country storefront.", 
    }, 
    {
        'name' : "translation_type", 
        'type' : "Reference", 
        'grouping' : "itunes", 
        'desc' : "The type of translation string.", 
    }, 
    {
        'name' : "video", 
        'type' : "Content", 
        'grouping' : "itunes", 
        'desc' : "Video metadata. In most cases, one video is only contained in one collection. But in some cases, one video is shared by multiple collections.", 
    }, 
    {
        'name' : "video_match", 
        'type' : "Content", 
        'grouping' : "match", 
        'desc' : "Mappings from the iTunes internal identifier for video to external identifiers.", 
    }, 
    {
        'name' : "video_price", 
        'type' : "Content", 
        'grouping' : "pricing", 
        'desc' : "The retail price of the video.", 
    }, 
    {
        'name' : "video_translation", 
        'type' : "Translation", 
        'grouping' : "itunes", 
        'desc' : "The translation string for video names for a specific language.", 
    }, 
]

def get_file_info(filename):
    filename = filename.lower()
    
    for f in files:
        if f['name'] == filename:
            return f
    
    return None

def parse_table_format(f, filename):
    epf_filename  = os.path.basename(filename)
    epf_filename  = re.sub(r'([^-]*)-.*', r'\1', epf_filename)
    epf_file_info = get_file_info(epf_filename)
    
    # parse column names
    l = f.readline()
    assert l.startswith('#')
    l = l[1:-2]
    
    cols = l.split('\x01')
    
    # parse primary key(s)
    l = f.readline()
    assert l.startswith('#')
    l = l[1:-2].replace('primaryKey:', '')
    primary_keys = l.split('\x01')
    
    # parse suggested types
    l = f.readline()
    assert l.startswith('#')
    l = l[1:-2].replace('dbTypes:', '')
    types = l.split('\x01')
    
    # parse export mode
    l = f.readline()
    assert l.startswith('#')
    l = l[1:-2]
    export_mode = l.replace('exportMode:', '')
    
    for primary_key in primary_keys:
        assert primary_key in cols
    assert len(types) == len(cols)
    
    columns = {}
    index = 0
    for col in cols:
        columns[col] = {
            'index' : index, 
            'type'  : types[index], 
        }
        index += 1
    
    return utils.AttributeDict({
        'filename' : filename, 
        'epf_filename' : epf_filename, 
        'epf_file_info' : epf_file_info, 
        'cols' : columns, 
        'primary_keys' : primary_keys, 
        'export_mode' : export_mode, 
    })

#PAGE_SIZE = int(utils.shell('pagesize')[0])
#MAP_SIZE  = PAGE_SIZE * 8

def parse_rows(f, table_format):
    row_len = len(dict(table_format['cols']))
    
    for l in f:
        if l.startswith('#'):
            continue
        
        l   = l[:-2].decode('utf8', 'ignore')
        row = l.split('\x01')
        
        # optional attributes at the end of a row may be cut off if they don't exist
        while len(row) < row_len:
            row.append(u'')
        
        assert len(row) == row_len
        yield row
