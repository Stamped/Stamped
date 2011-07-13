#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import grp, pwd, subprocess, pynode.utils

from pynode.exceptions import Fail
from pynode.provider import Provider

class UserProvider(Provider):
    def action_create(self):
        if not self.user:
            command = ['useradd', "-m"]
            
            options = dict(
                comment = "-c",
                gid = "-g",
                uid = "-u",
                shell = "-s",
                password = "-p",
                home = "-d",
            )
            
            if self.resource.system:
                command.append("--system")
            
            if self.resource.groups:
                command += ["-G", ",".join(self.resource.groups)]
            
            for option_name, option_flag in options.items():
                option_value = getattr(self.resource, option_name)
                
                if option_flag and option_value:
                    command += [option_flag, str(option_value)]
            
            command.append(self.resource.username)
            
            subprocess.check_call(command)
            self.resource.updated()
            utils.log("Added user %s" % self.resource)
    
    def action_remove(self):
        if self.user:
            command = ['userdel', self.resource.username]
            subprocess.check_call(command)
            self.resource.updated()
            utils.log("Removed user %s" % self.resource)
    
    @property
    def user(self):
        try:
            return pwd.getpwnam(self.resource.username)
        except KeyError:
            return None

class GroupProvider(Provider):
    def action_create(self):
        group = self.group
        if not group:
            command = ['groupadd']
            
            options = dict(
                gid = "-g",
                password = "-p",
            )
            
            for option_name, option_flag in options.items():
                option_value = getattr(self.resource, option_name)
                
                if option_flag and option_value:
                    command += [option_flag, str(option_value)]
            
            command.append(self.resource.name)
            
            subprocess.check_call(command)
            self.resource.updated()
            utils.log("Added group %s" % self.resource)
            
            group = self.group
        
        # if self.resource.members is not None:
        #     current_members = set(group.gr_mem)
        #     members = set(self.resource.members)
        #     for u in current_members - members:
        #         pass
    
    def action_remove(self):
        if self.user:
            command = ['groupdel', self.resource.name]
            subprocess.check_call(command)
            self.resource.updated()
            utils.log("Removed group %s" % self.resource)
    
    @property
    def group(self):
        try:
            return grp.getgrnam(self.resource.name)
        except KeyError:
            return None

