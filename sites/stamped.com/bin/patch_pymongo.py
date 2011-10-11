#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import os, socket, thread
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
    
    def __init__(self, pool_size, network_timeout):
        self.pool_size = pool_size
        self.network_timeout = network_timeout
        self.sockets = []
        self.active_sockets = { }
    
    def connect(self, host, port):
        """
            Connect to Mongo and return a new (connected) socket.
        """
        try:
            # Prefer IPv4. If there is demand for an option
            # to specify one or the other we can add it later.
            s = socket.socket(socket.AF_INET)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(self.network_timeout or _CONNECT_TIMEOUT)
            s.connect((host, port))
            s.settimeout(self.network_timeout)
            return s
        except socket.gaierror:
            # If that fails try IPv6
            s = socket.socket(socket.AF_INET6)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(self.network_timeout or _CONNECT_TIMEOUT)
            s.connect((host, port))
            s.settimeout(self.network_timeout)
            return s
    
    def get_socket(self, host, port):
        sock_id = get_ident()
        #utils.log(sock_id)
        cached = True
        
        try:
            sock = self.active_sockets[sock_id]
        except KeyError:
            try:
                sock = self.sockets.pop()
            except IndexError:
                sock = self.connect(host, port)
                cached = False
            
            self.active_sockets[sock_id] = sock
        
        return (sock, cached)
    
    def return_socket(self):
        sock = self.active_sockets.pop(get_ident(), None)
        if sock is not None:
            self.sockets.append(sock)

pymongo.connection._Pool = _Pool

