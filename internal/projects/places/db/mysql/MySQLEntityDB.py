#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import re, Utils
import MySQLdb as mysqldb

from AEntityDB import AEntityDB
from Entity import Entity
from threading import Lock
from datetime import datetime

class MySQLEntityDB(AEntityDB):
    USER  = 'root'
    DB    = 'stamped'
    DESC  = 'MySQL:%s@%s.entities' % (USER, DB)
    
    def __init__(self):
        AEntityDB.__init__(self, self.DESC)
        
        self._lock = Lock()
        self._setup()
    
    def addEntity(self, entity):
        entity = self._encodeEntity(entity)
        
        def _addEntity(cursor):
            query = """INSERT INTO entities 
                    (title, description, category, date_created) 
                    VALUES (%(title)s, %(desc)s, %(category)s, %(date_created)s)"""
            cursor.execute(query, entity)
            
            if cursor.rowcount > 0:
                return self.db.insert_id()
            else:
                return None
        
        return self._transact(_addEntity)
    
    def getEntity(self, entityID):
        entityID = int(entityID)
        
        def _getEntity(cursor):
            query = """SELECT * FROM entities WHERE entity_id = %d""" % \
                    (entityID)
            cursor.execute(query)
            
            if cursor.rowcount > 0:
                data = cursor.fetchone()
                
                return self._decodeEntity(entityID, data)
            else:
                return None
        
        return self._transact(_getEntity, mysqldb.cursors.DictCursor)
    
    def updateEntity(self, entity):
        entity = self._encodeEntity(entity)
        
        def _updateEntity(cursor):
            query = """UPDATE entities SET 
                       title = %(title)s, 
                       description = %(desc)s, 
                       category = %(category)s, 
                       date_created = %(date_created)s, 
                       WHERE entity_id = %(id)d"""
            cursor.execute(query, entity)
            
            return (cursor.rowcount > 0)
        
        return self._transact(_updateEntity)
    
    def removeEntity(self, entityID):
        def _removeEntity(cursor):
            query = "DELETE FROM entities WHERE entity_id = %d" % \
                    (entityID)
            cursor.execute(query)
            
            return (cursor.rowcount > 0)
        
        return self._transact(_removeEntity)
    
    def addEntities(self, entities):
        entities = (self._encodeEntity(e) for e in entities)
        entities = ((e['title'], e['desc'], e['category'], e['date_created']) for e in entities)
        
        def _addEntities(cursor):
            query = """INSERT INTO entities 
                    (title, description, category, date_created) VALUES 
                    (%s, %s, %s, %s)"""
            cursor.executemany(query, entities)
            
            return (cursor.rowcount == Utils.count(entities))
        
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
            query = """CREATE TABLE entities (
                entity_id INT NOT NULL AUTO_INCREMENT, 
                title VARCHAR(100), 
                description TEXT, 
                category VARCHAR(50), 
                image VARCHAR(100), 
                source VARCHAR(50), 
                location VARCHAR(100), 
                locale VARCHAR(100),
                affiliate VARCHAR(100),
                date_created DATETIME,
                date_updated DATETIME, 
                PRIMARY KEY(entity_id))"""
            cursor.execute(query)
            
            cursor.execute("CREATE INDEX ix_title ON entities (title)")
            cursor.execute("CREATE INDEX ix_category ON entities (category)")
            
            return True
        
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
    
    def _encodeEntity(self, entity):
        timestamp = datetime.now().isoformat()
        
        return {
            'title' : self._encode(entity.name), 
            'desc'  : self._encode(entity.desc), 
            'category' : self._encode('TODO'), 
            'date_created' : self._encode(timestamp)
        }
    
    def _decodeEntity(self, entityID, data):
        entity = Entity()
        
        entity['title'] = self._decode(data['title'])
        entity['desc'] = self._decode(data['description'])
        entity['category'] = self._decode(data['category'])
        
        entity['id'] = entityID
        entity['date_created'] = self._decode(data['date_created'])
        return entity
    
    def _encode(self, attr):
        if type(attr) == str:
            return self.db.escape_string(attr)
        else:
            return attr
    
    def _decode(self, attr):
        if type(attr) == str:
            return attr.replace("\\n", "\n").replace("\\", "")
        else:
            return attr

"""
db=MySQLEntityDB()
print str(db)

e=Entity({
    'title' : 'test', 
    'desc'  : 'This is a \' desc"\nit contains multiple lines."'
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

