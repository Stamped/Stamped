#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

__all__ = [ "Provider" ]

import utils
from exceptions import Fail

class Provider(object):
    BUILTIN_PREFIX = "pynode.providers."
    
    BUILTIN_PROVIDERS = dict(
        debian = dict(
            Package = BUILTIN_PREFIX + "package.apt.DebianAptProvider", 
            Service = BUILTIN_PREFIX + "service.debian.DebianServiceProvider", 
        ), 
        ubuntu = dict(
            Package = BUILTIN_PREFIX + "package.apt.DebianAptProvider", 
            Service = BUILTIN_PREFIX + "service.debian.DebianServiceProvider", 
        ), 
        mac_os_x = dict(
            Package = BUILTIN_PREFIX + "package.homebrew.HomebrewProvider", 
            Service = BUILTIN_PREFIX + "service.debian.DebianServiceProvider", # TODO!
        ), 
        default = dict(
            PythonPackage = BUILTIN_PREFIX + "package.easy_install.EasyInstallProvider", 
            File          = BUILTIN_PREFIX + "system.FileProvider", 
            Directory     = BUILTIN_PREFIX + "system.DirectoryProvider", 
            Link          = BUILTIN_PREFIX + "system.LinkProvider", 
            Execute       = BUILTIN_PREFIX + "system.ExecuteProvider", 
            Script        = BUILTIN_PREFIX + "system.ScriptProvider", 
            Mount         = BUILTIN_PREFIX + "mount.MountProvider", 
            User          = BUILTIN_PREFIX + "accounts.UserProvider", 
            Group         = BUILTIN_PREFIX + "accounts.GroupProvider", 
        ), 
    )
    
    def __init__(self, resource):
        self.resource = resource
        
        try:
            self._install()
        except Exception as e:
            utils.log("Unable to install provider %s for resource %s" % (self, self.resource))
            raise e
    
    def _install(self):
        pass
    
    def __repr__(self):
        return "Provider(%s)" % repr(self.resource)
    
    @staticmethod
    def resolve(env, resourceType, classPath=None):
        if not classPath:
            try:
                classPath = Provider.BUILTIN_PROVIDERS[env.system.platform][resourceType]
            except KeyError:
                try:
                    classPath = Provider.BUILTIN_PROVIDERS["default"][resourceType]
                except KeyError:
                    utils.log("Unable to resolve provider for resource '%s' on platform '%s'" % (resourceType, env.system.platform))
                    raise
        
        if classPath.startswith('*'):
            (cookbook, classname) = classPath[1:].split('.')
            return getattr(env.cookbooks[cookbook], classname)
        
        try:
            (modulePath, className) = classPath.rsplit('.', 1)
            module = __import__(modulePath, {}, {}, [ className ])
            return getattr(module, className)
        except ValueError, ImportError:
            utils.log("Unable to resolve provider for resource '%s' as '%s'" % (resourceType, classPath))
            raise

