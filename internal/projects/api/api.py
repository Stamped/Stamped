#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import sys, thread
import MySQLdb
from Entity import Entity

# import specific databases
from db.mysql.MySQLEntityDB import MySQLEntityDB






def main():

    db = MySQLEntityDB()

    entity = Entity({
        'title' : 'Little Owl',
        'category' : 'Restaurant'
        })
    # print entity
    

    entityID = db.addEntity(entity)
    print entityID
    
    entityCopy = db.getEntity(entityID)
    print entityCopy
    
    entityCopy['title'] = 'Little Owl 2'
    print entityCopy
    
    db.updateEntity(entityCopy)
    
    #db.removeEntity(entityID)
    
    db.addEntities([entity, entityCopy])

# where all the magic starts
if __name__ == '__main__':
    main()
