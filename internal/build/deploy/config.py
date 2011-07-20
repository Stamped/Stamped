#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import utils

def getInstances():
    replSetName = 'stamped-dev-01'
    dbs = [
        {
            'name' : 'db0', 
            'roles' : [ 'db', ], 
            'mongodb' : {
                'replSet' : replSetName, 
                'port' : 30000, 
            }, 
        }, 
        {
            'name' : 'db1', 
            'roles' : [ 'db', ], 
            'mongodb' : {
                'replSet' : replSetName, 
                'port' : 32000, 
            }, 
        }, 
        #{
        #    'name' : 'db2', 
        #    'roles' : [ 'db', ], 
        #    'mongodb' : {
        #        'replSet' : replSetName, 
        #        'port' : 34000, 
        #    }, 
        #}, 
    ]
    
    servers = [
        {
            'name' : 'dev0', 
            'roles' : [ 'webServer', 'replSetInit', ], 
            'port' : '5000', 
            
            'replSet' : {
                '_id' : replSetName, 
                'members' : [ ], 
            }, 
        }, 
    ]
    
    instances = [ ]
    for instance in dbs:
        instances.append(instance)
    
    for instance in servers:
        if 'replSet' in instance:
            assert 'replSetInit' in instance['roles']
            members = instance['replSet']['members']
            
            for index in xrange(len(dbs)):
                db = dbs[index]
                
                members.append({
                    '_id'  : index, 
                    'host' : 'localhost:%s' % db['mongodb']['port'], 
                })
        
        instances.append(instance)
    return instances

