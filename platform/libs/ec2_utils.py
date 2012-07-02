#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import keys.aws, utils
import datetime, json, os, time

from boto.route53.connection    import Route53Connection
from boto.exception             import EC2ResponseError
from boto.ec2.connection        import EC2Connection
from boto.ec2.elb               import ELBConnection
from collections                import defaultdict
from subprocess                 import Popen, PIPE

def get_local_instance_id():
    if not is_ec2():
        return None
    
    # cache instance id locally
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.instance.id.txt')
    
    if os.path.exists(path):
        f = open(path, 'r')
        instance_id = f.read()
        f.close()
        
        if len(instance_id) > 1 and instance_id.startswith('i-'):
            return instance_id
    
    ret = _shell('wget -q -O - http://169.254.169.254/latest/meta-data/instance-id')
    
    if 0 != ret[1]:
        return None
    else:
        f = open(path, 'w')
        f.write(ret[0])
        f.close()
        
        return ret[0]

def get_stack(stack=None):
    if not is_ec2():
        return None
    
    if stack is not None:
        stack = stack.lower()
    
    name = '.%s.stack.txt' % ('__local__' if stack is None else stack)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    
    if os.path.exists(path):
        modified = utils.get_modified_time(path)
        current  = datetime.datetime.utcnow() - datetime.timedelta(minutes=15)
        
        # only try to use the cached config if it's recent enough
        if modified >= current:
            try:
                f = open(path, 'r')
                info = json.loads(f.read())
                f.close()
                info = utils.AttributeDict(info)
                if info.instance is not None and len(info.nodes) > 0:
                    info.nodes = map(utils.AttributeDict, info.nodes)
                    return info
            except:
                utils.log("error getting cached stack info; recomputing")
                utils.printException()
    
    conn = EC2Connection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
    
    reservations = conn.get_all_instances()
    instance_id  = get_local_instance_id()
    stacks       = defaultdict(list)
    cur_instance = None
    
    for reservation in reservations:
        for instance in reservation.instances:
            try:
                if instance.state == 'running':
                    stack_name = instance.tags['stack']
                    
                    node = dict(
                        name=instance.tags['name'], 
                        stack=stack_name, 
                        roles=eval(instance.tags['roles']), 
                        instance_id=instance.id, 
                        public_dns_name=instance.public_dns_name, 
                        private_dns_name=instance.private_dns_name, 
                        private_ip_address=instance.private_ip_address, 
                    )
                    
                    stacks[stack_name].append(node)
                    
                    if stack is None and instance.id == instance_id:
                        stack = stack_name
                        cur_instance = node
            except:
                pass
    
    info = {
        'instance' : cur_instance, 
        'nodes'    : stacks[stack], 
    }
    
    f = open(path, 'w')
    f.write(json.dumps(info, indent=2))
    f.close()
    
    info = utils.AttributeDict(info)
    info.nodes = map(utils.AttributeDict, info.nodes)
    
    return info

def get_db_nodes():
    if not is_ec2():
        return None 
    
    # Check for local cache of db nodes
    name = '.__local__.db_nodes.txt'
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    
    if os.path.exists(path):
        modified = utils.get_modified_time(path)
        current  = datetime.datetime.utcnow() - datetime.timedelta(minutes=15)
        
        # only try to use the cached config if it's recent enough
        if modified >= current:
            try:
                f = open(path, 'r')
                nodes = json.loads(f.read())
                f.close()
                if len(nodes) > 0:
                    return map(utils.AttributeDict, nodes)
            except:
                utils.log("error getting cached stack info; recomputing")
                utils.printException()

    # Check current instance tags for specified db stack
    conn = EC2Connection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
    
    reservations = conn.get_all_instances()
    instance_id  = get_local_instance_id()
    cur_instance = None
    
    for reservation in reservations:
        for instance in reservation.instances:
            try:
                if instance.id == instance_id:
                    cur_instance = instance 
                    break
            except Exception:
                pass

    if cur_instance is None:
        raise Exception("DB nodes not found: %s" % instance_id)

    dbStackName = cur_instance.tags['stack']
    if 'db_stack' in cur_instance.tags:
        dbStackName = cur_instance.tags['db_stack']

    # Generate db nodes based on specified db stack
    dbStack = get_stack(dbStackName)

    dbNodes = set()
    for node in dbStack['nodes']:
        if 'db' in node.roles:
            dbNodes.add(node)

    if len(dbNodes) == 0:
        raise Exception("DB nodes not found for stack '%s'" % dbStackName)

    f = open(path, 'w')
    f.write(json.dumps(map(lambda x: dict(x), dbNodes), indent=2))
    f.close()

    return list(dbNodes)

def get_api_elb(stack=None):
    if not is_ec2():
        return None
    
    stack = get_stack(stack)
    api_nodes = filter(lambda n: 'apiServer' in n.roles, stack.nodes)
    api_ids   = (instance.instance_id for instance in api_ids)
    
    # get all ELBs
    conn = ELBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
    elbs = conn.get_all_load_balancers()
    
    # attempt to find the ELB belonging to this stack's set of API servers
    for elb in elbs:
        # TODO: this is deprecated; 
        for awsInstance in elb.instances: 
            if awsInstance.id in instance_ids:
                return elb
    
    return None

def is_prod_stack():
    if not is_ec2():
        return False
    
    stack = get_stack()
    prod  = get_prod_stack()
    
    if stack is not None and prod is not None:
        return stack.instance.stack == prod
    
    return False

def get_prod_stack():
    if not is_ec2():
        return None
    
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.prod_stack.txt')
    
    if os.path.exists(path):
        f = open(path, 'r')
        name = f.read()
        f.close()
        
        if len(name) > 1:
            return name
    
    conn  = Route53Connection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
    zones = conn.get_all_hosted_zones()
    name  = None
    host  = None
    
    for zone in zones['ListHostedZonesResponse']['HostedZones']:
        if zone['Name'] == u'stamped.com.':
            host = zone
            break
    
    if host is not None:
        records = conn.get_all_rrsets(host['Id'][12:])
        
        for record in records:
            if record.name == 'api.stamped.com.':
                name = record.alias_dns_name.split('-')[0].strip()
                break
    
    if name is not None:
        f = open(path, 'w')
        f.write(name)
        f.close()
    
    return name

def is_ec2():
    """ returns whether or not this python program is running on EC2 """
    
    return os.path.exists("/proc/xen") and os.path.exists("/etc/ec2_version")

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
                if isinstance(cfg, dict):
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
            pass
        
        try:
            return self.tags[key]
        except:
            # TODO: make this less hacky...
            return eval("self._instance.%s" % key)
    
    def __str__(self):
        return "%s(%s.%s)" % (self.__class__.__name__, self.stack.name, self.name)

