#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import json, random, re, sys, urllib, Utils

from optparse import OptionParser
from Google import Google

class AGeocoder(object):
    """
        Abstract geocoder which converts addresses to latitude / longitude.
    """
    
    DEFAULT_TOLERANCE = 0.9
    
    def __init__(self, name, apiKeys, log=Utils.log):
        self._name = name
        self._apiKeys = apiKeys
        self.log = log
    
    def addressToLatLng(self, address):
        pass

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
    
    def _getAPIKey(self, offset, count):
        # return a fresh API key for every call in which offset remains a 
        # random integer and count cycles from 0 to the number of API keys
        # available. once count overflows the API keys, return None.
        if self._apiKeys is None or count >= len(self._apiKeys):
            return None
        else:
            index = (offset + offset) % len(self._apiKeys)
            return self._apiKeys[index]
    
    def _initAPIKeyIndices(self):
        offset = random.randint(0, len(self._apiKeys) - 1)
        count  = 0
        
        return (offset, count)

class Geocoder(AGeocoder):
    """
        Converts addresses to latitude / longitude, utilizing a set of underlying 
        web services.
        Usage:
            geocoder = Geocoder();
            (lat, lng) = geocoder.addressToLatLng('701 First Ave, Sunnyvale CA')
    """
    
    def __init__(self, log=Utils.log):
        AGeocoder.__init__(self, "Geocoder", log)
        
        self.log = log
        self._decoders = [ 
            GoogleGeocoderService(), 
            BingGeocoderService(), 
            YahooGeocoderService(), 
            USGeocoderService()
        ]
    
    def addressToLatLng(self, address):
        latLng = None
        index  = 0
        
        while True:
            if index < len(self._decoders):
                decoder = self._decoders[index]
            else:
                return None
            
            self.log('[Geocoder] Service \'%s\' : %s' % (decoder.getName(), address))
            
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
    
    API_KEYS = [
        'AIzaSyAxgU3LPU-m5PI7Jh7YTYYKAz6lV6bz2ok',  # Travis
        'AIzaSyAEjlMEfxmlCBQeyw_82jjobQAFjYx-Las',  # Kevin
        'AIzaSyDTW6GnCmfP_mdxklSaArWrPoQo6cJQhOs',  # Bart
        'AIzaSyA90G9YbjX7q3kXOBdmi0JFB3mTCOl45c4',  # Ed
        'AIzaSyCZnt6jjlHxzRsyklNoYJKsv6kcPeQs-W8',  # Jake
    ]
    
    def __init__(self, log=Utils.log):
        AGeocoder.__init__(self, "Google", Google.API_KEYS, log)
    
    def addressToLatLng(self, address):
        params = {
            'address' : address, 
            'sensor'  : 'false', 
        }
        
        (offset, count) = self._initAPIKeyIndices()
        
        while True:
            try:
                # try a different API key for each attempt
                apiKey = self._getAPIKey(offset, count)
                if apiKey is None:
                    return None
                
                # construct the url
                params['key'] = apiKey
                url = self.BASE_URL + '?' + urllib.urlencode(params)
                
                # GET the data and parse the response as json
                response = json.loads(Utils.getFile(url))
                
                # extract the primary result from the json
                if response['status'] != 'OK':
                    self.log('[GoogleGeocoderService] error converting "' + url + '"\n' + 
                             'ErrorStatus: ' + response['status'] + '\n')
                    
                    if response['status' == 'OVER_QUERY_LIMIT']:
                        # over the quota for this api key; retry with another key
                        count += 1
                        continue
                    
                    return None
                
                result   = response['results'][0]
                location = result['geometry']['location']
                
                # extract the lat / lng from the primary result
                latLng = (float(location['lat']), float(location['lng']))
                
                return self.getValidatedLatLng(latLng)
            except:
                self.log('[GoogleGeocoderService] error converting "' + url + '"')
                Utils.printException()
                break
        
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
        'Av4b8Qag0v37rTVVXvnW5lLWASAu23UoZaIlRvlCGmAo3uVQpoZ_PYV4pOSAP2X-', 
        'Aj9gK4omLJOx0k8DaB1IAIEbxyDWSCqX3RcyHNwSi9JApwyH_IDPY-vX25ZcfhT3', 
        'AvAbfTexxi0yqXc5_jGXEWQo4lOFYEg8BGlbVQaYrQ8eD3n3A4BLK5hDDEPJmV4K', 
        'AjRt_gjwhN8do7Qfpdd4seGmIphm-yjnT6sCSaw3kq7WdwHjnh-Pi1J4RmGVTxFU', 
        'ApaKod0M073qzBAEsyePgwrz4m6CVsmpWEOwPJiWR45qm9U8b0ypPp1IyzK7IMzF', 
    ]
    
    def __init__(self, log=Utils.log):
        AGeocoder.__init__(self, "Bing", self.API_KEYS, log)
    
    def addressToLatLng(self, address):
        params = {
            'query'  : address, 
            'output' : 'json', 
        }
        
        (offset, count) = self._initAPIKeyIndices()
        
        while True:
            try:
                # try a different API key for each attempt
                apiKey = self._getAPIKey(offset, count)
                if apiKey is None:
                    return None
                
                # construct the url
                params['key'] = apiKey
                url = self.BASE_URL + '?' + urllib.urlencode(params)
                
                # GET the data and parse the response as json
                response = json.loads(Utils.getFile(url))
                
                # extract the primary result from the json
                resource = response['resourceSets'][0]['resources'][0]
                result   = resource['point']['coordinates']
                
                # extract the lat / lng from the primary result
                latLng = (float(result[0]), float(result[1]))
                
                return self.getValidatedLatLng(latLng)
            except:
                self.log('[BingGeocoderService] error converting "' + url + '"')
                Utils.printException()
                
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
    ]
    
    def __init__(self, log=Utils.log):
        AGeocoder.__init__(self, "Yahoo", self.API_KEYS, log)
    
    def addressToLatLng(self, address):
        params = {
            'location' : address, 
            'flags'    : 'J', # indicates json output format (defaults to xml)
        }
        
        (offset, count) = self._initAPIKeyIndices()
        
        while True:
            try:
                # try a different API key for each attempt
                apiKey = self._getAPIKey(offset, count)
                if apiKey is None:
                    return None
                
                # construct the url
                params['appid'] = apiKey
                url = self.BASE_URL + '?' + urllib.urlencode(params)
                
                # GET the data and parse the response as json
                response  = json.loads(Utils.getFile(url))
                resultSet = response['ResultSet']
                
                # extract the results from the json
                if resultSet['Error'] != 0:
                    self.log('[YahooGeocoderService] error converting "' + url + '"\n' + 
                             'ErrorCode: ' + resultSet['Error'] + '\n' + 
                             'ErrorMsg:  ' + resultSet['ErrorMessage'] + '\n')
                    return None
                
                primary = resultSet['Results'][0]
                
                # extract the lat / lng from the primary result
                latLng = (float(primary['latitude']), float(primary['longitude']))
                
                return self.getValidatedLatLng(latLng)
            except:
                self.log('[YahooGeocoderService] error converting "' + url + '"')
                Utils.printException()
                
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
    
    def __init__(self, log=Utils.log):
        AGeocoder.__init__(self, "US", log)
    
    def addressToLatLng(self, address):
        params = {
            'address' : address, 
        }
        
        url = self.BASE_URL + '?' + urllib.urlencode(params)
        
        try:
            # GET the data and parse the HTML response with BeautifulSoup
            soup = Utils.getSoup(url)
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
            self.log('[USGeocoderService] error converting "' + url + '"\n')
            Utils.printException()
        
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
        options.google = True
        options.bing = True
        options.yahoo = True
        options.us = True
    
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
        sys.exit(0)
    
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

