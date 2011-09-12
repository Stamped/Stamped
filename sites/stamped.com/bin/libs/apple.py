#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals
import copy, json, urllib, utils

from Schemas import Entity
from utils   import AttributeDict

__all__ = [ "AppleAPI", "AppleAPIError" ]

class AppleAPIError(Exception):
    pass

class AppleAPICall(object):
    _wrapper_type_to_subcategory = {
        'artist'        : 'artist', 
        'collection'    : 'album', 
        'track'         : 'song', 
    }
    
    _kind_to_subcategory = {
        'song'          : 'song', 
        'album'         : 'album', 
        'artist'        : 'artist', 
        'feature-movie' : 'movie', 
    }
    
    def __init__(self, **kwargs):
        self.transform = kwargs.pop('transform', False)
        
        self.method = kwargs.pop('method', None)
        self.params = kwargs
    
    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except:
            return AppleAPICall(method=k, transform=self.transform)
    
    def __call__(self, **kwargs):
        assert self.method is not None
        transform = kwargs.pop('transform', self.transform)
        params    = copy.copy(self.params)
        
        for kwarg in kwargs:
            params[kwarg] = kwargs[kwarg]
        
        if self.method == 'search':
            if 'term' not in params:
                raise AppleAPIError("required parameter 'term' missing to api method %s" % self.method)
        
        url    = self._get_url(params)
        result = json.loads(utils.getFile(url))
        
        if transform:
            return self.transform_result(result)
        else:
            return result
    
    def _get_url(self, params):
        return "http://itunes.apple.com/%s?%s" % (self.method, urllib.urlencode(params))
    
    def transform_result(self, result):
        if result is None or not 'results' in result:
            return result
        
        results = result['results']
        output  = []
        
        for result in results:
            try:
                wrapperType = result['wrapperType']
                
                try:
                    subcategory = self._wrapper_type_to_subcategory[wrapperType]
                except KeyError:
                    continue
                
                if 'kind' in result:
                    try:
                        subcategory = self._kind_to_subcategory[result['kind']]
                    except KeyError:
                        continue
                
                entity = Entity()
                entity.subcategory = subcategory
                
                if wrapperType == 'track':
                    entity.title    = result['trackName']
                    entity.aid      = result['trackId']
                    entity.view_url = result['trackViewUrl']
                    
                    if 'trackTimeMillis' in result:
                        entity.track_length = result['trackTimeMillis'] / 1000.0
                    
                    if 'trackPrice' in result:
                        price = result['trackPrice']
                        
                        entity.currency_code   = result['currency']
                        entity.amount          = int(price * 100)
                        entity.formatted_price = "$%.2f" % price
                    
                    if subcategory == 'song':
                        album_name = result['collectionName']
                        
                        if album_name is not None:
                            entity.album_name  = album_name
                        
                        album_id   = result['collectionId']
                        if album_id is not None:
                            entity.song_album_id = album_id
                elif subcategory == 'album':
                    entity.title    = result['collectionName']
                    entity.aid      = result['collectionId']
                    entity.view_url = result['collectionViewUrl']
                elif subcategory == 'artist':
                    entity.title    = result['artistName']
                    entity.aid      = result['artistId']
                    
                    try:
                        entity.view_url = result['artistViewUrl']
                    except:
                        entity.view_url = result['artistLinkUrl']
                else:
                    # should never reach this point, but not raising an error just 
                    # in case i'm wrong for robustness purposes if we receive 
                    # an unexpected result
                    continue
                
                if subcategory != 'artist':
                    entity.artist_display_name = result['artistName']
                
                entity_map = {
                    'previewUrl'            : 'preview_url', 
                    'artworkUrl100'         : 'large', 
                    'artworkUrl60'          : 'small', 
                    'artworkUrl30'          : 'tiny', 
                    'longDescription'       : 'desc', 
                    'shortDescription'      : 'desc', 
                    'primaryGenreName'      : 'genre', 
                    'releaseDate'           : 'original_release_date', 
                    'contentAdvisoryRating' : 'mpaa_rating', 
                    'copyright'             : 'copyright', 
                    'trackCount'            : 'track_count', 
                }
                
                for key in entity_map:
                    if key in result:
                        value = result[key]
                        
                        if value is not None:
                            entity[entity_map[key]] = result[key]
                
                if wrapperType == 'track':
                    try:
                        entity.track_length = result['trackTimeMillis'] / 1000.0
                    except KeyError:
                        pass
                
                output.append(AttributeDict(result=result, entity=entity))
            except:
                from pprint import pprint
                pprint(result)
                raise
        
        return output

class AppleAPI(AppleAPICall):
    
    def __init__(self, **kwargs):
        AppleAPICall.__init__(self, **kwargs)
    
    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except:
            valid_calls = set([ 'search', 'lookup' ])
            
            if k in valid_calls:
                return AppleAPICall.__getattr__(self, k)
            else:
                raise AppleAPIError("undefined api method '%s'" % k)

