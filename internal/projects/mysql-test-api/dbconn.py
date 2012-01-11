#!/usr/bin/env python

import MySQLdb

class DatabaseConnection:

    def connect(self):
        return MySQLdb.connect(user='root',db='stamped_api')



class MySQLConnection:

    def __init__(self):
        self.database = self.connectDatabase()
        
    ###########################################################################
    def connectDatabase(self):
        return MySQLdb.connect(user='root',db='stamped_api')
        
    ###########################################################################
    def getDatabase(self):
        if not self.database.open:
            self.database = DatabaseConnection().connect()
        return self.database
    
    ###########################################################################
    def closeDatabase(self):
        self.database.commit()
        self.database.close()
