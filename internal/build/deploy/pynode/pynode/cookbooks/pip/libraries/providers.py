#!/usr/bin/env python

__all__ = [ "PipPackageProvider" ]

import re

from subprocess import check_call, Popen, PIPE, STDOUT
from pynode.utils import log, lazyProperty, shell
from pynode.exceptions import Fail
from pynode.providers.package import PackageProvider

best_match_re = re.compile(r'Best match: (.*) (.*)\n')

class PipPackageProvider(PackageProvider):
    def _updateCurrentStatus(self):
        p = Popen("%s freeze | grep ^%s==" % \
            (self.pip_binary_path, self.resource.name), stdout=PIPE, stderr=STDOUT, shell=True)
        out = p.communicate()[0]
        res = p.wait()
        
        if res != 0:
            self.currentVersion = None
        else:
            try:
                self.currentVersion = out.split("==", 1)[1].strip()
            except IndexError:
                raise Fail("pip could not determine installed package version.")
    
    @lazyProperty
    def candidateVersion(self):
        if not self.resource.version and re.match("^[A-Za-z0-9_.-]+$", self.resource.name):
            p = Popen([self.easy_install_binary_path, "-n", self.resource.name], stdout=PIPE, stderr=STDOUT)
            out = p.communicate()[0]
            res = p.wait()
            if res != 0:
                log("easy_install check returned a non-zero result (%d) %s" % (res, self.resource))
            
            m = best_match_re.search(out)
            
            if not m:
                return None
            else:
                return m.group(2)
        else:
            return self.resource.version
    
    @property
    def pip_binary_path(self):
        return "pip"
    
    @property
    def easy_install_binary_path(self):
        return "easy_install"
    
    def _install_package(self, name, version):
        if self.resource.virtualenv is not None:
            prefix     = "source %s/bin/activate && " % self.resource.virtualenv
            virtualenv = "--environment %s" % self.resource.virtualenv
        else:
            prefix     = ""
            virtualenv = ""
        
        if name == 'pip' or not version:
            (_, status) = self._shell("%s %s %s install --upgrade %s" % \
                (prefix, self.pip_binary_path, virtualenv, name))
        else:
            (_, status) = self._shell("%s %s %s install %s==%s" % \
                (prefix, self.pip_binary_path, virtualenv, name, version))
        
        if 0 != status:
            raise Fail("error installing package %s with version %s" % (name, version))
    
    def _upgrade_package(self, name, version):
        (_, status) = self.install_package(name, version)
        if 0 != status:
            raise Fail("error upgrading package %s to version %s" % (name, version))
    
    def _remove_package(self, name, version):
        self._shell([self.pip_binary_path, "uninstall", name])
    
    def _shell(self, cmd):
        try:
            return shell(cmd)
        except Exception:
            log("error executing command: %s" % cmd)
            raise

