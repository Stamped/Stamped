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
    import re
    from datetime       import datetime
    from LibUtils           import months
except:
    report()
    raise


class FormatSource(BasicSource):
    """
    Data-Source wrapper for Factual services.
    """
    def __init__(self):
        BasicSource.__init__(self, 'format',
            'release_date',
        )

    def enrichEntity(self, entity, controller, decorations, timestamps):
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
                    #sample 2009-05-29T07:00:00Z
                    match = re.match(r'^(\d\d\d\d)-(\d\d)-(\d\d)\w+\d\d:\d\d:\d\d\w+$',date)
                    if match is not None:
                        try:
                            new_date = datetime(int(match.group(1)),int(match.group(2)),int(match.group(3)))
                        except ValueError:
                            pass
                        except TypeError:
                            pass
                    if new_date is not None:
                        entity['release_date'] = new_date
                    else:
                        logs.info('created release date (%s) from %s' % (new_date, date))
        return True

