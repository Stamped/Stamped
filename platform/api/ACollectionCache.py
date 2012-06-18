#!/usr/bin/env python

__author__    = "Stamped (dev@Stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped, Inc."
__license__   = "TODO"

import Globals, logs, time
from utils import abstract
from datetime import timedelta
from Memcache import globalMemcache

class ACollectionCache(object):

    def __init__(self, collectionName, blockSize=50, blockBufferSize=20):
        self._cache = globalMemcache()
        self._collectionName = collectionName
        self._blockSize = blockSize
        self._blockBufferSize = blockBufferSize

    def _generateKey(self, offset, **kwargs):
        return self._collectionName + '::' + '::'.join([str(k) + '=' + str(v) for k,v in iter(sorted(kwargs.items()))]) + '::' + str(offset)


    @abstract
    def _getFromDB(self, limit, before=None, **kwargs):
        pass

    def _prune(self, data, **kwargs):
        return data

    def _updateCache(self, offset, **kwargs):
        t0 = time.time()
        t1 = t0


        prevBlockOffset = offset - self._blockSize
        if prevBlockOffset < 0:
            prevBlockOffset = None

        # get the modified time of the last item of the previous data cache block.  We use it for the slice
        before = None
        if prevBlockOffset is not None:
            prevBlockKey = self._generateKey(prevBlockOffset, **kwargs)
            try:
                prevBlock = self._cache[prevBlockKey]
            except KeyError:
                # recursively fill previous blocks if they have expired
                prevBlock = self._updateCache(prevBlockOffset, **kwargs)
            except Exception as e:
                logs.error('Error retrieving data from memcached.  Is memcached running?')
                prevBlock = self._updateCache(prevBlockOffset, **kwargs)
            if len(prevBlock) < self._blockSize:
                raise Exception("Previous data block was final")
            assert(len(prevBlock) > 0)
            lastItem = prevBlock[-1]
            before = lastItem.timestamp.modified - timedelta(microseconds=1)

        # Pull the data from the database and prune it.
        limit = self._blockSize + self._blockBufferSize
        data = []
        while len(data) < self._blockSize:
            newData, final = self._getFromDB(limit, before, **kwargs)
            newData = self._prune(newData, **kwargs)
            data += newData
            if final:
                break
            before = newData[-1].timestamp.modified - timedelta(microseconds=1)

        key = self._generateKey(offset, **kwargs)
        data = data[:self._blockSize]
        try:
            self._cache[key] = data
        except Exception:
            logs.error('Error storing activity items to memcached.  Is memcached running?')

        logs.debug('Time for updateCache: %s' % (time.time() - t1))
        t1 = time.time()

        return data



    def _clearCacheForKeyParams(self, **kwargs):
        curOffset = 0
        key = self._generateKey(curOffset, **kwargs)
        try:
            while key in self._cache:
                del(self._cache[key])
                curOffset += self._blockSize
                key = self._generateKey(curOffset, **kwargs)
        except Exception:
            pass

    def setCacheBlockSize(self, cacheBlockSize):
        self._blockSize = cacheBlockSize

    def setCacheBlockBufferSize(self, cacheBlockBufferSize):
        self._blockBufferSize = cacheBlockBufferSize



    def getFromCache(self, limit, offset=0, **kwargs):
        """
        Pull the requested data from cache if it exists there, otherwise pull the data from db
        Returns a tuple of (the data list, bool indicating if the end of the collection stream was reached)
        """
        t0 = time.time()
        t1 = t0

        if offset == 0:
            self._clearCacheForKeyParams(**kwargs)

        data = []
        while len(data) < limit:
            curOffset = ((offset + len(data)) // self._blockSize) * self._blockSize
            key = self._generateKey(curOffset, **kwargs)
            try:
                newData = self._cache[key]
            except KeyError:
                newData = self._updateCache(offset=curOffset, **kwargs)
            except Exception:
                logs.error('Error retrieving data from memcached.  Is memcached running?')
                newData = self._updateCache(curOffset, **kwargs)
            start = (offset+len(data)) % self._blockSize
            data += newData[start:start+limit]
            if len(newData) < self._blockSize:
                break

        logs.debug('Time for getFromCache: %s' % (time.time() - t1))
        t1 = time.time()

        return data[:limit], len(data) < limit
