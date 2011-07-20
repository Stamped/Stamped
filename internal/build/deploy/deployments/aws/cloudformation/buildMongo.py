#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import cloudformation
import sys

###############################################################################
## VARIABLES
KEYPAIR             = 'test-keypair'
OUTPUT              = 'stamped-cloudformation-mongo'

DATABASE_PORT       = '27017'
DATABASE_SIZE       = 't1.micro'
DATABASE_REGION     = 'us-east-1'
DATABASE_ZONES      = ['us-east-1a']
DATABASE_EBS        = True
DATABASE_OS         = 'Ubuntu 10.04'

DATABASE_MIN_NODES  = '3'
DATABASE_MAX_NODES  = '3'
DATABASE_PREF_NODES = '3'


###############################################################################
## USERDATA COMMANDS

"""
    Define commands for the server to run after initialization. This should be
    set as a list, broken up into groups that you want to separate with 
    Wait Handles. It is then combined with the actual Wait Handles below.
"""




###############################################################################
## CLOUDFORMATION TEMPLATE

t = cloudformation.Template()
t.Description = 'Stamped CloudFormation Script (v1)'


## Resources

t.Resources.add('Ec2DatabaseClusterConfig',
    Type='AWS::AutoScaling::LaunchConfiguration',
    Properties={
        'SecurityGroups': [{'Ref': 'Ec2DatabaseClusterSecurityGroup'}],
        'ImageId': cloudformation.GetAMI(size=DATABASE_SIZE, 
                                         region=DATABASE_REGION, 
                                         software=DATABASE_OS, 
                                         ebs=DATABASE_EBS),
        'InstanceType': DATABASE_SIZE,
        'KeyName': KEYPAIR
    }
)

t.Resources.add('Ec2DatabaseCluster',
    Type='AWS::AutoScaling::AutoScalingGroup',
    Properties={
        'AvailabilityZones': DATABASE_ZONES,
        'LaunchConfigurationName': {'Ref': 'Ec2DatabaseClusterConfig'},
        'MinSize': DATABASE_MIN_NODES,
        'MaxSize': DATABASE_MAX_NODES,
        'DesiredCapacity': DATABASE_PREF_NODES
    }
)

t.Resources.add('Ec2DatabaseClusterSecurityGroup',
    Type='AWS::EC2::SecurityGroup',
    Properties={
        'GroupDescription': 'Enable SSH and HTTP access on the inbound port',
        'SecurityGroupIngress': [{'IpProtocol': 'tcp',
                                  'FromPort': '22',
                                  'ToPort': '22',
                                  'CidrIp': '0.0.0.0/0'},
                                 {'IpProtocol': 'tcp',
                                  'FromPort': DATABASE_PORT,
                                  'ToPort': DATABASE_PORT,
                                  'CidrIp': '0.0.0.0/0'}
                                ]})


## Produce the file
#t.dumps(OUTPUT)
