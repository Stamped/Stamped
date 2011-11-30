#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import config, json, pickle, os, re, string, utils
import AWSDeploymentSystem

from ADeploymentStack       import ADeploymentStack
from AWSInstance            import AWSInstance
from errors                 import Fail

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

ELASTIC_IP_ADDRESS = '184.73.229.100'

class AWSDeploymentStack(ADeploymentStack):
    def __init__(self, name, system, instances=None):
        ADeploymentStack.__init__(self, name, system)
        
        self.commonOptions = system.commonOptions
        self._pool = Pool(64)
        
        if instances is None:
            instances = config.getInstances()
            
            for instance in instances:
                if self.system.options.restore is not None and 'raid' in instance:
                    instance['raid']['restore'] = self.system.options.restore
        
        for instance in instances:
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
    
    def update(self):
        utils.log("[%s] updating %d instances" % (self, len(self.instances)))
        
        cmd = "sudo /bin/bash -c '. /stamped/bin/activate && python /stamped/bootstrap/bin/update.py'"
        pp  = []
        
        for instance in self.instances:
            pp.append((instance, utils.runbg(instance.public_dns_name, env.user, cmd)))
        
        for kv in pp:
            instance, p = kv
            ret = p.wait()
        
        utils.log("[%s] done updating %d instances" % (self, len(self.instances)))
    
    def run_mongo_cmd(self, mongo_cmd, transform=True, slave_okay=True, db='stamped'):
        """
            Runs the desired mongo shell command in the context of the given db, 
            on either a random db node in the stack if slave_okay is True or the 
            current primary node if slave_okay is False. If transform is True, 
            the console output of running the given command will be interpreted 
            as JSON and returned as a Python AttributeDict.
        """
        
        db_instances = self.db_instances
        assert len(db_instances) > 1
        
        env.user = 'ubuntu'
        env.key_filename = [ 'keys/test-keypair' ]
        
        cmd_template = "mongo %s --quiet --eval 'printjson(%s);'"
        cmd = cmd_template % (db, mongo_cmd)
        
        if not slave_okay:
            primary = self._get_primary()
            assert primary is not None
            
            db_instances = [ primary ]
        
        for instance in db_instances:
            try:
                with settings(host_string=instance.public_dns_name):
                    with hide('stdout'):
                        result = run(cmd, pty=False, shell=True)
                        
                        if transform:
                            result = re.sub(self.isodate_re, r'\1', result)
                            
                            try:
                                result = utils.AttributeDict(json.loads(result))
                                
                                if 'errmsg' in result:
                                    raise Fail(result['errmsg'])
                            except Fail:
                                raise
                            except:
                                utils.log("[%s] error interpreting results of mongo cmd on instance '%s' (%s)" % (self, instance, mongo_cmd))
                                utils.printException()
                                utils.log(result)
                                return None
                        
                        return result
            except Fail:
                raise
            except:
                utils.log("[%s] error running mongo cmd on instance '%s' (%s)" % (self, instance, mongo_cmd))
        
        return None
    
    def _get_primary(self):
        """
            Returns the current primary db node if one exists, retrying 
            several times in case the replica set is failing over and 
            reelecting a primary. If no primary is found, will raise an 
            Exception.
        """
        
        utils.log("[%s] attempting to find primary db node" % self)
        
        maxdelay = 16
        delay = 1
        
        while True:
            status = self._get_replset_status()
            
            primaries = filter(lambda m: 1 == m.state, status.members)
            if 0 == len(primaries):
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
    
    def _get_replset_status(self):
        status = self.run_mongo_cmd('rs.status()')
        if 'members' in status:
            status.members = list(utils.AttributeDict(node) for node in status.members)
        
        return status
    
    def _get_replset_conf(self):
        status  = self.run_mongo_cmd('rs.conf()')
        status.members = list(utils.AttributeDict(node) for node in status.members)
        
        return status
    
    def force_db_primary_change(self, *args):
        if 0 == len(args):
            utils.log("must specify instance to make primary (either node name or instance-id)")
            return
        
        db_instance = None
        arg   = args[0]
        force = (len(args) > 1 and args[1] == 'force')
        
        for instance in self.db_instances:
            if instance.name == arg or instance.instance_id == arg:
                db_instance = instance
                break
        
        if db_instance is None:
            utils.log("[%s] error: unavailable to find db instance '%s'" % (self, arg))
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
    
    def repair(self, *args):
        force = (len(args) >= 1 and args[0] == 'force')
        
        db_instances = self.db_instances
        utils.log("[%s] attempting to repair replica set containing %d db instances" % (self, len(db_instances)))
        
        try:
            status = self._get_replset_status()
            initialize = False
        except Fail:
            initialize = True
        
        if initialize or ('startupStatus' in status and 3 == status['startupStatus']):
            utils.log("[%s] initializing empty replica set")
            
            config = self._get_initial_replica_set_config()
            confs  = json.dumps(config)
            retval = self.run_mongo_cmd('rs.initiate(%s)' % confs, slave_okay=True, db='stamped')
            
            if 1 == retval.ok and 'info' in retval:
                utils.log("[%s] %s" % (self, retval.info))
            else:
                utils.log("[%s] error initializing replica set: '%s'" % (self, retval.info))
                return
            
            utils.log("[%s] waiting for replica set '%s' to come online..." % (self, config['_id']))
            while True:
                time.sleep(1)
                
                try:
                    status = self._get_replset_status()
                    if status is not None:
                        utils.log("[%s] replica set '%s' is online!" % (self, status.set))
                        break
                except:
                    pass
        
        # group replica set members by state
        node_state = defaultdict(list)
        for node in status.members:
            if node.state == 1:
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
        
        new_members = []
        
        for state, nodes in node_state.iteritems():
            for node in nodes:
                ip = node.name.split(':')[0].lower()
                valid = False
                
                if state != 'unhealthy':
                    for instance in db_instances:
                        if ip == instance.private_ip_address.lower():
                            valid = True
                            break
                
                if valid:
                    new_members.append({
                        '_id' : node._id, 
                        'host' : instance.private_ip_address, 
                    })
                else:
                    utils.log("[%s] warning: removing stale/unhealthy db node at '%s'" % (self, ip))
                    warn = True
        
        conf = {
            "_id" : status.set, 
            "members" : new_members, 
        }
        
        if warn:
            utils.log()
        
        if len(new_members) != len(status.members):
            utils.log("[%s] reinitializing replica set '%s' with %d nodes'" % 
                      (self, status.set, len(new_members)))
            
            pprint(conf)
            confs = json.dumps(conf)
            
            utils.log()
            ret = self.run_mongo_cmd('rs.reconfig(%s, {force : %s})' % 
                                     (confs, str(force).lower()), slave_okay=force)
            if 1 != ret['okay']:
                utils.log("[%s] successfully reconfigured replica set %s" % (self, status.set))
            else:
                msg = "[%s] error reconfiguring replica set %s" % (self, status.set)
                utils.log(msg)
                pprint(ret)
                raise msg
            
            min_members = 2
            if len(new_members) < min_members:
                utils.log()
                utils.log("[%s] warning: not enough replica set members to elect primary (%d minimum)" % (self, min_members))
                
                for i in xrange(min_members - len(new_members)):
                    utils.log("[%s] adding new db node to replica set" % self)
                    self.add('db')
        else:
            # everything looks peachy
            assert not warn
            utils.log("[%s] everything looks peachy with replica set %s" % (self, status.set))
    
    def delete(self):
        utils.log("[%s] deleting %d instances" % (self, len(self.instances)))
        pool = Pool(8)
        for instance in self.instances:
            pool.spawn(instance.terminate)
        
        pool.join()
        self.instances = [ ]
    
    def connect(self):
        web_server_instances = self.web_server_instances
        assert len(web_server_instances) > 0
        
        web_server = web_server_instances[0]
        if web_server.state != 'running':
            raise Fail("Unable to connect to '%s'" % web_server_instances[0])
        
        cmd = './connect.sh %s.%s' % (self.name, web_server.name)
        utils.log(cmd)
        os.system(cmd)
    
    def crawl(self, *args):
        crawlers = [
            {
                'sources' : [ 
                    'apple_artists', 
                    #'apple_albums', 
                    'apple_videos', 
                ], 
                'numInstances' : 1, 
                'mapSourceToProcess' : True, 
            }, 
            {
                'sources' : [ 
                    'opentable', 
                ], 
                'numInstances' : 2, 
                'numProcesses' : 8, 
            }, 
            {
                'sources' : [ 
                    'zagat', 
                    #'sfmag', 
                ], 
                'numInstances' : 1, 
                'mapSourceToProcess' : True, 
            }, 
        ]
        """
            {
                'sources' : [ 
                    'nymag', 
                    'bostonmag', 
                ], 
                'numInstances' : 1, 
                'mapSourceToProcess' : True, 
            }, 
            {
                'sources' : [ 
                    'phillymag', 
                    'chicagomag', 
                    'washmag', 
                ], 
                'numInstances' : 1, 
                'mapSourceToProcess' : True, 
            }, 
        ]
        """
        
        #crawler_instances = self.crawler_instances
        crawler_instances = []
        reservations = self.conn.get_all_instances()
        
        # find all previous crawler instances
        for reservation in reservations:
            for instance in reservation.instances:
                if hasattr(instance, 'tags') and 'stack' in instance.tags and instance.state == 'running':
                    stackName = instance.tags['stack']
                    
                    if stackName == self.name and instance.tags['name'].startswith('crawler'):
                        crawler_instances.append(AWSInstance(self, instance))
        
        # count the number of expected crawler instances per the crawlers config
        num_instances = 0
        for crawler in crawlers:
            num_instances += crawler['numInstances']
        
        # attempt to reuse previous crawler instances that are very likely already 
        # initialized for this crawler run, as opposed to spawning a new set
        if len(crawler_instances) == num_instances:
            for instance in crawler_instances:
                num  = int(instance.tags['name'].replace('crawler', ''))
                inum = 0
                while True:
                    num -= crawlers[inum]['numInstances']
                    if num < 0:
                        break
                    inum += 1
                
                if 'instances' in crawlers[inum]:
                    crawlers[inum]['instances'].append(instance)
                else:
                    crawlers[inum]['instances'] = [ instance ]
            #for crawler in crawlers:
            #    from pprint import pprint
            #    pprint(crawler)
        else:
            # unable to reuse previous crawler instances since their 
            # configuration doesn't match the current config. terminate all 
            # previous crawler instances and create a new set from scratch.
            if len(crawler_instances) > 0:
                utils.log("[%s] terminating %d stale crawler instances" % (self, len(crawler_instances)))
                for instance in crawler_instances:
                    instance.terminate()
            
            instances = []
            index = 0
            
            utils.log("[%s] creating %d crawler instances" % (self, num_instances))
            
            # spawn and initialize a new AWS instance per crawler requirements
            for crawler in crawlers:
                for i in xrange(crawler['numInstances']):
                    config = {
                        'name'  : 'crawler%d' % index, 
                        'roles' : [ 'crawler' ], 
                        'instance_type' : 'm1.small', 
                        # TODO: don't hardcode this
                        'placement' : 'us-east-1b', 
                    }
                    
                    instance = AWSInstance(self, config)
                    index += 1
                    if not 'instances' in crawler:
                        crawler['instances'] = []
                    
                    crawler['instances'].append(instance)
                    self._pool.spawn(instance.create)
            
            # wait until all crawler AWSInstances are initialized before 
            # beginning to crawl on any of them
            
            # TODO: this isn't really necessary; could start crawling on 
            # instance i once it's ready since each instance is wholly 
            # independent of all other instances.
            self._pool.join()
        
        env.user = 'ubuntu'
        env.key_filename = [ 'keys/test-keypair' ]
        
        db_instances = self.db_instances
        assert len(db_instances) > 1
        
        host = db_instances[0].private_ip_address
        
        # begin m crawler processes on each of the n crawler instances
        for crawler in crawlers:
            if 'mapSourceToProcess' in crawler and crawler['mapSourceToProcess']:
                numProcesses = len(crawler['sources'])
            else:
                numProcesses = crawler['numProcesses']
            
            numCrawlers = crawler['numInstances'] * numProcesses
            index = 0
            
            for instance in crawler['instances']:
                with settings(host_string=instance.public_dns_name):
                    num_retries = 5
                    while num_retries > 0:
                        try:
                            cmd = 'mkdir -p /stamped/logs && chmod -R 777 /stamped/logs'
                            sudo(cmd)
                            break
                        except SystemExit:
                            num_retries -= 1
                            time.sleep(1)
                    
                    for i in xrange(numProcesses):
                        mount = ""
                        
                        if 'mapSourceToProcess' in crawler and crawler['mapSourceToProcess']:
                            sources = [ crawler['sources'][i], ]
                            if i == 0:
                                mount = "-m"
                            
                            # for now, only change the source for each process, not the ratio
                            ratio = "%s/%s" % (1, 1)
                        else:
                            sources = crawler['sources']
                            ratio = "%s/%s" % (index + 1, numCrawlers)
                        
                        sources = string.joinfields(sources, ' ')
                        crawler_path = '/stamped/stamped/sites/stamped.com/bin/crawler/crawler.py'
                        
                        log = "/stamped/logs/crawler%d.log" % index
                        cmd = "sudo nohup bash -c '. /stamped/bin/activate && python %s --db %s -s merge -g %s --ratio %s %s' >& %s < /dev/null &" % (crawler_path, host, mount, ratio, sources, log)
                        index += 1
                        
                        num_retries = 5
                        while num_retries > 0:
                            ret = utils.runbg(instance.public_dns_name, env.user, cmd)
                            if 0 == ret:
                                break
                            num_retries -= 1
    
    def setup_crawler_data(self, *args):
        config = {
            'name' : 'crawler_setup0', 
            'roles' : [ ], 
            'instance_type' : 'm1.small', 
            'placement' : 'us-east-1b', 
        }
        
        # create temporary instance whose only purpose will be to attach and mount 
        # the crawler data AWS volume, add data to it, and then cleanup.
        instance = AWSInstance(self, config)
        instance.create(block=False)
        
        files = [
            "album_popularity_per_genre", 
            "artist_collection", 
            "artist", 
            "artist_type", 
            "collection", 
            "collection_type", 
            "genre", 
            "media_type", 
            #"song", 
            "role", 
            "storefront", 
            "video", 
            "video_price", 
        ]
        
        volume_dir = "/dev/sdh5"
        mount_dir = "/mnt/crawlerdata"
        
        env.user = 'ubuntu'
        env.key_filename = [ 'keys/test-keypair' ]
        
        # create and attach volume to temporary instance
        with settings(host_string=instance.public_dns_name):
            utils.log("creating volume and attaching to instance %s..." % instance._instance.id)
            volume = self.conn.create_volume(8, instance._instance.placement)
            #volume = self.conn.get_all_volumes(volume_ids=['vol-8cbb5ce6', ])[0]
            
            while volume.status == u'creating':
                time.sleep(2)
                volume.update()
            
            try:
                if volume.status != 'available':
                    i = self.conn.get_all_instances(instance_ids=[ volume.attach_data.instance_id, ])[0].instances[0]
                    with settings(host_string=i.public_dns_name):
                        sudo("umount %s" % volume_dir)
                    
                    volume.detach(force=True)
                    time.sleep(6)
                    while volume.status != 'available':
                        time.sleep(2)
                        print volume.update()
            except EC2ResponseError:
                pass
            
            try:
                #with settings(warn_only=True):
                #    sudo("umount %s" % volume_dir)
                
                volume.attach(instance._instance.id, volume_dir)
            except EC2ResponseError:
                volumes = self.conn.get_all_volumes()
                
                for v in volumes:
                    if v.status == u'in-use' and \
                       v.attach_data.instance_id == instance._instance.id:
                        with settings(warn_only=True):
                            sudo("umount %s" % volume_dir)
                        
                        v.detach(force=True)
                        
                        while v.status != u'available':
                            time.sleep(2)
                            v.update()
                
                while not volume.attach(instance._instance.id, volume_dir):
                    time.sleep(5)
            
            while volume.status != u'in-use':
                time.sleep(2)
                volume.update()
            
            cmds = [
                'mkdir -p %s' % mount_dir, 
                'sync', 
                'mkfs -t ext3 %s' % volume_dir, 
                'mount -t ext3 %s %s' % (volume_dir, mount_dir), 
                'chown -R %s %s' % (env.user, mount_dir, ), 
                'chmod -R 700 %s' % (mount_dir, ), 
            ]
            
            # initialize and mount volume
            for cmd in cmds:
                sudo(cmd)
            
            def _put_file(filename):
                zipped = filename + ".gz"
                if os.path.exists(zipped):
                    filename = zipped
                
                #remote_path = os.path.join(os.path.join(mount_dir, "data/apple"), name)
                
                utils.log("uploading file '%s'" % filename)
                #utils.scp(filename, instance.public_dns_name, env.user, mount_dir)
                put(local_path=filename, remote_path=mount_dir, use_sudo=True)
                utils.log("done uploading file '%s'" % filename)
                #if not fabricfiles.exists(os.path.join(mount_dir, os.path.basename(filename)), use_sudo=True):
                #else:
                #    utils.log("remote file '%s' already exists" % filename)
            
            pool = Pool(2)
            
            # copy all files over to volume
            epf_base = "/Users/fisch0920/dev/stamped/sites/stamped.com/bin/crawler/sources/dumps/data/apple"
            for name in files:
                filename = os.path.join(epf_base, name)
                pool.spawn(_put_file, filename)
                #_put_file(filename)
            
            pool.join()
            utils.log("upload successful; unmounting and detaching volume...")
            
            # unmount and detach volume
            sudo("umount %s" % mount_dir)
            volume.detach()
            
            while volume.status != u'available':
                time.sleep(2)
                volume.update()
            
            utils.log("volume: %s" % volume.id)
    
    def _getInstancesByRole(self, role):
        return filter(lambda instance: role in instance.roles, self.instances)
    
    def add(self, *args):
        types = [ 'db', 'api', 'web' ]
        if 0 == len(args) or args[0] not in types:
            raise Fail("must specify what type of instance to add (e.g., %s)" % types)
        
        add   = args[0]
        count = 1
        
        if 2 == len(args):
            try:
                count = int(args[1])
            except:
                raise Fail("last argument should be number of %s instances to add" % add)
        
        sim = []
        ids = set()
        placements = defaultdict(int)
        placements['us-east-1a'] = 0
        placements['us-east-1b'] = 0
        placements['us-east-1c'] = 0
        top = -1
        
        # infer the suffix number for the new instance (e.g., api4, db2, etc.)
        for instance in self.instances:
            if instance.name.startswith(add):
                sim.append(instance)
                ids.add(instance.instance_id)
                cur = int(instance.name[len(add):])
                
                placements[instance.placement] += 1
                
                if cur > top:
                    top = cur
        
        top += 1
        
        # assumes all instances are sequential and zero-indexed
        # TODO: reuse old / deleted IDs
        #assert len(sim) == top
        
        if 0 == len(sim):
            instances = config.getInstances()
            for instance in instances:
                if instance['name'].startswith(add):
                    sim.append(utils.AttributeDict({
                        'config' : instance, 
                    }))
        
        conf = dict(sim[0].config).copy()
        
        if isinstance(conf['roles'], basestring):
            conf['roles'] = eval(conf['roles'])
        
        # attempt to distribute the node evenly across availability zones by 
        # placing this new node into the AZ which has the minimum number of 
        # existing nodes
        placements = sorted(placements.iteritems(), key=lambda p: (p[1], p[0]))
        
        pool = Pool(8)
        instances = []
        
        def _create_instance(i):
            conf['name'] = '%s%d' % (add, top + i)
            
            if 0 == placements[-1][1] and count == 1:
                placement = 'us-east-1a' # default availability zone
            else:
                placement = placements[i][0]
            
            conf['placement'] = placement
            
            # create and bootstrap the new instance
            utils.log("[%s] creating instance %s in availability zone %s" % 
                      (self, conf['name'], conf['placement']))
            instance = AWSInstance(self, conf)
            
            try:
                instance.create()
                instances.append(instance)
            except:
                utils.printException()
                utils.log("error adding instance %s" % instance)
                raise
        
        # initialize instances in parallel
        for i in xrange(count):
            pool.spawn(_create_instance, i)
        
        pool.join()
        
        if len(instances) != count:
            utils.log("[%s] error: failed to add %d instances" % (self, count))
        
        if add in ['api', 'web']:
            utils.log("[%s] checking ELBs for stack %s" % (self, self.name))
            
            # get all ELBs
            conn = ELBConnection(AWSDeploymentSystem.AWS_ACCESS_KEY_ID, 
                                 AWSDeploymentSystem.AWS_SECRET_KEY)
            elbs = conn.get_all_load_balancers()
            the_elb = None
            
            # attempt to find the ELB belonging to this stack's set of API servers
            for elb in elbs:
                for awsInstance in elb.instances: 
                    if awsInstance.id in ids:
                        the_elb = elb
                        break
                
                if the_elb is not None:
                    break
            
            # register the new instance with the appropriate ELB
            if the_elb is not None:
                utils.log("[%s] registering instances with ELB '%s'" % (self, the_elb))
                the_elb.register_instances(list(i.instance_id for i in instances))
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
                status = self.run_mongo_cmd(mongo_cmd, transform=True, db='admin')
                
                pprint(status)
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
                
                """
                command   = "mongo --quiet %s:%s/admin --eval 'printjson(%s);'" % \
                             (host.public_dns_name, port, mongo_cmd)
                
                utils.log(command)
                ret = utils.shell(command)
                
                if 0 == ret[1]:
                    utils.log("[%s] added instance '%s' to replica set '%s'" % (self, instance.name, replSet))
                    utils.log("[%s] waiting for node to come online (may take a few minutes during initial sync)" % self)
                    print ret[0]
                    
                    mongo_cmd = 'rs.status()'
                    command   = "mongo --quiet %s:%s/admin --eval 'printjson(%s);'" % \
                                 (host.public_dns_name, port, mongo_cmd)
                    
                    # wait until the replica set reports the newly added instance as healthy
                    while True:
                        ret = utils.shell(command)
                        #print ret[0]
                        
                        if 0 == ret[1]:
                            status  = re.sub("ISODate\(([^)]*)\)", '""', ret[0])
                            status  = json.loads(status)
                            healthy = False
                            
                            for node in status['members']:
                                if node['name'] == node_name:
                                    healthy = (1 == node['health'])
                                    break
                            
                            if healthy:
                                break
                        
                        time.sleep(2)
                    
                    utils.log("[%s] instance '%s' is online with replica set '%s'" % (self, instance.name, replSet))
                else:
                    utils.log("[%s] error adding instance '%s' to replica set '%s'" % (self, instance.name, replSet))
                    print ret[0]
            """
        
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
            test_cmd = "/stamped/stamped/sites/stamped.com/bin/tests/stampede/StressTests.py"
            log = "/stamped/logs/test.log"
            cmd = "sudo nohup bash -c '. /stamped/bin/activate && python %s >& %s < /dev/null' &" % \
                   (test_cmd, log)
            
            num_retries = 5
            while num_retries > 0:
                ret = utils.runbg(instance.public_dns_name, env.user, cmd)
                if 0 == ret:
                    break
                
                num_retries -= 1

