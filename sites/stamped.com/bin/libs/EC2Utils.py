#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals
import copy, os, re, sys, utils

from pprint import pprint

class EC2Utils(object):
    
    def __init__(self):
        base  = os.path.dirname(os.path.abspath(__file__))
        root  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(base))))
        tools = os.path.join(base, 'ec2-api-tools')
        
        tools_path = os.path.join(tools, 'bin')
        
        self.env = os.environ
        self.env['PATH'] += ':%s' % tools_path
        self.env['EC2_HOME']        = tools
        self.env['JAVA_HOME']       = '/usr'
        self.env['EC2_PRIVATE_KEY'] = os.path.join(root, 'deploy/keys/pk-W7ITOSRSFD353R3K6MULWBZCDASTRG3L.pem')
        self.env['EC2_CERT']        = os.path.join(root, 'deploy/keys/cert-W7ITOSRSFD353R3K6MULWBZCDASTRG3L.pem')
    
    def get_tags(self):
        ret = utils.shell('ec2-describe-tags', self.env)
        
        if 0 != ret[1]:
            return None
        else:
            return ret[0]
    
    def get_local_instance_id(self):
        ret = utils.shell('wget -q -O - http://169.254.169.254/latest/meta-data/instance-id')
        
        if 0 != ret[1]:
            return None
        else:
            return ret[0]
    
    def get_stack(self, instance_id):
        ret = utils.shell('ec2-describe-tags | grep "%s[ \t]*stack"' % instance_id, self.env)
        
        if 0 != ret[1]:
            return None
        
        match = re.match('.*%s[ \t]*stack[ \t]*([a-zA-Z0-9_]*)[ \t]*' % instance_id, ret[0])
        if match is not None:
            return match.groups()[0]
        else:
            return None
    
    def get_instance_ids_in_stack(self, stack):
        ret = utils.shell('ec2-describe-tags | grep "stack[ \t]*%s$"' % stack, self.env)
        
        if 0 != ret[1]:
            return None
        else:
            out = []
            
            for row in ret[0].split('\n'):
                match = re.match('.*(i-[0-9a-zA-Z]*).*', row)
                if match is not None:
                    out.append(match.groups()[0])
            
            return out
    
    def get_instance_info(self, instance_id):
        ret = utils.shell('ec2-describe-instances %s' % instance_id, self.env)
        
        if 0 != ret[1]:
            return None
        
        return {
            'private_dns' : re.match('.*(ip-[0-9a-zA-Z.-]*internal).*', ret[0], re.DOTALL).groups()[0], 
            'public_dns'  : re.match('.*(ec2-[0-9a-zA-Z.-]*amazonaws\.com).*', ret[0], re.DOTALL).groups()[0], 
            'roles'       : eval(re.match('.*roles[ \t]*(\[[^\]]*\]).*', ret[0], re.DOTALL).groups()[0]), 
            'stack'       : re.match('.*stack[ \t]*([a-zA-Z0-9_]*).*', ret[0], re.DOTALL).groups()[0], 
            'name'        : re.match('.*name[ \t]*([a-zA-Z0-9_]*).*', ret[0], re.DOTALL).groups()[0], 
            'id'          : instance_id, 
        }
    
    def get_stack_info(self, instance_id=None):
        if instance_id is None:
            instance_id = self.get_local_instance_id()
        
        stack = self.get_stack(instance_id)
        ids = self.get_instance_ids_in_stack(stack)
        
        data  = {
            'instance' : {
                'id' : instance_id, 
            }, 
            'nodes' : {}
        }
        
        for cur_id in ids:
            info = self.get_instance_info(cur_id)
            name = info['name']
            data['nodes'][name] = info
            
            if cur_id.lower() == instance_id.lower():
                data['instance']['name'] = name
        
        return utils.AttributeDict(data)

"""
ec2 = EC2Utils()

print ec2.get_instance_ids_in_stack('waluigi')
print ec2.get_instance_info('i-b0ed82d0')

pprint(dict(ec2.get_stack_info('i-b0ed82d0')))
"""

