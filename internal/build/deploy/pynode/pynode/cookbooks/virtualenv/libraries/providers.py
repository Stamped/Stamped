#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

__all__ = [ "VirtualEnvProvider" ]

from pynode.utils import log, shell
from pynode.errors import Fail
from pynode.provider import Provider

try:
    import virtualenv
except ImportError as e:
    log("Error: must install virtualenv before using VirtualEnvProvider")
    raise e

class VirtualEnvProvider(Provider):
    def action_create(self):
        virtualenv.create_environment(home_dir=self.resource.path, 
                                      site_packages=self.resource.site_packages, 
                                      clear=self.resource.clear, 
                                      unzip_setuptools=self.resource.unzip_setuptools, 
                                      use_distribute=self.resource.use_distribute, 
                                      never_download=self.resource.never_download)
        
        log("Installed virtualenv '%s'" % self.resource.path)
    
    def action_activate(self):
        (output, status) = shell('source %s/bin/activate' % self.resource.path)
        if 0 != status:
            raise Fail("unable to activate virtualenv %s" % self.resource.name)
    
    def action_delete(self):
        (output, status) = shell('rm -rf %s' % self.resource.path)
        if 0 != status:
            raise Fail("unable to delete virtualenv %s" % self.resource.name)

