#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, Utils
import copy

class Entity(object):
    _schema = \
    {
        'id'   : int, 
        'name' : basestring, 
        'desc' : basestring, 
        
        'locale' : basestring, 
        'images' : list, 
        
        'date' : {
            'created'  : basestring, 
            'modified' : basestring, 
        }, 
        
        'details' : {
            'place' : {
                'address' : basestring, 
                'coordinates' : {
                    'lat' : float, 
                    'lng' : float
                }, 
                'types' : list, 
                'vicinity' : basestring, 
                'neighborhood' : basestring, 
                'crossStreet' : basestring, 
                'publicTransit' : basestring, 
                'parking' : basestring, 
                'parkingDetails' : basestring, 
                'wheelchairAccess' : basestring, 
            }, 
            
            'contact' : {
                'phone' : basestring, 
                'fax'   : basestring, 
                'site'  : basestring, 
                'email' : basestring, 
                'hoursOfOperation' : basestring, 
            }, 
            
            'restaurant' : {
                'diningStyle' : basestring, 
                'cuisine' : basestring, 
                'price' : basestring, 
                'payment' : basestring, 
                'dressCode' : basestring, 
                'acceptsReservations' : basestring, 
                'acceptsWalkins' : basestring, 
                'offers' : basestring, 
                'privatePartyFacilities' : basestring, 
                'privatePartyContact' : basestring, 
                'entertainment' : basestring, 
                'specialEvents' : basestring, 
                'catering' : basestring, 
                'takeout' : basestring, 
                'delivery' : basestring, 
                'kosher' : basestring, 
                'bar' : basestring, 
                'alcohol' : basestring, 
                'menuLink' : basestring, 
                'chef' : basestring, 
                'owner' : basestring, 
                'reviewLinks' : basestring, 
            }, 
            
            'iPhoneApp' : {
                'developer' : basestring, 
                'developerURL' : basestring, 
                'developerSupportURL' : basestring, 
                'publisher' : basestring, 
                'releaseDate' : basestring, 
                'price' : basestring, 
                'category' : basestring, 
                'language' : basestring, 
                'rating' : basestring, 
                'popularity' : basestring, 
                'parentalRating' : basestring, 
                'platform' : basestring, 
                'requirements' : basestring, 
                'size' : basestring, 
                'version' : basestring, 
                'downloadURL' : basestring, 
                'thumbnailURL' : basestring, 
                'screenshotURL' : basestring, 
                'videoURL' : basestring, 
            }, 
            'book' : {
                # TODO
            }, 
            'movie' : {
                # TODO
            }, 
        }, 
        
        'sources' : {
            'googlePlaces' : {
                'gid' : basestring, 
                'gurl' : basestring, 
                'reference' : basestring, 
            }, 
            'openTable' : {
                'rid' : basestring, 
                'reserveURL' : basestring, 
                'countryID'  : basestring, 
                'metroName'  : basestring, 
                'neighborhoodName' : basestring, 
            }, 
            'factual' : {
                'fid' : basestring, 
                'table' : basestring, 
            }
        }
    }
    
    def __init__(self, data=None):
        if data:
            self._data = data
        else:
            self._data = self._getSkeletonData()
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self.add({key : value})
    
    def __delitem__(self, key):
        del self._data[key]
    
    def __len__(self):
        return len(self._data)
    
    def __str__(self):
        return str(self._data)
    
    def __contains__(self, item):
        return item in self._data
    
    def __copy__(self):
        return Entity(copy.copy(self._data))
    
    def __deepcopy__(self):
        return Entity(copy.deepcopy(self._data))
    
    def __getattr__(self, name):
        if name == '_data':
            return object.__getattr__(self, name)
        
        def _get(dic):
            if name in dic:
                return dic[name]
            else:
                for k, v in dic.iteritems():
                    if isinstance(v, dict):
                        retVal = _get(v)
                        if retVal:
                            return retVal
            return None
        
        return _get(self._data)
    
    def __setattr__(self, name, value):
        #print "__setattr__ %s, %s" % (name, str(value))
        value = Utils.normalize(value)
        
        if name == '_data':
            object.__setattr__(self, name, value)
            return None
        
        return self.add({ name : value })
    
    def add(self, data):
        def _unionDict(source, schema, dest):
            for k, v in source.iteritems():
                if not _unionItem(k, v, schema, dest):
                    #Utils.log("item not found %s %s" % (k, v))
                    return False
            
            return True
        
        def _unionItem(k, v, schema, dest):
            #print "_union %s %s %s" % (type(source), type(schema), type(dest))
            
            if k in schema:
                schemaVal = schema[k]
                
                if isinstance(schemaVal, type):
                    schemaValType = schemaVal
                else:
                    schemaValType = type(schemaVal)
                
                # basic type checking
                if not isinstance(v, schemaValType):
                    isValid = True
                    
                    # basic implicit type conversion s.t. if you pass in, for example, 
                    # "23.4" for longitude as a string, it'll automatically parse to 
                    # the required float format.
                    try:
                        if schemaValType == basestring:
                            v = str(v)
                        elif schemaValType == float:
                            v = float(v)
                        elif schemaValType == int:
                            v = int(v)
                        else:
                            isValid = False
                    except ValueError:
                        isValid = False
                    
                    if not isValid:
                        raise KeyError("Entity error; key '%s' found '%s', expected '%s'" % \
                            (k, str(type(v)), str(schemaVal)))
                
                if isinstance(v, dict):
                    if k not in dest:
                        dest[k] = { }
                    
                    return _unionDict(v, schemaVal, dest[k])
                else:
                    dest[k] = v
                    return True
            else:
                for k2, v2 in schema.iteritems():
                    if isinstance(v2, dict):
                        if k2 in dest:
                            if not isinstance(dest[k2], dict):
                                raise KeyError(k2)
                            
                            if _unionItem(k, v, v2, dest[k2]):
                                return True
                        else:
                            temp = { }
                            
                            if _unionItem(k, v, v2, temp):
                                dest[k2] = temp
                                return True
            
            return False
        
        if not _unionDict(data, self._schema, self._data):
            raise KeyError("Entity error %s" % str(data))
        
        return
    
    @property
    def isValid(self):
        valid = True
        
        valid &= 'name' in self and isinstance(self.name, basestring)
        valid &= 'desc' in self and isinstance(self.desc, basestring)
        valid &= 'locale' in self and isinstance(self.locale, basestring)
        valid &= 'images' in self and isinstance(self.images, list)
        
        valid &= 'date' in self and isinstance(self.date, dict)
        valid &= 'created' in self.date and isinstance(self.date['created'], basestring)
        valid &= 'modified' in self.date and isinstance(self.date['modified'], basestring)
        
        valid &= 'sources' in self and isinstance(self.sources, dict)
        valid &= 'details' in self and isinstance(self.details, dict)
    
    def _getSkeletonData(self):
        return {
            'name' : None, 
            'desc' : None, 
            'locale' : None, 
            'images' : None, 
            'date' : { }, 
            'details' : { }, 
            'sources' : { }, 
        }

