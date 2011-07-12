#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from fabric.api import run, sudo
import os

def shell(cmd, customEnv=None):
    from subprocess import Popen, PIPE
    pp = Popen(cmd, shell=True, stdout=PIPE, env=customEnv)
    result = pp.stdout.read().strip()
    pp.kill()
    return result

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
java_home = os.path.join(os.path.dirname(os.path.abspath(shell("ls -l `which java` | sed 's/.*-> \\(.*\\)/\\1/'"))), "java_home")
env['JAVA_HOME'] = shell(java_home)

commonOptions = '--headers'

def local(cmd):
    print "[local] %s" % (cmd, )
    return shell(cmd, env)

def createStack(name):
    print local('cfn-create-stack %s --template-file %s' % (name, env['CLOUDFORMATION_TEMPLATE_FILE']))

def deleteStack(name):
    print local('cfn-delete-stack %s --force' % (name, ))

def describeStack(name=None):
    if name is not None:
        print local('cfn-describe-stacks --stack-name %s %s' % (name, commonOptions))
    else:
        print local('cfn-describe-stacks %s' % (commonOptions, ))

def describeStackEvents(name):
    print local('cfn-describe-stack-events --stack-name %s %s' % (name, commonOptions))

def listStacks(stackStatus=None):
    if stackStatus is not None:
        print local('cfn-list-stacks --stack-status %s %s' % (stackStatus, commonOptions))
    else:
        print local('cfn-list-stacks %s' % (commonOptions, ))

def createAndConnect(name):
    createStack(name)
    while True:
        result = local('cfn-describe-stack-events --stack-name %s | grep "%s *1CreateInstance .*CREATE_COMPLETE"' % (name, name))
        if len(result) > 5:
            break
        else:
            result = local('cfn-describe-stack-events --stack-name %s | grep "%s .*ROLLBACK.*"' % (name, name))
            if len(result) > 5:
                print "aborting connection because stack %s has been rolled back" % (name, )
                return 1
            
            result = local('cfn-describe-stack-events --stack-name %s | grep "%s .*DELETE.*"' % (name, name))
            if len(result) > 5:
                print "aborting connection because stack %s has been deleted" % (name, )
                return 1
            
            import time
            time.sleep(10)
    
    print "Default instance in stack %s has been initialized! Attempting to connect via ssh..." % (name, )
    os.system('connect.sh %s' % (name, ))
    return 0

def main():
    createAndConnect('StampedStagingStack0')
    listStacks()

# where all the magic starts
if __name__ == '__main__':
    main()

