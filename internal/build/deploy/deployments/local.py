#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import re, os
from utils import log, logRaw, shell, AttributeDict
from ADeployment import ADeploymentSystem, ADeploymentStack
from errors import Fail

class AWSDeploymentSystem(ADeploymentSystem):
    def __init__(self, name):
        ADeploymentSystem.__init__(self, name)
        self._stacks = { }
        self.commonOptions = '--headers'
        self._init_env()
    
    def _init_env(self):
        #env = AttributeDict(os.environ)
        env = os.environ
        env['CLOUDFORMATION_ROOT'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloudformation")
        env['CLOUDFORMATION_TEMPLATE_FILE'] = os.path.join(env['CLOUDFORMATION_ROOT'], "stamped-cloudformation-dev.template")
        env['AWS_CLOUDFORMATION_HOME'] = os.path.join(env['CLOUDFORMATION_ROOT'], "aws")
        env['AWS_CREDENTIAL_FILE'] = os.path.join(env['CLOUDFORMATION_ROOT'], "credentials.txt")
        env['PATH'] = env['PATH'] + ':' + env['AWS_CLOUDFORMATION_HOME'] + '/bin'
        
        # note (tfischer): JAVA_HOME is known to be incorrect on Mac OS X with the default 
        # Java installation of 1.6... this is a hack to get around this and should work on 
        # all of our dev machines.
        # this blog post was useful in debugging this quirk: 
        #    http://www.johnnypez.com/design-development/unable-to-find-a-java_home-at-on-mac-osx/
        java_home = os.path.join(os.path.dirname(os.path.abspath(shell("ls -l `which java` | sed 's/.*-> \\(.*\\)/\\1/'")[0])), "java_home")
        env['JAVA_HOME'] = shell(java_home)[0]
        self.env = env
        
        # find all stacks which haven't been deleted and add them to the initial 
        # set of stacks that this AWSDeploymentSystem knows about.
        (output, status) = shell(r'cfn-list-stacks | grep -v "DELETE_COMPLETE" | sed "s/STACK *[a-zA-Z0-9:.\/-]*[ \s]*\([A-Za-z0-9]*\) .*/\1/g"', self.env)
        
        if status == 0:
            stacks = output.split("\n")
            
            for stackName in stacks:
                self._stacks[stackName] = AWSDeploymentStack(stackName, self.env, self.commonOptions)
    
    def get_matching_stacks(self, stackNameRegex, unique=False):
        stacks = [ ]
        
        for stackName in self._stacks:
            if re.search(stackNameRegex, stackName):
                if len(stacks) > 0 and unique:
                    raise Fail("Error: stack name regex '%s' is not unique" % stackNameRegex)
                
                stacks.append(stackName)
        
        return stacks
    
    def create_stack(self, *args):
        for stackName in args:
            if stackName in self._stacks:
                raise Fail("Error: cannot create duplicate AWS stack '%s'" % stackName)
            
            stack = AWSDeploymentStack(stackName, self.env, self.commonOptions)
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
            log("'%s' contains %d stacks matching '%s':" % (self, len(stacks), stackNameRegex))
        else:
            stacks = self._stacks
            log("'%s' contains %d stacks:" % (self, len(stacks)))
        
        index = 1
        for (stackName, stack) in stacks.iteritems():
            log("%d) '%s'" % (index, stackName))
            index += 1
        
        if stackStatus is not None:
            self.local('cfn-list-stacks --stack-status %s %s' % (stackStatus, self.commonOptions))
        else:
            self.local('cfn-list-stacks %s' % (self.commonOptions, ))

class AWSDeploymentStack(ADeploymentStack):
    def __init__(self, name, env, commonOptions=""):
        ADeploymentStack.__init__(self, name)
        self.env = env
        self.commonOptions = commonOptions
   
    def create(self):
        self.local('cfn-create-stack %s --template-file %s' % (self.name, self.env['CLOUDFORMATION_TEMPLATE_FILE']))
    
    def delete(self):
        self.local('cfn-delete-stack %s --force' % (self.name, ))
    
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
            (result, status) = shell('cfn-describe-stack-events --stack-name %s | grep "%s *1CreateInstance .*CREATE_COMPLETE"' % (self.name, self.name))
            
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
        
        print "Default instance in stack %s has been initialized! Attempting to connect via ssh..." % (self.name, )
        os.system('connect.sh %s' % (self.name, ))

