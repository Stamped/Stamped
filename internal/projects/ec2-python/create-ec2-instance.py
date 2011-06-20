#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

"""
This script dynamically creates a number of EC2 instances and then runs a setup
script on each instance. Currently the setup script installs git and connects 
to GitHub to download the Stamped repository. 

Still to do:

* Allow the user to pass in the images they wish to create via a variable
  (instead of hard-coding).
  
* Pull out keys so they're not stored in the repo.

* Don't terminate the instance automatically, but add an option to let the user
  choose if they want it to terminate.
  
* Look into a better way of handling the connection to GitHub. Currently we're
  not password-protecting the id_rsa file and we're not validating the IP 
  address for GitHub. 
  
* Fix pexpect code. It works (in that it bypasses the need to verify the 
  connection), but it doesn't actually upload the file.
  
* Fix port permissions on EC2. Currently, setting the port for our IP address 
  doesn't actually work - still falling under 0.0.0.0 hierarchy. 

"""

import os
import time
import urllib
import re
import pexpect

from datetime import datetime
from boto.ec2.connection import EC2Connection

#------------------------------------------------------------------------------

# IDENTIFIERS
AWS_ACCESS_KEY_ID = 'AKIAIXLZZZT4DMTKZBDQ'
AWS_SECRET_ACCESS_KEY = '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'

KEY_NAME = 'test-keypair'

SSH_OPTS = '-i keys/test-keypair'

# This dictionary should contain the image ids you want to 
# benchmark as the keys, for each one the value should be
# the list of image types to test it on
IMAGES = {
    #'ami-5647a33f':    # Fedora Base 32 bit
    #    [ 'm1.small'   #   - Small 
    #    ],
    'ami-8c1fece5':
        [ 't1.micro']
}

#------------------------------------------------------------------------------

def run_instance(conn, image, instancetype):
    print "Starting the instance"
    reservation = conn.run_instances(image, instance_type=instancetype, key_name=KEY_NAME)
    instance = reservation.instances[0]
    
    while not instance.update() == 'running':
        time.sleep(5)
    
    print "Instance created: %s" % instance.dns_name
    
    # Wait a moment, just to make sure the instance is ready to run
    print "Pausing before we begin...."
    time.sleep(30)
    
    try:
        print "Connecting to %s" % instance.dns_name 
        # Use pexpect to connect to host
        child = pexpect.spawn("scp %s setup-instance.sh ec2-user@%s:/home/ec2-user/" % 
                               (SSH_OPTS, instance.dns_name))
        child.expect('Are you sure you want to continue connecting (yes/no)?')
        child.sendline('yes')
        child.expect(pexpect.EOF)
        
        # Setup the server
        print "Sending scripts and keys" 
        os.system( "scp %s setup-instance.sh ec2-user@%s:/home/ec2-user/" % 
                   (SSH_OPTS, instance.dns_name))
        os.system( "scp %s keys/id_rsa ec2-user@%s:/home/ec2-user/.ssh/" % 
                   (SSH_OPTS, instance.dns_name))
        os.system( "scp %s keys/id_rsa.pub ec2-user@%s:/home/ec2-user/.ssh/" % 
                   (SSH_OPTS, instance.dns_name))
        
        print "Running the setup script" 
        os.system("ssh -t %s ec2-user@%s \"bash /home/ec2-user/setup-instance.sh\"" % 
                   (SSH_OPTS, instance.dns_name))
        
        print "Run completed"
        
    except Exception, e:
        print e
    
    print "Terminating the instance in 30 seconds..." 
    time.sleep(30)
    
    if instance.root_device_type == 'ebs': 
        instance.stop()
    instance.terminate()
    
def main():
    # Get current IP address
    checkIP = urllib.urlopen("http://checkip.dyndns.org").read()
    our_ip  = re.findall(r'Current IP Address: (\d+\.\d+\.\d+\.\d+)', checkIP)[0]
    print "Current IP: %s" % our_ip
    
    conn = EC2Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    try:
        # Authorize local IP to connect to the instances
        conn.authorize_security_group('default', 
            ip_protocol='tcp', 
            from_port='22', 
            to_port='22', 
            cidr_ip='%s/32' % our_ip)
        
        # Run for images defined above
        for image in IMAGES:
            for instancetype in IMAGES[image]:  
                print 'Creating image %s on instance type %s' % (image, instancetype)
                run_instance(conn, image, instancetype)
        
    except Exception, e:
        print e
    finally:
        # Revoke authorization to our ip 
        conn.revoke_security_group('default', ip_protocol='tcp', from_port='22', to_port='22', cidr_ip='%s/32' % our_ip)

if __name__ == '__main__':
    main()