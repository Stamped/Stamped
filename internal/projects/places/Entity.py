#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

"""
{
    'name' : str, 
    'desc' : str, 
    
    'locale' : locale, 
    'images' : [ image* ], 
    
    'dates' : {
        'created'  : str, 
        'modified' : str, 
    }, 
    
    'details' : {
        'place' :? {
            'address' : str
            'coordinates' : {
                'lat' : float, 
                'lng' : float
            }
            'types' : [ str* ], 
            'vicinity' :? str, 
        }, 
        
        'contact' :? {
            'phone' :? str, 
            'site'  :? str, 
            'email' :? str, 
        }, 
        
        'restaurant' :? {
            'diningStyle', 
            'cuisine', 
            'price', 
            'payment', 
            'dressCode', 
            'acceptsWalkins', 
            'offers', 
            'publicTransit', 
            'parking', 
            'parkingDetails', 
            'catering', 
            'privatePartyFacilities', 
            'privatePartyContact', 
            'entertainment', 
            'specialEvents', 
            'catering', 
        }, 
        'book' :? {
        }, 
        'movie' :? {
        }, 
    }, 
    
    'sources' : {
        'googlePlaces' :? {
            'id' : str, 
            'reference' : str, 
        }, 
        'openTable' :? {
            'id' : str, 
            'reserveURL' : str, 
            'countryID'  : str, 
            'metroName'  : str, 
            'neighborhoodName' : str, 
        }
    }
}
"""

def __isString(s):
    return s and isinstance(s, basestring)

class Entity(object):
    __details = set([ 'place', 'contact', 'restaurant', 'book', 'movie' ])
    __sources = set([ 'googlePlaces', 'openTable' ])
    
    def __init__(self, data=None):
        if data:
            self._data = data
        else:
            self._data = self._getSkeletonData()
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __delitem__(self, key):
        del self._data[key]
    
    def __len__(self):
        return len(self._data)
    
    def __str__(self):
        return str(self._data)
    
    def __contains__(self, item):
        return item in self._data
    
    def __getattr__(self, name):
        if name == '_data':
            return object.__getattr__(self, name)
        
        def _get(dic):
            if name in dic:
                return dic[name]
            else:
                for k, v in dic.iteritems():
                    if v is dict:
                        retVal = _get(v)
                        if retVal:
                            return retVal
            return None
        return _get(self._data)
    
    def __setattr__(self, name, value):
        #print "__setattr__ %s, %s" % (name, str(value))
        
        if name == '_data':
            object.__setattr__(self, name, value)
            return
        
        if name in self.__details and not name in self.details:
            self._data['details'][name] = value
        if name in self.__sources and not name in self.sources:
            self._data['sources'][name] = value
        
        self.add({ name : value })
    
    def add(self, data):
        def _union(data, dic):
            for k, v in data.iteritems():
                if k in dic:
                    if v is dict:
                        _union(v, dic[v])
                    else:
                        dic[k] = v
                else:
                    dic[k] = v
        
        _union(data, self._data)
    
    @property
    def isValid(self):
        valid = True
        
        valid &= 'name' in self and __isString(self.name)
        valid &= 'desc' in self and __isString(self.desc)
        valid &= 'locale' in self and __isString(self.locale)
        valid &= 'images' in self and self.images is list
        
        valid &= 'dates' in self and self.dates is dict
        valid &= 'created' in self.dates and __isString(self.dateCreated)
        valid &= 'modified' in self.dates and __isString(self.dateModified)
        
        valid &= 'sources' in self and self.sources is dict
        valid &= 'details' in self and self.details is dict
    
    def _getSkeletonData(self):
        return {
            'name' : None, 
            'desc' : None, 
            'locale' : None, 
            'images' : None, 
            'dates' : {
                'created'  : None, 
                'modified' : None
            }, 
            'details' : {
            }, 
            'sources' : {
            }
        }

