#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

import keys.aws, logs

from boto.sdb.connection    import SDBConnection
from boto.exception         import SDBResponseError
from gevent.pool            import Pool
from utils                  import lazyProperty
from datetime               import datetime, timedelta

# An instantiation of a simpleDB connection 
class SimpleDBConnection(object):
    
    def __init__(self, stack='bowser'):
        try:
            self.conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
            logs.debug("Connected to SimpleDB stack %s" % stack)
        except SDBResponseError:
            logs.debug("SimpleDB Connection Refused")
            raise
        
        self._stack = stack

    @lazyProperty
    def domains(self):
        result = []
        for i in range(16):
            suffix = '0' + hex(i)[2]
            name = '%s_%s' % (self._stack, suffix)
            result.append(self.conn.get_domain(name))
        return result

    def _queryParams(self, params, bgn, end):
        
        if params is None:
            queryParams = []
        else:
            queryParams = params

        if bgn is not None:
            queryParams.append("end >= '%s'" % bgn.isoformat())

        if end is not None:
            queryParams.append("end < '%s'" % end.isoformat())

        return queryParams

    def _deserialize(self, item):

        def isoparse(s):
            # Credit: http://blog.client9.com/2010/02/fast-iso-datetime-format-parsing-in.html
            try:
                return datetime(int(s[0:4]), int(s[5:7]), int(s[8:10]), int(s[11:13]), int(s[14:16]), int(s[17:19]))
            except:
                return None

        # Convert datetimes
        if 'bgn' in item:
            item['bgn'] = isoparse(item['bgn'])

        if 'end' in item:
            item['end'] = isoparse(item['end'])

        # Convert numbers
        if 'dur' in item:
            item['dur'] = int(item['dur'])

        return item

    def query(self, params=None, bgn=None, end=None, fields=None, sort=None, limit=None):
        
        queryFields = '*'
        if fields is not None:
            queryFields = ','.join(fields)
        
        queryParams = self._queryParams(params, bgn, end)
        
        pool = Pool(len(self.domains))

        data = []
        def run(domain, query):
            if limit is None:
                data.extend(domain.select(query))
            else:
                count = 0
                for item in domain.select(query):
                    data.append(item)
                    count += 1
                    if count > limit:
                        break
        
        for domain in self.domains:
            
            # Build query
            query = "select %s from `%s`" % (queryFields, domain.name)
            if len(queryParams) > 0:
                query += " where %s" % (' and '.join(queryParams))
            if sort is not None:
                query += " order by %s %s" % (sort[0], sort[1])
            
            # Run it
            pool.spawn(run, domain, query)

        pool.join()


        results = []
        if sort is not None:
            if sort[1] == 'desc':
                data = sorted(data, key=(lambda x: x['%s' % sort[0]]), reverse=True)
            else:
                data = sorted(data, key=(lambda x: x['%s' % sort[0]]), reverse=False)
        
        if limit is not None:
            data = data[:limit]
        
        for item in data:
            results.append(self._deserialize(item))

        return results 

    def count(self, params=[], bgn=None, end=None):

        queryParams = self._queryParams(params, bgn, end)

        pool = Pool(len(self.domains))

        data = []
        def run(domain, query):
            data.extend(domain.select(query))

        for domain in self.domains:
            
            # Build query
            query = "select count(*) from `%s`" % domain.name
            if len(queryParams) > 0:
                query += " where %s" % (' and '.join(queryParams))
            
            # Run it
            pool.spawn(run, domain, query)

        pool.join()

        count = 0
        for item in data:
            count += int(item.pop('Count', 0))
        return count
    
    # Special case of query that returns the set of unique user ids that match a given query in a given time window
    def queryForUserSet(self, params=[], bgn=None, end=None):
        
        queryParams = self._queryParams(params, bgn, end)
        
        pool = Pool(len(self.domains))

        users = set()
        def run(domain, query):
            for item in domain.select(query):
                if 'uid' in item:
                    users.add(item['uid'])
        
        for domain in self.domains:
            
            # Build query
            query = "select uid from `%s`" % domain.name
            if len(queryParams) > 0:
                query += " where %s" % (' and '.join(queryParams))
            
            # Run it
            pool.spawn(run, domain, query)

        pool.join()

        return users

# Connect to a singular sdb domain being used as a cache for analytics pages
class SimpleDBCacheConnection(object):
       
    def __init__(self, cache_name):
        try:
            self.conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
            logs.debug("Connected to SimpleDB Cache %s" % cache_name)
        except SDBResponseError:
            logs.debug("SimpleDB Cache Connection Refused")
            raise

        self._cache = cache_name
        
    @lazyProperty
    def cache(self):
        return self.conn.get_domain(self._cache)

    def lookup(self, itemName):
        return self.cache.get_item(itemName)
    
    def store(self, item_name, attribute_dict):
        return self.cache.put_attributes(item_name, attribute_dict, replace=True)


# Example for testing purposes and insight into how this setup works      
def demo():
    print 'Display the number of stamps created and the average duration for the last hour'
    db = SimpleDBConnection('bowser')

    t = datetime.utcnow() - timedelta(minutes=60)
    now = datetime.utcnow()
    while t < now:
        increment = timedelta(minutes=10)
        stamps = db.count(params=['uri = "/v1/stamps/create.json"'], bgn=t, end=(t + increment))
        duration = sum(map(lambda x: x['dur'], db.query(params=['uri = "/v1/stamps/create.json"'], bgn=t, end=(t + increment), fields=['dur'])))
        avgDuration = 0.0
        if stamps > 0:
            avgDuration = (duration / 1000000.0 / stamps)

        print "%s %6s stamps  %10.2f seconds" % (t - timedelta(hours=4), stamps, avgDuration) 

        t = t + increment