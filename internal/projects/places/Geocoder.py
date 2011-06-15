#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
from googlemaps import *

import json, re, urllib, urllib2, Utils

class AGeocoder(object):
    """
        Abstract geocoder which converts addresses to latitude / longitude.
    """
    _isValid = True
    
    def addressToLatLng(self, address):
        pass

    def isValid(self):
        return _isValid
    
class Geocoder(AGeocoder):
    """
        Converts addresses to latitude / longitude, utilizing a set of underlying 
        web services.
        Usage:
            geocoder = Geocoder();
            (lat, lng) = geocoder.addressToLatLng('701 First Ave, Sunnyvale CA')
    """
    
    def __init__(self):
        AGeocoder.__init__(self)
        
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
                    ++self._decoderIndex
                    if self._decoderIndex >= len(self._decoders):
                        _isValid = False
                        return None
                else:
                    ++index;
    
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
    """
    API_KEY = 'AIzaSyAxgU3LPU-m5PI7Jh7YTYYKAz6lV6bz2ok'
    
    def __init__(self):
        AGeocoder.__init__(self)
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
    """
    
    API_KEY  = 'fa5cc08cf806ef67ab0dba71e7934da26fd9cdf7'
    BASE_URL = 'http://where.yahooapis.com/geocode'
    
    def __init__(self):
        AGeocoder.__init__(self)
    
    def addressToLatLng(self, address):
        (lat, lng) = (None, None)
        
        params = {
            'location'  : address, 
            'flags'     : 'J', # indicates JSON output format (defaults to XML)
            'appid'     : self.API_KEY
        }
        
        url = self.BASE_URL + '?' + urllib.urlencode(params)
        
        try:
            # GET the data
            response = urllib2.urlopen(url)
            
            # convert the response to JSON
            jsonData = json.loads(response.read())
            
            # extract the results from the JSON
            if jsonData['Error'] != 0:
                Utils.log('[YahooGeocoderService] error converting "' + url + '"\n' + 
                          'ErrorCode: ' + jsonData['Error'] + '\n' + 
                          'ErrorMsg:  ' + jsonData['ErrorMessage'] + '\n')
                return None
            
            results = jsonData['ResultSet']['Results']
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
    """
    
    BASE_URL = 'http://geocoder.us/demo.cgi'
    
    def __init__(self):
        AGeocoder.__init__(self)
    
    def addressToLatLng(self, address):
        (lat, lng) = (None, None)
        
        params = {
            'address' : address, 
        }
        
        url = self.BASE_URL + '?' + urllib.urlencode(params)
        
        try:
            # GET the data
            response = urllib2.urlopen(url)
            
            # extract the response HTML with BeautifulSoup
            soup = BeautifulSoup(response.read())
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

"""
geocoder = Geocoder()
(lat, lng) = geocoder.addressToLatLng('701 First Ave, Sunnyvale, CA')
print (lat, lng)
"""

geocoder = USGeocoderService()
(lat, lng) = geocoder.addressToLatLng('600 Pennsylvania Ave, Washington, DC')
print (lat, lng)

