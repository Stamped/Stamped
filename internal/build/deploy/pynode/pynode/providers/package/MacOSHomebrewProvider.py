#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import pynode.Utils
from pynode.exceptions import Fail
from pynode.providers.package import PackageProvider
from subprocess import STDOUT, PIPE, check_call

class MacOSHomebrewProvider(PackageProvider):
    def _installProvider(self):
        # TODO: support installing ruby as a prerequisite to homebrew...
        brewInstalled = (0 == Utils.shell('brew --help')[1])
        
        if brewInstalled:
            return True
        else:
            # attempt to install homebrew
            p = Popen('ruby -e "$(curl -fsSL https://raw.github.com/gist/323731)"', shell=TRUE)
            status = p.wait()
            
            return 0 == status
    
    def _updateCurrentStatus(self):
        super(__class__, self)._updateCurrentStatus()
        self.currentVersion = None
        self.candidateVersion = None
        
        (output, status) = Utils.shell("brew which %s" % self.resource.name)
        if output != "":
            output = output[len(self.resource.name):]
            self.currentVersion = output
            self.candidateVersion = output
        else:
            self.candidateVersion = "latest"
    
    def _install(self, name, version):
        return 0 == check_call("brew install %s" % (name, ), shell=True, 
                               stdout=PIPE, stderr=STDOUT)
    
    def _remove(self, name):
        return 0 == check_call("brew uninstall --force %s" % name,
            shell=True, stdout=PIPE, stderr=STDOUT)
    
    def _upgrade(self, name, version):
        return self._install(name, version)

