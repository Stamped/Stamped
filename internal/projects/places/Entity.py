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
    
    def add(self, data):
        self._union(data, self._data)
    
    def _union(self, data, dic):
        for k, v in data.iteritems():
            if k in dic:
                if v is dict:
                    self.union(v, dic[v])
                else:
                    dic[k] = v
            else:
                dic[k] = v
    
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
    
    @Property
    def name():
        def fget(self): return self['name']
        def fset(self, value): self['name'] = value
        return locals()
    
    @Property
    def desc():
        def fget(self): return self['desc']
        def fset(self, value): self['desc'] = value
        return locals()
    
    @Property
    def locale():
        def fget(self): return self['locale']
        def fset(self, value): self['locale'] = value
        return locals()
    
    @Property
    def images():
        def fget(self): return self['images']
        def fset(self, value): self['images'] = value
        return locals()
    
    @Property
    def dates():
        def fget(self): return self['dates']
        def fset(self, value): self['dates'] = value
        return locals()
    
    @property
    def dateCreated(self):
        return self['dates']['created']
    
    @property
    def dateModified(self):
        return self['dates']['modified']
    
    @property
    def sources(self):
        return self['sources']
    
    @property
    def details(self):
        return self['details']
    
    @Property
    def googlePlaces():
        def fget(self):
            if 'googlePlaces' in self.sources:
                return self.sources['googlePlaces']
            else:
                return None
        
        def fset(self, value):
            self.sources['googlePlaces'] = value
        
        return locals()
    
    @Property
    def openTable():
        def fget(self):
            if 'openTable' in self.sources:
                return self.sources['openTable']
            else:
                return None
        
        def fset(self, value):
            self.sources['openTable'] = value
        
        return locals()
    
    @Property
    def place():
        def fget(self):
            if 'place' in self.details:
                return self.details['place']
            else:
                return None
        def fset(self, value):
            self.details['place'] = value
        
        return locals()
    
    @Property
    def addr():
        def fget(self):
            if self.place and 'addr' in self.place:
                return self.place['addr']
            else:
                return None
        
        def fset(self, value):
            if not self.place:
                self.place = {}
            self.place['addr'] = value
        
        return locals()
    
    @Property
    def contact():
        def fget(self):
            if 'contact' in self.details:
                return self.details['contact']
            else:
                return None
        
        def fset(self, value):
            self.details['contact'] = value
        
        return locals()
    
    @Property
    def restaurant():
        def fget(self):
            if 'restaurant' in self.details:
                return self.details['restaurant']
            else:
                return None
        
        def fset(self, value):
            self.details['restaurant'] = value
        
        return locals()
    
    @Property
    def book():
        def fget(self):
            if 'book' in self.details:
                return self.details['book']
            else:
                return None
        
        def fset(self, value):
            self.details['book'] = value
        
        return locals()
    
    @Property
    def movie():
        def fget(self):
            if 'movie' in self.details:
                return self.details['movie']
            else:
                return None
        
        def fset(self, value):
            self.details['movie'] = value
        
        return locals()
    
    def _getSkeletonData(self):
        return {
            'name' : None, 
            'desc' : None, 
            'locale' : None, 
            'images' : None, 
            'dates' : {
                'created'  : None, 
                'modified' : None, 
            }, 
            'details' : {
            }, 
            'sources' : {
            }, 
        }
    
    @staticmethod
    def create(self, source, data):
        source = source.lower()
        
        if source == "opentable":
            entity = Entity()
            entity.name = data['name']
            entity.desc = data['desc']
            
            place = {
                'address' : data['address'], 
            }
            if 
            
            entity.place = place
            
            entity.openTable = {
                'id' : data['id'], 
                'reserveURL' : data['reserveURL'], 
                'countryID' : data['countryID'], 
                'metroName' : data['metroName'], 
                'neighborhoodName' : data['neighborhoodName'], 
            }

            'address' : str
            'coordinates' : {
                'lat' : float, 
                'lng' : float
            }
            'types' : [ str* ], 
            'vicinity' :? str, 

