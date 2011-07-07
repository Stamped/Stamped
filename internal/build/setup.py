#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

def shell(cmd, customEnv=None):
    from subprocess import Popen, PIPE
    pp = Popen(cmd, shell=True, stdout=PIPE, env=customEnv)
    result = pp.stdout.read().strip()
    return (pp.wait(), result)

def main():
    # assumes we're running on Ubuntu as root
    cmds = [
        r'echo "deb http://apt.opscode.com/ `lsb_release -cs`-0.10 main" | sudo tee /etc/apt/sources.list.d/opscode.list', 

        r'wget -qO - http://apt.opscode.com/packages@opscode.com.gpg.key | sudo apt-key add -', 
        r'apt-get update', 
        r'mkdir -p ~/.chef', 
        r'cp /etc/chef/validation.pem /etc/chef/webui.pem ~/.chef', 
        r'chown -R $USER ~/.chef', 
        r'cd /stamped/internal/build/deploy/chef && chef-solo -c solo.rb', 
    ]
    
    for cmd in cmds:
        print cmd
        (resultcode, stdout) = shell(cmd)
        
        if resultcode != 0:
            print "Error running command '%s'" % cmd
            print stdout
            
            import sys
            sys.exit(resultcode)

if __name__ == '__main__':
    main()

