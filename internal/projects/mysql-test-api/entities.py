#!/usr/bin/env python

from datetime import datetime
from dbconn import MySQLConnection
    
class Entity(MySQLConnection):

    def __init__(self):
        self.database = self.connectDatabase()
    
    ###########################################################################
    def show(self, entity_id):
        entity_id = int(entity_id)
        
        cursor = self.getDatabase().cursor() 
        
        query = ("""SELECT 
                    entity_id, 
                    title, 
                    description, 
                    category, 
                    image, 
                    source, 
                    location, 
                    locale, 
                    affiliate, 
                    date_created, 
                    date_updated
                FROM entities
                WHERE entity_id = %d""" %
                (entity_id))
        cursor.execute(query)
        
        if cursor.rowcount > 0:
            data = cursor.fetchone()
            
            result = {}
            result['entity_id'] = data[0]
            result['title'] = data[1]
            result['description'] = data[2]
            result['category'] = data[3]
            result['image'] = data[4]
            result['source'] = data[5]
            result['location'] = data[6]
            result['locale'] = data[7]
            result['affiliate'] = data[8]
            result['date_created'] = data[9]
            result['date_updated'] = data[10]
    
        else: 
            result = "NA"
            
        cursor.close()
        self.closeDatabase()
        
        return result
    
    ###########################################################################
    def create(self, title, category):
        timestamp = datetime.now().isoformat()
        title = title.replace("'", r"\'")
        
        cursor = self.getDatabase().cursor()
        
        query = ("""INSERT 
                INTO entities (title, category, date_created)
                VALUES ('%s', '%s', '%s')""" %
                (title, category, timestamp))
        cursor.execute(query)
        
        if cursor.rowcount > 0:
            result = "Success"
        else:
            result = "NA"
        
        cursor.close()
        self.closeDatabase()
        
        return result
    
    ###########################################################################
    def destroy(self, entity_id):
        entity_id = int(entity_id)
        
        cursor = self.getDatabase().cursor()
        
        query = "DELETE FROM entities WHERE entity_id = %d" % (entity_id)
        cursor.execute(query)
        if cursor.rowcount > 0:
            result = "Success"
        else:
            result = "NA"
        
        cursor.close()
        self.closeDatabase()
        
        return result
    
    ###########################################################################
    def update(self, entity_id, title, category):
        entity_id = int(entity_id)
        
        cursor = self.getDatabase().cursor()
        
        query = ("""UPDATE entities 
                SET title = '%s', category = '%s'
                WHERE entity_id = %d""" % 
                (title, category, entity_id))
        cursor.execute(query)
        if cursor.rowcount > 0:
            result = "Success"
        else:
            result = "NA"
        
        cursor.close()
        self.closeDatabase()
        
        return result
    
    ###########################################################################
    def match(self, query):
        
        cursor = self.getDatabase().cursor()
        
        query = ("""SELECT entity_id, title, category, image
                FROM entities
                WHERE LEFT(title, %d) = '%s'
                ORDER BY title ASC
                LIMIT 0, 10""" % (len(query), query))
        cursor.execute(query)
        
        resultData = cursor.fetchmany(10)
        result = []
        for recordData in resultData:
            record = {}
            record['entity_id'] = recordData[0]
            record['title'] = recordData[1]
            record['category'] = recordData[2]
            record['image'] = recordData[3]
            result.append(record)
        
        cursor.close()
        self.closeDatabase()
            
        return result