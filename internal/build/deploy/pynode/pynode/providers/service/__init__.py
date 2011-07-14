#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import os, subprocess
import pynode.utils as utils
from pynode.provider import Provider
from pynode.exceptions import Fail

class ServiceProvider(Provider):
    def action_start(self):
        if not self.status():
            self._exec_cmd("start", 0)
            self.resource.updated()
    
    def action_stop(self):
        if self.status():
            if not self.resource.supports_stop:
                raise Fail("Resource '%s' does not support action '%s'" % (self.resource, "stop"))
            
            self._exec_cmd("stop", 0)
            self.resource.updated()
    
    def action_restart(self):
        if not self.status():
            self._exec_cmd("start", 0)
            self.resource.updated()
        elif not self.resource.supports_restart:
            raise Fail("Resource '%s' does not support action '%s'" % (self.resource, "restart"))
        else:
            self._exec_cmd("restart", 0)
            self.resource.updated()
    
    def action_reload(self):
        if not self.status():
            self._exec_cmd("start", 0)
            self.resource.updated()
        elif not self.resource.supports_reload:
            raise Fail("Resource '%s' does not support action '%s'" % (self.resource, "reload"))
        else:
            self._exec_cmd("reload", 0)
            self.resource.updated()
    
    def status(self):
        if self.resource.supports_status:
            return self._exec_cmd("status") == 0
        else:
            return False
    
    def _exec_cmd(self, cmd, expect=None):
        if cmd != "status":
            utils.log("%s command '%s'" % (self.resource, cmd))
        
        custom_cmd = getattr(self.resource, "%s_cmd" % cmd, None)
        if custom_cmd:
            utils.log("%s executing '%s'" % (self.resource, custom_cmd))
            
            if hasattr(custom_cmd, "__call__"):
                if custom_cmd():
                    ret = 0
                else:
                    ret = 1
            else:
                ret = subprocess.call(custom_cmd, shell=True)#, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            ret = self._init_cmd(cmd)
        
        if expect is not None and expect != ret:
            raise Fail("%r command %s for service %s failed" % (self, cmd, self.resource.name))
        
        return ret
    
    def _init_cmd(self, cmd):
        if self._upstart:
            if cmd == "status":
                proc = subprocess.Popen(["/sbin/"+cmd, self.resource.name],
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                out = proc.communicate()[0]
                _proc, state = out.strip().split(' ', 1)
                ret = 0 if state != "stop/waiting" else 1
            else:
                ret = subprocess.call(["/sbin/"+cmd, self.resource.name],
                                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            ret = subprocess.call(["/etc/init.d/%s" % self.resource.name, cmd],
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return ret
    
    @property
    def _upstart(self):
        try:
            return self.__upstart
        except AttributeError:
            self.__upstart = os.path.exists("/sbin/start") \
                             and os.path.exists("/etc/init/%s.conf" % self.resource.name)
        
        return self.__upstart

