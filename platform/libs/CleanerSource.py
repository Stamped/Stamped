#!/usr/bin/python

"""
Not finished
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'CleanerSource' ]

import Globals
from logs import log, report

try:
    from AExternalSource    import AExternalSource
    import re
    from datetime           import datetime
    from LibUtils           import months
except:
    report()
    raise

class CleanerSource(AExternalSource):
    """
    Data-Source wrapper for Factual services.
    """
    def __init__(self):
        AExternalSource.__init__(self)
    
    def enrichEntity(self, entity, controller):
        """
        Attempt to populate data fields based on id data.

        Returns True if the entity was modified.
        """
        result = False
        if controller.shouldEnrich('release_date',self.sourceName,entity):
            if 'original_release_date' in entity:
                date = entity['original_release_date']
                if date is not None:
                    new_date = None
                    match = re.match(r'^(\d\d\d\d) (\d\d) (\d\d)$',date)
                    if match is not None:
                        try:
                            new_date = datetime(int(match.group(1)),int(match.group(2)),int(match.group(3)))
                        except ValueError:
                            pass
                        except TypeError:
                            pass
                    match = re.match(r'^(\w+) (\d+), (\d\d\d\d)$',date)
                    if match is not None:
                        try:
                            month = match.group(1)
                            if month in months:
                                new_date = datetime(int(match.group(3)),months[month],int(match.group(2)))
                        except ValueError:
                            pass
                        except TypeError:
                            pass
                    if new_date is not None:
                        self.writeSingleton(entity,'release_date',new_date,controller=controller)
                        result = True
        return result

    @property
    def sourceName(self):
        """
        Returns the name of this source as would be used with a SourceController.
        """
        return 'cleaner'
    

