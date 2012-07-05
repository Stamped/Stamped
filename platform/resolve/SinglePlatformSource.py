#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'SinglePlatformSource' ]

import Globals
from logs import report

try:
    from libs.SinglePlatform        import StampedSinglePlatform
    from resolve.BasicSource                import BasicSource
    from utils                      import lazyProperty
    import logs
    from urllib2                    import HTTPError
except:
    report()
    raise

class SinglePlatformSource(BasicSource):
    """
    """
    def __init__(self):
        BasicSource.__init__(self, 'singleplatform',
            groups=['menu'],
            kinds=['place'],
        )

    @lazyProperty
    def __singleplatform(self):
        return StampedSinglePlatform()

    def enrichEntity(self, entity, controller, decorations, timestamps):
        singleplatform_id = getattr(entity.sources, 'singleplatform_id')
        try:
            if singleplatform_id is not None:
                if controller.shouldEnrich('menu', self.sourceName, entity):
                    menu = self.__singleplatform.get_menu_schema(singleplatform_id)
                    entity.menu = menu != None
                    if menu is not None:
                        menu.entity_id = entity.entity_id
                        decorations['menu'] = menu
                        logs.debug('Regenerated menu for %s' % singleplatform_id)
        except HTTPError as e:
            logs.warning("HttpError %s from SinglePlatform for %s" % (e.code,singleplatform_id))
        except Exception as e:
            report("unexpected SinglePlatformSource error: %s" % e)
        return True

    def enrichEntityWithEntityProxy(self, proxy, entity, controller=None, decorations=None, timestamps=None):
        GenericSource.enrichEntityWithEntityProxy(self, proxy, entity, controller, decorations, timestamps)
        entity.sources.singleplatform_id = proxy.key
        return True

