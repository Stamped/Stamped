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
    def web_server_instances(self):
        return self._getInstancesByRole('webServer')
    
    def create(self):
        utils.log("[%s] creating %d instances" % (self, len(self.instances)))
        
        for instance in self.instances:
            self._pool.spawn(instance.create)
        
        self._pool.join()
        utils.log("[%s] done creating %d instances" % (self, len(self.instances)))
    
    def _get_init_config(self):
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
        
        return self._encode_params({
            "_id" : replica_set, 
            "members" : replica_set_members, 
        })
    
    def init(self):
        config = self._get_init_config()
        
        env.user = 'ubuntu'
        env.key_filename = [ 'keys/test-keypair' ]
        
        web_server_instances = self.web_server_instances
        assert len(web_server_instances) > 0
        
        for instance in web_server_instances:
            with settings(host_string=instance.public_dns_name):
                with cd("/stamped"):
                    sudo('. bin/activate && python /stamped/bootstrap/bin/init.py "%s"' % config, pty=False)
        
        if self.system.options.ip:
            """ associate ip address here"""
            address = Address(self.conn, ELASTIC_IP_ADDRESS)
            
            if not address.associate(web_server_instances[0].instance_id):
                raise Fail("Error: failed to set elastic ip")
    
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
        
        env.user = 'ubuntu'
        env.key_filename = [ 'keys/test-keypair' ]
        
        for instance in self.instances:
            with settings(host_string=instance.public_dns_name):
                with cd("/stamped"):
                    sudo('. bin/activate && python /stamped/bootstrap/bin/update.py', pty=False)
    
    def repair(self):
        # TODO
        pass
    
    def delete(self):
        utils.log("[%s] deleting %d instances" % (self, len(self.instances)))
        for instance in self.instances:
            instance.terminate()
        
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
    
    def _encode_params(self, params):
        return json.dumps(params).replace('"', "'")
    
    def add(self, *args):
        if 0 == len(args) or args[0] not in [ 'db', 'api' ]:
            raise Exception("must specify what type of instance to add (e.g., db, api)")
        
        add = args[0]
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
        #assert len(sim) == top
        
        if 0 == len(sim):
            instances = config.getInstances()
            for instance in instances:
                if instance['name'].startswith(add):
                    sim.append(utils.AttributeDict({
                        'config' : instance, 
                    }))
        
        conf = dict(sim[0].config).copy()
        conf['name'] = '%s%d' % (add, top)
        
        if isinstance(conf['roles'], basestring):
            conf['roles'] = eval(conf['roles'])
        
        # attempt to distribute the node evenly across availability zones by 
        # placing this new node into the AZ which has the minimum number of 
        # existing nodes
        min_v = None
        for k, v in placements.iteritems():
            if min_v is None or v < min_v[1]:
                min_v = (k, v)
        
        if min_v is None:
            placement = 'us-east-1a'
        else:
            placement = min_v[0]
        
        conf['placement'] = placement
        
        # create and bootstrap the new instance
        utils.log("[%s] creating instance %s in AZ %s" % (self, conf['name'], conf['placement']))
        instance = AWSInstance(self, conf)
        
        try:
            instance.create()
        except:
            utils.printException()
            utils.log("error adding instance %s" % instance)
            raise
        
        #self._pool.spawn(instance.create)
        #self._pool.join()
        
        if add == 'api':
            # initialize new API instance
            # ---------------------------
            conf = self._get_init_config()
            
            env.user = 'ubuntu'
            env.key_filename = [ 'keys/test-keypair' ]
            
            # initialize the new instance
            utils.log("[%s] initializing instance %s" % (self, instance.name))
            with settings(host_string=instance.public_dns_name):
                with cd("/stamped"):
                    sudo('. bin/activate && python /stamped/bootstrap/bin/init.py "%s"' % conf, pty=False)
            
            utils.log("[%s] done initializing instance %s" % (self, instance.name))
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
                utils.log("[%s] registering instance '%s' with ELB '%s'" % (self, instance.name, the_elb))
                the_elb.register_instances([ instance.instance_id ])
            else:
                utils.log("[%s] unable to find ELB for instance '%s'" % (self, instance.name))
        elif add == 'db':
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
        
        self.instances.append(instance)
        utils.log("[%s] done creating instance %s" % (self, instance.name))
    
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

