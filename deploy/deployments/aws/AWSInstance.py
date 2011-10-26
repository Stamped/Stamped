#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import base64, boto, convert, json, os, socket, time, utils
from boto.ec2.instance import Instance as BotoEC2Instance
from AInstance import AInstance
from errors import *

from fabric.operations import *
from fabric.api import *

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

def _getAMI(instanceType, region, software='Ubuntu 10.04', ebs=True):
    if software == 'Amazon' and ebs == True:
        return INSTANCE_AMI_AMAZON_EBS[region][INSTANCE_ARCHITECTURE[instanceType]]
    if software == 'Ubuntu 10.04' and ebs == True:
        return INSTANCE_AMI_UBUNTU_1004_EBS[region][INSTANCE_ARCHITECTURE[instanceType]]
    if software == 'Ubuntu 10.04' and ebs == False:
        return INSTANCE_AMI_UBUNTU_1004[region][INSTANCE_ARCHITECTURE[instanceType]]
    return False

INSTANCE_TYPE      = 'm1.large' #'t1.micro'
INSTANCE_REGION    = 'us-east-1'
INSTANCE_OS        = 'Ubuntu 10.04'
INSTANCE_EBS       = True
KEY_NAME           = 'test-keypair'

class AWSInstance(AInstance):
    def __init__(self, stack, configOrInstance):
        if isinstance(configOrInstance, BotoEC2Instance):
            self._instance = configOrInstance
            config = self._instance.tags
            
            def _fix_config(cfg):
                for elem in cfg:
                    val = cfg[elem]
                    
                    if isinstance(val, basestring):
                        try:
                            val = eval(val)
                            val = _fix_config(val)
                            cfg[elem] = val
                        except Exception:
                            pass
                return cfg
            
            config = _fix_config(config)
        else:
            self._instance = None
            config = configOrInstance
        
        AInstance.__init__(self, stack, config)
    
    @property
    def public_dns_name(self):
        self.update()
        return self._instance.public_dns_name
    
    @property
    def private_ip_address(self):
        self.update()
        return self._instance.private_ip_address
    
    @property
    def tags(self):
        self.update()
        
        if hasattr(self._instance, 'tags'):
            return self._instance.tags
        else:
            return None
    
    @property
    def state(self):
        if self._instance:
            return self._instance.state
        else:
            return None
    
    @property
    def instance_id(self):
        if self._instance:
            return self._instance.id
        else:
            return None
    
    @property
    def conn(self):
        return self.stack.conn
    
    def _create(self, block):
        assert self.state is None
        
        if 'placement' in self.config:
            placement = self.config.placement
        else:
            placement = None
        
        if 'instance_type' in self.config:
            instance_type = self.config.instance_type
        else:
            instance_type = INSTANCE_TYPE
        
        image = self._get_image(instance_type)
        
        security_groups = self._get_security_groups()
        user_data = self._get_user_data()
        key_name = KEY_NAME
        
        reservation = image.run(key_name=key_name, 
                                instance_type=instance_type, 
                                security_groups=security_groups, 
                                user_data=user_data, 
                                placement=placement)
        
        self._instance = reservation.instances[0]
    
    def _validate_port(self, port, desc=None, timeout=None):
        if desc is None:
            desc = "port %s" % (str(port))
        
        utils.log("[%s] waiting for %s to come online (this may take a few minutes)..." % (self, desc))
        sleepy_time = 2
        
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.public_dns_name, port))
                s.close()
                break
            except socket.error:
                if timeout is not None:
                    timeout -= sleepy_time
                    
                    if timeout <= 0:
                        msg = "[%s] timeout attempting to access port %d (%s)" % (self, port, desc)
                        utils.log(msg)
                        raise Exception(msg)
                
                time.sleep(sleepy_time)
        
        utils.log("[%s] %s is online" % (self, desc))
    
    def _post_create(self, block):
        # Check for SSH
        self._validate_port(22, desc="ssh service", timeout=40)
        
        if block:
            # Check for init to finish
            self._validate_port(8649, desc="init script / ganglia", timeout=1200)
            
            if 'db' in self.roles:
                # Check for mongo to finish
                self._validate_port(27017, desc="mongo", timeout=1000)
    
    def start(self):
        self.update()
        self._instance.start()
    
    def stop(self, force=False):
        self.update()
        self._instance.stop(force)
    
    def terminate(self):
        self.update()
        self._instance.terminate()
    
    def reboot(self):
        self.update()
        self._instance.reboot()
    
    def update(self, validate=False):
        if self._instance:
            self._instance.update(validate)
        else:
            raise NotInitializedError()
    
    def add_tag(self, key, value=None):
        if self._instance:
            self._instance.add_tag(key, value)
        else:
            raise NotInitializedError()
    
    def remove_tag(self, key, value=None):
        if self._instance:
            self._instance.remove_tag(key, value)
        else:
            raise NotInitializedError()
    
    def _get_security_groups(self):
        security_groups = [ ]
        
        for role in self.roles:
            security_groups.append(role.lower())
        
        return security_groups
    
    def _get_user_data(self):
        config = dict(self.config)
        for k in config:
            v = config[k]
            
            if isinstance(v, utils.AttributeDict):
                config[k] = dict(v)
        
        params = {
            # TODO: look at replacement of quotes
            'init_params' : json.dumps(config)
        }
        
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "userdata.sh")
        f = open(path, 'r')
        user_data = convert.parse_file(f, params)
        f.close()
        
        f2 = open('test', 'w')
        f2.write(user_data)
        f2.close()
        
        return user_data
        #user_data64 = base64.encodestring(user_data)
        #return user_data64
    
    def _get_image(self, instance_type):
        ami = _getAMI(instance_type, INSTANCE_REGION, INSTANCE_OS, INSTANCE_EBS)
        return self.conn.get_image(ami)
    
    #def __getattr__(self, name):
    #    if name in self.__dict__:
    #        return self.__dict__[name]
    #    else:
    #        return self[name]
    
    #def __getitem__(self, name):
    #    if name in self.__dict__:
    #        return self.__dict__[name]
    #    elif self._instance:
    #        return self._instance.__dict__[name]
    #    else:
    #        raise NotInitializedError()

