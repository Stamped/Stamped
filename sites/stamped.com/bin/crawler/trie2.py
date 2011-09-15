#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import aws, gzip, json, math, re, string, time, sys

from MongoStampedAPI    import MongoStampedAPI
from HTTPSchemas        import *
from Schemas            import *
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
        conn = S3Connection(aws.AWS_ACCESS_KEY_ID, aws.AWS_SECRET_KEY)
        rs = conn.get_all_buckets()
        rs = filter(lambda b: b.name == bucket_name, rs)
        
        if 1 == len(rs):
            self.bucket = rs[0]
        else:
            self.bucket = conn.create_bucket(bucket_name)
        
        self.bucket.set_acl('public-read')
        self.bucket_name = bucket_name
    
    def add_key(self, name, value, content_type=None, apply_gzip=False):
        assert isinstance(value, basestring)
        
        if apply_gzip:
            name += '.gz'
            
            # TODO: why does zlib compression not work?
            #value = zlib.compress(value, 6)
            f = gzip.open('temp.gz', 'wb')
            f.write(value)
            f.close()
            f = open('temp.gz', 'rb')
            value = f.read()
            f.close()
        
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
    
    def _add(orig_name):
        try:
            if 0 == len(orig_name):
                return
            
            name = encode_s3_name(orig_name)
            if 0 == len(name):
                return
            
            name = "search/%s.json" % name
            
            print "searching %s" % orig_name.encode('ascii', 'replace')
            try:
                results = stampedAPI.searchEntities(query=orig_name, limit=50, prefix=True)
            except:
                utils.printException()
                time.sleep(1)
                return
            
            if 0 == len(results):
                return False
            
            autosuggest = []
            for item in results:
                item = HTTPEntityAutosuggest().importSchema(item).exportSparse()
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
                try:
                    autocompleteDB.add_key(name, value, content_type='application/json', apply_gzip=True)
                except:
                    utils.printException()
                    time.sleep(1)
                    return
        except:
            utils.printException()
            time.sleep(1)
            return
    
    infile = file('autocomplete.txt', 'r')
    pool   = Pool(32)
    done   = 0
    offset = 0
    
    for line in infile:
        if offset < options.offset: offset += 1; continue
        if options.limit is not None and done > options.limit: break
        
        line = line[:-1]
        _add(line)
        
        done += 1
        if options.limit <= 100 or ((done - 1) % (options.limit / 100)) == 0:
            utils.log("done processing %s" % (utils.getStatusStr(done, options.limit), ))
    
    pool.join()
    infile.close()

if __name__ == '__main__':
    main()

