#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import os, sys, pymongo, json
from optparse import OptionParser
from utils import lazyProperty
from dateutil import tz

from errors import Fail

from db.mongodb.MongoLogsCollection import MongoLogsCollection
    
@lazyProperty
def _logsDB(self):
    return MongoLogsCollection()

def parseCommandLine():
    usage   = "Usage: %prog [options] command [args]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--headers", action="store_true", dest="show_headers", 
        default=False, help="Include HTTP headers in results")
    
    parser.add_option("-f", "--form", action="store_true", dest="show_form", 
        default=False, help="Include user-submitted input form in results")
    
    parser.add_option("-o", "--output", action="store_true", dest="show_output", 
        default=False, help="Include JSON result in results")
    
    parser.add_option("-e", "--errors", action="store_true", dest="show_errors", 
        default=False, help="Only display errors in results")
    
    parser.add_option("-u", "--user-id", dest="user_id", 
        default=None, type="string", help="Filter results on user id")
    
    parser.add_option("-l", "--limit", dest="limit", 
        default=10, type="int", help="Limit number of results returned")
    
    parser.add_option("-v", "--level", dest="level", 
        default='info', type="string", help="Set log level for display (debug, info, warning, error, or critical)")
    
    parser.add_option("-p", "--path", dest="path", 
        default=None, type="string", help="Filter results on url path")
    
    (options, args) = parser.parse_args()

    return options

def main():
    # parse commandline
    options = parseCommandLine()
    options = options.__dict__

    user_id = options.pop('user_id', None)
    limit   = options.pop('limit', 10)
    errors  = options.pop('show_errors', False)
    path    = options.pop('path', False)

    ### TODO: Get rid of dateutil dependency
    est = tz.gettz('America/New York')
    utc = tz.gettz('UTC')

    if options['level'].lower() == 'debug':
        levels = ['debug', 'info', 'warning', 'error', 'critical']
    elif options['level'].lower() == 'info':
        levels = ['info', 'warning', 'error', 'critical']
    elif options['level'].lower() == 'warning':
        levels = ['warning', 'error', 'critical']
    elif options['level'].lower() == 'error':
        levels = ['error', 'critical']
    else:
        levels = ['critical']

    logs = MongoLogsCollection().getLogs(userId=user_id, limit=limit, errors=errors, path=path)
    for i in xrange(len(logs)):
        print 
        print

        if 'path' in logs[i] and 'method' in logs[i]:
            print '%-10s %s %s' % (i+1, logs[i]['method'], logs[i]['path'])
        else:
            print i+1

        if 'result' in logs[i] and logs[i]['result'] != '200':
            print '%-10s %s ERROR' % ('', logs[i]['result'])
        print '-' * 40

        if 'request_id' in logs[i]:
            print '%-10s %s' % ('ID:', logs[i]['request_id'])

        if 'begin' in logs[i]:
            begin = logs[i]['begin'].replace(tzinfo=utc)
            print '%-10s %s UTC / %s EST' % ('Begin:', begin, begin.astimezone(est))
            
        if 'finish' in logs[i]:
            finish = logs[i]['finish'].replace(tzinfo=utc)
            print '%-10s %s UTC / %s EST' % ('Finish:', finish, finish.astimezone(est))
            
        if 'token' in logs[i]:
            print '%-10s %s' % ('Token:', logs[i]['token'])
            
        if 'client_id' in logs[i]:
            print '%-10s %s' % ('Client:', logs[i]['client_id'])
            
        if 'user_id' in logs[i]:
            print '%-10s %s' % ('User:', logs[i]['user_id'])
            
        if 'headers' in logs[i] and options['show_headers']:
            print '%-10s %s' % ('Headers:', logs[i]['headers'])
            
        if 'form' in logs[i] and options['show_form']:
            j = json.dumps(logs[i]['form'], indent=4)
            prefix = 'Form:'
            for line in j.splitlines():
                print '%-10s %s' % (prefix, line)
                prefix = ''
            
        if 'output' in logs[i] and options['show_output']:
            j = json.dumps(json.loads(logs[i]['output']), indent=4)
            prefix = 'Output:'
            for line in j.splitlines():
                print '%-10s %s' % (prefix, line)
                prefix = ''

        if 'log' in logs[i]:
            prefix = 'Logs:'
            for log in logs[i]['log']:
                if log[1] in levels:
                    print '%-10s %s | %-30s | %s' % (prefix, log[0].strftime('%H:%M:%S'), log[2], log[3])
                    prefix = ''

    print
    

if __name__ == '__main__':
    main()

