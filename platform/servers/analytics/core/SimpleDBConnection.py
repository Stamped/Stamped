import Globals

import keys.aws
from boto.sdb.connection    import SDBConnection
from boto.exception         import SDBResponseError
from gevent.pool            import Pool

def reveal (cursor,limit=None,duration=None):
    count = 0
    output = []
    for stat in  cursor:
        if duration is not None and 'bgn' in stat and 'end' in stat:
            bgn = stat['bgn'].split('T')
            end = stat['end'].split('T')
            if end[0] == bgn[0]:
                bgn = bgn[1].split(':')
                end = end[1].split(':')
                hours = float(end[0]) - float(bgn[0])
                minutes = float(end[1]) - float(bgn[1])
                seconds = float(end[2]) - float(bgn[2])
                diff = seconds + 60*(minutes + 60*hours)
        
        if duration is None or diff > duration:
            output.append(stat)
            count += 1
        
        if limit is not None and count > limit:
            break
    return output
#Base class for establishing a SimpleDB connection

class SimpleDBConnection(object):
    
    def __init__(self):
        try:
            self.conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
        except SDBResponseError:
            print "SimpleDB Connection Refused"
        
        self.statList = []
        self.statCount = 0
        
        self.v1_prod_domains = {}
        self.v2_prod_domains = {}
        self.v2_dev_domains = {}
        self.v2_stress_domains = {}
        
        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            
            self.v1_prod_domains[suffix] = self.conn.get_domain('stats_prod_%s' % suffix)
            self.v2_prod_domains[suffix] = self.conn.get_domain('bowser_%s' % suffix)
            self.v2_dev_domains[suffix] = self.conn.get_domain('stats_dev_%s' % suffix)
            self.v2_stress_domains[suffix] = self.conn.get_domain('stress_%s' % suffix)
    
    # Perform a query and write to an optional list, set or dict (key is first field specified)
    def execute(self, domain, query_dict, fields, bgn=None, end=None, destination=None, limit=None, duration=None):

        query = 'select %s from `%s`' % (fields,domain.name)
        transition = 'where'

        for key,value in query_dict.items():
            if "!=" in value:
                query = '%s %s %s != "%s"' %  (query, transition, key, value[2:])
            else:
                query = '%s %s %s="%s"' % (query, transition, key, value)
            transition = 'and'
        
        if bgn is not None: 
            query = '%s %s bgn > "%s"' % (query, transition, bgn.isoformat())
            transition = 'and'
        
        if end is not None:
            query = '%s %s bgn > "%s"' % (query, transition, bgn.isoformat())
            transition = 'and'
            
        init_results = domain.select(query)
        
        results = reveal(init_results,limit=limit,duration=duration)
        
        if destination != None:
            if fields == 'count(*)':
                destination += results[0]
            else:
                destination.extend(results)
        
        return results
    
    def query (self, stack, query_dict, fields='*', bgn=None, end=None, limit=None, duration=None):
        
        if fields == 'count(*)':
            self.statCount = 0
            destination = self.statCount
        else:
            self.statList = []
            destination = self.statList
            
        if stack == 'bowser':
            domains = self.v2_prod_domains
        else:
            domains = self.v2_dev_domains
        
        pool = Pool(16)
        
        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            
            pool.spawn(self.execute, domains[suffix], query_dict, fields=fields, bgn=bgn,end=end, destination=destination, limit=limit/16 + 1, duration=duration)

        pool.join()
        
        if fields == 'count(*)':
            return self.statCount
        else:
            return self.statList[:limit]
        
        
            
            
            
            
            
            
            
            
            