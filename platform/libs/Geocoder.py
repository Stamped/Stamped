#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import json, re, urllib

from optparse       import OptionParser
from libs.AKeyBasedAPI   import AKeyBasedAPI
from errors         import *
from libs.CachedFunction import cachedFn

class AGeocoder(AKeyBasedAPI):
    """
        Abstract geocoder which converts addresses to latitude / longitude.
    """
    
    DEFAULT_TOLERANCE = 0.9
    
    def __init__(self, name, apiKeys=None):
        AKeyBasedAPI.__init__(self, apiKeys)
        self._name = name
        self._isValid = True
    
    def addressToLatLng(self, address):
        raise NotImplementedError

    def getName(self):
        return self._name
    
    def getEncodedLatLng(self, latLng):
        return str(latLng[0]) + ',' + str(latLng[1])
    
    def getValidatedLatLng(self, latLng):
        # validate that the given latLng object is in the correct format
        if latLng is not None and len(latLng) == 2 and latLng[0] is not None and latLng[1] is not None:
            return latLng
        else:
            return None
    
    @property
    def isValid(self):
        return self._isValid
    
    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self._name)

class Geocoder(AGeocoder):
    """
        Converts addresses to latitude / longitude, utilizing a set of underlying 
        web services.
        Usage:
            geocoder = Geocoder();
            (lat, lng) = geocoder.addressToLatLng('701 First Ave, Sunnyvale CA')
    """
    
    def __init__(self):
        AGeocoder.__init__(self, "Geocoder")
        
        self._decoders = [
            GoogleGeocoderService(), 
            BingGeocoderService(), 
            YahooGeocoderService(), 
            USGeocoderService()
        ]
    
    @property
    def isValid(self):
        isValid = False
        
        for decoder in self._decoders:
            isValid |= decoder.isValid
        
        return True

    @cachedFn()
    def addressToLatLng(self, address):
        address = utils.removeNonAscii(address)
        latLng = None
        index = 0
        
        while True:
            loop = True
            while loop:
                if index < len(self._decoders):
                    decoder = self._decoders[index]
                    loop = not self._decoders[index].isValid
                    if loop:
                        index += 1
                else:
                    utils.log('[Geocoder] Error: all geocoders failed to convert address "%s"' % address)
                    return None
            
            #utils.log('[Geocoder] Service \'%s\' : %s' % (decoder.getName(), address))
            
            latLng = decoder.addressToLatLng(address)
            if latLng is not None:
                return latLng
            else:
                index += 1

class GoogleGeocoderService(AGeocoder):
    """
        Uses the Google Geocoding API to convert between addresses and latitude
        longitude for a given location.
        <a href="http://code.google.com/apis/maps/documentation/geocoding/">Google Geocoding API</a>
    """
    
    BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
    
    def __init__(self):
        AGeocoder.__init__(self, "Google")
    
    def addressToLatLng(self, address):
        if not self.isValid:
            return False
        
        params = {
            'address' : address, 
            'sensor'  : 'false', 
        }
        url = ""
        
        try:
            # construct the url
            url = self.BASE_URL + '?' + urllib.urlencode(params)
            
            # GET the data and parse the response as json
            response = json.loads(utils.getFile(url))
            
            # extract the primary result from the json
            if response['status'] != 'OK':
                if response['status'] == 'OVER_QUERY_LIMIT':
                    utils.log("GoogleGeocoderService over quota usage")
                    self._isValid = False
                    return None
                else:
                    utils.log('[GoogleGeocoderService] error converting "' + url + '"\n' + 
                             'ErrorStatus: ' + response['status'] + '\n')
                    return None
            
            result   = response['results'][0]
            location = result['geometry']['location']
            
            # extract the lat / lng from the primary result
            latLng = (float(location['lat']), float(location['lng']))
            
            return self.getValidatedLatLng(latLng)
        except:
            utils.log('[GoogleGeocoderService] error converting "' + url + '"')
        
        return None

class BingGeocoderService(AGeocoder):
    """
        Uses the Bing Geocoding API to convert between addresses and latitude 
        longitude for a given location.
        <a href="http://msdn.microsoft.com/en-us/library/ff701711.aspx">Bing Location Services API</a>
    """
    
    BASE_URL = 'http://dev.virtualearth.net/REST/v1/Locations'
    
    API_KEYS = [
        # http://www.bingmapsportal.com
        # fisch0920
        'Av4b8Qag0v37rTVVXvnW5lLWASAu23UoZaIlRvlCGmAo3uVQpoZ_PYV4pOSAP2X-', 
        'Aj9gK4omLJOx0k8DaB1IAIEbxyDWSCqX3RcyHNwSi9JApwyH_IDPY-vX25ZcfhT3', 
        'AvAbfTexxi0yqXc5_jGXEWQo4lOFYEg8BGlbVQaYrQ8eD3n3A4BLK5hDDEPJmV4K', 
        'AjRt_gjwhN8do7Qfpdd4seGmIphm-yjnT6sCSaw3kq7WdwHjnh-Pi1J4RmGVTxFU', 
        'ApaKod0M073qzBAEsyePgwrz4m6CVsmpWEOwPJiWR45qm9U8b0ypPp1IyzK7IMzF', 
        # fisch09202
        'AhnmEmOJgjBANPQI5iaV9rcySH8YizDQAwVbDiuO5WxUFcbxxwNSbd5wYVkL21bz', 
        'AkaGlNCaf-hac53qrbaqFLw-FEjFUSUfX0GjcBdwyI0xbCv6dltyXvo91Y6TskmY', 
        'AmSDMaSSykwPgh9uD-wuK5sqpnjm9FidB_7gdo3mBOfVLeRHSfMmST1ZP81rPFdZ', 
        'Ak2jWnk1TM9zUBEEnm4WdyaFUj4JHCKvmViqjQHBnnwlm7bo0zSF4jlN19UBeFuc', 
        'AqS61Bh-P1Xy5n0BMSLpdWd2Warsy3ilFcrofCuWVsLllOKHDsYPLCD56IMnlYe3', 
    ]
    
    def __init__(self):
        AGeocoder.__init__(self, "Bing", self.API_KEYS)
    
    def addressToLatLng(self, address):
        if not self.isValid:
            return False
        
        params = {
            'query'  : address, 
            'output' : 'json', 
        }
        
        (offset, count) = self._initAPIKeyIndices()
        url = ""
        
        while True:
            try:
                # try a different API key for each attempt
                apiIndex = self._getAPIIndex(offset, count)
                if apiIndex is None:
                    self._isValid = False
                    return None
                
                apiKey = self._apiKeys[apiIndex]
                if apiKey is None:
                    count += 1
                    continue
                
                # construct the url
                params['key'] = apiKey
                url = self.BASE_URL + '?' + urllib.urlencode(params)
                
                # GET the data and parse the response as json
                response = json.loads(utils.getFile(url))
                
                status = response['statusCode']
                if status != 200:
                    if status != 400:
                        self._apiKeys[apiIndex] = None
                        continue
                    else:
                        return None
                
                # extract the primary result from the json
                resource = (((response['resourceSets'])[0])['resources'])[0]
                result   = (resource['point'])['coordinates']
                
                # extract the lat / lng from the primary result
                latLng = (float(result[0]), float(result[1]))
                
                return self.getValidatedLatLng(latLng)
            except:
                #utils.log('[BingGeocoderService] error converting "' + url + '"')
                
                # retry with another api key
                count += 1
        
        return None

class YahooGeocoderService(AGeocoder):
    """
        Uses the Yahoo Geocoding API (named PlaceFinder) to convert between 
        addresses and latitude longitude for a given location.
        <a href="http://developer.yahoo.com/geo/placefinder/guide/">Yahoo PlaceFinder</a>
    """
    
    BASE_URL = 'http://where.yahooapis.com/geocode'
    
    API_KEYS = [
        'fa5cc08cf806ef67ab0dba71e7934da26fd9cdf7', 
        'b3cdf45cd8a49b87be7ad3536d0c692bb5190fd9', 
        '02dded0de677c823c1a55d595b34dc060e6ec134', 
        'fa22a2913484737761258707411ae062c74f01c1', 
        '299e8883e4b3495df615b7fa2c416bc4cddf22b2', 
        'f174496b5adb0a5f642c068ff8afdddf5f24f889', 
        '6d2b7fd860e2675c039eca27b422cf048c583105', 
        'b91274e18118bf79ddbd63228e8ef4b661fa0741', 
        '90dccb1eedfb4406ceff382071aae08f2ba09daf', 
    ]
    
    def __init__(self):
        AGeocoder.__init__(self, "Yahoo", self.API_KEYS)
    
    def addressToLatLng(self, address):
        if not self.isValid:
            return None
        
        params = {
            'location' : address, 
            'flags'    : 'J', # indicates json output format (defaults to xml)
        }
        
        (offset, count) = self._initAPIKeyIndices()
        url = ""
        
        while True:
            try:
                # try a different API key for each attempt
                apiIndex = self._getAPIIndex(offset, count)
                if apiIndex is None:
                    #self._isValid = False
                    return None
                
                apiKey = self._apiKeys[apiIndex]
                if apiKey is None:
                    count += 1
                    continue
 
                # construct the url
                params['appid'] = apiKey
                url = self.BASE_URL + '?' + urllib.urlencode(params)
                
                # GET the data and parse the response as json
                response  = json.loads(utils.getFile(url))
                
                resultSet = response['ResultSet']
                
                # extract the results from the json
                if resultSet['Error'] != 0:
                    utils.log('[YahooGeocoderService] error converting "' + url + '"\n' + 
                             'ErrorCode: ' + str(resultSet['Error']) + '\n' + 
                             'ErrorMsg:  ' + resultSet['ErrorMessage'] + '\n')
                    return None
                
                if not 'Results' in resultSet or 0 == len(resultSet['Results']):
                    return None
                
                primary = resultSet['Results'][0]
                
                # extract the lat / lng from the primary result
                latLng = (float(primary['latitude']), float(primary['longitude']))
                
                return self.getValidatedLatLng(latLng)
            except:
                #utils.log('[YahooGeocoderService] error converting "' + url + '"')
                
                # retry with another api key
                count += 1
        
        return None

class USGeocoderService(AGeocoder):
    """
        Uses the Geocoder.us site to convert between addresses and latitude 
        longitude for a given location.
        <a href="http://geocoder.us/">Geocoder.us</a>
    """
    
    BASE_URL = 'http://geocoder.us/demo.cgi'
    
    def __init__(self):
        AGeocoder.__init__(self, "US")
    
    def addressToLatLng(self, address):
        params = {
            'address' : address, 
        }
        
        url = self.BASE_URL + '?' + urllib.urlencode(params)
        
        try:
            # GET the data and parse the HTML response with BeautifulSoup
            soup = utils.getSoup(url)
            rows = soup.find("table").findAll("tr")
            
            # extract the latitude
            latRow = rows[1]
            latStr = latRow.findAll("td")[1].renderContents()
            lat    = float(re.search("([0-9.-]+)", latStr).group(0))
            
            # extract the longitude
            lngRow = rows[2]
            lngStr = lngRow.findAll("td")[1].renderContents()
            lng    = float(re.search("([0-9.-]+)", lngStr).group(0))
            
            return self.getValidatedLatLng((lat, lng))
        except:
            #utils.log('[USGeocoderService] error converting "' + url + '"\n')
            pass
        
        return None

def parseCommandLine():
    usage   = "Usage: %prog [options] address+"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-g", "--google", action="store_true", dest="google", 
        default=False, help="Use Google Geocoding service")
    parser.add_option("-b", "--bing", action="store_true", dest="bing", 
        default=False, help="Use Bing Geocoding service")
    parser.add_option("-y", "--yahoo", action="store_true", dest="yahoo", 
        default=False, help="Use Yahoo Geocoding service")
    parser.add_option("-u", "--us", action="store_true", dest="us", 
        default=False, help="Use US Geocoding service")
    parser.add_option("-a", "--all", action="store_true", dest="all", 
        default=False, help="Use all Geocoding services")
    
    parser.set_defaults(google=False)
    parser.set_defaults(bing=False)
    parser.set_defaults(yahoo=False)
    parser.set_defaults(us=False)
    parser.set_defaults(all=False)
    
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.print_help()
        return None
    
    if options.all:
        options.google  = True
        options.bing    = True
        options.yahoo   = True
        options.us      = True
    
    options.geocoders = []
    
    if options.google or options.bing or options.yahoo or options.us:
        if options.google:
            options.geocoders.append(GoogleGeocoderService())
        if options.bing:
            options.geocoders.append(BingGeocoderService())
        if options.yahoo:
            options.geocoders.append(YahooGeocoderService())
        if options.us:
            options.geocoders.append(USGeocoderService())
    else:
        options.geocoders.append(Geocoder())
    
    return (options, args)

def main():
    """
        Usage: Geocoder.py [options] address+

        Options:
          --version     show program's version number and exit
          -h, --help    show this help message and exit
          -g, --google  Use Google Geocoding service
          -b, --bing    Use Bing Geocoding service
          -y, --yahoo   Use Yahoo Geocoding service
          -u, --us      Use US Geocoding service
          -a, --all     Use all Geocoding services
    """
    
    result = parseCommandLine()
    if result is None:
        return
    
    (options, args) = result
    
    numAddresses = len(args)
    numConverted = 0
    
    # attempt to convert each address in the argument list
    for address in args:
        isConverted = False
        
        for geocoder in options.geocoders:
            latLng = geocoder.addressToLatLng(address)
            
            if latLng is None or latLng[0] is None or latLng[1] is None:
                print "Service %s failed to convert address '%s'" % (geocoder.getName(), address)
            else:
                isConverted = True
                result = {
                    'Service' : geocoder.getName(), 
                    'Address' : address, 
                    'Latitude' : latLng[0], 
                    'Longitude' : latLng[1], 
                    'LatLng' : geocoder.getEncodedLatLng(latLng)
                }
                
                print str(result)
        
        if isConverted:
            numConverted += 1
    
    print "Converted %d out of %d addresses (%g%%)" % \
        (numConverted, numAddresses, (100.0 * numConverted) / numAddresses)

if __name__ == '__main__':
    main()

