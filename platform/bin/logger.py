#!/usr/bin/env python

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

from db.mongodb.MongoLogsCollection import MongoLogsCollection

LOG_COLLECTION_SIZE         = 1024*1024*1024   # 1 gb
LOG_LOCAL_COLLECTION_SIZE   = 1024*1024*100    # 100 mb

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
    
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", 
        default=False, help="Set verbosity of logs")
    
    parser.add_option("-s", "--stack", default=None, type="string",
        action="store", dest="stack", help="stack to pull logs from")
    
    parser.add_option("-u", "--user-id", dest="user_id", 
        default=None, type="string", help="Filter results on user id")

    parser.add_option("-i", "--request-id", dest="request_id",
        default=None, type="string", help="Filter on request id")
    
    parser.add_option("-m", "--method", dest="method", 
        default=None, type="string", help="Request method (POST, GET, or ASYNC)")
    
    parser.add_option("-l", "--limit", dest="limit", 
        default=10, type="int", help="Limit number of results returned")
    
    parser.add_option("-p", "--path", dest="path", 
        default=None, type="string", help="Filter results on url path")
    
    parser.add_option("-t", "--severity", dest="severity", 
        default=None, type="string", help="Filter results on severity (debug, info, warning, error, critical)")
    
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
        instance_name = '%s.%s' % (logger_nodes[0]['stack'], logger_nodes[0]['name'])
        utils.init_log_db_config(instance_name)
        if options.stack is None:
            options.stack = get_stack().instance.stack

    return options

def main():
    # parse commandline
    options     = parseCommandLine()
    options     = options.__dict__
    
    user_id     = options.pop('user_id', None)
    request_id  = options.pop('request_id', None)
    limit       = options.pop('limit', 10)
    errors      = options.pop('show_errors', False)
    path        = options.pop('path', False)
    severity    = options.pop('severity', None)
    verbose     = options.pop('verbose', False)
    method      = options.pop('method', None)
    code        = options.pop('code', None)
    stack       = options.pop('stack', None)
    slow        = options.pop('slow', None)
    
    if severity not in ['debug', 'info', 'warning', 'error', 'critical']:
        severity = None
    
    if verbose:
        levels = ['debug', 'info', 'warning', 'error', 'critical']
    else:
        levels = ['info', 'warning', 'error', 'critical']

    logsCollection = MongoLogsCollection(stack)
    if not logsCollection.isCapped:
        size = LOG_COLLECTION_SIZE if is_ec2() else LOG_LOCAL_COLLECTION_SIZE
        logsCollection.convertToCapped(size)
    logs = logsCollection.getLogs(userId=user_id, requestId=request_id, limit=limit, errors=errors,
                                    path=path, severity=severity, method=method, code=code, slow=slow)
    for i in xrange(len(logs)):
        print 
        print
        
        if 'path' in logs[i] and 'method' in logs[i]:
            node = ''
            if 'node' in logs[i]:
                node = '(%s)' % logs[i]['node']
            print u'%-10s %s %s %s' % (i+1, logs[i]['method'], logs[i]['path'], node)
        else:
            print i+1
        
        if 'result' in logs[i] and logs[i]['result'] != '200':
            print u'%-10s %s ERROR' % ('', logs[i]['result'])
        print '-' * 40
        
        if 'request_id' in logs[i]:
            print u'%-10s %s' % ('ID:', logs[i]['request_id'])
        
        if 'begin' in logs[i]:
            begin_utc = logs[i]['begin']
            begin_est = begin_utc - timedelta(hours=4)
            print u'%-10s %s' % ('Begin:', begin_est.strftime("%a %b %d %H:%M:%S.%f"))
            
            if 'finish' in logs[i]:
                duration = logs[i]['finish'] - begin_utc
                print u'%-10s %s' % ('Duration:', duration)
        
        if 'token' in logs[i]:
            print u'%-10s %s' % ('Token:', logs[i]['token'])
        
        if 'client_id' in logs[i]:
            print u'%-10s %s' % ('Client:', logs[i]['client_id'])
        
        if 'user_id' in logs[i]:
            print u'%-10s %s' % ('User:', logs[i]['user_id'])
        
        if 'headers' in logs[i] and options['show_headers']:
            print u'%-10s %s' % ('Headers:', logs[i]['headers'])
        
        if 'form' in logs[i] and options['show_form']:
            j = json.dumps(logs[i]['form'], indent=4)
            prefix = 'Form:'
            for line in j.splitlines():
                print u'%-10s %s' % (prefix, line)
                prefix = ''
        
        if 'output' in logs[i] and options['show_output']:
            j = json.dumps(json.loads(logs[i]['output']), indent=4)
            prefix = 'Output:'
            for line in j.splitlines():
                print u'%-10s %s' % (prefix, line)
                prefix = ''
        
        if 'log' in logs[i]:
            prefix = 'Logs:'
            for log in logs[i]['log']:
                if log[1] in levels:
                    try:
                        # TODO: eventually get rid of the if condition and always assume len() == 6.  Must wait for
                        # old logs to flush out
                        if len(log) == 6:
                            print u"{0:10} {1} | {2:25}:{3:>5} | {4:25} | {5}".format(prefix, log[0].strftime('%H:%M:%S'), log[2], int(log[3]), log[4], log[5])
                        elif len(log) == 5:
                            print u'%-10s %s | %-30s | %-5s | %s' % (prefix, log[0].strftime('%H:%M:%S'), log[2], log[3], log[4])
                        else:
                            print u'%-10s %s | %-30s | %s' % (prefix, log[0].strftime('%H:%M:%S'), log[2], log[3])

                    except:
                        utils.printException()
                    
                    prefix = ''
        
        if 'stack_trace' in logs[i]:
            print '-' * 40
            print logs[i]['stack_trace']
    
    print
    

if __name__ == '__main__':
    main()

