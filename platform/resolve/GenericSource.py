#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'GenericSource' ]

import Globals
from logs import report

try:
    from BasicSource                import BasicSource
    from utils                      import lazyProperty
    import logs
    from pprint                     import pprint, pformat
    import sys
    from Resolver                   import Resolver
    from abc                        import ABCMeta, abstractmethod
except:
    report()
    raise

class GenericSource(BasicSource):
    """
    """
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        BasicSource.__init__(self, *args, **kwargs)
        self.addGroup(self.sourceName)

    @lazyProperty
    def resolver(self):
        return Resolver()

    @lazyProperty
    def stamped(self):
        import StampedSource
        return StampedSource.StampedSource()

    @abstractmethod
    def matchSource(self, query):
        pass

    def emptySource(self, start, count):
        return []

    def generatorSource(self, generator, constructor=None):
        if constructor is None:
            constructor = lambda x: x
        results = []
        def source(start, count):
            total = start + count
            while total - len(results) > 0:
                try:
                    results.append(generator.next())
                except StopIteration:
                    break

            if start + count <= len(results):
                result = results[start:start+count]
            elif start < len(results):
                result = results[start:]
            else:
                result = []
            return [
                constructor(entry)
                    for entry in result
            ]
        return source

    @property
    def idField(self):
        return "%s_id" % self.sourceName

    def enrichEntity(self, entity, controller, decorations, timestamps):
        if controller.shouldEnrich(self.sourceName, self.sourceName, entity):
            try:
                query = self.stamped.wrapperFromEntity(entity)
                timestamps[self.sourceName] = controller.now
                results = self.resolver.resolve(query, self.matchSource(query))
                if len(results) != 0:
                    best = results[0]
                    if best[0]['resolved']:
                        entity[self.idField] = best[1].key
            except ValueError:
                pass
        return True

