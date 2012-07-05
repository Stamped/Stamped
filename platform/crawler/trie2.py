#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import keys.aws, utils
import gzip, json, math, re, string, time, sys, threading

from api.MongoStampedAPI    import MongoStampedAPI
from api.HTTPSchemas        import *
from api.Schemas        import *
from gevent.pool        import Pool
from optparse           import OptionParser
from pprint             import pprint, pformat

from boto.s3.connection import S3Connection
from boto.s3.key        import Key

#-----------------------------------------------------------

class S3AutocompleteDB(object):
    
    def __init__(self, bucket_name='stamped.com.static.images'):
        # find or create bucket
        # ---------------------
        conn = S3Connection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
        rs = conn.get_all_buckets()
        rs = filter(lambda b: b.name == bucket_name, rs)
        
        if 1 == len(rs):
            self.bucket = rs[0]
        else:
            self.bucket = conn.create_bucket(bucket_name)
        
        self.bucket_name = bucket_name
    
    def add_key(self, name, value, content_type=None, apply_gzip=False, temp_prefix=None):
        assert isinstance(value, basestring)
        
        if apply_gzip:
            name += '.gz'
            
            if temp_prefix is None:
                temp_prefix = threading.currentThread().getName()
            
            # TODO: why does zlib compression not work?
            #value = zlib.compress(value, 6)
            temp  = '.temp.%s.gz' % temp_prefix
            tries = 0
            
            while True:
                try:
                    f = gzip.open(temp, 'wb')
                    f.write(value)
                    f.close()
                    f = open(temp, 'rb')
                    value = f.read()
                    f.close()
                    break
                except:
                    tries += 1
                    
                    if tries >= 5:
                        raise
        
        key = Key(self.bucket, name)
        
        meta = { }
        if content_type is not None:
            meta['Content-Type'] = content_type
        
        if apply_gzip:
            meta['Content-Encoding'] = 'gzip'
        
        if len(meta) > 0:
            key.update_metadata(meta)
        
        # note that the order of setting the key's metadata, contents, and 
        # ACL is important for some seriously stupid boto reason...
        key.set_contents_from_string(value)
        key.set_acl('public-read')
        key.close()

def parseCommandLine():
    usage   = "Usage: %prog [options] [sources]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", 
        help="db to connect to for output")
    
    parser.add_option("-n", "--noop", default=False, action="store_true", 
        help="run in noop mode without modifying anything")
    
    parser.add_option("-r", "--ratio", default=None, type="string", 
        action="store", dest="ratio", 
        help="where this crawler fits in to a distributed stack")
    
    parser.add_option("-o", "--offset", default=0, 
        type="int", dest="offset", 
        help="start index of entities to import")
    
    parser.add_option("-l", "--limit", default=None, type="int", 
        help="limits the number of entities to import")

    (options, args) = parser.parse_args()
    Globals.options = options
    
    if options.db:
        utils.init_db_config(options.db)
    
    infile = file('autocomplete.txt', 'r')
    options.count = utils.getNumLines(infile)
    infile.close()
    
    if options.ratio:
        num, den = options.ratio.split('/')
        num, den = int(num), int(den)
        num, den = float(num), float(den)
        
        options.offset = int(math.floor((options.count * (num - 1)) / den))
        options.limit  = int(math.ceil(options.count / den) + 1)
        
        utils.log("ratio %s) offset=%d, limit=%d" % (options.ratio, options.offset, options.limit))
    else:
        if options.limit is None:
            options.limit = options.count
    
    options.verbose = False
    return options

def encode_s3_name(name):
    name = name.lower().replace(' ', '_').encode('ascii', 'ignore')
    name = re.sub('([^a-zA-Z0-9._-])', '', name)
    return name

_globals = {}
def main():
    options  = parseCommandLine()
    
    stampedAPI = MongoStampedAPI()
    entityDB   = stampedAPI._entityDB
    placesDB   = stampedAPI._placesEntityDB
    
    autocompleteDB = S3AutocompleteDB()
    
    prefixes = set()
    wrapper  = {
        'time_sum' : 0.0, 
        'time_num' : 0, 
    }
    
    def _add(orig_name, wrapper):
        try:
            if 0 == len(orig_name) or orig_name in prefixes:
                return
            
            name = encode_s3_name(orig_name)
            if 0 == len(name):
                return
            
            name = "search/v2/%s.json" % name
            
            print "searching %s" % orig_name.encode('ascii', 'replace')
            tries = 0
            
            while True:
                try:
                    t1 = time.time()
                    results = stampedAPI.searchEntities(query=orig_name, limit=10, prefix=True, full=False)
                    t2 = time.time()
                    duration = (t2 - t1)
                    
                    wrapper['time_sum'] += duration
                    wrapper['time_num'] += 1
                    
                    break
                except:
                    tries += 1
                    
                    if tries >= 3:
                        utils.printException()
                        time.sleep(1)
                        return
                    
                    time.sleep(1)
            
            """
            if len(results) <= 1:
                i = len(orig_name)
                
                while i > 0:
                    prefixes.add(orig_name[0:i])
                    i -= 1
                
                if 0 == len(results):
                    return False
            """
            
            autosuggest = []
            for item in results:
                item = HTTPEntityAutosuggest().importSchema(item[0], item[1]).dataExport()
                autosuggest.append(item)
            
            value = json.dumps(autosuggest, sort_keys=True)
            
            data  = {
                'name1' : orig_name.encode('ascii', 'replace'), 
                'name2' : name, 
                'num_r' : len(results)
            }
            
            pprint(data)
            sys.stdout.flush()
            
            if not options.noop:
                retries = 0
                while True:
                    try:
                        autocompleteDB.add_key(name, value, content_type='application/json', apply_gzip=True)
                        break
                    except:
                        retries += 1
                        if retries > 5:
                            utils.printException()
                            return
                        
                        time.sleep(1)
        except:
            utils.printException()
            time.sleep(1)
            return
    
    infile = file('autocomplete.txt', 'r')
    pool   = Pool(4)
    done   = 0
    offset = 0
    
    for line in infile:
        if offset < options.offset: offset += 1; continue
        if options.limit is not None and done > options.limit: break
        
        line = line[:-1]
        pool.spawn(_add, line, wrapper)
        
        done += 1
        if options.limit <= 100 or ((done - 1) % (options.limit / 100)) == 0:
            utils.log("done processing %s (avg search time %s ms)" % (utils.getStatusStr(done, options.limit), 1000.0 * (wrapper['time_sum'] / (wrapper['time_num'] if wrapper['time_num'] > 0 else 1))))
    
    pool.join()
    infile.close()

if __name__ == '__main__':
    main()

