#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import config, json, os, pickle, utils
from ADeploymentStack import ADeploymentStack
from errors import Fail

class LocalDeploymentStack(ADeploymentStack):
    def __init__(self, name, parent):
        ADeploymentStack.__init__(self, name, parent.options)
        self.parent = parent
        self.env = parent.env
        self.root = "/stamped"
        self.path = os.path.join(self.root, self.name)
        
        self.instances = config.getInstances()
        
        index = 30000
        for instance in self.instances:
            instance['stack_name'] = self.name
            
            # ensure each mongod instance will have a unique port
            if 'mongodb' in instance:
                instance['mongodb']['port'] = index
                index += 2000
    
    def create(self):
        self.delete()
        os.system('mkdir -p %s' % self.path)
        
        for instance in self.instances:
            instance_path = self._get_instance_path(instance)
            os.system('mkdir -p %s' % instance_path)
            instance_bootstrap_path = os.path.join(instance_path, 'bootstrap')
            instance_bootstrap_init_path = os.path.join(instance_bootstrap_path, 'init.py')
            
            params_str = self._encode_params(instance)
            
            self.local('git clone git@github.com:Stamped/stamped-bootstrap.git %s' % instance_bootstrap_path)
            self.local('python %s "%s"' % (instance_bootstrap_init_path, params_str))
        
        self.init()
    
    def init(self):
        dbs = filter(lambda instance: 'db' in instance['roles'], self.instances)
        
        members = []
        for index in xrange(len(dbs)):
            db = dbs[index]
            
            members.append({
                '_id'  : index, 
                'host' : 'localhost:%s' % db['mongodb']['port']
            })
        
        for instance in self.instances:
            if 'replSet' in instance:
                replSet = {
                    '_id' : instance['replSet'], 
                    'members' : members
                }
                
                params_str = self._encode_params(replSet)
                instance_path = self._get_instance_path(instance)
                instance_init_path = os.path.join(instance_path, 'bootstrap/bin/init.py')
                
                self.local('python %s "%s"' % (instance_init_path, params_str))
    
    def update(self):
        for instance in self.instances:
            instance_path = self._get_instance_path(instance)
            instance_update_path = os.path.join(instance_path, 'bootstrap/bin/update.py')
            
            self.local('python %s' % instance_update_path)
    
    def _encode_params(self, params):
        return json.dumps(params).replace('"', "'")
    
    def _get_instance_path(self, instance):
        return os.path.join(self.path, instance['name'])
    
    def delete(self):
        if os.path.exists(self.path):
            utils.log("deleting stack '%s' at '%s'" % (self.name, self.path))
            
            # delete all instances
            for instance in self.instances:
                instance_path = self._get_instance_path(instance)
                instance_bootstrap_path = os.path.join(instance_path, 'bootstrap')
                instance_bootstrap_delete_path = os.path.join(instance_bootstrap_path, 'destroy.py')
                
                if os.path.exists(instance_bootstrap_delete_path):
                    params_str = pickle.dumps(instance)
                    self.local('python %s "%s"' % (instance_bootstrap_delete_path, params_str), show_cmd=False)
            
            self.local('rm -rf %s' % self.path)
            assert not os.path.exists(self.path)
    
    def describe(self):
        raise NotImplementedError
    
    def describe_events(self):
        raise NotImplementedError
    
    def connect(self):
        cmd = "cd %s" % self.path
        utils.log(cmd)
        os.system(cmd)

