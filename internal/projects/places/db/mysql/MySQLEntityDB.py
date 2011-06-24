#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import re, string, Utils
import MySQLdb as mysqldb

from AEntityDB import AEntityDB
from Entity import Entity
from threading import Lock
from datetime import datetime

class MySQLEntityDB(AEntityDB):
    USER  = 'root'
    DB    = 'stamped'
    DESC  = 'MySQL:%s@%s.entities' % (USER, DB)
    
    _rawSchema = {
        #'entity_id' : 'INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE', 
        'title' : 'VARCHAR(128)', 
        'description' : 'TEXT', 
        'locale' : 'VARCHAR(32)', 
        'image' : 'BLOB', 
        
        'dateCreated' : 'DATETIME', 
        'dateModified' : 'DATETIME', 
        
        'detailsPlace' : 'BOOL', 
        'detailsPlaceAddress' : 'VARCHAR(128)', 
        'detailsPlaceCoordinatesLat' : 'FLOAT', 
        'detailsPlaceCoordinatesLng' : 'FLOAT', 
        'detailsPlaceTypes' : 'VARCHAR(256)', 
        'detailsPlaceVicinity' : 'VARCHAR(128)', 
        'detailsPlaceNeighborhood' : 'VARCHAR(128)', 
        'detailsPlaceCrossStreet' : 'VARCHAR(256)', 
        'detailsPlacePublicTransit' : 'VARCHAR(1024)', 
        'detailsPlaceParking' : 'VARCHAR(128)', 
        'detailsPlaceParkingDetails' : 'TEXT', 
        
        'detailsContact' : 'BOOL', 
        'detailsContactPhone' : 'VARCHAR(128)', 
        'detailsContactSite' : 'VARCHAR(2048)', 
        'detailsContactEmail' : 'VARCHAR(256)', 
        'detailsContactHoursOfOperation' : 'VARCHAR(256)', 
        
        'detailsRestaurant' : 'BOOL', 
        'detailsRestaurantDiningStyle' : 'VARCHAR(256)', 
        'detailsRestaurantCuisine' : 'VARCHAR(256)', 
        'detailsRestaurantPrice' : 'VARCHAR(256)', 
        'detailsRestaurantPayment' : 'VARCHAR(256)', 
        'detailsRestaurantDressCode' : 'VARCHAR(256)', 
        'detailsRestaurantAcceptsWalkins' : 'VARCHAR(256)', 
        'detailsRestaurantOffers' : 'VARCHAR(1024)', 
        'detailsRestaurantPrivatePartyFacilities' : 'VARCHAR(1024)', 
        'detailsRestaurantPrivatePartyContact' : 'VARCHAR(128)', 
        'detailsRestaurantEntertainment' : 'VARCHAR(256)', 
        'detailsRestaurantSpecialEvents' : 'VARCHAR(1024)', 
        'detailsRestaurantCatering' : 'VARCHAR(1024)', 
        
        'detailsBook' : 'BOOL', 
        'detailsMovie' : 'BOOL', 
        
        'sourcesGooglePlaces' : 'BOOL', 
        'sourcesGooglePlacesID' : 'VARCHAR(128)', 
        'sourcesGooglePlacesReference' : 'VARCHAR(256)', 
        
        'sourcesOpenTable' : 'BOOL', 
        'sourcesOpenTableID' : 'VARCHAR(128)', 
        'sourcesOpenTableReserveURL' : 'VARCHAR(128)', 
        'sourcesOpenTableCountryID' : 'VARCHAR(32)', 
        'sourcesOpenTableMetroName' : 'VARCHAR(128)', 
        'sourcesOpenTableNeighborhoodName' : 'VARCHAR(256)', 
    }
    
    def __init__(self):
        AEntityDB.__init__(self, self.DESC)
        
        self._lock = Lock()
        self._setup()
    
    def addEntity(self, entity):
        def _addEntity(cursor):
            (paramNames, paramFormat, paramValues) = self._getEncodedParams(entity)
            
            query = "INSERT INTO entities %s VALUES %s" % (paramNames, paramFormat)
            numRowsAffected = cursor.execute(query, paramValues)
            
            if numRowsAffected > 0:
                return self.db.insert_id()
            else:
                return None
        
        return self._transact(_addEntity)
    
    def getEntity(self, entityID):
        entityID = int(entityID)
        
        def _getEntity(cursor):
            query = "SELECT * FROM entities WHERE entity_id = %d" % (entityID, )
            numRowsAffected = cursor.execute(query)
            
            if numRowsAffected > 0:
                data = cursor.fetchone()
                
                return self._decodeEntity(entityID, data)
            else:
                return None
        
        return self._transact(_getEntity, mysqldb.cursors.DictCursor)
    
    def updateEntity(self, entity):
        def _updateEntity(cursor):
            (paramNames, paramFormat, paramValues) = self._getEncodedParams(entity)
            
            # TODO: look into using UPDATE
            query = "REPLACE INTO entities %s VALUES %s" % (paramNames, paramFormat)
            numRowsAffected = cursor.execute(query, paramValues)
            
            return (numRowsAffected > 0)
        
        return self._transact(_updateEntity)
    
    def removeEntity(self, entityID):
        def _removeEntity(cursor):
            query = "DELETE FROM entities WHERE entity_id = %d" % (entityID, )
            numRowsAffected = cursor.execute(query)
            
            return (numRowsAffected > 0)
        
        return self._transact(_removeEntity)
    
    def addEntities(self, entities):
        #for entity in entities:
        #    Utils.log(entity)
        
        def _addEntities(cursor):
            (paramNames, paramFormat, paramValues) = self._getEncodedParamsMany(entities)
            query = "INSERT INTO entities %s VALUES %s" % (paramNames, paramFormat)
            
            #Utils.log(query)
            #for e in paramValues:
            #    Utils.log(e)
            
            numRowsExpected = Utils.count(paramValues)
            numRowsAffected = cursor.executemany(query, paramValues)
            #Utils.log("%d vs %d" % (numRowsAffected, numRowsExpected))
            
            return (numRowsAffected == numRowsExpected)
        
        return self._transact(_addEntities)
    
    def close(self):
        AEntityDB.close(self)
        
        if self.db:
            self.db.commit()
            self.db.close()
            self.db = None
    
    def _setup(self):
        def _createDB(cursor):
            cursor.execute('DROP DATABASE IF EXISTS %s' % self.DB)
            cursor.execute('CREATE DATABASE %s' % self.DB)
            return True
        
        def _createTables(cursor):
            # SERIAL = BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE
            
            query = """CREATE TABLE entities (
                entity_id INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE, 
                """ + self._schema + "PRIMARY KEY(entity_id))"
            #Utils.log(query)
            cursor.execute(query)
            
            cursor.execute("CREATE INDEX ix_title ON entities (title)")
            return True
        
        self._schema = self._createSchema(self._rawSchema)
        
        self.db = mysqldb.connect(user=self.USER)
        self._transact(_createDB)
        self.close()
        
        self._transact(_createTables)
    
    def _transact(self, func, customCursor=None):
        retVal = None
        
        self._lock.acquire()
        try:
            if self.db is None:
                self.db = self._getConnection()
            
            if customCursor:
                cursor = self.db.cursor(customCursor)
            else:
                cursor = self.db.cursor()
            
            retVal = func(cursor)
            if retVal is not None and (type(retVal) is not bool or retVal == True):
                self.db.commit()
            else:
                Utils.log('[MySQLEntityDB] __rollback__')
                self.db.rollback()
            
            cursor.close()
        except mysqldb.Error, e:
            Utils.log("[MySQLEntityDB] Error: %s" % str(e))
            self.db.rollback()
        finally:
            self._lock.release()
        
        return retVal
    
    def _getConnection(self):
        return mysqldb.connect(user=self.USER, db=self.DB)
    
    def _getEncodedParamsMany(self, entities):
        rawParams = self._createDefaultParams(self._rawSchema)
        (paramNames, paramFormat) = self._getEncodedParamKeys(rawParams)
        paramValues = [ ]
        
        for entity in entities:
            curParams = self._getParams(entity)
            
            unionParams = rawParams.copy()
            unionParams.update(curParams)
            
            curValues = self._getEncodedParamValues(unionParams)
            paramValues.append(curValues)
        
        return (paramNames, paramFormat, paramValues)
    
    def _getParams(self, entity):
        def _encode(attr):
            if isinstance(attr, basestring):
                return self.db.escape_string(attr)
            else:
                return attr
        
        def _flattenOptionalParams(keyPrefix, source, dest):
            for k, v in source.iteritems():
                if keyPrefix:
                    kl = k.lower()
                    keySuffix = ''
                    
                    if kl == 'id':
                        keySuffix = 'ID'
                    elif len(k) > 0:
                        keySuffix = k[0:1].upper() + k[1:]
                    
                    key = keyPrefix + keySuffix
                else:
                    key = k
                
                if isinstance(v, dict):
                    #print "%s dict" % key
                    dest[key] = True
                    _flattenOptionalParams(key, v, dest)
                else:
                    #print "%s = %s (%s)" % (key, _encode(v), type(v))
                    dest[key] = _encode(v)
        
        params = {
            'title' : _encode(entity.name), 
            'description' : _encode(entity.desc), 
        }
        
        if 'id' in entity:
            params['entity_id'] = entity['id']
        
        if 'locale' in entity and entity.locale is not None:
            params['locale'] = _encode(entity.locale)
        else:
            params['locale'] = "en_US"
        
        date = _encode(datetime.now().isoformat())
        
        if 'created' in entity.date and entity.date['created'] is not None:
            params['dateCreated'] = _encode(entity.date['created'])
        else:
            params['dateCreated'] = date
        
        if 'modified' in entity.date and entity.date['modified'] is not None:
            params['dateModified'] = _encode(entity.date['modified'])
        else:
            params['dateModified'] = date
        
        # TODO: support saving more than one image
        if entity.images and len(entity.images) > 0:
            param['image'] = _encode(entity.images[0])
        
        _flattenOptionalParams('details', entity.details, params)
        _flattenOptionalParams('sources', entity.sources, params)
        
        return params
    
    def _getEncodedParams(self, entity):
        params = self._getParams(entity)
        
        (paramNames, paramFormat) = self._getEncodedParamKeys(params)
        paramValues = self._getEncodedParamValues(params.values())
        
        return (paramNames, paramFormat, paramValues)
    
    def _getEncodedParamKeys(self, params):
        keys = params.keys()
        paramNames  = '(' + string.joinfields(keys, ', ') + ')'
        paramFormat = '(' + string.joinfields(('%s' for param in keys), ', ') + ')'
        
        return (paramNames, paramFormat)
    
    def _getEncodedParamValues(self, params):
        return tuple(params.values())
    
    def _decodeEntity(self, entityID, data):
        entity = Entity()
        # TODO
        
        entity['name'] = self._decode(data['title'])
        entity['desc'] = self._decode(data['description'])
        entity['category'] = self._decode(data['category'])
        
        entity['id'] = entityID
        entity['date_created'] = self._decode(data['date_created'])
        return entity
    
    def _decode(self, attr):
        if type(attr) == str:
            return attr.replace("\\n", "\n").replace("\\", "")
        else:
            return attr
    
    def _createSchema(self, schema):
        return string.joinfields((k + ' ' + v + ', ' for k, v in schema.iteritems()))
    
    def _createDefaultParams(self, schema):
        return dict((k, None) for k in schema.iterkeys())

"""
db=MySQLEntityDB()
print str(db)

e=Entity({
    'name' : 'test', 
    'desc' : 'This is a \' desc"\nit contains multiple lines."'
})

entityID = db.addEntity(e)
print entityID

f = db.getEntity(entityID)
print e
print f

for k, v in e._data.iteritems():
    if f[k] != v:
        print "Error: '%s'\n'%s'" % (str(f[k]), str(v))

"""

import EntityDatabases
EntityDatabases.registerDB('mysql', MySQLEntityDB)

