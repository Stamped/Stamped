#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import config, json, pickle, os, string, utils
from ADeploymentStack import ADeploymentStack
from AWSInstance import AWSInstance
from errors import Fail
from boto.ec2.connection import EC2Connection
from boto.ec2.address import Address
from boto.exception import EC2ResponseError

from gevent.pool import Pool
from fabric.operations import *
from fabric.api import *
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
    
    def init(self):
        db_instances = self.db_instances
        assert len(db_instances) > 1
        
        replica_set_members = []
        replica_set = None
        
        for instance in db_instances:
            replica_set = instance.config.mongodb.replSet
            replica_set_members.append({
                "_id": len(replica_set_members), 
                "host": instance.private_ip_address
            })
        
        config = self._encode_params({
            "_id" : replica_set, 
            "members" : replica_set_members, 
        })
        
        env.user = 'ubuntu'
        env.key_filename = [ 'keys/test-keypair' ]
        
        web_server_instances = self.web_server_instances
        assert len(web_server_instances) > 0
        
        with settings(host_string=web_server_instances[0].public_dns_name):
            with cd("/stamped"):
                sudo('. bin/activate && python /stamped/bootstrap/bin/init.py "%s"' % config, pty=False)
        
        if self.system.options.ip:
            """ associate ip address here"""
            address = Address(self.conn, ELASTIC_IP_ADDRESS)
            
            if not address.associate(web_server_instances[0]['instance_id']):
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
                'sources' : [ 'apple_artists', 'apple_albums', 'apple_videos', ], 
                'numInstances' : 1, 
                'mapSourceToProcess' : True, 
            }, 
            #{
            #    'sources' : [ 'opentable', ], 
            #    'numInstances' : 16, 
            #    'numProcesses' : 4, 
            #}, 
            #{
            #    'sources' : [ 'factualusrestaurants', ], 
            #    'numInstances' : 40, 
            #    'numProcesses' : 8, 
            #}, 
        ]
        
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
                num = int(instance.tags['name'].replace('crawler', ''))
                if 'instances' in crawlers[num]:
                    crawlers[num]['instances'].append(instance)
                else:
                    crawlers[num]['instances'] = [ instance ]
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
                        cmd = "sudo nohup bash -c '. /stamped/bin/activate && python %s --db %s -g %s --ratio %s %s' >& %s < /dev/null &" % (crawler_path, host, mount, ratio, sources, log)
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
        instance.create()
        
        files = [
            "artist", 
            "artist_type", 
            "collection", 
            "collection_type", 
            "media_type", 
            #"song", 
            "video", 
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
            
            pool = Pool(64)
            
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

