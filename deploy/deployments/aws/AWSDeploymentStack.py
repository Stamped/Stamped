#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import config, json, pickle, os, utils
from ADeploymentStack import ADeploymentStack
from AWSInstance import AWSInstance
from errors import Fail
from boto.ec2.connection import EC2Connection
from boto.ec2.address import Address

from gevent.pool import Pool
from fabric.operations import *
from fabric.api import *
from fabric.contrib.console import *

ELASTIC_IP_ADDRESS = '184.73.229.100'

class AWSDeploymentStack(ADeploymentStack):
    def __init__(self, name, system, instances=None):
        ADeploymentStack.__init__(self, name, system)
        
        self.commonOptions = system.commonOptions
        
        # maximum number of instances to create at one time
        self._pool = Pool(8)
        
        if instances is None:
            instances = config.getInstances()
        
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
        raise NotImplementedError
        # TODO
        
        numCrawlers = len(crawlers)
        count = 1
        
        env.user = 'ubuntu'
        env.key_filename = [ 'keys/test-keypair' ]
        
        for crawler in crawler_instances:
            with settings(host_string=crawler[0].public_dns_name):
                with cd("/stamped"):
                    ratio = "%s/%s" % (count, numCrawlers)
                    crawler_path = "/stamped/stamped/sites/stamped.com/bin/crawler/crawler.py"
                    
                    # TODO: GET PRIMARY
                    host = db_instances[i].private_ip_address
                    
                    cmd = '. bin/activate && python %s --db %s --ratio %s&' % (crawler_path, host, ratio)
                    
                    run(cmd, pty=False)
                    count += 1
    
    def _getInstancesByRole(self, role):
        return filter(lambda instance: role in instance.roles, self.instances)
    
    def _encode_params(self, params):
        return json.dumps(params).replace('"', "'")

