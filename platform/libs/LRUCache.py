#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

import copy
import logs
import collections
import functools, operator

from itertools import ifilterfalse
from heapq import nsmallest
from operator import itemgetter

class Counter(dict):
    'Mapping where default values are zero'
    def __missing__(self, key):
        return 0

def lru_cache(maxsize=100):
    '''Least-recently-used cache decorator.
    
    Arguments to the cached function must be hashable.
    Cache performance statistics stored in f.hits and f.misses.
    Clear the cache with f.clear().
    http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used
    
    '''
    maxqueue = maxsize * 10
    def decorating_function(user_function, len=len, iter=iter, tuple=tuple, 
                            sorted=sorted, KeyError=KeyError):
        cache = {}                  # mapping of args to results
        queue = collections.deque() # order that keys have been used
        refcount = Counter()        # times each key is in the queue
        sentinel = object()         # marker for looping around the queue
        kwd_mark = object()         # separate positional and keyword args
        
        # lookup optimizations (ugly but fast)
        queue_append, queue_popleft = queue.append, queue.popleft
        queue_appendleft, queue_pop = queue.appendleft, queue.pop
        
        @functools.wraps(user_function)
        def wrapper(*args, **kwds):
            # cache key records both positional and keyword args
            key = '%s' % user_function.__name__
            for arg in args:
                try:
                    arg = arg.dataExport()
                except Exception:
                    pass
                # TODO: Should really complain if this isn't a type that's going to serialize meaningfully
                # to string.
                key = "%s - %s" % (key, arg)
            for k, v in sorted(kwds.iteritems()):
                try:
                    v = v.dataExport()
                except Exception:
                    pass
                # TODO: Should really complain if this isn't a type that's going to serialize meaningfully
                # to string.
                key = "%s - %s (%s)" % (key, k, v)

            if key == '':
                raise Exception("Key not set! (%s)" % user_function)

            # get cache entry or compute if not found
            try:
                result = cache[key]
                # Record recent use of this key.
                queue_append(key)
                refcount[key] += 1

                wrapper.hits += 1

            except KeyError:
                result = user_function(*args, **kwds)
                cache[key] = result
                # Record recent use of this key. If we do this before the call to user_function, we can get in
                # trouble where, while we're waiting on I/O, someone else encounters the cache in an inconsistent
                # state where an element is in the queue and the refcount dict but not the cache dict itself.
                queue_append(key)
                refcount[key] += 1
                wrapper.misses += 1
                
                # purge least recently used cache entry
                if len(cache) > maxsize:
                    key = queue_popleft()
                    refcount[key] -= 1
                    while refcount[key]:
                        key = queue_popleft()
                        refcount[key] -= 1
                    del cache[key]
                    del refcount[key]
            
            # periodically compact the queue by eliminating duplicate keys
            # while preserving order of most recent access
            if len(queue) > maxqueue:
                refcount.clear()
                queue_appendleft(sentinel)
                
                for key in ifilterfalse(refcount.__contains__,
                                        iter(queue_pop, sentinel)):
                    queue_appendleft(key)
                    refcount[key] = 1

            return copy.deepcopy(result)
        
        def clear():
            cache.clear()
            queue.clear()
            refcount.clear()
            wrapper.hits = wrapper.misses = 0
        
        wrapper.hits = wrapper.misses = 0
        wrapper.clear = clear
        return wrapper
    
    return decorating_function

def lfu_cache(maxsize=100):
    '''Least-frequenty-used cache decorator.
    
    Arguments to the cached function must be hashable.
    Cache performance statistics stored in f.hits and f.misses.
    Clear the cache with f.clear().
    http://en.wikipedia.org/wiki/Least_Frequently_Used

    '''
    def decorating_function(user_function):
        cache = {}                      # mapping of args to results
        use_count = Counter()           # times each key has been accessed
        kwd_mark = object()             # separate positional and keyword args

        @functools.wraps(user_function)
        def wrapper(*args, **kwds):
            key = args
            if kwds:
                key += (kwd_mark,) + tuple(sorted(kwds.items()))
            use_count[key] += 1

            # get cache entry or compute if not found
            try:
                result = cache[key]
                wrapper.hits += 1
            except KeyError:
                result = user_function(*args, **kwds)
                cache[key] = result
                wrapper.misses += 1

                # purge least frequently used cache entry
                if len(cache) > maxsize:
                    for key, _ in nsmallest(maxsize // 10,
                                            use_count.iteritems(),
                                            key=itemgetter(1)):
                        del cache[key], use_count[key]

            return copy.deepcopy(result)

        def clear():
            cache.clear()
            use_count.clear()
            wrapper.hits = wrapper.misses = 0

        wrapper.hits = wrapper.misses = 0
        wrapper.clear = clear
        return wrapper
    return decorating_function


if __name__ == '__main__':
    
    @lru_cache(maxsize=20)
    def f(x, y):
        return 3*x+y
    
    domain = range(5)
    from random import choice
    for i in range(1000):
        r = f(choice(domain), choice(domain))
    
    print(f.hits, f.misses)
    
    @lfu_cache(maxsize=20)
    def f(x, y):
        return 3*x+y
    
    domain = range(5)
    from random import choice
    for i in range(1000):
        r = f(choice(domain), choice(domain))
    
    print(f.hits, f.misses)

