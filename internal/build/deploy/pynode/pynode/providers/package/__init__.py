#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from pynode.utils import log
from pynode.errors import Fail
from pynode.provider import Provider
from abc import abstractmethod

class PackageProvider(Provider):
    def __init__(self, *args, **kwargs):
        super(PackageProvider, self).__init__(*args, **kwargs)
        self._updateCurrentStatus()
    
    def action_install(self):
        if self.resource.version != None and self.resource.version != self.currentVersion:
            installVersion = self.resource.version
        elif self.currentVersion is None:
            installVersion = self.candidateVersion
        else:
            return
        
        if not installVersion:
            log("No version specified, and no candidate version available for resource %s." % str(self.resource))
            #raise Fail("No version specified, and no candidate version available.")
        
        log("Install %s version %s" % (self.resource.name, installVersion))
        log("(current: %s, candidate: %s)" % (self.currentVersion, self.candidateVersion))
        
        status = self._install_package(self.resource.name, installVersion)
        if status:
            self.resource.updated()
    
    def action_upgrade(self):
        if self.currentVersion != self.candidateVersion:
            origVersion = self.currentVersion or "uninstalled"
            log("Upgrading %s from version %s to %s" % \
                (str(self.resource), origVersion, self.candidateVersion))
            
            status = self._upgrade(self.resource.name, self.candidateVersion)
            if status:
                self.resource.updated()
    
    def action_remove(self):
        if self.currentVersion:
            log("Remove %s version %s" % (self.resource.name, self.currentVersion))
            self._remove_package(self.resource.name)
            self.resource.updated()
    
    @abstractmethod
    def _updateCurrentStatus(self):
        pass
    
    @abstractmethod
    def _install_package(self, name, version):
        pass
    
    @abstractmethod
    def _remove_package_package(self, name):
        pass
    
    @abstractmethod
    def _upgrade_package(self, name, version):
        pass
    
    def __repr__(self):
        return "PackageProvider(%s)" % repr(self.resource)

