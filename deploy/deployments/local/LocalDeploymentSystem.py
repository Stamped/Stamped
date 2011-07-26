#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import copy, getpass, os, pickle, re, utils
from ..DeploymentSystem import DeploymentSystem
from errors import Fail
from LocalDeploymentStack import LocalDeploymentStack

class LocalDeploymentSystem(DeploymentSystem):
    def __init__(self, name, options):
        DeploymentSystem.__init__(self, name, options, LocalDeploymentStack)
    
    def _init_env(self):
        env = os.environ
        env['PYNODE_PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local")
        self.env = env
        
        user = getpass.getuser()
        self._config_path_dir = os.path.join(os.getenv("HOME"), ".stamped")
        self._config_path = os.path.join(self._config_path_dir, "local_stacks_config.py")
        
        if not os.path.exists(self._config_path_dir):
            os.system('mkdir -p %s' % self._config_path_dir)
        
        config = utils.getPythonConfigFile(self._config_path, pickled=True)
        for (stackName, params) in config.iteritems():
            #env = copy.deepcopy(self.env)
            self._stacks[stackName] = LocalDeploymentStack(stackName, self)
    
    def shutdown(self):
        self.saveConfigFile()
        DeploymentSystem.shutdown(self)
    
    def saveConfigFile(self):
        f = open(self._config_path, "w")
        f.write(pickle.dumps(self._stacks))
        f.close()

