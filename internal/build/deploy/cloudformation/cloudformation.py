#!/usr/bin/env python

__author__ = "Richard Crowley, Kevin Palms"
__version__ = "0.0.0"
__copyright__ = "Copyright 2011 DevStructure"
__license__ = "TODO"

"""
Modified from Crowley's tools for creating CloudFormation templates.

http://devstructure.github.com/python-cloudformation/python-cloudformation.7.html
https://github.com/devstructure/python-cloudformation#readme

COPYRIGHT:
    Copyright 2011 DevStructure. All rights reserved.
    
    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:
    
        1.  Redistributions of source code must retain the above copyright
            notice, this list of conditions and the following disclaimer.
    
        2.  Redistributions in binary form must reproduce the above
            copyright notice, this list of conditions and the following
            disclaimer in the documentation and/or other materials provided
            with the distribution.
    
    THIS SOFTWARE IS PROVIDED BY DEVSTRUCTURE ``AS IS'' AND ANY EXPRESS
    OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL DEVSTRUCTURE OR CONTRIBUTORS BE LIABLE
    FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
    THE POSSIBILITY OF SUCH DAMAGE.
    
    The views and conclusions contained in the software and documentation
    are those of the authors and should not be interpreted as representing
    official policies, either expressed or implied, of DevStructure.

"""

from collections import defaultdict
import json


INSTANCE_ARCHITECTURE = {
    "t1.micro"    : "64",
    "m1.small"    : "32",
    "m1.large"    : "64",
    "m1.xlarge"   : "64",
    "m2.xlarge"   : "64",
    "m2.2xlarge"  : "64",
    "m2.4xlarge"  : "64",
    "c1.medium"   : "32",
    "c1.xlarge"   : "64",
    "cc1.4xlarge" : "64"
}

INSTANCE_AMI_AMAZON_EBS = {
    "us-east-1"      : { "32" : "ami-8c1fece5", "64" : "ami-8e1fece7" },
    "us-west-1"      : { "32" : "ami-c9c7978c", "64" : "ami-cfc7978a" },
    "eu-west-1"      : { "32" : "ami-37c2f643", "64" : "ami-31c2f645" },
    "ap-southeast-1" : { "32" : "ami-66f28c34", "64" : "ami-60f28c32" },
    "ap-northeast-1" : { "32" : "ami-9c03a89d", "64" : "ami-a003a8a1" }
}

INSTANCE_AMI_UBUNTU_1004 = {
    "us-east-1"      : { "32" : "ami-e4d42d8d", "64" : "ami-04c9306d" },
    "us-west-1"      : { "32" : "ami-991c4edc", "64" : "ami-f11d4fb4" },
    "eu-west-1"      : { "32" : "ami-3693a542", "64" : "ami-8293a5f6" },
    "ap-southeast-1" : { "32" : "ami-76c4bd24", "64" : "ami-c0c4bd92" },
    "ap-northeast-1" : { "32" : "ami-fe49e3ff", "64" : "ami-304ee431" }
}

INSTANCE_AMI_UBUNTU_1004_EBS = {
    "us-east-1"      : { "32" : "ami-2cc83145", "64" : "ami-2ec83147" },
    "us-west-1"      : { "32" : "ami-831d4fc6", "64" : "ami-8d1d4fc8" },
    "eu-west-1"      : { "32" : "ami-4090a634", "64" : "ami-4290a636" },
    "ap-southeast-1" : { "32" : "ami-e8c4bdba", "64" : "ami-eec4bdbc" },
    "ap-northeast-1" : { "32" : "ami-624ee463", "64" : "ami-644ee465" }
}


def _dict_property(name):
    """
    Return a property that gets and sets the given dictionary item.
    """
    def get(self):
        return self[name]
    def set(self, value):
        self[name] = value
    return property(get, set)
    
def EncodeUserData(string):
    data = []
    for line in string.split('\n'):
        data.append(line)
        data.append("\n")
    return data
    
def AddWaitHandle(handle):
    data = ["\n"]
    data.append("curl -X PUT -H 'Content-Type:' --data-binary '{\"Status\": \"SUCCESS\", \"Reason\": \"Instance is ready\", \"UniqueId\": \"stamped\", \"Data\": \"Done\"}' \"")
    data.append({"Ref": handle})
    data.append("\"\n")
    return data
    
def GetAMI(size, region, software='Ubuntu 10.04', ebs=True):
    if software == 'Amazon' and ebs == True:
        return INSTANCE_AMI_AMAZON_EBS[region][INSTANCE_ARCHITECTURE[size]]
    if software == 'Ubuntu 10.04' and ebs == True:
        return INSTANCE_AMI_UBUNTU_1004_EBS[region][INSTANCE_ARCHITECTURE[size]]
    if software == 'Ubuntu 10.04' and ebs == False:
        return INSTANCE_AMI_UBUNTU_1004[region][INSTANCE_ARCHITECTURE[size]]
    return False
        

class Template(defaultdict):
    """
    A CloudFormation template.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize a neverending tree of Template objects.
        """
        super(self.__class__, self).__init__(*args, **kwargs)
        self.default_factory = lambda: self.__class__(self.__class__)
        self.user_data = []

    # Shortcuts to the typical keys in a Template template.
    Description = _dict_property('Description')
    Mappings = _dict_property('Mappings')
    Outputs = _dict_property('Outputs')
    Parameters = _dict_property('Parameters')
    Resources = _dict_property('Resources')

    def add(self, key, *args, **kwargs):
        """
        Add an item to this CloudFormation template.  This is typically
        called on non-root Template objects, for example

            t.Parameters.add(...)

        to add an item to the Parameters object.
        """
        self[key] = self.__class__(*args, **kwargs)

    def dumps(self, saveAs):
        """
        Return a string representation of this CloudFormation template.
        """
        self['AWSTemplateFormatVersion'] = '2010-09-09'
        
        f = open(saveAs+'.template', 'w')
        json.dump(self, f, indent=2, sort_keys=True)
        f.close()
        
        print json.JSONEncoder(indent=2, sort_keys=True).encode(self)




class CloudFormation(object):
    
    def __init__(self):
        self._description = 'Stamped: CloudFormation Script'
        self._mappings = {}
        self._outputs = {}
        self._parameters = {}
        self._resources = {}
        
    def setDescription(self, string):
        self._description = string

    def buildSecurityGroupProperties(self, fromPort, toPort, ipProtocol = 'tcp', cidrIp = '0.0.0.0/0'):
        return {'IpProtocol': ipProtocol,
                'FromPort': fromPort,
                'ToPort': toPort,
                'CidrIp': cidrIp}

    def addEC2SecurityGroup(self, groupName, groupDescription, groupProperties):
        data = {'Type': 'AWS::EC2::SecurityGroup',
                'Properties': {
                    'GroupDescription': groupDescription,
                    'SecurityGroupIngress': groupProperties}
                }
        self._resources[groupName] = data
        
    def addEC2Instance(self, instanceName, securityGroups, imageId, instanceType, keyName, tags = [], userData = []):
        data = {'Type': 'AWS::EC2::Instance',
                'Properties': {
                    'SecurityGroups': securityGroups,
                    'ImageId': imageId,
                    'InstanceType': instanceType,
                    'Tags': tags,
                    'UserData': {'Fn::Base64': {'Fn::Join': ["", userData]}}
                    }
                }
        self._resources[instanceName] = data
        
    def addEC2WaitHandle(self, waitName, dependsOn, timeout = '600'):
        waitName = waitName + 'Wait'
        handleName = waitName + 'Handle'
        wait = {'Type': 'AWS::CloudFormation::WaitCondition',
                'DependsOn': dependsOn,
                'Properties': {
                    'Handle': {'Ref': handleName},
                    'Timeout': timeout
                    }
                }
        handle = {'Type': 'AWS::CloudFormation::WaitConditionHandle',
                'Properties': {}
                }
        self._resources[waitName] = wait
        self._resources[handleName] = handle
        
    def build(self):
        return {
            'AWSTemplateFormatVersion': '2010-09-09',
            'Description': self._description,
            'Resources': self._resources
        }
        
    def save(self, filename):
        f = open(filename + '.template', 'w')
        json.dump(self.build(), f, indent=2, sort_keys=True)
        f.close()
        


class CloudInit(object):

    def __init__(self, instanceName):
        self.instanceName = instanceName
        self._bootstrap = []
        self._createDefaultBootstrapScript()
    
    def add(self, cmd):
        self._bootstrap.append(cmd)
        self._bootstrap.append('\n')

    def get(self):
        return self._bootstrap
                
    def _createDefaultBootstrapScript(self, operatingSystem = 'Ubuntu'):
        
        self.add('#!/bin/bash -ex')
                
        # Create keys for root to connect to GitHub
        self.add('echo "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAvAzcTXbF0V/Pjja3b2Q9hsBQSHv8R8S6yoESb' \
                 '6CuR5HNzD3rIcfP9r2t3dJnVjeCZKx4JTadGXAr7ysVysGMLgbUMkngJ0bgnqkXPfLnKW07uYsrAF6Q' \
                 '1Gz79RSEIFfQP53p8XKpIkiRnbogM5RG2aIjJobuAsu0J8F9bGL6UfoRv1gGR0VcDbWAnp5SV8iJUBI' \
                 '0ULvVmdKKkFyeVHEZe2zjoplFr4b9jAUwDnNYpWobmsNoC4+1pw5fZRREJ32gCp4iYJIN5eJvylfpbh' \
                 'p6DtKPqrWmCEtIeVkS9pvqgVrlXMiaOPG972FuQJWiC5/iMApUlcTwCcAWkWfRTC4K1w== devbot@s' \
                 'tamped.com" > ~/.ssh/id_rsa.pub')
        self.add('echo "-----BEGIN RSA PRIVATE KEY-----" > ~/.ssh/id_rsa')
        self.add('echo "MIIEogIBAAKCAQEAvAzcTXbF0V/Pjja3b2Q9hsBQSHv8R8S6yoESb6CuR5HNzD3r" >> ~/.ssh/id_rsa')
        self.add('echo "IcfP9r2t3dJnVjeCZKx4JTadGXAr7ysVysGMLgbUMkngJ0bgnqkXPfLnKW07uYsr" >> ~/.ssh/id_rsa')
        self.add('echo "AF6Q1Gz79RSEIFfQP53p8XKpIkiRnbogM5RG2aIjJobuAsu0J8F9bGL6UfoRv1gG" >> ~/.ssh/id_rsa')
        self.add('echo "R0VcDbWAnp5SV8iJUBI0ULvVmdKKkFyeVHEZe2zjoplFr4b9jAUwDnNYpWobmsNo" >> ~/.ssh/id_rsa')
        self.add('echo "C4+1pw5fZRREJ32gCp4iYJIN5eJvylfpbhp6DtKPqrWmCEtIeVkS9pvqgVrlXMia" >> ~/.ssh/id_rsa')
        self.add('echo "OPG972FuQJWiC5/iMApUlcTwCcAWkWfRTC4K1wIBIwKCAQAVfdAI2l/AKDT6T2Vr" >> ~/.ssh/id_rsa')
        self.add('echo "0PEWtuSakdOwbkE7tvrK7crGWc5gfBrfSgkjg2RT3YgnHElql14wI3+rIsMxRsCp" >> ~/.ssh/id_rsa')
        self.add('echo "dTSXi8B6xp1GUT4+BLIy9zBcgYMrJdkHW0PAgXvhfrADskOvf8L3Bcovzcd/vYAF" >> ~/.ssh/id_rsa')
        self.add('echo "5Q9pVFvJ44jqYGxcUKCerDnde3fmxRqmZT96NnY2VQcDXJWOs4Z0n5cN5caobZ4Q" >> ~/.ssh/id_rsa')
        self.add('echo "rFnOa23YbY0EFsUrrl1cFsfxy0LhXWJFIS38SaIQ2RNIxMVgOGvelN6aah1hROn2" >> ~/.ssh/id_rsa')
        self.add('echo "sYRbiYXpGEIGU6xsOtBY79SAX4NYIhFfJuCACQyQp8Iq+QXolggl0NkK0jY2blNt" >> ~/.ssh/id_rsa')
        self.add('echo "MiirAoGBAPAjjWUlJVTvRoVIygiWEVNW2uJOjl2MfkO/LgYOzlczpz87QRMEfeBD" >> ~/.ssh/id_rsa')
        self.add('echo "jz6CyqNCsiJZwW/1tdcjwkpBNPuVIHFHjPTv0VBZ852YTy0Z5vga681VRbNiDP7T" >> ~/.ssh/id_rsa')
        self.add('echo "Jkltgoft8S4fBYZ/WvFaqhq1Mk/k5hMVLEd8mnVEzCG5NWUTN0gzAoGBAMh4jffy" >> ~/.ssh/id_rsa')
        self.add('echo "KhuxEnD6bExkTRlYlHmFuQ5TubyPb3EzvrB5maNBmaDHQeAKQECl4V/fBXANENw4" >> ~/.ssh/id_rsa')
        self.add('echo "94wjx8sQc9/Vo2+5I32VKiHEzlEe7b0lojvS826d27Du4iTzMCp+5t8wJfn6mPu5" >> ~/.ssh/id_rsa')
        self.add('echo "AqA0aCWZp28utttnvUXORw+mRJp77RI9f97NAoGAUlVVDLxHUFIJjMh/yG33T8YB" >> ~/.ssh/id_rsa')
        self.add('echo "5zDgWpaRsNPVQ+fRt39sirU64fLpVDRroGdbayzPXDwHzp1i6q0sq76V0pmHd0u7" >> ~/.ssh/id_rsa')
        self.add('echo "TKn+nzTIjc3SANWuRm+hTbbWEZ3107YbwWdf9BcQ3Jzr85lhAkr4fi9+9tIi/zp1" >> ~/.ssh/id_rsa')
        self.add('echo "lNpDleuzs8p4tPClPVMCgYEAg7zvlE6t9PC0WN8T96+gYRzz2tQ3x5Ya+EEAFzCh" >> ~/.ssh/id_rsa')
        self.add('echo "4a7+j9qmyL10bqemkOIJIb5xSaIvpqkXs9z/orMKUUM/g+6w7CAxoSmO5NnPbasE" >> ~/.ssh/id_rsa')
        self.add('echo "NfEGXqI/6UyF+wY1mETDmfsRpEWXu1xSLsNaYdoAUGCGyrHix3js3mXykWdhRoAv" >> ~/.ssh/id_rsa')
        self.add('echo "dScCgYEAxOhXQNfCBQPBiVaApYCblNb0ASMh9gQyh5ZVhdcGu84qpTTxt2cIOV2p" >> ~/.ssh/id_rsa')
        self.add('echo "ylKJVSS3R3bzPw3goGkvFL0e7Mlzr7uwj70pGqw1kXzbe4pLC1GE3PC4QlvPA8lE" >> ~/.ssh/id_rsa')
        self.add('echo "WCy7/RohwIRd02/7s7UUW118xQYcrT27o/4BJpNd1uWsUT07BgI=" >> ~/.ssh/id_rsa')
        self.add('echo "-----END RSA PRIVATE KEY-----" >> ~/.ssh/id_rsa')
        self.add('echo "" >> ~/.ssh/id_rsa')
        
        # Set permissions for keys
        self.add('chmod 600 ~/.ssh/id_rsa')
        self.add('chmod 644 ~/.ssh/id_rsa.pub')
        
        # Install git
        if operatingSystem == 'Ubuntu':
            self.add('apt-get -y install git-core')
        elif operatingSystem == 'Amazon':
            self.add('yum -y install git-core')
        else:
            return
        
        # Set bash to ignore errors, then run ssh so that clone command ignores validation of URL
        self.add('set +e')
        self.add('ssh -o StrictHostKeyChecking=no git@github.com')
        self.add('set -e')
        
        # Clone stamped-bootstrap repo
        self.add('git clone git@github.com:Stamped/stamped-bootstrap.git /stamped-bootstrap')
        
        # Add wait 
        waitName = self.instanceName + 'WaitHandle'
        self._bootstrap.append("curl -X PUT -H 'Content-Type:' --data-binary '{"\
            "\"Status\": \"SUCCESS\", \"Reason\": \"Instance is ready\", "\
            "\"UniqueId\": \"stamped\", \"Data\": \"Done\"}' \"")
        self._bootstrap.append({"Ref": waitName})
        self._bootstrap.append("\"\n")
        