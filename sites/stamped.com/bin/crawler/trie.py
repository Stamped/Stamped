#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import aws, gzip, json, math, re, string, time

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

class Trie(object):
    
    def __init__(self, key=None, parent=None):
        self.key       = key
        self.parent    = parent
        self.count     = 0
        self.children  = {}
    
    def add(self, key, scale_factor):
        if len(key) <= 0:
            return
        
        self.count += scale_factor
        l = key[0]
        
        if not l in self.children:
            self.children[l] = Trie(key=l, parent=self)
        
        self.children[l].add(key[1:], scale_factor)
    
    def full(self):
        if self.parent is None:
            return ""
        
        return self.parent.full() + self.key
    
    def get(self):
        children = {}
        for child in self.children:
            children[child] = self.children[child].get()
        
        data = {
            'key' : self.key, 
            'children' : children, 
        }
        
        return data
    
    def num_nodes(self):
        count = sum(self.children[child].num_nodes() for child in self.children)
        return 1 + count
    
    def max_depth(self):
        depth = 0
        for child in self.children:
            depth = max(depth, self.children[child].max_depth())
        
        return 1 + depth
    
    def avg_depth(self):
        depths = []
        if 0 == len(self.children):
            depths = [ 0 ]
        
        for child in self.children:
            depths.extend(self.children[child].avg_depth())
        
        for i in xrange(len(depths)):
            depths[i] += 1
        
        if self.parent is None:
            return sum(depths) / float(len(depths))
        else:
            return depths
    
    def prune(self, max_depth, min_count=0):
        if max_depth <= 1 or self.count <= min_count:
            self.children = {}
        else:
            to_delete = []
            for child in self.children:
                if self.children[child].count <= min_count:
                    to_delete.append(child)
                else:
                    self.children[child].prune(max_depth - 1, min_count)
            
            for d in to_delete:
                del self.children[d]
    
    def visit(self, func):
        ret = func(self)
        if ret is not False:
            for child in self.children:
                self.children[child].visit(func)
    
    def __str__(self):
        return pformat(self.get(), indent=1)

def parseCommandLine():
    usage   = "Usage: %prog [options] [sources]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", 
        help="db to connect to for output")
    
    (options, args) = parser.parse_args()
    Globals.options = options
    
    if options.db:
        utils.init_db_config(options.db)
    
    options.verbose = False
    return options

def add_entries(entries, hint, output, scale_factor=1.0):
    count = entries.count()
    done  = 0
    
    utils.log("[%s] processing %d entity titles..." % (hint, count, ))
    for entry in entries:
        if 'title' in entry:
            output.add(entry['title'].lower(), scale_factor)
            
            done += 1
            if count <= 100 or ((done - 1) % (count / 100)) == 0:
                utils.log("[%s] done processing %s" % (hint, utils.getStatusStr(done, count)))

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
    
    trie = Trie()
    _globals['t'] = trie
    
    # weight places results to count for more when pruning the trie tree
    # later on for less important subtrees
    entries = placesDB._collection.find(fields={'title' : 1})
    add_entries(entries, 'places', trie, 5.0)
    
    for s in [ ('song', 0.5), ('album', 0.5), ('artist', 0.5), ('book', 4.0), ('movie', 3.0) ]:
        entries = entityDB._collection.find({"subcategory" : s[0]}, fields={'title' : 1})
        add_entries(entries, s[0], trie, s[1])
    
    print "done constructing trie!"
    pprint({
        'num_nodes' : trie.num_nodes(), 
        'max_depth' : trie.max_depth(), 
        'avg_depth' : trie.avg_depth(), 
    })
    
    print "pruning tree..."
    trie.prune(max_depth=20, min_count=30)
    
    pprint({
        'num_nodes' : trie.num_nodes(), 
        'max_depth' : trie.max_depth(), 
        'avg_depth' : trie.avg_depth(), 
    })
    
    """
    def _print(tree):
        print "%s) %d" % (tree.full().encode('ascii', 'replace'), tree.count)
    trie.visit(_print)
    return
    """
    
    autocompleteDB = S3AutocompleteDB()
    names = set()
    
    def _add(tree):
        try:
            orig_name = tree.full()
            
            if 0 == len(orig_name):
                return
            
            name = encode_s3_name(orig_name)
            name = "search/%s.json" % name
            
            if 0 == len(name) or name in names:
                return
            names.add(name)
            
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
                'count' : tree.count, 
                'num_r' : len(results)
            }
            
            pprint(data)
            
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
    
    trie.visit(_add)

if __name__ == '__main__':
    main()

#t=Trie()
#t.add('fred')
#t.add('google')
#t.add('goo')
t = _globals['t']

