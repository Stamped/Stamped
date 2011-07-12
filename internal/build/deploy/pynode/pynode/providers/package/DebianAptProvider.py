#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import pynode.Utils
from pynode.exceptions import Fail
from pynode.providers.package import PackageProvider
from subprocess import Popen, STDOUT, PIPE, check_call

class DebianAptProvider(PackageProvider):
    def _updateCurrentStatus(self):
        self.currentVersion = None
        self.candidateVersion = None
        
        proc = Popen("apt-cache policy %s" % self.resource.name, shell=True, stdout=PIPE)
        out = proc.communicate()[0]
        
        for line in out.split("\n"):
            line = line.strip().split(':', 1)
            if len(line) != 2:
                continue
            
            ver = line[1].strip()
            if line[0] == "Installed":
                self.currentVersion = None if ver == '(none)' else ver
                Utils.log("Current version of package %s is %s" % (self.resource.name, self.currentVersion))
            elif line[0] == "Candidate":
                self.candidateVersion = ver
        
        if self.candidateVersion == "(none)":
            raise Fail("APT does not provide a version of package %s" % self.resource.name)
    
    def _install(self, name, version):
        return 0 == check_call("DEBIAN_FRONTEND=noninteractive apt-get -q -y install %s=%s" % (name, version),
            shell=True, stdout=PIPE, stderr=STDOUT)
    
    def _remove(self, name):
        return 0 == check_call("DEBIAN_FRONTEND=noninteractive apt-get -q -y remove %s" % name,
            shell=True, stdout=PIPE, stderr=STDOUT)
    
    def _upgrade(self, name, version):
        return self._install(name, version)

