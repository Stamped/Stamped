#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import os, sys, utils

from utils import lazyProperty, Singleton
from subprocess import Popen, PIPE

class System(Singleton):
    @lazyProperty
    def os(self):
        platform = sys.platform.lower()
        
        if platform.startswith('linux'):
            return "linux"
        elif platform == "darwin":
            return "darwin"
        else:
            return "unknown"
    
    def unquote(self, val):
        if val[0] == '"':
            val = val[1:-1]
        
        return val

    @lazyProperty
    def arch(self):
        machine = self.machine
        if machine in ("i386", "i486", "i686"):
            return "x86_32"
        return machine

    @lazyProperty
    def machine(self):
        return utils.shell(["uname", "-m"])
    
    @lazyProperty
    def lsb(self):
        if os.path.exists("/etc/lsb-release"):
            with open("/etc/lsb-release", "rb") as fp:
                lsb = (x.split('=') for x in fp.read().strip().split('\n'))
            return dict((k.split('_', 1)[-1].lower(), self.unquote(v)) for k, v in lsb)
        elif os.path.exists("/usr/bin/lsb_release"):
            p = Popen(["/usr/bin/lsb_release","-a"], stdout=PIPE, stderr=PIPE)
            lsb = {}
            for l in p.communicate()[0].split('\n'):
                v = l.split(':', 1)
                if len(v) != 2:
                    continue
                lsb[v[0].strip().lower()] = self.unquote(v[1].strip().lower())
            lsb['id'] = lsb.pop('distributor id')
            return lsb
    
    @lazyProperty
    def platform(self):
        operatingsystem = self.os
        
        if operatingsystem == "linux":
            lsb = self.lsb
            if not lsb:
                if os.path.exists("/etc/redhat-release"):
                    return "redhat"
                if os.path.exists("/etc/fedora-release"):
                    return "fedora"
                if os.path.exists("/etc/debian_version"):
                    return "debian"
                if os.path.exists("/etc/gentoo-release"):
                    return "gentoo"
                return "unknown"
            return lsb['id'].lower()
        elif operatingsystem == "darwin":
            out = Popen("/usr/bin/sw_vers", stdout=PIPE).communicate()[0]
            sw_vers = dict([y.strip() for y in x.split(':', 1)] for x in out.strip().split('\n'))
            # ProductName, ProductVersion, BuildVersion
            return sw_vers['ProductName'].lower().replace(' ', '_')
        else:
            return "unknown"

    @lazyProperty
    def locales(self):
        p = Popen("locale -a", shell=True, stdout=PIPE)
        out = p.communicate()[0]
        return out.strip().split("\n")
    
    @lazyProperty
    def ec2(self):
        if not os.path.exists("/proc/xen"):
            return False
        if os.path.exists("/etc/ec2_version"):
            return True
        
        return False
    
    @lazyProperty
    def vm(self):
        if os.path.exists("/usr/bin/VBoxControl"):
            return "vbox"
        elif os.path.exists("/usr/bin/vmware-toolbox-cmd") or os.path.exists("/usr/sbin/vmware-toolbox-cmd"):
            return "vmware"
        elif os.path.exists("/proc/xen"):
            return "xen"
        return None

