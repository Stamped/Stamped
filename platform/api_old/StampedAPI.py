#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from logs import report

try:
    import utils
    import os, logs, re, time, urlparse, math, pylibmc, gevent, traceback, random

    from api_old import Blacklist
    import libs.ec2_utils
    import libs.Memcache
    import tasks.Tasks
    from api_old import Entity
    from api_old import SchemaValidation

    from api_old.auth                       import convertPasswordForStorage
    from utils                      import lazyProperty, LoggingThreadPool
    from functools                  import wraps
    from errors                     import *
    from libs.ec2_utils             import is_prod_stack
    from pprint                     import pprint, pformat
    from operator                   import itemgetter, attrgetter
    from random                     import seed, random

    from api_old.AStampedAPI                import AStampedAPI
    
    from api_old.Schemas                import *


    from search.AutoCompleteIndex import normalizeTitle, loadIndexFromS3, emptyIndex, pushNewIndexToS3
    
    import datetime
except Exception:
    report()
    raise


# TODO (travis): refactor API function calling conventions to place optional authUserId last
# instead of first, especially for function which don't require auth.

class StampedAPI(AStampedAPI):
    """
        Database-agnostic implementation of the internal API for accessing
        and manipulating all Stamped backend databases.
    """


    def __init__(self, desc, **kwargs):
        AStampedAPI.__init__(self, desc)

        if utils.is_ec2():
            self._node_name = "unknown"
        else:
            self._node_name = "localhost"

        try:
            self.__is_prod = is_prod_stack()
        except Exception:
            logs.warning('is_prod_stack threw an exception; defaulting to True',exc_info=1)
            self.__is_prod = True
        self.__is_prod = True



    @property
    def node_name(self):
        if self._node_name == 'unknown':
            try:
                stack_info = libs.ec2_utils.get_stack()
                self._node_name = "%s.%s" % (stack_info.instance.stack, stack_info.instance.name)
            except Exception:
                pass

        return self._node_name




    """
    ######
    #     # #####  # #    #   ##   ##### ######
    #     # #    # # #    #  #  #    #   #
    ######  #    # # #    # #    #   #   #####
    #       #####  # #    # ######   #   #
    #       #   #  #  #  #  #    #   #   #
    #       #    # #   ##   #    #   #   ######
    """

    def addClientLogsEntry(self, authUserId, entry):
        entry.user_id = authUserId
        entry.created = datetime.datetime.utcnow()

        return self._clientLogsDB.addEntry(entry)

