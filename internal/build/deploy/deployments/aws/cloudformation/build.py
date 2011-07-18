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
OUTPUT              = 'stamped-cloudformation-dev'

WEBSERVER_IMAGEID   = 'ami-8c1fece5'
WEBSERVER_PORT      = '8888'
WEBSERVER_SIZE      = 't1.micro'
WEBSERVER_REGION    = 'us-east-1'
WEBSERVER_EBS       = True
WEBSERVER_OS        = 'Ubuntu 10.04'

DATABASE_IMAGEID    = 'ami-8c1fece5'
DATABASE_PORT       = '8888'
DATABASE_SIZE       = 't1.micro'
DATABASE_REGION     = 'us-east-1'
DATABASE_EBS        = True
DATABASE_OS         = 'Ubuntu 10.04'


###############################################################################
## USERDATA COMMANDS

"""
    Define commands for the server to run after initialization. This should be
    set as a list, broken up into groups that you want to separate with 
    Wait Handles. It is then combined with the actual Wait Handles below.
"""

Ec2WebServerCommands = [
    """
    echo '>>>> Create keys for root to connect to GitHub'
    echo "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAvAzcTXbF0V/Pjja3b2Q9hsBQSHv8R8S6yoESb6CuR5HNzD3rIcfP9r2t3dJnVjeCZKx4JTadGXAr7ysVysGMLgbUMkngJ0bgnqkXPfLnKW07uYsrAF6Q1Gz79RSEIFfQP53p8XKpIkiRnbogM5RG2aIjJobuAsu0J8F9bGL6UfoRv1gGR0VcDbWAnp5SV8iJUBI0ULvVmdKKkFyeVHEZe2zjoplFr4b9jAUwDnNYpWobmsNoC4+1pw5fZRREJ32gCp4iYJIN5eJvylfpbhp6DtKPqrWmCEtIeVkS9pvqgVrlXMiaOPG972FuQJWiC5/iMApUlcTwCcAWkWfRTC4K1w== devbot@stamped.com" > ~/.ssh/id_rsa.pub
    echo "-----BEGIN RSA PRIVATE KEY-----" > ~/.ssh/id_rsa
    echo "MIIEogIBAAKCAQEAvAzcTXbF0V/Pjja3b2Q9hsBQSHv8R8S6yoESb6CuR5HNzD3r" >> ~/.ssh/id_rsa
    echo "IcfP9r2t3dJnVjeCZKx4JTadGXAr7ysVysGMLgbUMkngJ0bgnqkXPfLnKW07uYsr" >> ~/.ssh/id_rsa
    echo "AF6Q1Gz79RSEIFfQP53p8XKpIkiRnbogM5RG2aIjJobuAsu0J8F9bGL6UfoRv1gG" >> ~/.ssh/id_rsa
    echo "R0VcDbWAnp5SV8iJUBI0ULvVmdKKkFyeVHEZe2zjoplFr4b9jAUwDnNYpWobmsNo" >> ~/.ssh/id_rsa
    echo "C4+1pw5fZRREJ32gCp4iYJIN5eJvylfpbhp6DtKPqrWmCEtIeVkS9pvqgVrlXMia" >> ~/.ssh/id_rsa
    echo "OPG972FuQJWiC5/iMApUlcTwCcAWkWfRTC4K1wIBIwKCAQAVfdAI2l/AKDT6T2Vr" >> ~/.ssh/id_rsa
    echo "0PEWtuSakdOwbkE7tvrK7crGWc5gfBrfSgkjg2RT3YgnHElql14wI3+rIsMxRsCp" >> ~/.ssh/id_rsa
    echo "dTSXi8B6xp1GUT4+BLIy9zBcgYMrJdkHW0PAgXvhfrADskOvf8L3Bcovzcd/vYAF" >> ~/.ssh/id_rsa
    echo "5Q9pVFvJ44jqYGxcUKCerDnde3fmxRqmZT96NnY2VQcDXJWOs4Z0n5cN5caobZ4Q" >> ~/.ssh/id_rsa
    echo "rFnOa23YbY0EFsUrrl1cFsfxy0LhXWJFIS38SaIQ2RNIxMVgOGvelN6aah1hROn2" >> ~/.ssh/id_rsa
    echo "sYRbiYXpGEIGU6xsOtBY79SAX4NYIhFfJuCACQyQp8Iq+QXolggl0NkK0jY2blNt" >> ~/.ssh/id_rsa
    echo "MiirAoGBAPAjjWUlJVTvRoVIygiWEVNW2uJOjl2MfkO/LgYOzlczpz87QRMEfeBD" >> ~/.ssh/id_rsa
    echo "jz6CyqNCsiJZwW/1tdcjwkpBNPuVIHFHjPTv0VBZ852YTy0Z5vga681VRbNiDP7T" >> ~/.ssh/id_rsa
    echo "Jkltgoft8S4fBYZ/WvFaqhq1Mk/k5hMVLEd8mnVEzCG5NWUTN0gzAoGBAMh4jffy" >> ~/.ssh/id_rsa
    echo "KhuxEnD6bExkTRlYlHmFuQ5TubyPb3EzvrB5maNBmaDHQeAKQECl4V/fBXANENw4" >> ~/.ssh/id_rsa
    echo "94wjx8sQc9/Vo2+5I32VKiHEzlEe7b0lojvS826d27Du4iTzMCp+5t8wJfn6mPu5" >> ~/.ssh/id_rsa
    echo "AqA0aCWZp28utttnvUXORw+mRJp77RI9f97NAoGAUlVVDLxHUFIJjMh/yG33T8YB" >> ~/.ssh/id_rsa
    echo "5zDgWpaRsNPVQ+fRt39sirU64fLpVDRroGdbayzPXDwHzp1i6q0sq76V0pmHd0u7" >> ~/.ssh/id_rsa
    echo "TKn+nzTIjc3SANWuRm+hTbbWEZ3107YbwWdf9BcQ3Jzr85lhAkr4fi9+9tIi/zp1" >> ~/.ssh/id_rsa
    echo "lNpDleuzs8p4tPClPVMCgYEAg7zvlE6t9PC0WN8T96+gYRzz2tQ3x5Ya+EEAFzCh" >> ~/.ssh/id_rsa
    echo "4a7+j9qmyL10bqemkOIJIb5xSaIvpqkXs9z/orMKUUM/g+6w7CAxoSmO5NnPbasE" >> ~/.ssh/id_rsa
    echo "NfEGXqI/6UyF+wY1mETDmfsRpEWXu1xSLsNaYdoAUGCGyrHix3js3mXykWdhRoAv" >> ~/.ssh/id_rsa
    echo "dScCgYEAxOhXQNfCBQPBiVaApYCblNb0ASMh9gQyh5ZVhdcGu84qpTTxt2cIOV2p" >> ~/.ssh/id_rsa
    echo "ylKJVSS3R3bzPw3goGkvFL0e7Mlzr7uwj70pGqw1kXzbe4pLC1GE3PC4QlvPA8lE" >> ~/.ssh/id_rsa
    echo "WCy7/RohwIRd02/7s7UUW118xQYcrT27o/4BJpNd1uWsUT07BgI=" >> ~/.ssh/id_rsa
    echo "-----END RSA PRIVATE KEY-----" >> ~/.ssh/id_rsa
    echo "" >> ~/.ssh/id_rsa
    
    echo '>>>> Set permissions for keys'
    chmod 600 ~/.ssh/id_rsa
    chmod 644 ~/.ssh/id_rsa.pub
    
    echo '>>>> Install git'
    apt-get -y install git-core
    
    echo '>>>> Set bash to ignore errors, then run ssh so that clone command ignores validation of URL'
    set +e
    ssh -o StrictHostKeyChecking=no git@github.com
    set -e
    
    echo '>>>> Clone repo'
    git clone git@github.com:Stamped/stamped-bootstrap.git /bootstrap
    """,
    """
    echo '>>>> Running init script'
    bash /bootstrap/init.sh &> /bootstrap/log
    """
]

Ec2WebServerUserData = cloudformation.EncodeUserData('#!/bin/bash -ex')
Ec2WebServerUserData += cloudformation.AddWaitHandle('1CreateInstanceWaitHandle')
Ec2WebServerUserData += cloudformation.EncodeUserData(Ec2WebServerCommands[0])
Ec2WebServerUserData += cloudformation.AddWaitHandle('2CloneRepoWaitHandle')
Ec2WebServerUserData += cloudformation.EncodeUserData(Ec2WebServerCommands[1])
Ec2WebServerUserData += cloudformation.AddWaitHandle('3RunInitWaitHandle')


###############################################################################
## CLOUDFORMATION TEMPLATE

t = cloudformation.Template()
t.Description = 'Stamped CloudFormation Script (v1)'


## Outputs
t.Outputs.add('InstanceId',
              Description='InstanceId of the EC2 WebServer instance',
              Value={'Ref': 'Ec2WebServerInstance'})

t.Outputs.add('AZ',
              Description='Availability Zone of the EC2 WebServer instance',
              Value={'Fn::GetAtt': ['Ec2WebServerInstance', 'AvailabilityZone']})


## Parameters
t.Parameters.add('InstanceType',
                 Description='Type of EC2 instance to launch',
                 Type='String',
                 Default='m1.small')
t.Parameters.add('WebServerPort',
                 Description='TCP/IP port of the web server',
                 Type='String',
                 Default=WEBSERVER_PORT)
t.Parameters.add('KeyName',
                 Description='Name of an existing EC2 KeyPair to enable SSH access to the instance',
                 Type='String',
                 Default=KEYPAIR)

## Resources
t.Resources.add('Ec2WebServerInstance',
    Type='AWS::EC2::Instance',
    Properties={'SecurityGroups': [{'Ref': 'Ec2WebServerSecurityGroup'}],'ImageId': {'Ref': 'ImageId'},
                'KeyName': {'Ref': 'KeyName'},
                'ImageId': cloudformation.GetAMI(size=WEBSERVER_SIZE, 
                                                 region=WEBSERVER_REGION, 
                                                 software=WEBSERVER_OS, 
                                                 ebs=WEBSERVER_EBS),
                'InstanceType': WEBSERVER_SIZE,
                'Tags': [
                        {'Key': 'stamped:family', 'Value': 'WebServer'},
                        {'Key': 'stamped:server:role', 'Value': 'API'}],
                 'UserData': {'Fn::Base64': {'Fn::Join': ["", Ec2WebServerUserData]}}
    })

t.Resources.add('Ec2WebServerSecurityGroup',
    Type='AWS::EC2::SecurityGroup',
    Properties={
        'GroupDescription': 'Enable SSH and HTTP access on the inbound port',
        'SecurityGroupIngress': [{'IpProtocol': 'tcp',
                                  'FromPort': '22',
                                  'ToPort': '22',
                                  'CidrIp': '0.0.0.0/0'
                                 },
                                 {'IpProtocol': 'tcp',
                                  'FromPort': {'Ref': 'WebServerPort'},
                                  'ToPort': {'Ref': 'WebServerPort'},
                                  'CidrIp': '0.0.0.0/0'}
                                ]})

# The wait handlers should be named so that they are run in alphabetical order.
t.Resources.add('3RunInitWaitHandle',
    Type='AWS::CloudFormation::WaitConditionHandle',
    Properties={})

t.Resources.add('3RunInit',
    Type='AWS::CloudFormation::WaitCondition',
    DependsOn='Ec2WebServerInstance',
    Properties={
        'Handle': {'Ref': '3RunInitWaitHandle'},
        'Timeout': '600'})
        
t.Resources.add('2CloneRepoWaitHandle',
    Type='AWS::CloudFormation::WaitConditionHandle',
    Properties={})

t.Resources.add('2CloneRepo',
    Type='AWS::CloudFormation::WaitCondition',
    DependsOn='Ec2WebServerInstance',
    Properties={
        'Handle': {'Ref': '2CloneRepoWaitHandle'},
        'Timeout': '600'})
        
t.Resources.add('1CreateInstanceWaitHandle',
    Type='AWS::CloudFormation::WaitConditionHandle',
    Properties={})

t.Resources.add('1CreateInstance',
    Type='AWS::CloudFormation::WaitCondition',
    DependsOn='Ec2WebServerInstance',
    Properties={
        'Handle': {'Ref': '1CreateInstanceWaitHandle'},
        'Timeout': '600'})
        
## Produce the file
t.dumps(OUTPUT)
