#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import MySQLdb as mysqldb

from AEntityDB import AEntityDB
from threading import Lock

class MySQL():
    USER  = 'root'
    PASS  = None
    DB    = 'stamped_test'
    DESC  = 'MySQL:%s@%s.entities' % (USER, DB)
    
    def __init__(self):
        self._desc = self.DESC
        self._lock = Lock()
        self._setup()
    
    def _getConnection(self):
        return mysqldb.connect(user=self.USER, db=self.DB)
    
    def commit(self):
        if self.db:
            self.db.commit()
            self.db.close()
            self.db = None
    
    def _setup(self, reset=False):
        def _checkDB(cursor):
            cursor.execute("""SELECT SCHEMA_NAME 
                FROM INFORMATION_SCHEMA.SCHEMATA 
                WHERE SCHEMA_NAME = '%s'""" % self.DB)
            if cursor.rowcount > 0:
                return True
            else:
                return False
    
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
        if not self._transact(_checkDB) or reset == True:
            self.db = mysqldb.connect(user=self.USER)
            self._transact(_createDB)
            self.commit()
            
            self._transact(_createTables)
        else:
            self.db = self._getConnection()
    
    def _transact(self, func, returnDict=False):
        retVal = None
        
        self._lock.acquire()
        try:
            if self.db is None:
                self.db = self._getConnection()
            
            if returnDict:
                cursor = self.db.cursor(cursorclass=mysqldb.cursors.DictCursor)
            else:
                cursor = self.db.cursor()
            
            retVal = func(cursor)
            if retVal is not None and (type(retVal) is not bool or retVal == True):
                self.db.commit()
            else:
                self.db.rollback()
            
            cursor.close()
        finally:
            self._lock.release()
        
        return retVal
