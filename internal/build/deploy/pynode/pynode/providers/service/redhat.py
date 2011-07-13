#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"
__all__ = ["RedhatServiceProvider"]

from pynode.providers.service import ServiceProvider

class RedhatServiceProvider(ServiceProvider):
    def enable_runlevel(self, runlevel):
        pass

