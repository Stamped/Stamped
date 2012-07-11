import gevent
from gevent import monkey
monkey.patch_all()
from rpyc.utils.server import Server

class GreenletServer(Server):
    """
    A server that spawns a greenlet for each connection.

    Parameters: see :class:`Server`
    """
    def _accept_method(self, sock):
        gevent.spawn(self._authenticate_and_serve_client, sock)
