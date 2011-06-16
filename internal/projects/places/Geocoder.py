#!/usr/bin/python

import json, re, sys, urllib, Utils

from optparse import OptionParser
from googlemaps import *

class AGeocoder(object):
    """
        Abstract geocoder which converts addresses to latitude / longitude.
    """
    
    def __init__(self, name):
        self._isValid = True
        self._name = name
    
    def addressToLatLng(self, address):
        pass

    def isValid(self):
        return _isValid
    
    def getName(self):
        return self._name
    
    def getEncodedLatLng(self, latLng):
        return str(latLng[0]) + ',' + str(latLng[1])

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
        
        self._decoderIndex = 0
        self._decoders = [ 
            GoogleGeocoderService(), 
            YahooGeocoderService(), 
            USGeocoderService()
        ]
    
    def addressToLatLng(self, address):
        index  = self._decoderIndex
        latLng = None
        while True:
            decoder = self._getDecoder(index)
            if decoder is None:
                return None
            
            latLng = decoder.addressToLatLng(address)
            if latLng is not None:
                return latLng
            else:
                if not decoder.isValid:
                    self._decoderIndex += 1
                    if self._decoderIndex >= len(self._decoders):
                        _isValid = False
                        return None
                else:
                    index += 1;
    
    def _getDecoder(self, index):
        if index is None:
            index = self._decoderIndex
        
        if index < len(self._decoders):
            return self._decoders[index];
        
        return None;

class GoogleGeocoderService(AGeocoder):
    """
        Uses the Google Geocoding API to convert between addresses and latitude
        longitude for a given location.
        <a href="http://code.google.com/apis/maps/documentation/geocoding/">Google Geocoding API</a>
    """
    API_KEY = 'AIzaSyAxgU3LPU-m5PI7Jh7YTYYKAz6lV6bz2ok'
    
    def __init__(self):
        AGeocoder.__init__(self, "Google")
        self.googleMaps = GoogleMaps(self.API_KEY)
    
    def addressToLatLng(self, address):
        (lat, lng) = (None, None)
        
        try:
            (lat, lng) = self.googleMaps.address_to_latlng(address)
        except (GoogleMapsError):
            _isValid = False
            pass
        
        return (lat, lng)

class YahooGeocoderService(AGeocoder):
    """
        Uses the Yahoo Geocoding API (named PlaceFinder) to convert between 
        addresses and latitude longitude for a given location.
        <a href="http://developer.yahoo.com/geo/placefinder/guide/">Yahoo PlaceFinder</a>
    """
    
    API_KEY  = 'fa5cc08cf806ef67ab0dba71e7934da26fd9cdf7'
    BASE_URL = 'http://where.yahooapis.com/geocode'
    
    def __init__(self):
        AGeocoder.__init__(self, "Yahoo")
    
    def addressToLatLng(self, address):
        (lat, lng) = (None, None)
        
        params = {
            'location'  : address, 
            'flags'     : 'J', # indicates json output format (defaults to xml)
            'appid'     : self.API_KEY
        }
        
        url = self.BASE_URL + '?' + urllib.urlencode(params)
        
        try:
            # GET the data and parse the response as json
            response = json.loads(Utils.getFile(url))
            
            # extract the results from the json
            if response['Error'] != 0:
                Utils.log('[YahooGeocoderService] error converting "' + url + '"\n' + 
                          'ErrorCode: ' + response['Error'] + '\n' + 
                          'ErrorMsg:  ' + response['ErrorMessage'] + '\n')
                return None
            
            results = response['ResultSet']['Results']
            primary = results[0]
            
            # extract the lat / lng from the primary result
            (lat, lng) = (float(primary['latitude']), float(primary['longitude']))
        except:
            _isValid = False
            pass
        
        return (lat, lng)

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
        (lat, lng) = (None, None)
        
        params = {
            'address' : address, 
        }
        
        url = self.BASE_URL + '?' + urllib.urlencode(params)
        
        try:
            # GET the data and parse the HTML response with BeautifulSoup
            soup = Utils.getSoup(url)
            row = soup.find("table").findAll("tr")[1]
            
            # extract the latitude
            latStr = row.find("td").renderContents()
            lat = float(re.search("([0-9.]+)", latStr).group(0))
            
            # extract the longitude
            lngStr = row.findAll("td")[1].renderContents()
            lng = float(re.search("([0-9.]+)", lngStr).group(0))
        except:
            Utils.log('[USGeocoderService] error converting "' + url + '"\n')
            pass
        
        return (lat, lng)

def parseCommandLine():
    usage = "Usage: %prog [options] address+"
    parser = OptionParser(usage)
    
    parser.add_option("-g", "--google", action="store_true", dest="google", 
        default=False, help="Use Google Geocoding service")
    parser.add_option("-y", "--yahoo", action="store_true", dest="yahoo", 
        default=False, help="Use Yahoo Geocoding service")
    parser.add_option("-u", "--us", action="store_true", dest="us", 
        default=False, help="Use US Geocoding service")
    parser.add_option("-a", "--all", action="store_true", dest="all", 
        default=False, help="Use all Geocoding services")
    
    parser.set_defaults(google=False)
    parser.set_defaults(yahoo=False)
    parser.set_defaults(us=False)
    parser.set_defaults(all=False)
    
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.print_help()
        return None
    
    if options.all:
        options.google = True
        options.yahoo = True
        options.us = True
    
    options.geocoders = []
    
    if options.google or options.yahoo or options.us:
        if options.google:
            options.geocoders.append(GoogleGeocoderService())
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
          -h, --help    show this help message and exit
          -g, --google  Use Google Geocoding service
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

