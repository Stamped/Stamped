#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import json, logs, string, sys, urllib, urllib2

from pprint         import pprint
from optparse       import OptionParser
from libs.Geocoder       import Geocoder
from crawler.AEntitySource  import AExternalServiceEntitySource
from Schemas        import Entity

class GoogleLocal(AExternalServiceEntitySource):
    NAME            = 'GoogleLocal'
    TYPES           = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalServiceEntitySource.__init__(self, self.NAME, self.TYPES)
        
        self._geocoder = Geocoder()
    
    def _run(self):
        pass
    
    def getLocalSearchResults(self, query, latLng=None, params=None, transform=True):
        response, url = self._getLocalSearchResponse(query, latLng, params)
        
        if response is None:
            return None
        
        if 200 != response["responseStatus"]:
            utils.log('[GoogleLocal] unexpected return status "' + \
                      response["responseStatus"] + ' (' + url + ')"')
            return None
        
        if not transform:
            return response
        
        output  = []
        try:
            results = response['responseData']['results']
            
            for result in results:
                output.append(self._parseEntity(result))
        except:
            utils.printException()
            raise
        
        return output
    
    def _parseEntity(self, result):
        entity = Entity()
        entity.subcategory = 'other'
        
        if 'titleNoFormatting' in result:
            entity.title = result['titleNoFormatting']
        
        if 'addressLines' in result:
            entity.address = string.joinfields(result['addressLines'], ', ')
            entity.subtitle = entity.address
        
        if 'lat' in result and 'lng' in result:
            entity.lat = float(result['lat'])
            entity.lng = float(result['lng'])
        
        if 'region' in result:
            entity.vicinity = result['region']
        
        if 'phoneNumbers' in result:
            phoneNumbers = result['phoneNumbers']
            
            if len(phoneNumbers) > 0:
                entity.phone = phoneNumbers[0]['number']
        
        entity.googleLocal = {}
        entity.titlel = entity.title.lower()
        
        return entity
    
    def _getLocalSearchResponse(self, query, latLng=None, optionalParams=None):
        params = {
            'v'   : '1.0', 
            'q'   : query, 
            'rsz' : 8, 
            'mrt' : 'localonly', 
            'key' : 'ABQIAAAAwHbLTrUsG9ibtIA3QrujsRRB6mhcr2m5Q6fm3mUuDbLfyI5H4xTNn-E18G_3Zu-sDQ3-BTh9hK2BeQ', 
        }
        
        if latLng is not None:
            params['sll'] = self._geocoder.getEncodedLatLng(latLng)
        
        self._handleParams(params, optionalParams)
        
        url = "http://ajax.googleapis.com/ajax/services/search/local?%s" % urllib.urlencode(params)
        utils.log('[GoogleLocal] ' + url)
        
        try:
            # GET the data and parse the response as json
            request = urllib2.Request(url, None, {'Referer' : 'http://www.stamped.com' })
            return json.loads(utils.getFile(url, request)), url
        except:
            utils.log('[GoogleLocal] unexpected error searching "' + url + '"')
            utils.printException()
            
            return None, url
        
        return None, url
    
    def _handleParams(self, params, optionalParams):
        if optionalParams is not None:
            for key in optionalParams:
                params[key] = optionalParams[key]
        
        for k in params:
            v = params[k]
            
            if isinstance(v, unicode):
                params[k] = v.encode("ascii", "xmlcharrefreplace")
    
    def getSubcategoryFromTypes(self, types):
        for t in types:
            if t != "establishment":
                try:
                    return self._googleTypeToSubcategoryMap[t]
                except KeyError:
                    return t
        
        return "other"

def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-b", "--latLng", action="store", type="string", 
        default=None, help="Parse the argument as an encoded latitude/longitude pair (e.g., '40.144729,-74.053527')")
    
    parser.add_option("-l", "--limit", action="store", type="int", dest="limit", 
        default=None, help="Limit the number of results shown to the top n results")
    
    parser.add_option("-v", "--verbose", action="store_true", default=False, 
                      help="Print out verbose results")
    
    #parser.add_option("-d", "--detail", action="store_true", dest="detail", 
    #    default=False, help="Included more detailed search result info.")
    
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.print_help()
        sys.exit(1)
    
    if options.latLng is not None:
        lat, lng = options.latLng.split(',')
        lat, lng = float(lat), float(lng)
        options.latLng = (lat, lng)
    
    return (options, args)

def main():
    options, args = parseCommandLine()
    
    local = GoogleLocal()
    params  = {}
    
    results = local.getLocalSearchResults(args[0], options.latLng, params, transform=not options.verbose)
    
    if not options.verbose:
        if options.limit:
            results = results[0:min(len(results), options.limit)]
        
        for entity in results:
            pprint(entity.value)
    else:
        print json.dumps(results, sort_keys=True, indent=2)

if __name__ == '__main__':
    main()

