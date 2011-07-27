#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import re, os, utils
from ..DeploymentSystem import DeploymentSystem
from errors import Fail
from AWSDeploymentStack import AWSDeploymentStack
from boto.ec2.connection import EC2Connection

AWS_ACCESS_KEY_ID = 'AKIAIXLZZZT4DMTKZBDQ'
AWS_SECRET_KEY = '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'

class AWSDeploymentSystem(DeploymentSystem):
    def __init__(self, name, options):
        self.commonOptions = '--headers'
        DeploymentSystem.__init__(self, name, options, AWSDeploymentStack)
    
    def _get_security_group(self, name):
        security_groups = self.conn.get_all_security_groups()
        
        for sg in security_groups:
            if sg.name == name:
                return sg
        
        return None
    
    def _init_security_groups(self):
        ssh_rule = {
            'ip_protocol' : 'tcp', 
            'from_port'   : 22, 
            'to_port'   : 22, 
        }
        
        groups = [
            {
                'name' : 'db', 
                'desc' : 'Database security group', 
                'rules' : [
                    ssh_rule, 
                    {
                        'ip_protocol' : 'tcp', 
                        'from_port'   : 27017, 
                        'to_port'     : 27017, 
                    }, 
                    #{
                    #    'src_group' : 'webserver', 
                    #}, 
                    #{
                    #    'src_group' : 'crawler', 
                    #}, 
                ], 
            }, 
            {
                'name' : 'webserver', 
                'desc' : 'WebServer security group', 
                'rules' : [
                    ssh_rule, 
                    {
                        'ip_protocol' : 'tcp', 
                        'from_port'   : 5000, 
                        'to_port'     : 5000, 
                    }, 
                ], 
            }, 
            {
                'name' : 'crawler', 
                'desc' : 'Crawler security group', 
                'rules' : [
                    ssh_rule, 
                ], 
            }, 
        ]
        
        for group in groups:
            name = group['name']
            sg = self._get_security_group(name)
            
            if sg is None:
                self.conn.create_security_group(name, group['desc'])
        
        for group in groups:
            name = group['name']
            sg = self._get_security_group(name)
            
            for rule in group['rules']:
                ret = sg.authorize(**rule)
                assert ret
    
    def _init_env(self):
        self.conn = EC2Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)
        self._init_security_groups()
        
        self.env = utils.AttributeDict(os.environ)
        reservations = self.conn.get_all_instances()
        stacks = { }
        
        for reservation in reservations:
            for instance in reservation.instances:
                if hasattr(instance, 'tags') and 'stack' in instance.tags:
                    stackName = instance.tags['stack']
                    
                    if stackName in stacks:
                        stacks[stackName].append(instance)
                    else:
                        stacks[stackName] = [ instance ]
        
        utils.log("%d stacks exist" % len(stacks))
        index = 0
        
        for stackName in stacks:
            utils.log("%d) %s" % (index, stackName))
            index += 1
            
            instances = stacks[stackName]
            self._stacks[stackName] = AWSDeploymentStack(stackName, self, instances)
    
    def list_stacks(self, stackNameRegex=None, stackStatus=None):
        DeploymentSystem.list_stacks(self, stackNameRegex, stackStatus)
        
        #if stackStatus is not None:
        #    self.local('cfn-list-stacks --stack-status %s %s' % (stackStatus, self.commonOptions))
        #else:
        #    self.local('cfn-list-stacks %s' % (self.commonOptions, ))

