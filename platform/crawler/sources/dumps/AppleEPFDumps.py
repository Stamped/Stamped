#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from crawler.sources.dumps.AppleEPFDump import AAppleEPFDump
from crawler.sources.dumps.AppleEPFRelationalDB import *

class AppleEPFArtistDump(AAppleEPFDump):
    
    _map = {
        'name'              : 'title', 
        'export_date'       : 'export_date', 
        'artist_id'         : 'aid', 
        'is_actual_artist'  : None, 
        'view_url'          : 'view_url', 
        'artist_type_id'    : None, 
    }
    
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Artists", self._map, [ "artist" ], "artist")
        
        self.artist_to_albums = AppleEPFArtistsToAlbumsRelationalDB()
        self.artist_to_albums.start()
        
        #self.artist_to_songs = AppleEPFArtistsToSongsRelationalDB()
        #self.artist_to_songs.start()
        
        self.album_popularity_per_genre = AppleEPFAlbumPopularityPerGenreRelationalDB()
        self.album_popularity_per_genre.start()
        
        self.song_popularity_per_genre = AppleEPFSongPopularityPerGenreRelationalDB()
        self.song_popularity_per_genre.start()
        
        self.genres = AppleEPFGenreRelationalDB()
        self.genres.start()
        
        self.artist_to_albums.join()
        #self.artist_to_songs.join()
        self.album_popularity_per_genre.join()
        self.song_popularity_per_genre.join()
        self.genres.join()
    
    def _filter(self, row):
        artist_id = row.artist_id
        
        # query for all albums by this artist
        albums = self.artist_to_albums.get_rows('artist_id', artist_id)
        
        out_albums = []
        popularity = None
        
        for album in albums:
            album_id = album['collection_id']
            pop = self.album_popularity_per_genre.get_row('album_id', album_id)
            
            out_album = {
                'album_id' : album_id, 
            }
            
            if pop is not None:
                rank = pop['album_rank']
                
                if popularity is None or rank < popularity:
                    popularity = rank
                
                out_album['rank']     = rank
                out_album['genre_id'] = pop['genre_id']
            
            out_albums.append(out_album)
        
        return {
            'albums' : out_albums, 
            'popularity' : popularity, 
        }
        
        # query for all songs by this artist
        songs = self.artist_to_songs.get_rows('artist_id', artist_id)
        
        out_songs = []
        
        for song in songs:
            song_id = song['song_id']
            pop = self.song_popularity_per_genre.get_row('song_id', song_id)
            
            out_song = {
                'song_id' : song_id, 
            }
            
            if pop is not None:
                rank = pop['song_rank']
                
                if popularity is None or rank < popularity:
                    popularity = rank
            
            out_songs.append(out_song)
        
        return {
            'albums' : out_albums, 
            'popularity' : popularity, 
        }

class AppleEPFSongDump(AAppleEPFDump):
    
    _map = {
        'name'                      : 'title', 
        'export_date'               : 'export_date', 
        'song_id'                   : 'aid', 
        'title_version'             : 'title_version', 
        'search_terms'              : 'search_terms', 
        'parental_advisory_id'      : 'parental_advisory_id', 
        'artist_display_name'       : 'artist_display_name', 
        'collection_display_name'   : 'collection_display_name', 
        'view_url'                  : 'view_url', 
        'original_release_date'     : 'original_release_date', 
        'itunes_release_date'       : 'itunes_release_date', 
        'track_length'              : 'track_length', 
        'copyright'                 : 'copyright', 
        'p_line'                    : 'p_line', 
        'preview_url'               : 'preview_url', 
        'preview_length'            : 'preview_length', 
    }
    
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Songs", self._map, [ "song" ], "song")

class AppleEPFAlbumDump(AAppleEPFDump):
    
    _map = {
        'name'                      : 'title', 
        'export_date'               : 'export_date', 
        'collection_id'             : 'aid', 
        'title_version'             : 'title_version', 
        'search_terms'              : 'search_terms', 
        'parental_advisory_id'      : 'parental_advisory_id', 
        'artist_display_name'       : 'artist_display_name', 
        'view_url'                  : 'view_url', 
        'artwork_url'               : 'artwork_url', 
        'original_release_date'     : 'original_release_date', 
        'itunes_release_date'       : 'itunes_release_date', 
        'label_studio'              : 'label_studio', 
        'content_provider_name'     : 'content_provider_name', 
        'copyright'                 : 'copyright', 
        'p_line'                    : 'p_line', 
        'media_type_id'             : 'media_type_id', 
        'is_compilation'            : 'is_compilation', 
        'collection_type_id'        : None, 
    }
    
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Albums", self._map, [ "album" ], "collection")
        
        self.album_prices = AppleEPFAlbumPriceRelationalDB()
        self.album_prices.start()
        
        self.album_prices.join()
    
    def _filter(self, row):
        collection_id = row.collection_id
        
        # only retain albums which are available for purchase in the US storefront
        price_info = self.album_prices.get_row('collection_id', collection_id)
        
        if price_info is None:
            return False
        
        return {
            'a_retail_price' : price_info['retail_price'], 
            'a_hq_price' : price_info['hq_price'], 
            'a_currency_code' : price_info['currency_code'], 
            'a_availability_date' : price_info['availability_date'], 
        }

class AppleEPFVideoDump(AAppleEPFDump):
    
    _map = {
        'name'                      : 'title', 
        'export_date'               : 'export_date', 
        'video_id'                  : 'aid', 
        'title_version'             : 'title_version', 
        'search_terms'              : 'search_terms', 
        'parental_advisory_id'      : 'parental_advisory_id', 
        'artist_display_name'       : 'artist_display_name', 
        'collection_display_name'   : 'collection_display_name', 
        'view_url'                  : 'view_url', 
        'artwork_url'               : 'artwork_url', 
        'original_release_date'     : 'original_release_date', 
        'itunes_release_date'       : 'itunes_release_date', 
        'studio_name'               : 'studio_name', 
        'network_name'              : 'network_name', 
        'content_provider_name'     : 'content_provider_name', 
        'track_length'              : 'track_length', 
        'copyright'                 : 'copyright', 
        'p_line'                    : 'p_line', 
        'short_description'         : 'short_description', 
        'episode_production_number' : 'episode_production_number', 
        'media_type_id'             : None, 
    }
    
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Videos", self._map, [ "movie" ], "video")
        
        self.video_prices = AppleEPFVideoPriceRelationalDB()
        self.video_prices.start()
        
        self.video_prices.join()
    
    def _filter(self, row):
        video_id = row.video_id
        
        # only retain videos which are available for purchase in the US storefront
        price_info = self.video_prices.get_row('video_id', video_id)
        
        if price_info is None:
            return False
        
        return {
            'v_retail_price' : price_info['retail_price'], 
            'v_currency_code' : price_info['currency_code'], 
            'v_availability_date' : price_info['availability_date'], 
            'v_sd_price' : price_info['sd_price'], 
            'v_hq_price' : price_info['hq_price'], 
            'v_lc_rental_price' : price_info['lc_rental_price'], 
            'v_sd_rental_price' : price_info['sd_rental_price'], 
            'v_hd_rental_price' : price_info['hd_rental_price'], 
        }

from crawler import EntitySources

#EntitySources.registerSource('apple', AppleEPFDumps)
EntitySources.registerSource('apple_artists', AppleEPFArtistDump)
EntitySources.registerSource('apple_songs',   AppleEPFSongDump)
EntitySources.registerSource('apple_albums',  AppleEPFAlbumDump)
EntitySources.registerSource('apple_videos',  AppleEPFVideoDump)

