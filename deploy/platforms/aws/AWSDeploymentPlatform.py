#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import re, os, time, utils

from ..DeploymentPlatform       import DeploymentPlatform
from errors                     import Fail
from utils                      import lazy_property

from datetime                   import datetime, timedelta
from AWSInstance                import AWSInstance
from AWSDeploymentStack         import AWSDeploymentStack
from boto.route53.connection    import Route53Connection
from boto.ec2.connection        import EC2Connection
from boto.exception             import EC2ResponseError

AWS_ACCESS_KEY_ID = 'AKIAIXLZZZT4DMTKZBDQ'
AWS_SECRET_KEY    = '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'
AWS_AMI_USER_ID   = '688550672341'

class AWSDeploymentPlatform(DeploymentPlatform):
    def __init__(self, options):
        self.commonOptions = '--headers'
        dbStack = None
        optionsDict = vars(options)
        if 'db_stack' in optionsDict and optionsDict['db_stack'] is not None:
            dbStack = optionsDict['db_stack'].lower()
        DeploymentPlatform.__init__(self, AWSDeploymentStack, db_stack=dbStack)
        self.options = options
        self._ami_re = re.compile('.*stamped\.base\.ami \(([0-9]+)-([0-9]+)-([0-9]+) +([0-9]+)\.([0-9]+)\.([0-9]+)\).*')
        self.name = str(self)
    
    def _get_security_group(self, name):
        security_groups = self.conn.get_all_security_groups()
        
        for sg in security_groups:
            if sg.name == name:
                return sg
        
        return None
    
    def _init_security_groups(self):
        ssh_rule = {
            'ip_protocol' : 'tcp', 
            'from_port'   : 22, 
            'to_port'     : 22, 
            'cidr_ip'     : '0.0.0.0/0', 
        }
        ganglia_udp_rule = {
            'ip_protocol' : 'udp', 
            'from_port'   : 8649, 
            'to_port'     : 8649, 
            'cidr_ip'     : '0.0.0.0/0', 
        }
        ganglia_tcp_rule = {
            'ip_protocol' : 'tcp', 
            'from_port'   : 8649, 
            'to_port'     : 8649, 
            'cidr_ip'     : '0.0.0.0/0', 
        }
        
        dev_rule = {
            'ip_protocol' : 'tcp', 
            'from_port'   : 27017, 
            'to_port'     : 27017, 
            'cidr_ip'     : '0.0.0.0/0', 
        }
        
        common_rules = [
            ssh_rule, 
            ganglia_udp_rule, 
            ganglia_tcp_rule, 
        ]
        
        groups = [
            {
                'name' : 'db', 
                'desc' : 'Database security group', 
                'rules' : [
                    #{
                    #    'ip_protocol' : 'tcp', 
                    #    'from_port'   : 27017, 
                    #    'to_port'     : 27017, 
                    #    'cidr_ip'     : '0.0.0.0/0', 
                    #}, 
                    #{
                    #    'src_group' : 'webserver', 
                    #}, 
                    #{
                    #    'src_group' : 'crawler', 
                    #}, 
                ], 
            }, 
            {
                'name' : 'apiserver', 
                'desc' : 'ApiServer security group', 
                'rules' : [
                    {
                        'ip_protocol' : 'tcp', 
                        'from_port'   : 5000, 
                        'to_port'     : 5000, 
                        'cidr_ip'     : '0.0.0.0/0', 
                    }, 
                ], 
            }, 
            {
                'name' : 'webserver', 
                'desc' : 'WebServer security group', 
                'rules' : [
                    {
                        'ip_protocol' : 'tcp', 
                        'from_port'   : 5000, 
                        'to_port'     : 5000, 
                        'cidr_ip'     : '0.0.0.0/0', 
                    }, 
                ], 
            }, 
            {
                'name' : 'crawler', 
                'desc' : 'Crawler security group', 
                'rules' : [ ], 
            }, 
            {
                'name' : 'bootstrap', 
                'desc' : 'Bootstrap security group', 
                'rules' : [ ], 
            }, 
            {
                'name' : 'work', 
                'desc' : 'Work security group', 
                'rules' : [ ], 
            }, 
            {
                'name' : 'mem', 
                'desc' : 'Memcached security group', 
                'rules' : [ ], 
            }, 
            {
                'name' : 'temp', 
                'desc' : 'Temporary security group', 
                'rules' : [ ], 
            }, 
            {
                'name' : 'dev', 
                'desc' : 'Dev security group', 
                'rules' : [ dev_rule ], 
            }, 
            {
                'name' : 'search', 
                'desc' : 'ElasticSearch security group', 
                'rules' : [
                    {
                        'ip_protocol' : 'tcp', 
                        'from_port'   : 9200, 
                        'to_port'     : 9200, 
                        'cidr_ip'     : '0.0.0.0/0', 
                    }, 
                ], 
            }, 
            {
                'name' : 'monitor', 
                'desc' : 'Monitor security group', 
                'rules' : [
                    {
                        'ip_protocol' : 'tcp', 
                        'from_port'   : 8080, 
                        'to_port'     : 8080, 
                        'cidr_ip'     : '0.0.0.0/0', 
                    }, 
                    {
                        'ip_protocol' : 'udp', 
                        'from_port'   : 8125, 
                        'to_port'     : 8125, 
                        'cidr_ip'     : '0.0.0.0/0', 
                    }, 
                ], 
            }, 
            {
                'name' : 'analytics', 
                'desc' : 'Analytics security group', 
                'rules' : [
                    {
                        'ip_protocol' : 'tcp', 
                        'from_port'   : 5000, 
                        'to_port'     : 5000, 
                        'cidr_ip'     : '0.0.0.0/0', 
                    }, 
                ], 
            }, 
        ]
        
        for group in groups:
            name = group['name']
            sg = self._get_security_group(name)
            
            if sg is None:
                self.conn.create_security_group(name, group['desc'])
            
            group['rules'].extend(common_rules)
        
        for group in groups:
            name = group['name']
            sg = self._get_security_group(name)
            
            assert sg is not None
            
            for rule in group['rules']:
                try:
                    ret = sg.authorize(**rule)
                    assert ret
                except Exception:
                    #utils.log("error initializing security group '%s'" % name)
                    #utils.printException()
                    break
    
    def _init_env(self):
        self.conn = EC2Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)
        
        self.env = utils.AttributeDict(os.environ)
        reservations = self.conn.get_all_instances()
        stacks = { }
        
        for reservation in reservations:
            for instance in reservation.instances:
                if hasattr(instance, 'tags') and 'stack' in instance.tags and instance.state == 'running':
                    stackName = instance.tags['stack']
                    
                    if stackName in stacks:
                        stacks[stackName].append(instance)
                    else:
                        stacks[stackName] = [ instance ]
        
        #self._init_security_groups()
        
        #sl = len(stacks)
        #utils.log("found %d stack%s:" % (sl, "s" if sl != 1 else ""))
        index = 1
        
        for stackName in stacks:
            #utils.log("%d) %s" % (index, stackName))
            index += 1
            
            instances = stacks[stackName]
            self._stacks[stackName] = AWSDeploymentStack(stackName, self, instances)
    
    def get_bootstrap_image(self):
        if hasattr(self, '_bootstrap_image') and self._bootstrap_image is not None:
            return self._bootstrap_image
        
        images = self.conn.get_all_images(owners=[ AWS_AMI_USER_ID ])
        if 0 == len(images):
            utils.log("[%s] unable to find custom AMI to use" % self)
        
        recent = None
        
        # return the latest image (empirically the last one returned from amazon, 
        # though as far as i can tell, there is no guarantee this is the latest)
        for i in xrange(len(images)):
            try:
                image = images[-(i + 1)]
                # stamped.base.ami (2011-12-7 22.47.9)
                
                if image.state == u'available':
                    match = self._ami_re.match(image.name)
                    
                    if match is not None:
                        groups = map(lambda s: int(s), match.groups())
                        date = datetime(*groups)
                        
                        if recent is None or date > recent[0]:
                            recent = (date, image)
                elif image.state == u'pending':
                    utils.log("[%s] warning: recent AMI %s still pending; falling back to earlier image" % \
                              self, image)
                else:
                    utils.log("[%s] warning: found AMI %s with unexpected state (%s)" % \
                              self, image, image.state)
            except Exception:
                utils.printException()
        
        if recent is not None:
            self._bootstrap_image = recent[1]
            return recent[1]
        
        return None
    
    def bootstrap(self, *args):
        utils.log("[%s] initializing temp instance to create bootstrap AMI" % self)
        
        config = { 'roles' : [ 'bootstrap', 'temp', ], 'name' : 'temp0' }
        instance = AWSInstance(self, config)
        instance.create()
        
        now     = datetime.utcnow()
        name    = 'stamped.base.ami (%s-%s-%s %s.%s.%s)' % (now.year, now.month, now.day, now.hour, now.minute,  now.second)
        ami_id  = self.conn.create_image(instance.instance_id, name, "Base AMI for Stamped instances")
        image   = None
        
        utils.log("[%s] waiting for AMI %s (%s) to come online" % (self, name, ami_id))
        while True:
            try:
                images = self.conn.get_all_images(image_ids=[ ami_id ])
                image  = images[0]
            except Exception:
                time.sleep(1)
        
        success = False
        
        while True:
            image.update()
            
            if image.state == u'pending':
                time.sleep(2)
            elif image.state == u'available':
                success = True
                break
            else:
                utils.log("[%s] error creating AMI %s (%s) (invalid state: %s)" % (self, name, ami_id, image.state))
                break
        
        if success:
            utils.log("[%s] successfully created AMI %s (%s)" % (self, name, ami_id))
        
        utils.log("[%s] cleaning up temp instance %s" % (self, instance))
        instance.terminate()
    
    @lazy_property
    def prod_stack(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.prod_stack.txt')
        
        if os.path.exists(path):
            modified = utils.get_modified_time(path)
            current  = datetime.utcnow() - timedelta(hours=24)
            
            # only try to use the cached config if it's recent enough
            if modified >= current:
                f = open(path, 'r')
                name = f.read().strip()
                f.close()
                
                if len(name) >= 1:
                    return name
        
        conn  = Route53Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)
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

