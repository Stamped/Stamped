#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import gzip, json, math, re, string, time, sys, unicodedata

from api.MongoStampedAPI    import MongoStampedAPI
from api.HTTPSchemas        import *
from api.Schemas            import *
from gevent.pool        import Pool
from optparse           import OptionParser
from pprint             import pprint, pformat

#-----------------------------------------------------------

class Trie(object):
    
    def __init__(self, key=None, parent=None):
        self.key       = key
        self.parent    = parent
        self.count     = 0
        self.children  = {}
    
    def add(self, key, scale_factor):
        self.count += scale_factor
        if len(key) <= 0:
            return
        
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
        return self._prune(max_depth, max_depth, min_count)
    
    def _prune(self, max_depth, orig_max_depth, min_count=0):
        if max_depth <= 1 or self.count < min_count:
            self.children = {}
        #elif orig_max_depth > max_depth + 4 and self.count == min_count:
        #    self.children = {}
        else:
            to_delete = []
            for child in self.children:
                if self.children[child].count < min_count:
                    to_delete.append(child)
                else:
                    self.children[child]._prune(max_depth - 1, orig_max_depth, min_count)
            
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
            key = entry['title'].lower()
            
            # attempt to replace accented characters with their ascii equivalents
            key = unicodedata.normalize('NFKD', unicode(key)).encode('ascii', 'ignore')
            key = re.sub('([^a-zA-Z0-9._ -])', '', key)
            key = key.strip()
            
            output.add(key, scale_factor)
            
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
    importance_threshold = 20
    
    # weight places results to count for more when pruning the trie tree
    # later on for less important subtrees
    entries = placesDB._collection.find(fields={'title' : 1, '_id' : 0})
    add_entries(entries, 'places', trie, importance_threshold)
    
    subcategories = [
        ('song', 1.0, ), 
        ('album', 1.0, ), 
        ('app', importance_threshold, ), 
        ('song', importance_threshold, {'sources.apple.a_popular' : True}), 
        ('album', importance_threshold, {'sources.apple.a_popular' : True}), 
        ('artist', importance_threshold), 
        ('book', importance_threshold), 
        ('movie', importance_threshold / 2), 
        ('tv', importance_threshold), 
    ]
    
    for s in subcategories:
        query = { "subcategory" : s[0] }
        if 3 == len(s):
            for k, v in s[2].iteritems():
                query[k] = v
        
        entries = entityDB._collection.find(query, fields={'title' : 1, '_id' : 0})
        add_entries(entries, s[0], trie, s[1])
    
    print "done constructing trie!"
    pprint({
        'num_nodes' : trie.num_nodes(), 
        'max_depth' : trie.max_depth(), 
        'avg_depth' : trie.avg_depth(), 
    })
    
    print "pruning tree..."
    trie.prune(max_depth=17, min_count=importance_threshold)
    
    pprint({
        'num_nodes' : trie.num_nodes(), 
        'max_depth' : trie.max_depth(), 
        'avg_depth' : trie.avg_depth(), 
    })
    
    #def _print(tree):
    #    print "%s) %d" % (tree.full().encode('ascii', 'replace'), tree.count)
    #trie.visit(_print)
    
    out   = file('autocomplete.txt', 'w')
    names = set()
    
    def _add(tree):
        try:
            orig_name = tree.full()
            if 0 == len(orig_name):
                return
            
            name = encode_s3_name(orig_name)
            if 0 == len(name) or name in names:
                return
            
            names.add(name)
            
            out_name = orig_name.encode('ascii', 'replace')
            if out_name == orig_name:
                out.write(orig_name + "\n")
            
            return
        except:
            utils.printException()
            time.sleep(1)
            return
    
    trie.visit(_add)
    out.close()

if __name__ == '__main__':
    main()

#t=Trie()
#t.add('fred')
#t.add('google')
#t.add('goo')
t = _globals['t']

