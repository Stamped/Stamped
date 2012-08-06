#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import os, sys, pymongo, json

from optparse   import OptionParser
from utils      import lazyProperty
from datetime   import *
from errors     import Fail
from libs.ec2_utils import is_ec2, get_db_nodes, get_stack
from servers.analytics.core.SimpleDBConnection import SimpleDBConnection

from api.db.mongodb.MongoLogsCollection import MongoLogsCollection


def parseCommandLine():
    usage   = "Usage: %prog [options] command [args]"
    parser  = OptionParser(usage=usage)
    
    parser.add_option("-f", "--form", action="store_true", dest="show_form", 
        default=False, help="Include user-submitted input form in results")
    
    parser.add_option("-s", "--stack", default=None, type="string",
        action="store", dest="stack", help="stack to pull logs from")
    
    parser.add_option("-u", "--user-id", dest="user_id", 
        default=None, type="string", help="Filter results on user id")
    
    parser.add_option("-m", "--method", dest="method", 
        default=None, type="string", help="Request method (POST, GET, or ASYNC)")
    
    parser.add_option("-l", "--limit", dest="limit", 
        default=10, type="int", help="Limit number of results returned")
    
    parser.add_option("-p", "--path", dest="path", 
        default=None, type="string", help="Filter results on url path")
    
    parser.add_option("-c", "--code", dest="code", 
        default=None, type="int", help="Filter results on status code")

    parser.add_option("-S", "--slow", dest="slow", action="store",
        default=None, type="int", help="Filter results that took longer than n seconds")


    (options, args) = parser.parse_args()
    
    if is_ec2() or options.stack:
        logger_nodes = get_db_nodes('logger')
        if len(logger_nodes) == 0:
            print("Warning: No instances exist on stack 'logger'")
            return options
        if options.stack is None:
            options.stack = 'bowser'

    return options

def main():
    # parse commandline
    options     = parseCommandLine()
    options     = options.__dict__
    
    user_id     = options.pop('user_id', None)
    limit       = options.pop('limit', 10)
    path        = options.pop('path', None)
    method      = options.pop('method', None)
    code        = options.pop('code', None)
    slow        = options.pop('slow', None)
    show_form   = options.pop('show_form',False)

    conn = SimpleDBConnection()
    
    query_dict = {}
    
    if user_id is not None:
        query_dict['uid'] = user_id
    
    if path is not None:
        query_dict['uri'] = path
        
    if method is not None:
        query_dict['mtd'] = method
        
    if code is not None:
        query_dict['cde'] = code
        
    if slow is not None:
        min_duration = slow
    else:
        min_duration = None
    
    logs = conn.query('bowser', query_dict, limit=limit, duration = min_duration)
    
    for i in xrange(len(logs)):
        print 
        print
        
        if 'uri' in logs[i] and 'mtd' in logs[i]:
            node = ''
            if 'nde' in logs[i]:
                node = '(%s)' % logs[i]['nde']
            print '%-10s %s %s %s' % (i+1, logs[i]['mtd'], logs[i]['uri'], node)
        else:
            print i+1
        
        print "-----------------------------------------"
        if 'bgn' in logs[i]:
            begin_utc = logs[i]['bgn']
            print '%-10s %s' % ('Begin:', begin_utc)
            
        if 'end' in logs[i]:
            end_utc = logs[i]['end']
            print '%-10s %s' % ('End:', end_utc)
        
        if 'cid' in logs[i]:
            print '%-10s %s' % ('Client:', logs[i]['cid'])
        
        if 'uid' in logs[i]:
            print '%-10s %s' % ('User:', logs[i]['uid'])
        
        print "Form:"
        for key in logs[i]:
            if 'frm' in key:
                print '\t%-10s %s' % (key[4:], logs[i][key])
            
    

if __name__ == '__main__':
    main()

        
            
            
            
