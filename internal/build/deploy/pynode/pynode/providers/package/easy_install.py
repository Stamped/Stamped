#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import re, pynode.utils
from pynode.utils import lazyProperty
from pynode.exceptions import Fail
from pynode.providers.package import PackageProvider
from subprocess import check_call, Popen, PIPE, STDOUT

VERSION_RE = re.compile(r'\S\S(.*)\/(.*)-(.*)-py(.*).egg\S')
BEST_MATCH_RE = re.compile(r'Best match: (.*) (.*)\n')

class EasyInstallProvider(PackageProvider):
    def _updateCurrentStatus(self):
        proc = Popen(["python", "-c", "import %s; print %s.__path__" % (self.resource.name, self.resource.name)], stdout=PIPE, stderr=STDOUT)
        path = proc.communicate()[0]
        
        if proc.wait() != 0:
            self.currentVersion = None
        else:
            match = VERSION_RE.search(path)
            if match:
                self.currentVersion = match.group(3)
            else:
                self.currentVersion = "unknown"
    
    @lazyProperty
    def candidateVersion(self):
        proc = Popen([self._binaryPath, "-n", self.resource.name], stdout=PIPE, stderr=STDOUT)
        out  = proc.communicate()[0]
        res  = proc.wait()
        
        if res != 0:
            utils.log("easy_install check returned a non-zero result (%d) %s" % (res, self.resource))
        
        match = BEST_MATCH_RE.search(out)
        
        if not match:
            return None
        else:
            return match.group(2)
    
    @property
    def _binaryPath(self):
        return "easy_install"
    
    def _install_package(self, name, version):
        check_call([self._binaryPath, "-U", "%s==%s" % (name, version)], stdout=PIPE, stderr=STDOUT)
    
    def _remove_package(self, name):
        check_call([self._binaryPath, "-m", name])
    
    def _upgrade_package(self, name, version):
        self.install_package(name, version)

