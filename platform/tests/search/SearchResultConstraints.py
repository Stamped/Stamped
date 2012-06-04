#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, logs

from pprint                 import pprint, pformat
from abc                    import ABCMeta, abstractmethod
from collections            import defaultdict

from resolve.Resolver       import Resolver, simplify
from resolve.StampedSource  import StampedSource
from resolve.GenericSource  import generatorSource

class ASearchResultConstraint(object):
    
    """
        Represents a single constraint with respect to entity search results, 
        providing the ability to verify that the constraint is satisfied via 
        the validate function.
    """
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def validate(self, results):
        """
            Validates this constraint against the given search results.         
            
            Returns True if the constraint was satisfied or False otherwise.
        """
        pass
    
    def _eq(self, a, b, strict=False, match=None):
        """ Returns whether or not a fuzzily matches b """
        
        a = unicode(a)
        b = unicode(b)
        
        if not strict:
            a = simplify(a)
            b = simplify(b)
            
            if len(a) > len(b):
                a, b = b, a
            
            if match == 'prefix':
                return b.startswith(a)
            
            if match == 'contains':
                return a in b
        
        return a == b
    
    def __str__(self):
        return self.__class__.__name__

class SearchResultConstraint(ASearchResultConstraint):
    
    """
        Represents a single constraint with respect to entity search results, 
        providing the ability to verify that the constraint is satisfied via 
        the validate function.
    """
    
    def __init__(self, 
                 title      = None, 
                 source     = None, 
                 id         = None, 
                 types      = None, 
                 index      = None, 
                 strict     = False, 
                 match      = None, 
                 soft       = True, 
                 **extras):
        ASearchResultConstraint.__init__(self)
        
        if types is not None and not isinstance(types, set):
            if isinstance(types, (tuple, list)):
                types = set(types)
            else:
                types = set([ types ])
        
        self.title  = title
        self.source = source
        self.id     = id
        self.types  = types
        self.index  = index
        self.strict = strict
        self.match  = match
        self.soft   = True
        self.extras = extras
    
    def validate(self, results):
        """
            Validates this constraint against the given search results, verifying 
            one or more of the following:
                * a specific result exists
                * a specific result exists at the desired index
                * a specific result does *not* exist
            
            Returns True if the constraint was satisfied or False otherwise.
        """
        
        for i in xrange(len(results)):
            result = results[i]
            valid  = (self.index is None or self.index == i or (self.index != -1 and self.soft))
            
            if valid:
                t0 = list(self.types)
                t1 = list(result.types)
                
                if len(t0) == 1: t0 = t0[0]
                if len(t1) == 1: t1 = t1[0]
                
                utils.log("VALIDATE %s/%s | %s vs %s (%s vs %s)" % 
                          (i, self.index, self.title, result.title, t0, t1))
                logs.debug(pformat(utils.normalize(result.dataExport(), strict=True)))
            
            # optionally verify the validity of this result's title
            if self.title  is not None and not self._eq(self.title, result.title):
                continue
            
            # optionally verify the origin of this result and/or it's source_id
            if self.source is not None:
                source_id_key = "%s_id" % self.source
                
                if source_id_key not in result:
                    continue
                
                if self.id is not None and not self._eq(self.id, result[source_id_key]):
                    continue
            
            # optionally ensure the validity of this result's type
            if self.types is not None:
                match = False
                for t in self.types:
                    for t2 in result.types:
                        try:
                            t2 = t2.dataExport()
                        except Exception:
                            pass
                        
                        if self._eq(t, t2):
                            match = True
                            break
                    
                    if not match:
                        break
                
                if not match:
                    continue
            
            # optionally ensure the validity of other misc entity attributes
            if self.extras is not None:
                match = True
                for key, value in self.extras.iteritems():
                    if not hasattr(result.sources, key) or not self._eq(value, getattr(result.sources, key)):
                        match = False
                        break
                
                if not match:
                    continue
            
            # constrainted result was matched
            if valid:
                return True
            
            if self.index != -1:
                # match was not found at the desired index
                return False
        
        # specified result was not found; constraint is only satisfied if the 
        # expected index is invalid (e.g., constraint specifies that the result 
        # should not be found in the result set)
        return (self.index == -1)
    
    def _eq(self, a, b):
        return ASearchResultConstraint._eq(self, a, b, strict = self.strict, match = self.match)
    
    def __str__(self):
        options = { }
        
        if self.title is not None:  options['title']    = self.title
        if self.source is not None: options['source']   = self.source
        if self.id is not None:     options['id']       = self.id
        if self.types is not None:  options['types']    = self.types
        if self.index is not None:  options['index']    = self.index
        
        return "%s(%s)" % (self.__class__.__name__, str(options))

class UniqueSearchResultConstraint(ASearchResultConstraint):
    
    """
        Represents a single uniqueness constraint with respect to entity search 
        results, providing the ability to verify that the constraint is 
        satisfied via the validate function.
    """
    
    def __init__(self):
        ASearchResultConstraint.__init__(self)
        
        self.__stamped  = StampedSource()
        self.__resolver = Resolver()
    
    def validate(self, results):
        """
            Validates the search result set to ensure that there are no obvious 
            duplicate results.
            
            Returns True if all results are unique within a fuzzy margin of error 
            or False otherwise.
        """
        
        proxies = map(self.__stamped.proxyFromEntity, results)
        
        # ensure that no result resolves definitively to any other result in the result set
        for i in xrange(len(proxies)):
            proxy = proxies[i]
            
            def dedup():
                for j in xrange(len(proxies)):
                    proxy2 = proxies[j]
                    
                    if i != j and proxy.kind == proxy2.kind:
                        yield proxy2
            
            dups = self.__resolver.resolve(proxy, generatorSource(dedup()), count=1)
            
            if len(dups) > 0 and dups[0][0]['resolved']:
                return False
        
        seen = defaultdict(set)
        
        # ensure that there are no obvious duplicate results without using the resolver
        for i in xrange(len(results)):
            result = results[i]
            keys   = [ k for k in result.sources if k.endswith('_id') ]
            
            # ensure that the same source id doesn't appear twice in the result set
            # (source ids are supposed to be unique)
            for key in keys:
                value = str(result[key])
                
                if value in seen[key]:
                    return False
                
                seen[key].add(value)
            
            for j in xrange(i + 1, len(results)):
                result2 = results[j]
                
                if i != j and self._eq(result.kind, result2.kind) and self._eq(result.title, result2.title):
                    if len(result.types.intersection(result2.types)) > 0:
                        utils.log("")
                        utils.log("!" * 80)
                        utils.log("dupe encountered: %s\n%s" % (result, result2))
                        utils.log("!" * 80)
                        utils.log("")
                        
                        return False
        
        return True

