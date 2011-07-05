#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, Utils
import MySQLdb as mysqldb
import re, string

from AEntitySink import AEntitySink
from Entity import Entity
from threading import Lock
from datetime import datetime

class MySQLEntityDB(AEntitySink):
    USER = 'root'
    DB   = 'stamped'
    
    # TODO: truncate / validate sql input
    _rawSchema = {
        'title' : 'VARCHAR(512)', 
        'description' : 'TEXT', 
        'locale' : 'VARCHAR(32)', 
        'image' : 'BLOB', 
        
        'dateCreated' : 'DATETIME', 
        'dateModified' : 'DATETIME', 
        
        'detailsPlace' : 'BOOL', 
        'detailsPlaceAddress' : 'VARCHAR(128)', 
        'detailsPlaceCoordinates' : 'BOOL', 
        'detailsPlaceCoordinatesLat' : 'FLOAT', 
        'detailsPlaceCoordinatesLng' : 'FLOAT', 
        'detailsPlaceTypes' : 'VARCHAR(256)', 
        'detailsPlaceVicinity' : 'VARCHAR(128)', 
        'detailsPlaceNeighborhood' : 'VARCHAR(128)', 
        'detailsPlaceCrossStreet' : 'VARCHAR(256)', 
        'detailsPlacePublicTransit' : 'VARCHAR(1024)', 
        'detailsPlaceParking' : 'VARCHAR(128)', 
        'detailsPlaceParkingDetails' : 'TEXT', 
        'detailsPlaceWheelchairAccess' : 'VARCHAR(256)', 
        
        'detailsContact' : 'BOOL', 
        'detailsContactPhone' : 'VARCHAR(128)', 
        'detailsContactFax' : 'VARCHAR(128)', 
        'detailsContactSite' : 'VARCHAR(2048)', 
        'detailsContactEmail' : 'VARCHAR(512)', 
        'detailsContactHoursOfOperation' : 'VARCHAR(1024)', 
        
        'detailsRestaurant' : 'BOOL', 
        'detailsRestaurantDiningStyle' : 'VARCHAR(512)', 
        'detailsRestaurantCuisine' : 'VARCHAR(512)', 
        'detailsRestaurantPrice' : 'VARCHAR(512)', 
        'detailsRestaurantPayment' : 'VARCHAR(512)', 
        'detailsRestaurantDressCode' : 'VARCHAR(512)', 
        'detailsRestaurantAcceptsReservations' : 'VARCHAR(128)', 
        'detailsRestaurantAcceptsWalkins' : 'VARCHAR(512)', 
        'detailsRestaurantOffers' : 'VARCHAR(1024)', 
        'detailsRestaurantPrivatePartyFacilities' : 'VARCHAR(1024)', 
        'detailsRestaurantPrivatePartyContact' : 'VARCHAR(512)', 
        'detailsRestaurantEntertainment' : 'VARCHAR(1024)', 
        'detailsRestaurantSpecialEvents' : 'VARCHAR(1024)', 
        'detailsRestaurantCatering' : 'VARCHAR(1024)', 
        'detailsRestaurantAlcohol' : 'VARCHAR(256)', 
        'detailsRestaurantTakeout' : 'VARCHAR(256)', 
        'detailsRestaurantDelivery' : 'VARCHAR(256)', 
        'detailsRestaurantKosher' : 'VARCHAR(256)', 
        'detailsRestaurantBar' : 'VARCHAR(256)', 
        'detailsRestaurantMenuLink' : 'VARCHAR(2048)', 
        'detailsRestaurantChef' : 'VARCHAR(512)', 
        'detailsRestaurantOwner' : 'VARCHAR(512)', 
        'detailsRestaurantReviewLinks' : 'VARCHAR(2048)', 
        
        'detailsIPhoneApp' : 'BOOL', 
        'detailsIPhoneAppDeveloper' : 'VARCHAR(512)', 
        'detailsIPhoneAppDeveloperURL' : 'VARCHAR(2048)', 
        'detailsIPhoneAppDeveloperSupportURL' : 'VARCHAR(2048)', 
        'detailsIPhoneAppPublisher' : 'VARCHAR(256)', 
        'detailsIPhoneAppReleaseDate' : 'VARCHAR(256)', 
        'detailsIPhoneAppPrice' : 'VARCHAR(256)', 
        'detailsIPhoneAppCategory' : 'VARCHAR(256)', 
        'detailsIPhoneAppLanguage' : 'VARCHAR(256)', 
        'detailsIPhoneAppRating' : 'VARCHAR(256)', 
        'detailsIPhoneAppPopularity' : 'VARCHAR(256)', 
        'detailsIPhoneAppParentalRating' : 'VARCHAR(256)', 
        'detailsIPhoneAppPlatform' : 'VARCHAR(256)', 
        'detailsIPhoneAppRequirements' : 'VARCHAR(256)', 
        'detailsIPhoneAppSize' : 'VARCHAR(256)', 
        'detailsIPhoneAppVersion' : 'VARCHAR(256)', 
        'detailsIPhoneAppDownloadURL' : 'VARCHAR(2048)', 
        'detailsIPhoneAppThumbnailURL' : 'VARCHAR(2048)', 
        'detailsIPhoneAppScreenshotURL' : 'VARCHAR(2048)', 
        'detailsIPhoneAppVideoURL' : 'VARCHAR(2048)', 
        
        'detailsBook' : 'BOOL', 
        'detailsMovie' : 'BOOL', 
        
        'sourcesGooglePlaces' : 'BOOL', 
        'sourcesGooglePlacesGid' : 'VARCHAR(128)', 
        'sourcesGooglePlacesGurl' : 'VARCHAR(1024)', 
        'sourcesGooglePlacesReference' : 'VARCHAR(256)', 
        
        'sourcesOpenTable' : 'BOOL', 
        'sourcesOpenTableRid' : 'VARCHAR(128)', 
        'sourcesOpenTableReserveURL' : 'VARCHAR(128)', 
        'sourcesOpenTableCountryID' : 'VARCHAR(64)', 
        'sourcesOpenTableMetroName' : 'VARCHAR(128)', 
        'sourcesOpenTableNeighborhoodName' : 'VARCHAR(256)', 
        
        'sourcesFactual' : 'BOOL', 
        'sourcesFactualFid' : 'VARCHAR(128)', 
        'sourcesFactualTable' : 'VARCHAR(256)', 
    }
    
    def __init__(self):
        self._table = Globals.options.collection
        desc = 'MySQL:%s@%s.%s' % (self.USER, self.DB, self._table)
        AEntitySink.__init__(self, desc)
        
        self._lock = Lock()
        self._setup()
    
    def _run(self):
        self.processQueue(self._input)
        self.close()
    
    def _processItem(self, item):
        return self.addEntity(item)
    
    def _processItems(self, items):
        return self.addEntities(items)
    
    def addEntity(self, entity):
        Utils.log("[MySQLEntityDB] adding 1 entity")
        
        def _addEntity(cursor):
            (paramNames, paramFormat, paramValues) = self._getEncodedParams(entity)
            
            query = "INSERT INTO %s %s VALUES %s" % (self._table, paramNames, paramFormat)
            
            Utils.log(query)
            Utils.log(paramValues)
            
            numRowsAffected = cursor.execute(query, paramValues)
            
            if numRowsAffected > 0:
                return self.db.insert_id()
            else:
                return None
        
        return self._transact(_addEntity)
    
    def getEntity(self, entityID):
        entityID = int(entityID)
        
        def _getEntity(cursor):
            query = "SELECT * FROM %s WHERE entity_id = %d" % (self._table, entityID, )
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
            query = "REPLACE INTO %s %s VALUES %s" % (self._table, paramNames, paramFormat)
            numRowsAffected = cursor.execute(query, paramValues)
            
            return (numRowsAffected > 0)
        
        return self._transact(_updateEntity)
    
    def removeEntity(self, entityID):
        def _removeEntity(cursor):
            query = "DELETE FROM %s WHERE entity_id = %d" % (self._table, entityID, )
            numRowsAffected = cursor.execute(query)
            
            return (numRowsAffected > 0)
        
        return self._transact(_removeEntity)
    
    def addEntities(self, entities):
        #for entity in entities:
        #    self.addEntity(entity)
        #return True
        
        numEntities = Utils.count(entities)
        Utils.logRaw("[MySQLEntityDB] adding %d %s... " % \
            (numEntities, Utils.numEntitiesToStr(numEntities)), True)
        
        #Utils.log("%s %s" % (str(type(entities)), str(entities)))
        #for entity in entities:
        #    Utils.log(entity)
        
        def _addEntities(cursor):
            (paramNames, paramFormat, paramValues) = self._getEncodedParamsMany(entities)
            query = "INSERT INTO %s %s VALUES %s" % (self._table, paramNames, paramFormat)
            
            #Utils.log(query)
            #for e in paramValues:
            #    Utils.log(e)
            
            #Utils.log(query)
            #Utils.log(paramValues[0])
            
            numRowsExpected = Utils.count(paramValues)
            numRowsAffected = cursor.executemany(query, paramValues)
            #Utils.log("%d vs %d" % (numRowsAffected, numRowsExpected))
            
            if numRowsAffected != numRowsExpected:
                Utils.log('[MySQLEntityDB.addEntities] error inserting %d %s' % (numRowsExpected, self._table))
                Utils.log(query)
                
                for e in paramValues:
                    Utils.log(e)
                
                return False
            else:
                return True
        
        retVal = self._transact(_addEntities)
        if retVal:
            Utils.logRaw("done!\n")
        
        return retVal
    
    def close(self):
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
            
            query = """CREATE TABLE %s (
                entity_id INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE, 
                %s PRIMARY KEY(entity_id))""" % (self._table, self._schema)
            
            #Utils.log(query)
            cursor.execute(query)
            
            cursor.execute("CREATE INDEX ix_title ON %s (title)" % self._table)
            return True
        
        self._schema = self._createSchema(self._rawSchema)
        
        if not Globals.options.update:
            self.db = mysqldb.connect(user=self.USER)
            self._transact(_createDB)
            self.close()
            
            self._transact(_createTables)
        else:
            self.db = self._getConnection()
    
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
            retVal = None
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
            
            curValues = self._getEncodedParamValues(unionParams, rawParams)
            paramValues.append(curValues)
        
        return (paramNames, paramFormat, paramValues)
    
    def _getParams(self, entity):
        def _encode(attr):
            attr = Utils.normalize(attr)
            
            if isinstance(attr, basestring):
                return self.db.escape_string(attr)
            else:
                return attr
        
        def _flattenOptionalParams(keyPrefix, source, dest):
            for k, v in source.iteritems():
                if keyPrefix:
                    keySuffix = ''
                    
                    if len(k) > 0:
                        keySuffix = k[0:1].upper() + k[1:]
                    
                    key = keyPrefix + keySuffix
                else:
                    key = k
                
                if isinstance(v, dict):
                    #print "%s dict" % key
                    dest[key] = True
                    _flattenOptionalParams(key, v, dest)
                elif isinstance(v, list):
                    # TODO: ensure encoding of a list separated by a 
                    # given character is robust. note: this is a hack...
                    separator = ';'
                    dest[key] = _encode(reduce(lambda x, y: x + separator + y, v))
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
        paramValues = self._getEncodedParamValues(params)
        
        return (paramNames, paramFormat, paramValues)
    
    def _getEncodedParamKeys(self, params):
        keys = params.keys()
        paramNames  = '(' + string.joinfields(keys, ', ') + ')'
        paramFormat = '(' + string.joinfields(('%s' for param in keys), ', ') + ')'
        
        return (paramNames, paramFormat)
    
    def _getEncodedParamValues(self, params, stableParams=None):
        if stableParams is None:
            stableParams = params
        
        return tuple(params[k] for k in stableParams.keys())
    
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
        return dict([ k, None ] for k in schema.iterkeys())

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

import EntitySinks
EntitySinks.registerSink('mysql', MySQLEntityDB)

