#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from MySQL import MySQL
from AEntityDB import AEntityDB
from Entity import Entity

class MySQLEntityDB(AEntityDB, MySQL):

    # Denotes relationship between object and SQL table structure -- primary
    # use is to map fields between both structures.
    # First item in tuple is OBJECT ATTRIBUTE, second is COLUMN NAME.
    MAPPING = [
            ('id', 'entity_id'),
            ('title', 'title'),
            ('description', 'description'),
            ('category', 'category'),
            ('image', 'image'),
            ('source', 'source'),
            ('location', 'locale'),
            ('date_created', 'date_created'),
            ('date_updated', 'date_updated')
        ]

    def __init__(self, setup=False):
        AEntityDB.__init__(self, self.DESC)
        MySQL.__init__(self, mapping=self.MAPPING)
        
        self.db = self._getConnection()
        self._lock = Lock()
        if setup:
            self._createEntityTable()
        
    ### PUBLIC
    
    def addEntity(self, entity):
        entity = self._mapObjToSQL(entity)
        entity['date_created'] = datetime.now().isoformat()
        
        def _addEntity(cursor):
            query = """INSERT INTO entities 
                    (title, description, category, date_created) 
                    VALUES (%(title)s, %(description)s, %(category)s, %(date_created)s)"""
            cursor.execute(query, entity)
            return cursor.lastrowid

        return self._transact(_addEntity)
    
    def getEntity(self, entityID):
        entityID = int(entityID)
        
        def _getEntity(cursor):
            query = "SELECT * FROM entities WHERE entity_id = %d" % (entityID)
            cursor.execute(query)
            
            if cursor.rowcount > 0:
                data = cursor.fetchone()
                #return self._decodeEntity(entityID, data)
                entity = Entity()
                return self._mapSQLToObj(data, entity)
            else:
                return None
        
        return self._transact(_getEntity, returnDict=True)
    
    def updateEntity(self, entity):
        entity = self._mapObjToSQL(entity)
        entity['date_updated'] = datetime.now().isoformat()
                
        def _updateEntity(cursor):
            query = """UPDATE entities SET 
                       title = %(title)s, 
                       description = %(description)s, 
                       category = %(category)s, 
                       date_updated = %(date_updated)s 
                       WHERE entity_id = %(entity_id)s"""
            cursor.execute(query, entity)
            
            return (cursor.rowcount > 0)
        
        return self._transact(_updateEntity)
      
    def removeEntity(self, entityID):
        def _removeEntity(cursor):
            query = "DELETE FROM entities WHERE entity_id = %s" % \
                    (entityID)
            cursor.execute(query)
            
            return (cursor.rowcount > 0)
        
        return self._transact(_removeEntity)
    
    def matchEntities(self, string):
        def _matchEntities(cursor):
            query = ("""SELECT entity_id, title, category 
                    FROM entities 
                    WHERE LEFT(title, %d) = '%s'
                    LIMIT 0, 10""" % 
                    (len(string), string))
            cursor.execute(query)
            entitiesData = cursor.fetchall()
            
            entities = []
            for entityData in entitiesData:
                entity = Entity()
                entity = self._mapSQLToObj(entityData, entity)
                entities.append(entity)
            return entities
        
        return self._transact(_matchEntities, returnDict=True)
    
    ### PRIVATE
    
    def _createEntityTable(self):
        def _createTable(cursor):
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
            
        return self._transact(_createTable)
        
