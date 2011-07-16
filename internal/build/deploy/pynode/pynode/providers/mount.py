#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import os, re, pynode.utils

from subprocess import Popen, PIPE, STDOUT, check_call
from pynode.errors import Fail
from pynode.provider import Provider

class MountProvider(Provider):
    def action_mount(self):
        if not os.path.exists(self.resource.mountPoint):
            os.makedirs(self.resource.mountPoint)
        
        if self._isMounted():
            utils.log("%s already mounted" % self)
        else:
            args = ["mount"]
            
            if self.resource.fstype:
                args += ["-t", self.resource.fstype]
            if self.resource.options:
                args += ["-o", ",".join(self.resource.options)]
            if self.resource.device:
                args.append(self.resource.device)
            
            args.append(self.resource.mountPoint)
            check_call(args)
            
            utils.log("%s mounted" % self)
            self.resource.updated()
    
    def action_umount(self):
        if self._isMounted():
            check_call(["umount", self.resource.mountPoint])
            
            utils.log("%s unmounted" % self)
            self.resource.updated()
        else:
            utils.log("%s is not mounted" % self)
    
    def action_enable(self):
        if self._isEnabled():
            utils.log("%s already enabled" % self)
        else:
            if not self.resource.device:
                raise Fail("[%s] device not set but required for enable action" % self)
            
            if not self.resource.fstype:
                raise Fail("[%s] fstype not set but required for enable action" % self)
            
            with open("/etc/fstab", "a") as fp:
                fp.write("%s %s %s %s %d %d\n" % (
                        self.resource.device,
                        self.resource.mountPoint,
                        self.resource.fstype,
                        ",".join(self.resource.options or ["defaults"]),
                        self.resource.dump,
                        self.resource.passno,
                    ))
            
            utils.log("%s enabled" % self)
            self.resource.updated()
    
    def action_disable(self):
        pass # TODO
    
    def _isMounted(self):
        if not os.path.exists(self.resource.mountPoint):
            return False
        
        if self.resource.device and not os.path.exists(self.resource.device):
            raise Fail("%s Device %s does not exist" % (self, self.resource.device))
        
        mounts = self._getMounted()
        for m in mounts:
            if m['mountPoint'] == self.resource.mountPoint:
                return True
        
        return False
    
    def _isEnabled(self):
        mounts = self._getfstab()
        for m in mounts:
            if m['mountPoint'] == self.resource.mountPoint:
                return True
        
        return False
    
    def _getMounted(self):
        p   = Popen("mount", stdout=PIPE, stderr=STDOUT, shell=True)
        out = p.communicate()[0]
        
        if p.wait() != 0:
            raise Fail("[%s] Getting list of mounts (calling mount) failed" % self)
        
        mounts = [ x.split(' ') for x in out.strip().split('\n') ]
        
        return [ dict(
                    device      = m[0],
                    mountPoint  = m[2],
                    fstype      = m[4],
                    options     = m[5][1:-1].split(','),
            ) for m in mounts if m[1] == "on" and m[3] == "type"]
    
    def _getfstab(self):
        mounts = []
        
        with open("/etc/fstab", "r") as fp:
            for line in fp:
                line  = line.split('#', 1)[0].strip()
                mount = re.split('\s+', line)
                
                if len(mount) == 6:
                    mounts.append(dict(
                        device      = mount[0],
                        mountPoint  = mount[1],
                        fstype      = mount[2],
                        options     = mount[3].split(","),
                        dump        = int(mount[4]),
                        passno      = int(mount[5]),
                    ))
        
        return mounts

