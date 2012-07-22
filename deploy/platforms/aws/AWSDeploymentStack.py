#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import config, json, pickle, os, re, string, time, utils
import AWSDeploymentPlatform

from ADeploymentStack       import ADeploymentStack
from AWSInstance            import AWSInstance
from errors                 import Fail
from utils                  import lazy_property

from boto.ec2.elb           import ELBConnection
from boto.ec2.connection    import EC2Connection
from boto.ec2.address       import Address
from boto.exception         import EC2ResponseError

from collections            import defaultdict
from gevent.pool            import Pool
from pprint                 import pprint
from fabric.operations      import *
from fabric.api             import *
import fabric.contrib.files as fabricfiles

class AWSDeploymentStack(ADeploymentStack):
    
    def __init__(self, name, system, instances=None, db_stack=None):
        ADeploymentStack.__init__(self, name, system)
        
        self.commonOptions = system.commonOptions
        self._pool = Pool(64)
        
        if instances is None:
            instances = config.getInstances()
            
            """
            for instance in instances:
                if self.system.options.restore is not None and 'raid' in instance:
                    instance['raid']['restore'] = self.system.options.restore
            """
        
        for instance in instances:
            # Skip database nodes if db_stack is specified
            if db_stack is not None:
                if 'db' in instance['roles']:
                    print 'Skipping db node: %s' % instance['name']
                    continue
                instance['db_stack'] = db_stack
            
            awsInstance = AWSInstance(self, instance)
            self.instances.append(awsInstance)
        
        self.isodate_re = re.compile('ISODate\(([^)]+)\)')
        env.user = 'ubuntu'
        env.key_filename = [ 'keys/test-keypair' ]
    
    @property
    def conn(self):
        return self.system.conn
    
    @property
    def crawler_instances(self):
        return self._getInstancesByRole('crawler')
    
    @property
    def test_instances(self):
        return self._getInstancesByRole('test')
    
    @property
    def db_instances(self):
        return self._getInstancesByRole('db')
    
    @property
    def api_server_instances(self):
        return self._getInstancesByRole('apiServer')
    
    @property
    def web_server_instances(self):
        return self._getInstancesByRole('webServer')
    
    @property
    def work_server_instances(self):
        return self._getInstancesByRole('work')
    
    @property
    def mem_server_instances(self):
        return self._getInstancesByRole('mem')
    
    def create(self):
        utils.log("[%s] creating %d instances" % (self, len(self.instances)))
        
        for instance in self.instances:
            self._pool.spawn(instance.create)
        
        self._pool.join()
        utils.log("[%s] done creating %d instances" % (self, len(self.instances)))

        # initialize replica set
        self.repair()
    
    def _get_initial_replica_set_config(self):
        db_instances = self.db_instances
        assert len(db_instances) >= 1
        if len(db_instances) == 1:
            utils.log("[%s] warning found only 1 db instance (at least 2 needed for a valid replica set)" % (self, ))
        
        replica_set_members = []
        replica_set = None
        
        for instance in db_instances:
            replica_set = instance.config.mongodb.replSet
            replica_set_members.append({
                "_id": len(replica_set_members), 
                "host": instance.private_ip_address
            })
        
        return {
            "_id" : replica_set, 
            "members" : replica_set_members, 
        }
    
    def backup(self):
        db_instances = self.db_instances
        assert len(db_instances) > 1
        
        replica_set_members = []
        replica_set = None
        
        env.user = 'ubuntu'
        env.key_filename = [ 'keys/test-keypair' ]
        
        for instance in db_instances:
            with settings(host_string=instance.public_dns_name):
                with cd("/stamped"):
                    sudo('. bin/activate && python /stamped/bootstrap/bin/ebs_backup.py', pty=False)
    
    def update(self, *args, **kwargs):
        force = (len(args) >= 1 and args[0] == 'force')
        utils.log("[%s] updating %d instances" % (self, len(self.instances)))

        branch = kwargs.get('branch', None)

        cmd = "sudo /bin/bash -c '. /stamped/bin/activate && python /stamped/bootstrap/bin/update.py%s%s'" %\
              (" --force" if force else "", " --branch %s" % branch if branch is not None else "")
        pp  = []
        separator = "-" * 80
        
        if force:
            # update all instances in parallel
            for instance in self.instances:
                pp.append((instance, utils.runbg(instance.public_dns_name, env.user, cmd)))
            
            for instance, p in pp:
                ret = p.wait()
        else:
            # update all instances synchronously, removing them one-at-a-time from 
            # their respective ELBs and readding them once we're sure that the 
            # update was applied successfully and the resulting instance is healthy
            for instance in self.instances:
                utils.log()
                utils.log(separator)
                utils.log("[%s] UPDATING %s" % (self, instance))
                
                # TODO: this logic doesn't account for the case where an instance 
                # may belong to multiple ELBs. NOTE that this scenario will never 
                # arise in our current stack architecture, but I'm leaving this 
                # note in here just in case that assumption changes in the future.
                elb = self._get_elb(instance)
                
                # only deregister instance if it belongs to a non-trivial ELB
                deregister = (elb is not None) # and len(elb.instances) > 1)
                
                if deregister:
                    utils.log("[%s] temporarily deregistering %s from %s" % (self, instance, elb))
                    instances = elb.deregister_instances([ instance.instance_id ])
                    
                    # TODO: this sleep shouldn't be necessary since the instance 
                    # is definitely removed from the ELB at this point, but without 
                    # pausing, the ELB seems to ignore performing a new health check 
                    # before successfully re-registering the instance. pausing here 
                    # effectively ensures that the state of the instance will be 
                    # set to OutOfService s.t. the health check must be passed 
                    # before the instance is considered InService after instance 
                    # re-registration.
                    # 
                    # NOTE: an additional advantage of pausing here is that the 
                    # instance update script may restart certain daemons, and a 
                    # small pause after removing the instance from its ELB should  
                    # give the instance's daemons a chance to finish handling any 
                    # in-progress requests (e.g., gunicorn / nginx).
                    time.sleep(10)
                
                # apply update synchronously
                with settings(host_string=instance.public_dns_name):
                    try:
                        result = run(cmd, pty=False, shell=True)
                        status = result.return_code
                    except Exception:
                        # if run fails, ask the user whether or not to continue instead of aborting
                        status = 1
                
                if 0 != status:
                    utils.log("[%s] warning: failure updating %s" % (self, instance))
                    
                    confirmation = utils.get_input()
                    if deregister and (confirmation == 'n' or confirmation == 'a'):
                        utils.log("[%s] warning: not re-registering %s with %s" % \
                                  (self, instance, elb))
                    
                    if confirmation == 'n':
                        continue
                    elif confirmation == 'a':
                        return
                
                if deregister:
                    utils.log("[%s] %s re-registering with %s" % (self, instance, elb))
                    elb.register_instances([ instance.instance_id ])
                    
                    utils.log("[%s] %s is waiting to come back online..." % (self, instance))
                    
                    # TODO: infer max timeout from health check settings
                    timeout = 600
                    delay   = 2
                    
                    # wait for the instance to come back online with the ELB
                    while True:
                        try:
                            health = elb.get_instance_health([ instance.instance_id ])[0]
                            
                            if health.state == 'InService':
                                utils.log("[%s] %s is back online with elb %s..." % \
                                          (self, instance, elb))
                                break
                        except Exception, e:
                            health = utils.AttributeDict(dict(
                                state = "error retrieving health", 
                                description = str(e), 
                            ))
                        
                        utils.log("[%s] %s is '%s' (%s)" % (self, instance, health.state, health.description))
                        
                        # instance is not in service yet; sleep for a bit before retrying
                        timeout -= delay
                        if timeout <= 0:
                            utils.log("[%s] %s timed out with elb %s (state=%s, desc=%s)..." % \
                                      (self, instance, elb, health.state, health.description))
                            
                            confirmation = utils.get_input()
                            if confirmation == 'n' or confirmation == 'a':
                                return
                            else:
                                break
                        
                        time.sleep(delay)
                
                utils.log("[%s] successfully updated %s" % (self, instance))
        
        utils.log()
        utils.log("[%s] done updating %d instances" % (self, len(self.instances)))
    
    def run_mongo_cmd(self, mongo_cmd, transform=True, slave_okay=True, 
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
        
        db_instances = self.db_instances
        assert len(db_instances) > 1
        
        env.user = 'ubuntu'
        env.key_filename = [ 'keys/test-keypair' ]
        env.warn_only = True
        
        cmd_template = "mongo %s --quiet --eval 'printjson(%s);'"
        cmd = cmd_template % (db, mongo_cmd)
        
        if instance is not None:
            db_instances = [ instance ]
        elif not slave_okay:
            primary = self._get_primary()
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
                            except Exception:
                                if verbose:
                                    utils.log("[%s] error interpreting results of mongo cmd on instance '%s' (%s)" % (self, instance, mongo_cmd))
                                    utils.printException()
                                    utils.log(result)
                                
                                return None
                        
                        return result
            except Fail:
                raise
            except Exception:
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
        delay    = 1
        offset   = 0
        
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
    
    def _find_db_node(node):
        for instance in self.db_instances:
            if instance.name == node or instance.instance_id == node:
                return instance
        
        return None
    
    def force_db_primary_change(self, *args):
        if 0 == len(args):
            utils.log("must specify instance to make primary (either node name or instance-id)")
            return
        
        db_instance = None
        force = (len(args) > 1 and args[1] == 'force')
        db_instance = self._find_db_node(args[0])
        
        if db_instance is None:
            utils.log("[%s] error: unavailable to find db instance '%s'" % (self, args[0]))
            return
        
        conf = self._get_replset_conf()
        highest_nodes = []
        priority = 1
        
        # find highest existing priority in replica set config
        for node in conf.members:
            if 'priority' in node:
                cur_priority = node['priority']
                
                if cur_priority > priority:
                    priority = cur_priority
                    highest_nodes = [ node.host ]
                elif cur_priority == priority:
                    highest_nodes.append(node.host)
        
        found = False
        for node in conf.members:
            ip = node.host.split(':')[0].lower()
            
            if ip == db_instance.private_ip_address:
                if 1 == len(highest_nodes) and node.host in highest_nodes:
                    utils.log("[%s] warning: node %s already set to highest priority in replica set %s" % 
                              (self, db_instance, conf._id))
                    return
                else:
                    node['priority'] = priority + 1
                    found = True
                    break
         
        if not found:
            utils.log("[%s] error: unable to find db instance '%s'" % (self, arg))
            return
        
        utils.log()
        utils.log("[%s] attempting to reconfigure replica set '%s'" % (self, conf._id))
        conf['version'] += 1
        conf = dict(conf)
        conf['members'] = list(dict(m) for m in conf['members'])
        pprint(conf)
        
        # TODO: if force is true and a primary exists, step down current primary first?
        # TODO: test sync'ing on dev stack during stress
        confs = json.dumps(conf)
        ret   = self.run_mongo_cmd('rs.reconfig(%s, {force : %s})' % 
                                   (confs, str(force).lower()), slave_okay=force)
        pprint(ret)
    
    def remove_db_node(self, *args):
        if 0 == len(args):
            utils.log("must specify an instance to remove (either node name or instance-id)")
            return
        
        db_instance = self._find_db_node(args[0])
        force = (len(args) > 1 and args[1] == 'force')
        
        # TODO: only allow a node to be removed if it wouldn't cause indecision around primary
        
        if db_instance is None:
            utils.log("[%s] error: unavailable to find db instance '%s'" % (self, args[0]))
            return
        
        conf = self._get_replset_conf()
        index = -1
        
        # find node to remove in replica set's config
        for i in xrange(len(conf.members)):
            node = conf.members[i]
            ip = node.host.split(':')[0].lower()
            
            if ip == db_instance.private_ip_address:
                index = i
                break
         
        if index < 0:
            utils.log("[%s] error: unable to find db instance '%s'" % (self, arg))
            return
        
        conf.members.pop(index)
        utils.log()
        utils.log("[%s] attempting to reconfigure replica set '%s'" % (self, conf._id))
        conf = dict(conf)
        conf['members'] = list(dict(m) for m in conf['members'])
        pprint(conf)
        
        confs = json.dumps(conf)
        ret   = self.run_mongo_cmd('rs.reconfig(%s, {force : %s})' % 
                                   (confs, str(force).lower()), slave_okay=force)
        pprint(ret)
        if force:
            db_node.terminate()
    
    def clear_cache(self, *args):
        force = (len(args) >= 1 and args[0] == 'force')
        cmd   = "sudo /bin/bash -c 'restart memcached'"
        pp    = []
        
        # restart memcached across all memcached servers
        for instance in self.mem_server_instances:
            pp.append((instance, utils.runbg(instance.public_dns_name, env.user, cmd)))
        
        for instance, p in pp:
            ret = p.wait()
    
    def repair(self, *args):
        force = (len(args) >= 1 and args[0] == 'force')
        
        db_instances = self.db_instances

        if len(db_instances) == 0:
            utils.log("[%s] No db instances" % self)
            return

        utils.log("[%s] attempting to repair replica set containing %d db instances" % (self, len(db_instances)))
        
        try:
            status = self._get_replset_status()
            utils.log(status)
            
            initialize = (status is None)
        except Fail:
            initialize = True
        
        # check if replica set needs to be initialized
        if initialize or ('startupStatus' in status and 3 == status['startupStatus']):
            utils.log("[%s] initializing empty replica set" % self)
            
            # initialize the replica set with a default configuration
            config = self._get_initial_replica_set_config()
            confs  = json.dumps(config)
            retval = self.run_mongo_cmd('rs.initiate(%s)' % confs, slave_okay=True, db='stamped')
            
            if 1 == retval.ok and 'info' in retval:
                utils.log("[%s] %s" % (self, retval.info))
            else:
                utils.log("[%s] error initializing replica set: '%s'" % (self, retval.info))
                return
            
            # wait until replica set reports its status as online
            utils.log("[%s] waiting for replica set '%s' to come online..." % (self, config['_id']))
            while True:
                time.sleep(1)
                
                try:
                    status = self._get_replset_status()
                    if status is not None:
                        utils.log("[%s] replica set '%s' is online!" % (self, status.set))
                        pprint(status)
                        break
                except Exception:
                    pass
        
        # group replica set members by state
        node_state = defaultdict(list)
        
        # replica set member state reference
        # ----------------------------------
        #   0 => Starting up, phase 1 (parsing configuration)
        #   1 => Primary
        #   2 => Secondary
        #   3 => Recovering (initial syncing, post-rollback, stale members)
        #   4 => Fatal error
        #   5 => Starting up, phase 2 (forking threads)
        #   6 => Unknown state (member has never been reached)
        #   7 => Arbiter
        #   8 => Down
        #   9 => Rollback
        # 
        # (http://www.mongodb.org/display/DOCS/Replica+Set+Commands)
        
        for node in status.members:
            if node.state == 0 or node.state == 5 or \
                ((node.state == 8 or node.state == 6) and 'errmsg' in node and node.errmsg == u'still initializing'):
                node_state['initializing'].append(node)
            elif node.state == 1:
                node_state['primary'].append(node)
            elif node.state == 2:
                node_state['secondary'].append(node)
            elif node.state == 3 or node.state == 9:
                node_state['recovering'].append(node)
            elif node.state == 7:
                node_state['arbiter'].append(node)
            else:
                node_state['unhealthy'].append(node)
        
        utils.log()
        for state, nodes in node_state.iteritems():
            l = len(nodes)
            utils.log("[%s] found %d %s node%s" % (self, l, state, '' if 1 == l else 's'))
        
        utils.log()
        warn = False
        
        # display warnings if there are obvious problems with the replica set
        if not 'primary' in node_state or 0 == len(node_state['primary']):
            utils.log("[%s] warning: replica set has no primary!" % self)
            warn = True
        
        if len(status.members) < len(db_instances):
            utils.log("[%s] warning: #nodes in replica set > #db-nodes in stack!" % self)
            warn = True
        elif len(status.members) > len(db_instances):
            utils.log("[%s] warning: #nodes in replica set < #db-nodes in stack!" % self)
            warn = True
        
        if warn:
            utils.log()
        
        new_members  = []
        db_members   = {}
        highest_id   = 0
        changed_conf = False
        
        for instance in db_instances:
            db_members[instance.private_ip_address] = -1
        
        # initialize a new replica set configuration by finding the intersection 
        # between db nodes in this stack and healthy nodes in the replica set
        for state, nodes in node_state.iteritems():
            for node in nodes:
                if node._id > highest_id:
                    highest_id = node._id
                
                ip = node.name.split(':')[0].lower()
                valid = False
                
                for instance in db_instances:
                    if ip == instance.private_ip_address.lower():
                        if state == 'unhealthy':
                            db_members[instance.private_ip_address] = 0
                        else:
                            valid = True
                            db_members[instance.private_ip_address] = 1
                            break
                
                if valid:
                    new_members.append({
                        '_id' : node._id, 
                        'host' : instance.private_ip_address, 
                    })
                else:
                    utils.log("[%s] warning: removing stale/unhealthy db node at '%s'" % (self, ip))
                    warn = True
                    changed_conf = True
        
        # add any db nodes which weren't originally in the replica set to the 
        # new configuration
        for ip, state in db_members.iteritems():
            if state == -1:
                instance = None
                for node in db_instances:
                    if node.private_ip_address == ip:
                        instance = node
                        break
                
                if instance is None:
                    continue
                
                # test if this db node is healthy by running a serverStatus command
                error = None
                try:
                    ret = self.run_mongo_cmd('db.serverStatus()', slave_okay=True, instance=instance)
                    if not 'ok' in ret or ret['ok'] != 1:
                        error = str(ret)
                except Exception, e:
                    error = e
                
                if error is not None:
                    utils.log("[%s] db node %s not reachable / healthy: '%s'" % 
                              (self, instance.name, str(error)))
                    continue
                
                utils.log("[%s] adding db node %s to replica set" % (self, instance.name))
                highest_id += 1
                changed_conf = True
                warn = True
                
                new_members.append({
                    '_id' : highest_id, 
                    'host' : ip, 
                })
        
        conf = {
            "_id" : status.set, 
            "members" : new_members, 
        }
        
        if warn:
            utils.log()
        
        # check if desired configuration has changed
        if changed_conf or len(new_members) != len(status.members):
            utils.log("[%s] reinitializing replica set '%s' with %d nodes" % 
                      (self, status.set, len(new_members)))
            
            pprint(conf)
            confs = json.dumps(conf)
            
            utils.log()
            ret = self.run_mongo_cmd('rs.reconfig(%s, {force : %s})' % 
                                     (confs, str(force).lower()), slave_okay=force)
            
            if ret is not None and 'ok' in ret and 1 == ret['ok']:
                utils.log("[%s] successfully reconfigured replica set %s" % (self, status.set))
            else:
                msg = "[%s] error reconfiguring replica set %s" % (self, status.set)
                utils.log(msg)
                pprint(ret)
                raise Fail(msg)
            
            # ensure there are enough members in the replica set
            min_members = 2
            if len(new_members) < min_members:
                utils.log()
                utils.log("[%s] warning: not enough replica set members to elect primary (%d minimum)" % (self, min_members))
                
                for i in xrange(min_members - len(new_members)):
                    utils.log("[%s] adding new db node to replica set" % self)
                    self.add('db')
        else:
            # everything looks peachy
            if warn:
                utils.log("[%s] replica set %s seems healthy (possibly still initializing)" % (self, status.set))
            else:
                utils.log("[%s] replica set %s is healthy" % (self, status.set))
    
    def delete(self):
        utils.log("[%s] deleting %d instances" % (self, len(self.instances)))
        pool = Pool(8)
        for instance in self.instances:
            pool.spawn(instance.terminate)
        
        pool.join()
        self.instances = [ ]
    
    def _getInstancesByRole(self, role):
        return filter(lambda instance: role in instance.roles, self.instances)
    
    def _get_elb(self, instance_or_instances):
        # TODO: this function doesn't account for the case where an instance 
        # may belong to multiple ELBs. NOTE that this scenario will never 
        # arise in our current stack architecture, but I'm leaving this 
        # note in here just in case that assumption changes in the future.
        
        if isinstance(instance_or_instances, (list, tuple, set)):
            instances = instance_or_instances
        else:
            instances = [ instance_or_instances ]
        
        # get all ELBs
        conn = ELBConnection(AWSDeploymentPlatform.AWS_ACCESS_KEY_ID, 
                             AWSDeploymentPlatform.AWS_SECRET_KEY)
        elbs = conn.get_all_load_balancers()
        
        # attempt to find the ELB belonging to this stack's set of API servers
        for elb in elbs:
            for awsInstance in elb.instances: 
                for instance in instances:
                    if awsInstance.id == instance.instance_id:
                        return elb
        
        return None
    
    def add(self, *args):
        types = [ 'db', 'api', 'web', 'work', 'mem', 'mon', 'stat', 'work-api', 'work-enrich' ]
        if 0 == len(args) or args[0] not in types:
            raise Fail("must specify what type of instance to add (e.g., %s)" % types)
        
        add   = args[0]
        count = 1
        
        if 2 == len(args):
            try:
                count = int(args[1])
            except Exception:
                raise Fail("last argument should be number of %s instances to add" % add)
        
        sim = []
        placements = defaultdict(int)
        placements['us-east-1a'] = 0
        placements['us-east-1b'] = 0
        placements['us-east-1c'] = 0
        top = -1
        
        dbStack = None
        # infer the suffix number for the new instance (e.g., api4, db2, etc.)
        for instance in self.instances:
            if 'db_stack' in instance.tags:
                dbStack = instance.tags['db_stack']
            if instance.name.startswith(add):
                sim.append(instance)
                cur = int(instance.name[len(add):])
                
                placements[instance.placement] += 1
                
                if cur > top:
                    top = cur
        
        top += 1
        
        # assumes all instances are sequential and zero-indexed
        # TODO: reuse old / deleted IDs
        #assert len(sim) == top
        
        if 0 == len(sim):
            instance = config.getInstance(add)
            
            sim.append(utils.AttributeDict({
                'config' : instance, 
            }))
        
        conf = dict(sim[0].config).copy()

        # Add db stack
        if dbStack is not None:
            conf['db_stack'] = dbStack 
        
        if isinstance(conf['roles'], basestring):
            conf['roles'] = eval(conf['roles'])
        
        # attempt to distribute the node evenly across availability zones by 
        # placing this new node into the AZ which has the minimum number of 
        # existing nodes
        placements = sorted(placements.iteritems(), key=lambda p: (p[1], p[0]))
        #pprint(placements)
        
        pool = Pool(8)
        instances = []
        
        def _create_instance(i):
            cur_conf = conf.copy()
            cur_conf['name'] = '%s%d' % (add, top + i)
            
            # TODO: this assumes nodes were previously evenly distributed
            # instead, calculate minimal placement each iteration
            placement = placements[i % len(placements)][0]
            cur_conf['placement'] = placement
            
            # create and bootstrap the new instance
            utils.log("[%s] creating instance %s in availability zone %s" % 
                      (self, cur_conf['name'], cur_conf['placement']))
            instance = AWSInstance(self, cur_conf)
            
            try:
                instance.create()
                instances.append(instance)
            except Exception:
                utils.printException()
                utils.log("error adding instance %s" % instance)
                raise
        
        # initialize instances in parallel
        for i in xrange(count):
            pool.spawn(_create_instance, i)
        
        pool.join()
        
        if len(instances) != count:
            utils.log("[%s] error: failed to add %d instances" % (self, count))
            return
        
        if add in ['api', 'web']:
            utils.log("[%s] checking for matching ELBs within stack %s" % (self, self.name))
            
            # attempt to find the ELB associated with nodes of the desired type for this stack
            elb = self._get_elb(sim)
            
            # register the new instance with the appropriate ELB
            if elb is not None:
                utils.log("[%s] registering instances with ELB '%s'" % (self, elb))
                elb.register_instances(list(i.instance_id for i in instances))
            else:
                utils.log("[%s] unable to find ELB for instances'" % (self, ))
        elif add == 'db':
            # TODO: check if we can initialize N instances in parallel here instead of synchronously
            for instance in instances:
                # initialize new DB instance
                # --------------------------
                db_instances = self.db_instances
                assert len(db_instances) > 0
                
                host = db_instances[0]
                port = conf['mongodb']['port']
                replSet = conf['mongodb']['replSet']
                
                utils.log("[%s] registering instance '%s' with replica set '%s'" % (self, instance.name, replSet))
                
                # register new instance with existing replia set
                node_name = '%s:%d' % (instance.private_ip_address, port)
                mongo_cmd = 'rs.add("%s")' % node_name
                
                utils.log("[%s] added instance '%s' to replica set '%s'" % (self, instance.name, replSet))
                status = self.run_mongo_cmd(mongo_cmd, transform=True, db='admin', slave_okay=False)
                
                pprint(status)
                utils.log()
                
                status = self._get_replset_status()
                found  = False
                
                for node in status.members:
                    ip = node.name.split(':')[0].lower()
                    
                    if ip == instance.private_ip_address:
                        found = True
                        break
                
                if found:
                    utils.log("[%s] instance '%s' is online with replica set '%s'" % (self, instance.name, replSet))
                else:
                    utils.log("[%s] error adding instance '%s' to replica set '%s'" % (self, instance.name, replSet))
                    status.members = list(dict(m) for m in status.members)
                    pprint(dict(status))
        
        self.instances.extend(instances)
        utils.log("[%s] done creating %d %s instance%s" % 
                  (self, count, add, 's' if 1 != count else ''))
    
    def stress(self, *args):
        numInstances = 2
        
        if len(args) > 0:
            numInstances = int(args[0])
        
        if numInstances <= 0:
            utils.log("[%s] invalid number of instances to run stress tests on")
        
        test_instances = self.test_instances
        
        if len(test_instances) != numInstances:
            if len(test_instances) > 0:
                utils.log("[%s] removing %d stale test instances before create can occur" % (self, len(test_instances)))
                ids = set()
                
                # remove stale test instances
                for instance in test_instances:
                    ids.add(instance.instance_id)
                    instance.terminate()
                
                self.instances = filter(lambda instance: instance.instance_id not in ids, self.instances)
            
            utils.log("[%s] creating %d test instances" % (self, numInstances))
            
            # create new test instances
            test_instances = []
            for i in xrange(numInstances):
                config = {
                    'name'  : 'test%d' % i, 
                    'roles' : [ 'test' ], 
                    'instance_type' : 'm1.small', 
                }
                
                instance = AWSInstance(self, config)
                test_instances.append(instance)
                self._pool.spawn(instance.create)
            
            self._pool.join()
            
            self.instances.extend(test_instances)
            utils.log("[%s] done creating %d test instances; initiating tests..." % (self, numInstances))
        
        env.user = 'ubuntu'
        env.key_filename = [ 'keys/test-keypair' ]
        
        # TODO: test just this portion
        
        for instance in test_instances:
            test_cmd = "/stamped/stamped/platform/tests/stampede/StressTests.py"
            log = "/stamped/logs/test.log"
            cmd = "sudo nohup bash -c '. /stamped/bin/activate && python %s >& %s < /dev/null' &" % \
                   (test_cmd, log)
            
            num_retries = 5
            while num_retries > 0:
                ret = utils.runbg(instance.public_dns_name, env.user, cmd)
                if 0 == ret:
                    break
                
                num_retries -= 1
    
    @lazy_property
    def is_prod(self):
        prod_stack_name = self.system.prod_stack
        
        return prod_stack_name is not None and prod_stack_name == self.name

