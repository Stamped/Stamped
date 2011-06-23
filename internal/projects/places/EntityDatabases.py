#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

__databases = { }

def registerDB(name, factory):
    database = __getDB(name)
    
    if database:
        return database['id']
    else:
        databaseID = len(__databases)
        
        __databases[name] = {
            'factory' : factory, 
            'id' : databaseID, 
        }
        
        return databaseID

def getDBID(name):
    database = __getDB(name)
    
    if database:
        return database['id']
    else:
        return None

def instantiateDB(name):
    database = __getDB(name)
    
    if database:
        return database['factory']()
    else:
        return None

def instantiateAll():
    return (v['factory']() for v in __databases.itervalues())

def __getDB(name):
    name = name.lower().strip()
    
    for k, v in __databases.iteritems():
        if name == k.lower():
            return v
    
    return None

