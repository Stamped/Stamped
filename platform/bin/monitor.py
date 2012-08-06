#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import libs.ec2_utils, logs, re, sys, time, urllib2, utils

from libs.notify    import StampedNotificationHandler
from optparse       import OptionParser
from pprint         import pprint

is_ec2 = utils.is_ec2()

class MonitorException(Exception):
    def __init__(self, desc, detail=None, email=True, sms=False):
        Exception.__init__(self, desc)
        self.detail = None
        self.email  = email
        self.sms    = sms

class Monitor(object):
    
    def __init__(self, options=None):
        self.handler  = StampedNotificationHandler()
        self.status   = { }
        self._info    = None
        
        if options is not None:
            self.options = options
        else:
            self.options = utils.AttributeDict({
                'stack'     : None, 
                'time'      : 10, 
                'noop'      : False, 
                'verbose'   : False, 
            })
    
    def update(self, force=False):
        if self._info is None or force:
            self._info = libs.ec2_utils.get_stack(stack=self.options.stack)
            
            if self._info is None:
                utils.log("error retrieving stack data from AWS")
    
    def run(self):
        while True:
            self.update(force=True)
            self.ping()
        
        time.sleep(self.options.time)
    
    def ping(self):
        self.update()
        
        if self.options.stack:
            mich = None
        else:
            mich = self._info.instance.instance_id
        
        for node in self._info.nodes:
            node_status = 1
            
            # don't try to monitor myself
            if node.instance_id == mich:
                continue
            
            try:
                utils.logRaw("pinging node '%s.%s'..." % (node.stack, node.name), True)
                
                if 'apiServer' in node.roles:
                    self._try_ping_apiServer(node)
                
                if 'webServer' in node.roles:
                    self._try_ping_webServer(node)
                
                if 'db' in node.roles:
                    self._try_ping_db(node)
                
                utils.logRaw("success!\n")
            except Exception, e:
                node_status = -1
                unexpected  = False
                detail      = None
                
                if isinstance(e, MonitorException):
                    logs.error("monitor error: %s" % e)
                    utils.log ("monitor error: %s" % e)
                    detail = e.detail
                else:
                    logs.error("unexpected error: %s" % e)
                    utils.log ("unexpected error: %s" % e)
                    unexpected = True
                
                # only send a notification if this node's status has changed since 
                # the last time we checked, so we don't get duplicate notifications 
                # related to the same incident.
                try:
                    notify = (-1 != self.status[node.instance_id])
                except KeyError:
                    notify = False
                
                if notify and not self.options.noop:
                    subject = '%s.%s error' % (node.stack, node.name)
                    message = str(e)
                    
                    if unexpected or e.email:
                        if detail is not None:
                            message = "%s\n\n--- detail ---\n\n%s" % (message, detail)
                        
                        self.handler.email(subject, message)
                    
                    if unexpected or e.sms:
                        self.handler.sms(subject, message)
            
            self.status[node.instance_id] = node_status
    
    def _try_ping_webServer(self, node):
        url = 'http://%s/index.html' % node.public_dns
        retries = 0
        
        while retries < 5:
            try:
                response = urllib2.urlopen(url)
            except urllib2.HTTPError, e:
                utils.log(url)
                utils.printException()
            else:
                return
            
            retries += 1
            time.sleep(retries * retries)
        
        error = "unable to ping web server at '%s.%s'" % (node.stack, node.name)
        raise MonitorException(error, email=True, sms=True)
    
    def _try_ping_apiServer(self, node):
        url = 'https://%s/v0/ping.json' % node.public_dns_name
        retries = 0
        
        while retries < 5:
            try:
                response = urllib2.urlopen(url)
            except urllib2.HTTPError, e:
                utils.log(url)
                utils.printException()
            else:
                return
            
            retries += 1
            time.sleep(retries * retries)
        
        error = "unable to ping api server at '%s.%s'" % (node.stack, node.name)
        raise MonitorException(error, email=True, sms=True)
    
    def _try_ping_db(self, node):
        cmd_template = "mongo --quiet %s:27017/admin --eval 'printjson(%s);'"
        
        # ensure that the server and replica set and both responding and healthy
        mongo_cmds = [
            'db.serverStatus()', 
            'rs.status()', 
        ]
        
        for mongo_cmd in mongo_cmds:
            dns = node.private_ip_address if is_ec2 else node.public_dns_name
            cmd = cmd_template % (dns, mongo_cmd)
            
            retries = 0
            
            while retries < 5:
                logs.debug(cmd)
                utils.log(cmd)
                
                ret = utils.shell(cmd)
                
                if 0 == ret[1]:
                    break
                
                retries += 1
                time.sleep(retries * retries)
            
            if 0 != ret[1]:
                error = "unable to reach db server at '%s.%s'" % \
                         (node.stack, node.name)
                
                raise MonitorException(error, detail=ret[0], email=True, sms=True)
            
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
    
    if options.stack is None and not utils.is_ec2():
        utils.log("error: if this program isn't run from an EC2 instance, you must specify a stack to monitor")
        parser.print_help()
        sys.exit(1)
    
    return (options, args)

def main():
    options, args = parseCommandLine()
    
    Monitor(options).run()

if __name__ == '__main__':
    main()

