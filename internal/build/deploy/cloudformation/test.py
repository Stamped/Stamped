#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from cloudformation import CloudFormation, CloudInit
import sys

webInit = CloudInit('testEc2')
webInit.add('bash /stamped-bootstrap/init.sh &> /stamped-bootstrap/log')

#print(webInit.get())

t = CloudFormation()

webSSH = t.buildSecurityGroupProperties(ipProtocol = 'tcp', fromPort = '22', toPort = '22', cidrIp = '0.0.0.0/0')
webHTTP = t.buildSecurityGroupProperties(ipProtocol = 'tcp', fromPort = '8888', toPort = '8888', cidrIp = '0.0.0.0/0') 
t.addEC2SecurityGroup('Ec2WebServerSecurityGroup', 'Open up basic ports', [webSSH, webHTTP])



t.addEC2Instance(instanceName = 'Ec2WebServerInstance', 
                securityGroups = ['Ec2WebServerSecurityGroup'], 
                imageId = 'ami-2ec83147', 
                instanceType = 't1.micro', 
                keyName = 'test-keypair',
                userData = webInit.get())

t.addEC2WaitHandle(waitName = 'testEc2', dependsOn = 'Ec2WebServerInstance')


print(t.build())
t.save('test')


