#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from api_old import Entity
import copy, json, urllib, utils

from api_old.Schemas    import *
from optparse   import OptionParser
from utils      import AttributeDict
from pprint     import pprint

__all__ = [ "AppleAPI", "AppleAPIError" ]

class AppleAPIError(Exception):
    pass

class AppleAPICall(object):
    _wrapper_type_to_subcategory = {
        'artist'        : 'artist', 
        'collection'    : 'album', 
        'track'         : 'song', 
        'software'      : 'app', 
    }
    
    _kind_to_subcategory = {
        'song'          : 'song', 
        'album'         : 'album', 
        'artist'        : 'artist', 
        'feature-movie' : 'movie', 
        'software'      : 'app', 
    }
    
    def __init__(self, **kwargs):
        self.transform = kwargs.pop('transform', False)
        self.verbose   = kwargs.pop('verbose',   False)
        
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
        verbose   = kwargs.pop('verbose',   self.verbose)
        params    = copy.copy(self.params)
        
        for kwarg in kwargs:
            params[kwarg] = kwargs[kwarg]
        
        if self.method == 'search':
            if 'term' not in params:
                raise AppleAPIError("required parameter 'term' missing to api method %s" % self.method)
        
        if 'term' in params:
            term = params['term']
            term = term.replace(' ', '+')
            params['term'] = term
        
        url    = self._get_url(params)
        if verbose:
            utils.log(url)
        
        result = utils.getFile(url)
        
        """
        f=open('out.apple.xml', 'w')
        f.write(result)
        f.close()
        """
        
        result = json.loads(result)
        
        if transform:
            return self.transform_result(result)
        else:
            return result
    
    def _get_url(self, params):
        return "http://itunes.apple.com/%s?%s" % (self.method, urllib.urlencode(params))
    
    def transform_result(self, result):
        if result is None or not 'results' in result:
            return []
        
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
                
                entity = utils.AttributeDict()
                entity.subcategory = subcategory
                
                if wrapperType == u'track':
                    entity.title    = result['trackName']
                    entity.aid      = result['trackId']
                    entity.view_url = result['trackViewUrl']
                    
                    if 'trackTimeMillis' in result:
                        length = result['trackTimeMillis']
                        if length is not None:
                            entity.track_length = length / 1000.0
                    
                    if 'trackPrice' in result:
                        price = result['trackPrice']
                        
                        if result['currency'] is not None:
                            entity.currency_code   = result['currency']
                        
                        if price is not None:
                            entity.amount          = int(price * 100)
                            entity.formatted_price = "$%.2f" % price
                    
                    if subcategory == 'song':
                        album_name = result['collectionName']
                        
                        if album_name is not None:
                            entity.album_name  = album_name
                        
                        album_id   = result['collectionId']
                        if album_id is not None:
                            entity.song_album_id = album_id
                elif subcategory == u'album':
                    entity.title    = result['collectionName']
                    entity.aid      = result['collectionId']
                    entity.view_url = result['collectionViewUrl']
                elif subcategory == u'artist':
                    entity.title    = result['artistName']
                    entity.aid      = result['artistId']
                    
                    try:
                        entity.view_url = result['artistViewUrl']
                    except:
                        try:
                            entity.view_url = result['artistLinkUrl']
                        except:
                            pass
                elif wrapperType == u'software':
                    entity.title    = result['trackName']
                    entity.aid      = result['trackId']
                    entity.view_url = result['trackViewUrl']
                else:
                    # should never reach this point, but not raising an error just 
                    # in case i'm wrong for robustness purposes if we receive 
                    # an unexpected result
                    print "warning: unexpected / invalid entity type returned from iTunes API"
                    pprint(result)
                    continue
                
                if subcategory != 'artist':
                    entity.artist_display_name = result['artistName']
                    
                    if 'artistId' in result and result['artistId'] is not None:
                        entity.artist_id       = result['artistId']
                
                entity_map = [
                    ('artistName',            'artist_display_name'), 
                    ('description',           'desc'), 
                    ('previewUrl',            'preview_url'), 
                    ('artworkUrl100',         'large'), 
                    ('artworkUrl60',          'small'), 
                    ('artworkUrl30',          'tiny'), 
                    ('artworkUrl512',         'large'), 
                    ('longDescription',       'desc'), 
                    ('shortDescription',      'desc'), 
                    ('primaryGenreName',      'genre'), 
                    ('releaseDate',           'original_release_date'), 
                    ('contentAdvisoryRating', 'mpaa_rating'), 
                    ('copyright',             'copyright'), 
                    ('trackCount',            'track_count'), 
                    ('sellerName',            'studio_name'), 
                    ('sellerUrl',             'studio_url'), 
                    ('screenshotUrls',        'screenshots'), 
                ]
                
                for t in entity_map:
                    key, key2 = t
                    
                    if key in result:
                        value = result[key]
                        
                        if value is not None:
                            entity[key2] = result[key]
                
                if wrapperType == 'track':
                    if 'trackTimeMillis' in result:
                        length = result['trackTimeMillis']
                        
                        if length is not None:
                            entity.track_length = length / 1000.0
                
                if u'genres' in result:
                    entity.genre = u', '.join(result[u'genres'])
                
                entity = Entity.upgradeEntityData(dict(entity))
                output.append(AttributeDict(result=result, entity=entity))
            except:
                utils.printException()
                pprint(result)
        
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

def parseCommandLine():
    usage   = "Usage,%prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-s", "--search", action="store_true", default=False, 
                      help="Perform search query")
    
    parser.add_option("-t", "--term", action="store", type="string", default=None, 
                      help="Term to search for")
    
    parser.add_option("-c", "--country", action="store", type="string", default='US', 
                      help="Two-letter country code for the store you want to search (defaults to US)")
    
    parser.add_option("-m", "--media", action="store", type="string", default=None, 
                      help="Media type you want to search for")
    
    parser.add_option("-e", "--entity", action="store", type="string", default=None, 
                      help="Type of results you want returned, relative to the specified media type. For example, movieArtist for a movie media type search.")
    
    parser.add_option("-a", "--attribute", action="store", type="string", default=None, 
                      help="The attribute you want to search for in the stores, relative to the specified media type. For example, if you wnat to search for an artist by name, specify --entity=allArtist --attribute=allArtistTerm")
    
    parser.add_option("-l", "--limit", action="store", type="int", default=None, 
                      help="Numer of search results to return (1 to 200)")
    
    parser.add_option("-L", "--language", action="store", type="string", default=None, 
                      help="Language to use when returning search results, using the five-character codename (default en_us)")
    
    parser.add_option("-E", "--explicit", action="store_true", default=None, 
                      help="Whether or not to include explicit content in search results (default is True)")
    
    parser.add_option("-v", "--verbose", action="store_true", default=False, 
                      help="Whether or not to transform results (not verbose) or return results from the API verbatim")
    
    (options, args) = parser.parse_args()
    
    return (options, args)

def extract_args(options):
    func_args = copy.copy(options.__dict__)
    delete = []
    
    for arg in func_args:
        if func_args[arg] is None or arg == 'search':
            delete.append(arg)
    
    for d in delete:
        del func_args[d]
    
    func_args['transform'] = not options.verbose
    return func_args

def main():
    options, args = parseCommandLine()
    
    api = AppleAPI()
    func_args = extract_args(options)
    
    if options.search:
        results = api.search(**func_args)
    else:
        if len(args) < 1:
            print "default lookup search takes an apple id"
            return
        
        func_args['id'] = args[0]
        results = api.lookup(**func_args)
    
    if options.verbose:
        pprint(results)
    else:
        for result in results:
            entity = result.entity
            pprint(entity.value)

if __name__ == '__main__':
    main()

