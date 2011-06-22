#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import re
from MySQL import MySQL

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
    
    def addEntity(self, entity):
        entity = self._encodeEntity(entity)
        
        def _addEntity(cursor):
            query = """INSERT INTO entities 
                    (title, description, category, date_created) 
                    VALUES (%(title)s, %(desc)s, %(category)s, %(date_created)s)"""
            cursor.execute(query, entity)
            return cursor.lastrowid

        return MySQL()._transact(_addEntity)
   
    def getEntity(self, entityID):
        entityID = int(entityID)
        
        def _getEntity(cursor):
            query = "SELECT * FROM entities WHERE entity_id = %d" % (entityID)
            cursor.execute(query)
            
            if cursor.rowcount > 0:
                data = cursor.fetchone()
                return self._decodeEntity(entityID, data)
            else:
                return None
        
        return MySQL()._transact(_getEntity, returnDict=True)
    
    def updateEntity(self, entity):
        entity = self._encodeEntity(entity)
        
        def _updateEntity(cursor):
            query = """UPDATE entities SET 
                       title = %(title)s, 
                       description = %(desc)s, 
                       category = %(category)s, 
                       date_created = %(date_created)s 
                       WHERE entity_id = %(id)s"""
            print entity
            cursor.execute(query, entity)
            
            return (cursor.rowcount > 0)
        
        return MySQL()._transact(_updateEntity)
      
    def removeEntity(self, entityID):
        def _removeEntity(cursor):
            query = "DELETE FROM entities WHERE entity_id = %s" % \
                    (entityID)
            cursor.execute(query)
            
            return (cursor.rowcount > 0)
        
        return MySQL()._transact(_removeEntity)
    
    def _encodeEntity(self, entity):
        timestamp = datetime.now().isoformat()
        
        encodedEntity = {}
        encodedEntity['date_created'] = timestamp
        
        attributes = ['title', 'desc', 'category', 'id']
        for attribute in attributes:
            if attribute in entity:
                encodedEntity[attribute] = self._encode(entity[attribute])
            else:
                encodedEntity[attribute] = None
        return encodedEntity
    
    def _decodeEntity(self, entityID, data):
        entity = Entity()
        
        entity['title'] = self._decode(data['title'])
        entity['desc'] = self._decode(data['description'])
        entity['category'] = self._decode(data['category'])
        
        entity['id'] = entityID
        entity['date_created'] = self._decode(data['date_created'])
        return entity
    
    def _encode(self, attr):
        return attr
    
    def _decode(self, attr):
        if type(attr) == str:
            return attr.replace("\\n", "\n").replace("\\", "")
        else:
            return attr
