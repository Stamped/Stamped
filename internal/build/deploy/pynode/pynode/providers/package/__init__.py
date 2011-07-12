#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Utils
from abc import abstractmethod
from exceptions import Fail
from Provider import Provider

class PackageProvider(Provider):
    def __init__(self, *args, **kwargs):
        super(PackageProvider, self).__init__(*args, **kwargs)
        self._updateCurrentStatus()
    
    def install(self):
        if self.resource.version != None and self.resource.version != self.currentVersion:
            installVersion = self.resource.version
        elif self.currentVersion is None:
            installVersion = self.candidateVersion
        else:
            return
        
        if not installVersion:
            raise Fail("No version specified, and no candidate version available.")
        
        Utils.log("Install %s version %s (resource %s, current %s, candidate %s) location %s",
                  self.resource.name, installVersion, self.resource.version,
                  self.currentVersion, self.candidateVersion, self.resource.location)
        
        status = self._install(self.resource.location, installVersion)
        if status:
            self.resource.updated()
    
    def upgrade(self):
        if self.currentVersion != self.candidateVersion:
            origVersion = self.currentVersion or "uninstalled"
            Utils.log("Upgrading %s from version %s to %s",
                str(self.resource), origVersion, self.candidateVersion)
            
            status = self._upgrade(self.resource.location, self.candidateVersion)
            if status:
                self.resource.updated()
    
    def remove(self):
        if self.currentVersion:
            Utils.log("Remove %s version %s", self.resource.name, self.currentVersion)
            self._remove(self.resource.name)
            self.resource.updated()
    
    def purge(self):
        if self.currentVersion:
            Utils.log("Purging %s version %s", self.resource.name, self.currentVersion)
            self._purge(self.resource.name)
            self.resource.updated()
    
    def _updateCurrentStatus(self):
        if not self.installed:
            raise Fail("Unable to install provider %s for resource %s" % str(self), str(self.resource))
    
    @abstractmethod
    def _install(self, name, version):
        pass
    
    @abstractmethod
    def _remove(self, name):
        pass
    
    @abstractmethod
    def _upgrade(self, name, version):
        pass
    
    def __repr__(self):
        return "PackageProvider(%s)" % repr(self.resource)

