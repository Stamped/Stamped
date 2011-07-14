#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from pynode.utils import log, shell
from pynode.exceptions import Fail
from pynode.providers.package import PackageProvider
from subprocess import STDOUT, PIPE, check_call

class HomebrewProvider(PackageProvider):
    def _install(self):
        # TODO: support installing ruby as a prerequisite to homebrew...
        brewInstalled = (0 == shell('brew --help')[1])
        
        if brewInstalled:
            return
        else:
            log("installing homebrew...")
            
            # attempt to install homebrew
            p = Popen('ruby -e "$(curl -fsSL https://raw.github.com/gist/323731)"', shell=TRUE)
            status = p.wait()
            
            if 0 != status:
                raise Fail("error installing homebrew")
    
    def _updateCurrentStatus(self):
        PackageProvider._updateCurrentStatus(self)
        self.currentVersion   = None
        self.candidateVersion = None
        
        (output, status) = shell("brew which %s" % self.resource.name)
        if output != "":
            output = output[len(self.resource.name):]
            self.currentVersion   = output
            self.candidateVersion = output
        else:
            self.candidateVersion = "latest"
    
    def _install_package(self, name, version):
        return 0 == check_call("brew install %s" % (name, ), shell=True)
        #, stdout=PIPE, stderr=STDOUT)
    
    def _remove_package(self, name):
        return 0 == check_call("brew uninstall --force %s" % name, shell=True)
        #, stdout=PIPE, stderr=STDOUT)
    
    def _upgrade_package(self, name, version):
        return self._install_package(name, version)

