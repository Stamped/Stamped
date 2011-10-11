#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import init
import logs, re, sys, time, urllib2, utils

from libs.notify    import StampedNotificationHandler
from libs.EC2Utils  import EC2Utils
from optparse       import OptionParser

is_ec2 = utils.is_ec2()

class MonitorException(Exception):
    def __init__(self, desc, detail=None, email=True, sms=False):
        Exception.__init__(self, desc)
        self.detail = None
        self.email  = email
        self.sms    = sms

def try_ping_webServer(node):
    url = 'https://%s/v0/entities/show.json' % node.public_dns
    
    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        if e.code == 401:
            return
    
    raise MonitorException("unable to ping api server at '%s.%s'" % (node.stack, node.name), 
                           email=True, sms=True)

def try_ping_db(node):
    cmd_template = "mongo %s:27017/admin --eval 'printjson(%s);'"
    
    # ensure that the server and replica set and both responding and healthy
    mongo_cmds = [
        'db.serverStatus()', 
        'rs.status()', 
    ]
    
    for mongo_cmd in mongo_cmds:
        dns = node.private_dns if is_ec2 else node.public_dns
        cmd = cmd_template % (dns, mongo_cmd)
        logs.debug(cmd)
        
        ret = utils.shell(cmd)
        
        if 0 != ret[1]:
            error = "unable to reach db server at '%s.%s'" % \
                     (node.stack, node.name)
            
            raise MonitorException(error, email=True, sms=True)
        
        if re.match('.*"ok"[ \t]*:[ \t]*1.*', ret[0], re.DOTALL) is None:
            error = "db server '%s.%s' returned invalid status for cmd '%s'" % \
                     (node.stack, node.name, mongo_cmd)
            
            raise MonitorException(error, detail=ret[0], email=True, sms=True)

def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-s", "--stack", default=None, action="store", type="string", 
        help="stack to monitor (defaults to whatever stack the local AWS instance belongs to)")
    
    parser.add_option("-t", "--time", default=10, action="store", type="int", 
        help="polling interval (in seconds)")
    
    parser.add_option("-n", "--noop", default=False, action="store_true", 
        help="don't send any notifications; just monitor and report to stdout")
    
    parser.add_option("-v", "--verbose", default=False, action="store_true", 
        help="enable verbose logging")
    
    (options, args) = parser.parse_args()
    
    if options.time < 0:
        utils.log("invalid time parameter")
        parser.print_help()
        sys.exit(1)
    
    return (options, args)

def main():
    options, args = parseCommandLine()
    
    handler  = StampedNotificationHandler()
    ec2utils = EC2Utils()
    
    status = { }
    
    while True:
        info = ec2utils.get_stack_info(stack=options.stack)
        
        if info is None:
            utils.log("unable to obtain stack data!")
        else:
            if options.stack:
                mich = None
            else:
                mich = info.instance.id
            
            for node in info.nodes:
                node_status = 1
                
                # don't try to monitor myself
                if node.id == mich:
                    continue
                
                try:
                    utils.logRaw("pinging node '%s.%s'..." % (node.stack, node.name), True)
                    
                    if 'webServer' in node.roles:
                        try_ping_webServer(node)
                    
                    if 'db' in node.roles:
                        try_ping_db(node)
                    
                    utils.logRaw("success!\n")
                except Exception, e:
                    raise
                    
                    node_status = -1
                    unexpected  = False
                    detail      = None
                    
                    if isinstance(e, MonitorException):
                        logs.error("monitor error: %s" % e)
                        detail = e.detail
                    else:
                        logs.error("unexpected error: %s" % e)
                        unexpected = True
                    
                    # only send a notification if this node's status has changed since 
                    # the last time we checked, so we don't get duplicate notifications 
                    # related to the same incident.
                    if (not options.noop) and (node.id not in status or status[node.id] != -1):
                        subject = '%s.%s error' % (node.stack, node.name)
                        message = str(e)
                        
                        if unexpected or e.email:
                            if detail is not None:
                                message = "%s\n\n--- detail ---\n\n%s" % (message, detail)
                            
                            handler.email(subject, message)
                        
                        if unexpected or e.sms:
                            handler.email(subject, message)
                
                status[node.id] = node_status
        
        time.sleep(options.time)

if __name__ == '__main__':
    main()

