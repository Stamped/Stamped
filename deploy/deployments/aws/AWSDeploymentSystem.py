#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import re, os
from utils import log, shell, AttributeDict
from ..DeploymentSystem import DeploymentSystem
from errors import Fail
from AWSDeploymentStack import AWSDeploymentStack

class AWSDeploymentSystem(DeploymentSystem):
    def __init__(self, name, options):
        self.commonOptions = '--headers'
        DeploymentSystem.__init__(self, name, options, AWSDeploymentStack)
    
    def _init_env(self):
        environ = AttributeDict(os.environ)
        curdir = os.path.dirname(os.path.abspath(__file__))
        environ.CLOUDFORMATION_ROOT = os.path.join(curdir, "cloudformation")
        environ.CLOUDFORMATION_TEMPLATE_FILE = os.path.join(environ.CLOUDFORMATION_ROOT, "stamped-cloudformation-dev.template")
        environ.AWS_CLOUDFORMATION_HOME = os.path.join(environ.CLOUDFORMATION_ROOT, "aws")
        environ.AWS_CREDENTIAL_FILE = os.path.join(environ.CLOUDFORMATION_ROOT, "credentials.txt")
        environ.PATH = environ.PATH + ':' + environ.AWS_CLOUDFORMATION_HOME + '/bin' + ':' + curdir
        
        # note (tfischer): JAVA_HOME is known to be incorrect on Mac OS X with the default 
        # Java installation of 1.6... this is a hack to get around this and should work on 
        # all of our dev machines.
        # this blog post was useful in debugging this quirk: 
        #    http://www.johnnypez.com/design-development/unable-to-find-a-java_home-at-on-mac-osx/
        java_home = os.path.join(os.path.dirname(os.path.abspath(shell("ls -l `which java` | sed 's/.*-> \\(.*\\)/\\1/'")[0])), "java_home")
        environ.JAVA_HOME = shell(java_home)[0]
        self.env = environ
        
        # find all stacks which haven't been deleted and add them to the initial 
        # set of stacks that this AWSDeploymentSystem knows about.
        (output, status) = shell(r'cfn-list-stacks | grep -v "DELETE_COMPLETE" | sed "s/STACK *[a-zA-Z0-9:.\/-]*[ \t]*\([A-Za-z0-9]*\) .*/\1/g"', self.env)
        
        if status == 0:
            stacks = output.split("\n")
            
            for stackName in stacks:
                self._stacks[stackName] = AWSDeploymentStack(stackName, self)
    
    def list_stacks(self, stackNameRegex=None, stackStatus=None):
        DeploymentSystem.list_stacks(self, stackNameRegex, stackStatus)
        
        if stackStatus is not None:
            self.local('cfn-list-stacks --stack-status %s %s' % (stackStatus, self.commonOptions))
        else:
            self.local('cfn-list-stacks %s' % (self.commonOptions, ))

