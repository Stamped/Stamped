#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import copy, getpass, os, pickle, re, string, utils
from ADeployment import ADeploymentSystem, ADeploymentStack
from errors import Fail

class LocalDeploymentSystem(ADeploymentSystem):
    def __init__(self, name, options):
        ADeploymentSystem.__init__(self, name, options)
        
        self._stacks = { }
        self._init_env()
    
    def _init_env(self):
        env = os.environ
        env['PYNODE_PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local")
        self.env = env
        
        user = getpass.getuser()
        self._config_path_dir = os.path.join(os.getenv("HOME"), ".stamped")
        self._config_path = os.path.join(self._config_path_dir, "local.stacks.config.py")
        
        if not os.path.exists(self._config_path_dir):
            os.system('mkdir -p %s' % self._config_path_dir)
        
        config = utils.getPythonConfigFile(self._config_path)
        for (stackName, params) in config.iteritems():
            #env = copy.deepcopy(self.env)
            self._stacks.append(LocalDeploymentStack(stackName, params, env))
    
    def get_matching_stacks(self, stackNameRegex, unique=False):
        stacks = [ ]
        
        for stackName in self._stacks:
            if re.search(stackNameRegex, stackName):
                if len(stacks) > 0 and unique:
                    raise Fail("Error: stack name regex '%s' is not unique" % stackNameRegex)
                
                stacks.append(stackName)
        
        return stacks
    
    def create_stack(self, *args):
        #if 0 == len(self.options.params):
        #    raise Fail("%s.%s requires a PyNode config file to be passed via --params" % \
        #        (self, utils.getFuncName()))
        
        for stackName in args:
            if stackName in self._stacks:
                raise Fail("Error: cannot create duplicate Local stack '%s'" % stackName)
            
            stack = LocalDeploymentStack(stackName, self.options, self.env)
            stack.create()
            
            self._stacks[stackName] = stack
    
    def delete_stack(self, *args):
        for stackNameRegex in args:
            stacks = self.get_matching_stacks(stackNameRegex)
            
            for stackName in stacks:
                if stackName in self._stacks:
                    stack = self._stacks[stackName]
                    stack.delete()
                    
                    del self._stacks[stackName]
    
    def describe_stack(self, *args):
        for stackNameRegex in args:
            stacks = self.get_matching_stacks(stackNameRegex)
            
            for stackName in stacks:
                stack = self._stacks[stackName]
                stack.describe()
    
    def describe_stack_events(self, *args):
        for stackNameRegex in args:
            stacks = self.get_matching_stacks(stackNameRegex)
            
            for stackName in stacks:
                stack = self._stacks[stackName]
                stack.describe_events()
    
    def connect(self, *args):
        for stackNameRegex in args:
            stacks = self.get_matching_stacks(stackNameRegex)
            
            for stackName in stacks:
                stack = self._stacks[stackName]
                stack.connect()
    
    def list_stacks(self, stackNameRegex=None, stackStatus=None):
        if stackNameRegex is not None:
            stacks = self.get_matching_stacks(stackNameRegex)
            utils.log("'%s' contains %d stacks matching '%s':" % (self, len(stacks), stackNameRegex))
        else:
            stacks = self._stacks
            utils.log("'%s' contains %d stacks:" % (self, len(stacks)))
        
        index = 1
        for (stackName, stack) in stacks.iteritems():
            utils.log("%d) '%s'" % (index, stackName))
            index += 1
        
        # TODO: list stack info
        raise NotImplementedError

class LocalDeploymentStack(ADeploymentStack):
    def __init__(self, name, options, env):
        ADeploymentStack.__init__(self, name, options)
        self.env = env
        self.root = "/stamped"
        self.path = os.path.join(self.root, self.name)
        self.instances = utils.OrderedDict([
            ('dev0' : {
                'roles' : [ 'web_server', ], 
                'port_base' : '70217', 
            }), 
            ('db0' : {
                'roles' : [ 'db', ], 
                'mongodb' : {
                }, 
            }), 
        ])
   
    def create(self):
        self.delete()
        os.system('mkdir -p %s' % self.path)
        
        for (name, params) in self.instances.iteritems():
            instance_path = os.path.join(self.path, name)
            os.system('mkdir -p %s' % instance_path)
            instance_bootstrap_path = os.path.join(instance_path, 'bootstrap')
            instance_bootstrap_init_path = os.path.join(instance_bootstrap_path, 'init.py')
            
            #flatten = lambda v: v if not isinstance(v, (tuple, list)) else string.joinfields(v, ',')
            #params_str = string.joinfields(('%s=%s' % (k, flatten(v)) for k, v in params.iteritems()), ' ')
            params_str = pickle.dumps({ name : params })
            
            self.local('git clone git@github.com:Stamped/stamped-bootstrap.git %s' % instance_bootstrap_path)
            self.local('python %s %s' % (instance_bootstrap_init_path, params_str))
    
    def delete(self):
        if os.path.exists(self.path):
            utils.log("deleting stack '%s' at '%s'" % (self.name, self.path))
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

