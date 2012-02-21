#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'FormatSource' ]

import Globals
from logs import report

try:
    from BasicSource    import BasicSource
    import logs
except:
    report()
    raise


class FormatSource(BasicSource):
    """
    Data-Source wrapper for Factual services.
    """
    def __init__(self):
        BasicSource.__init__(self, 'format',
            'subtitle',
        )

    def enrichEntity(self, entity, controller, decorations, timestamps):
        return False

