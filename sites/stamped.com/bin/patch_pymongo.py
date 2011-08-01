#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import os, socket, thread, utils
import pymongo.connection

try:
    from greenlet import greenlet
except ImportError:
    def get_ident():
        return os.getpid(), thread.get_ident()
else:
    def get_ident():
        return os.getpid(), thread.get_ident(), greenlet.getcurrent()

_CONNECT_TIMEOUT = 20.0

class _Pool(object):
    """A simple connection pool patched to work with gevent."""
    
    def __init__(self, socket_factory, pool_size):
        self.pool_size = pool_size
        self.socket_factory = socket_factory
        self.network_timeout = None
        self.sockets = []
        self.active_sockets = { }
    
    def socket(self):
        sock_id = get_ident()
        #utils.log(sock_id)
        
        try:
            sock = self.active_sockets[sock_id]
        except KeyError:
            try:
                sock = self.sockets.pop()
            except IndexError:
                sock = self.socket_factory()
            
            self.active_sockets[sock_id] = sock
        
        return sock
    
    def return_socket(self):
        sock = self.active_sockets.pop(get_ident(), None)
        if sock is not None:
            self.sockets.append(sock)

pymongo.connection._Pool = _Pool

