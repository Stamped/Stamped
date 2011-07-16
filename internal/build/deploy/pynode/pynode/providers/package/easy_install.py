#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import re
from pynode.utils import lazyProperty, log, shell
from pynode.errors import Fail
from pynode.providers.package import PackageProvider
from subprocess import check_call, Popen, PIPE, STDOUT

VERSION_RE = re.compile(r'\S\S(.*)\/(.*)-(.*)-py(.*).egg\S')
BEST_MATCH_RE = re.compile(r'Best match: (.*) (.*)\n')

class EasyInstallProvider(PackageProvider):
    def _updateCurrentStatus(self):
        prog = "import pkg_resources; print pkg_resources.get_distribution('virtualenv').version"
        (output, status) = shell('python -c "%s"' % prog)
        
        if 0 == status:
            self.currentVersion = output
        else:
            self.currentVersion = None
        
        log(self.currentVersion)
    
    @lazyProperty
    def candidateVersion(self):
        proc = Popen([self._binaryPath, "-n", self.resource.name], stdout=PIPE, stderr=STDOUT)
        out  = proc.communicate()[0]
        res  = proc.wait()
        
        if res != 0:
            log("easy_install check returned a non-zero result (%d) %s" % (res, self.resource))
        
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

