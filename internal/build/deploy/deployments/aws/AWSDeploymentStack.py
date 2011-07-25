#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import config, json, pickle, os
from utils import log, logRaw, shell, AttributeDict
from ADeploymentStack import ADeploymentStack
from errors import Fail
from boto.ec2.connection import EC2Connection

from fabric.operations import *
from fabric.api import *
from fabric.contrib.console import *

AWS_ACCESS_KEY_ID = 'AKIAIXLZZZT4DMTKZBDQ'
AWS_SECRET_KEY = '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'

class AWSDeploymentStack(ADeploymentStack):
    def __init__(self, name, parent):
        ADeploymentStack.__init__(self, name, parent.options)
        
        self.parent = parent
        self.env = parent.env
        self.commonOptions = parent.commonOptions
        self.instances = config.getInstances()
        
        for instance in self.instances:
            instance['stack_name'] = self.name
            instance['aws_access_key_id'] = AWS_ACCESS_KEY_ID
            instance['aws_access_key_secret'] = AWS_SECRET_KEY
    
    def create(self):
        print "1) " + self.name
        params_str = pickle.dumps(self.instances)
        build_template_path = os.path.join(self.env.CLOUDFORMATION_ROOT, "build.py")
        
        self.local('python %s "%s" > %s' % (build_template_path, params_str, self.env.CLOUDFORMATION_TEMPLATE_FILE), show_cmd=False)
        self.local('cfn-create-stack "%s" --template-file %s' % (self.name, self.env.CLOUDFORMATION_TEMPLATE_FILE))
    
    def getInstances(self):
        webServerInstances = []
        dbInstances = []
        
        conn = EC2Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)
        reservations = conn.get_all_instances()
        stackNameKey = 'aws:cloudformation:stack-name'
        stackFamilyKey = 'stamped:family'
        
        stackName = self.name.lower()
        for reservation in reservations:
            for instance in reservation.instances:
                if stackNameKey in instance.tags and instance.tags[stackNameKey].lower() == stackName:
                    if instance.tags[stackFamilyKey].lower() == 'database':
                        dbInstances.append({
                            'private_ip_address' : instance.private_ip_address, 
                            'public_dns_name' : instance.public_dns_name, 
                        })
                    if instance.tags[stackFamilyKey].lower() == 'webserver':
                        webServerInstances.append({
                            'private_ip_address' : instance.private_ip_address, 
                            'public_dns_name' : instance.public_dns_name, 
                        })
        
        return (webServerInstances, dbInstances)
    
    def init(self):
        replSet = None
        for instance in self.instances:
            if 'replSet' in instance:
                replSet = instance['replSet']
                break
        
        if replSet is None:
            raise Fail("Error: no replica set defined in config")
        
        webServerInstances, dbInstances = self.getInstances()
        
        if len(dbInstances) > 1: # Only run if multiple instances exist
            replSetMembers = []
            for i in range(len(dbInstances)):
                replSetMembers.append({"_id": i, "host": dbInstances[i]['private_ip_address']})
            
            config = {"_id": replSet, "members": replSetMembers}
        else:
            raise Fail("Error: invalid number of db instances -- must have at least two instances to form a replica set")
        
        print "Databases:  %s" % str(dbInstances)
        print "WebServers: %s" % str(webServerInstances)
        
        # TODO: setting env.hosts fails miserably
        env.hosts = webServerInstances
        env.user = 'ubuntu'
        env.key_filename = [
            'keys/test-keypair'
        ]
        
        params_str = self._encode_params(config)
        
        with settings(host_string=webServerInstances[0]['public_dns_name']):
            with cd("/stamped"):
                sudo('. bin/activate && python /stamped/bootstrap/bin/init.py "%s"' % params_str, pty=False)
    
    def update(self):
        webServerInstances, dbInstances = self.getInstances()
        env.user = 'ubuntu'
        env.key_filename = [
            'keys/test-keypair'
        ]
        
        instances = []
        for instance in webServerInstances:
            instances.append(instance)
        for instance in dbInstances:
            instances.append(instance)
        
        for instance in instances:
            with settings(host_string=instance['public_dns_name']):
                with cd("/stamped"):
                    sudo('. bin/activate && python /stamped/bootstrap/bin/update.py', pty=False)
    
    def delete(self):
        self.local('cfn-delete-stack %s --force' % (self.name, ))
    
    def _encode_params(self, params):
        return json.dumps(params).replace('"', "'")
    
    def describe(self):
        if self.name is not None:
            self.local('cfn-describe-stacks --stack-name %s %s' % (self.name, self.commonOptions))
        else:
            self.local('cfn-describe-stacks %s' % (self.commonOptions, ))
    
    def describe_events(self):
        self.local('cfn-describe-stack-events --stack-name %s %s' % (self.name, self.commonOptions))
    
    def connect(self):
        while True:
            logRaw("Checking if stack '%s' is ready for connection... " % self.name, True)
            (result, status) = shell('cfn-describe-stack-events --stack-name %s | grep "%s *CreateWebServerInstance .*CREATE_COMPLETE"' % (self.name, self.name))
            
            if len(result) > 5:
                logRaw("ready! connecting...\n")
                break
            else:
                (result, status) = shell('cfn-describe-stack-events --stack-name %s | grep "%s .*ROLLBACK.*"' % (self.name, self.name))
                if len(result) > 5:
                    print "aborting connection because stack %s has been rolled back" % (self.name, )
                    return 1
                
                (result, status) = shell('cfn-describe-stack-events --stack-name %s | grep "%s .*DELETE.*"' % (self.name, self.name))
                if len(result) > 5:
                    print "aborting connection because stack %s has been deleted" % (self.name, )
                    return 1
                
                wait = 10
                logRaw("not ready (sleeping for %d seconds before retrying)...\n" % wait)
                import time
                time.sleep(wait)
        
        print "WebServer instance in stack %s has been initialized! Attempting to connect via ssh..." % (self.name, )
        os.system('connect.sh %s %s' % (self.name, "WebServer"))
    
    def crawl(self, *args):
        webServerInstances, dbInstances = self.getInstances()
        env.user = 'ubuntu'
        env.key_filename = [
            'keys/test-keypair'
        ]
        
        # TODO: run with non-root priveleges
        with settings(host_string=webServerInstances[0]['public_dns_name']):
            with cd("/stamped"):
                sudo('. bin/activate && python /stamped/stamped/sites/stamped.com/bin/crawler/crawler.py', pty=False)

