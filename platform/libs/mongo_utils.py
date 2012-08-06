#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils

def get_db_instances():
    if utils.is_ec2():
        stack = ec2_utils.get_stack()
        members = filter(lambda m: 'db' in m.roles, stack.members)

def run_mongo_cmd(mongo_cmd, transform=True, slave_okay=True, 
                  db='stamped', instance=None, verbose=False, error_okay=False, 
                  offset=0):
    """
        Runs the desired mongo shell command in the context of the given db, 
        on either a random db node in the stack if slave_okay is True or the 
        current primary node if slave_okay is False. If transform is True, 
        the console output of running the given command will be interpreted 
        as JSON and returned as a Python AttributeDict.
        
        If an instance is specified, the command will be run on that instance, instead.
    """
    
    db_instances = get_db_instances()
    assert len(db_instances) > 1
    
    env.user = 'ubuntu'
    env.key_filename = [ 'keys/test-keypair' ]
    env.warn_only = True
    
    cmd_template = "mongo %s --quiet --eval 'printjson(%s);'"
    cmd = cmd_template % (db, mongo_cmd)
    
    if instance is not None:
        db_instances = [ instance ]
    elif not slave_okay:
        primary = get_primary()
        assert primary is not None
        
        db_instances = [ primary ]
    
    hide_args = [ 'stdout', ]
    if not verbose:
        hide_args.append('running')
        hide_args.append('stderr')
        hide_args.append('warnings')
        hide_args.append('aborts')
        hide_args.append('status')
    
    num_db_instances = len(db_instances)
    for i in xrange(num_db_instances):
        instance = db_instances[(i + offset) % num_db_instances]
        
        try:
            with settings(host_string=instance.public_dns_name):
                with hide(*hide_args):
                    result = run(cmd, pty=False, shell=True)
                    
                    if transform:
                        result = re.sub(self.isodate_re, r'\1', result)
                        
                        try:
                            result = utils.AttributeDict(json.loads(result))
                            
                            if not error_okay and 'errmsg' in result:
                                raise Fail(result['errmsg'])
                        except Fail:
                            raise
                        except:
                            if verbose:
                                utils.log("[%s] error interpreting results of mongo cmd on instance '%s' (%s)" % (self, instance, mongo_cmd))
                                utils.printException()
                                utils.log(result)
                            
                            return None
                    
                    return result
        except Fail:
            raise
        except:
            if verbose:
                utils.log("[%s] error running mongo cmd on instance '%s' (%s)" % (self, instance, mongo_cmd))
            raise
    
    return None

def _get_primary(self):
    """
        Returns the current primary db node if one exists, retrying 
        several times in case the replica set is failing over and 
        reelecting a primary. If no primary is found, will raise an 
        Exception.
    """
    
    #utils.log("[%s] attempting to find primary db node" % self)
    maxdelay = 16
    delay = 1
    offset = 0
    
    while True:
        status = self._get_replset_status(offset=offset)
        offset += 1
        
        primaries = filter(lambda m: 1 == m.state, status.members)
        if 0 == len(primaries):
            pprint(dict(status))
            utils.log("[%s] unable to find a primary! retrying..." % self)
            
            if delay > maxdelay:
                msg = "timeout trying to find primary node on stack %s" % self
                utils.log(msg)
                raise Fail(msg)
            
            time.sleep(delay)
            delay *= 2
        elif len(primaries) > 1:
            msg = "stack %s contains more than one primary!" % self
            utils.log(msg)
            raise Fail(msg)
        else:
            primary = primaries[0]
            ip = primary.name.split(':')[0].lower()
            
            for instance in self.db_instances:
                if ip == instance.private_ip_address.lower():
                    return instance
            
            msg = "stack %s contains an unrecognized primary!" % self
            utils.log(msg)
            raise Fail(msg)

def _get_replset_status(self, offset=0):
    status = self.run_mongo_cmd('rs.status()', offset=offset)
    
    if status is not None and 'members' in status:
        status.members = list(utils.AttributeDict(node) for node in status.members)
    
    return status

def _get_replset_conf(self, offset=0):
    status = self.run_mongo_cmd('rs.conf()', offset=offset)
    
    if status is not None and 'members' in status:
        status.members = list(utils.AttributeDict(node) for node in status.members)
    
    return status

