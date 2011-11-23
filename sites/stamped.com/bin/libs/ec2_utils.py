#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals
import aws, time, utils

from boto.exception         import EC2ResponseError
from boto.ec2.connection    import EC2Connection
from boto.ec2.elb           import ELBConnection
from collections            import defaultdict
from subprocess             import Popen, PIPE

def get_local_instance_id():
    ret = _shell('wget -q -O - http://169.254.169.254/latest/meta-data/instance-id')
    
    if 0 != ret[1]:
        return None
    else:
        return ret[0]

def get_stack(stack=None):
    if stack is not None:
        stack = stack.lower()
    
    conn = EC2Connection(aws.AWS_ACCESS_KEY_ID, aws.AWS_SECRET_KEY)
    
    reservations = conn.get_all_instances()
    instance_id  = get_local_instance_id()
    stacks       = defaultdict(list)
    cur_instance = None
    
    for reservation in reservations:
        for instance in reservation.instances:
            try:
                if instance.state == 'running':
                    stack_name = instance.tags['stack'].lower()
                    instance = AWSInstance(instance)
                    stacks[stack_name].append(instance)
                    
                    if stack is None and instance.instance_id == instance_id:
                        stack = stack_name
                        cur_instance = instance
            except:
                pass
    
    return utils.AttributeDict({
        'instance' : cur_instance, 
        'nodes'    : stacks[stack], 
    })

def get_elb(stack=None):
    stack = get_stack(stack)
    instance_ids = (instance.id for instance in stack.nodes)
    
    # get all ELBs
    conn = ELBConnection(aws.AWS_ACCESS_KEY_ID, aws.AWS_SECRET_KEY)
    elbs = conn.get_all_load_balancers()
    
    # attempt to find the ELB belonging to this stack's set of API servers
    for elb in elbs:
        for awsInstance in elb.instances: 
            if awsInstance.id in instance_ids:
                return elb
    
    return None

def _shell(cmd, env=None):
    utils.log(cmd)
    pp = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, env=env)
    delay = 0.01
    
    while pp.returncode is None:
        time.sleep(delay)
        delay *= 2
        if delay > 1:
            delay = 1
        
        pp.poll()
    
    output = pp.stdout.read().strip()
    return (output, pp.returncode)

class AWSInstance(object):
    """
        Small wrapper around boto.ec2.instance.Instance which makes it more 
        user friendly, easier to reference tags, etc.
    """
    
    def __init__(self, instance):
        assert instance is not None
        
        self._instance = instance
    
    @property
    def tags(self):
        self.update()
        
        if hasattr(self._instance, 'tags'):
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
            
            return utils.AttributeDict(_fix_config(self._instance.tags))
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
    
    def start(self):
        self.update()
        return self._instance.start()
    
    def stop(self, force=False):
        self.update()
        return self._instance.stop(force)
    
    def terminate(self):
        self.update()
        return self._instance.terminate()
    
    def reboot(self):
        self.update()
        return self._instance.reboot()
    
    def update(self, validate=False):
        if self._instance:
            num_retries = 0
            
            while True:
                try:
                    return self._instance.update(validate)
                except:
                    num_retries += 1
                    if num_retries >= 5:
                        raise
                    
                    time.sleep(1)
        else:
            raise NotInitializedError()
    
    def add_tag(self, key, value=None):
        if self._instance:
            num_retries = 0
            
            while True:
                try:
                    return self._instance.add_tag(key, value)
                except:
                    num_retries += 1
                    if num_retries >= 5:
                        raise
                    
                    time.sleep(2)
        else:
            raise NotInitializedError()
    
    def remove_tag(self, key, value=None):
        if self._instance:
            return self._instance.remove_tag(key, value)
        else:
            raise NotInitializedError()
    
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
    
    def _get_security_groups(self):
        return map(role.lower() for role in self.roles)
    
    def __getattr__(self, key):
        try:
            if key in self.__dict__:
                return self.__dict__[key]
        except:
            try:
                # TODO: make this less hacky...
                return eval("self._instance.%s" % key)
            except:
                return self.tags[key]
    
    def __str__(self):
        return "%s(%s.%s)" % (self.__class__.__name__, self.stack.name, self.name)

