#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from crawler.sources.dumps import epf
import gzip, os, sqlite3, time

try:
    import psycopg2
    import psycopg2.extensions

    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
    use_sqlite = False
except ImportError:
    utils.log("Warning: missing required psycopg2 module")
    use_sqlite = True

from utils          import lazyProperty, AttributeDict, Singleton
from crawler.AEntitySource  import AExternalDumpEntitySource
from Schemas        import Entity
from pprint         import pprint

from boto.ec2.connection import EC2Connection
from boto.exception      import EC2ResponseError
from errors              import Fail

AWS_ACCESS_KEY_ID = 'AKIAIXLZZZT4DMTKZBDQ'
AWS_SECRET_KEY = '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'

class AppleEPFDistro(Singleton):
    @property
    def apple_data_dir(self):
        if not hasattr(self, 'lock'):
            self.lock = True
        else:
            while True:
                if hasattr(self, '_apple_data_dir'):
                    return self._apple_data_dir
                time.sleep(5)
        
        if False:
            #self.ec2:
            #self._volume = 'vol-52db3938'
            self._volume = 'vol-ccf832a6'
            
            self._instance_id = utils.shell('wget -q -O - http://169.254.169.254/latest/meta-data/instance-id')[0]
            
            self.conn = EC2Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)
            volume_dir = "/dev/sdh5"
            mount_dir  = "/mnt/crawlerdata"
            
            if not Globals.options.mount:
                while not os.path.exists(mount_dir):
                    time.sleep(5)
            else:
                volume = self.conn.get_all_volumes(volume_ids=[self._volume])[0]
                
                if volume.status != 'in-use' or volume.attach_data.instance_id != self._instance_id or volume.attach_data.device != volume_dir:
                    utils.shell("sudo mkdir -p %s" % mount_dir)
                    
                    if volume.status != 'available':
                        try:
                            utils.log("unmounting and detaching volume '%s' from '%s'" % (self._volume, volume_dir))
                            utils.shell('umount %s' % volume_dir)
                            volume.detach(force=True)
                        except EC2ResponseError:
                            pass
                        time.sleep(6)
                        while volume.status != 'available':
                            time.sleep(2)
                            print volume.update()
                    
                    utils.log("apple data volume '%s' on instance '%s': attaching at '%s' and mounting at '%s'" % (self._volume, self._instance_id, volume_dir, mount_dir))
                    try:
                        ret = self.conn.attach_volume(self._volume, self._instance_id, volume_dir)
                        assert ret
                    except EC2ResponseError:
                        utils.log("unable to mount apple data volume '%s' on instance '%s'" % (self._volume, self._instance_id))
                        raise
                    
                    while volume.status != u'in-use':
                        time.sleep(2)
                        volume.update()
                    
                    time.sleep(4)
                    
                    while not os.path.exists(mount_dir):
                        time.sleep(2)
                    
                    mounted = False
                    while not mounted:
                        mounted = 0 == utils.shell('mount -t ext3 %s %s' % (volume_dir, mount_dir))[1]
                        time.sleep(3)
            
            self._apple_data_dir = mount_dir
        else:
            base = os.path.dirname(os.path.abspath(__file__))
            
            apple_dir = os.path.join(os.path.join(base, "data"), "apple")
            assert os.path.exists(apple_dir)
            self._apple_data_dir = apple_dir
        
        return self._apple_data_dir
    
    def cleanup(self):
        if self.ec2:
            # unmount and detach volume
            sudo("umount %s" % self.apple_data_dir)
            # TODO: detach volume
            #volume.detach()
    
    @lazyProperty
    def ec2(self):
        return utils.is_ec2()

class AAppleEPFDump(AExternalDumpEntitySource):
    
    def __init__(self, name, entityMap, types, filename):
        AExternalDumpEntitySource.__init__(self, name, types, 512)
        global use_sqlite
        
        self._sqlite    = use_sqlite
        self._filename  = filename
        self._columnMap = entityMap
        
        self._distro = AppleEPFDistro.getInstance()
        self._init_db(filename)
    
    def _init_db(self, filename):
        # initialize db connection
        self.dbpath = "apple_epf.db"
        self.table  = filename
        
        if self._sqlite:
            self.conn   = sqlite3.connect(self.dbpath)
            self.db     = self.conn.cursor()
        else:
            self.conn = psycopg2.connect(host='localhost', database='stamped')
            self.db   = self.conn.cursor()
    
    def close(self):
        if self.db is not None:
            self.db.close()
            self.db = None
    
    def execute(self, cmd, verbose=False, error_okay=False):
        if verbose:
            utils.log(cmd)
        
        if self._sqlite:
            try:
                self.db.execute(cmd)
            except sqlite3.OperationalError, e:
                if not error_okay:
                    utils.log('warning: error running db cmd "%s"' % (cmd, ))
                    raise
        else:
            try:
                self.db.execute(cmd)
            except psycopg2.Error, e:
                if not error_okay:
                    utils.log('warning: error running db cmd "%s"' % (cmd, ))
                    utils.log(e.pgerror)
                    raise
                
                self.conn.rollback()
        
        return self.db
    
    def _open_file(self, countLines=True):
        filename = os.path.join(self._distro.apple_data_dir, self._filename)
        zipped = filename + ".gz"
        
        if not os.path.exists(filename) and not os.path.exists(zipped):
            if Globals.options.mount:
                raise Fail("ERROR: mount failed!")
            else:
                while (not os.path.exists(filename)) and (not os.path.exists(zipped)):
                    utils.log("waiting for mount to complete for file '%s'" % filename)
                    time.sleep(4)
        
        if os.path.exists(zipped):
            filename = zipped
        
        #utils.log("Opening Apple EPF file '%s'" % filename)
        if not os.path.exists(filename):
            utils.log("Apple EPF file '%s' does not exist!" % filename)
            raise Fail("Apple EPF file '%s' does not exist!" % filename)
        
        if filename.endswith(".gz"):
            f = gzip.open(filename, 'rb')
        else:
            f = open(filename, 'r+b')
        
        if countLines:
            numLines = max(0, utils.getNumLines(f) - 8)
        else:
            numLines = 0
        
        return f, numLines, filename
    
    def getMaxNumEntities(self):
        f, numLines, filename = self._open_file()
        f.close()
        
        return numLines
    
    def _run(self):
        utils.log("[%s] initializing" % self)
        f, numLines, filename = self._open_file(countLines=False)
        
        table_format = epf.parse_table_format(f, filename)
        self.table_format = table_format
        f.close()
        
        numLines = self.execute('SELECT COUNT(*) FROM "%s"' % self.table).fetchone()[0]
        utils.log("[%s] parsing ~%d entities from '%s'" % (self, numLines, self.table))
        
        rows  = self.execute('SELECT * FROM "%s"' % self.table)
        #self._globals['rows'] = rows; self._output.put(StopIteration); return
        count = 0
        
        for row in rows:
            row = self._format_result(row)
            self._parseRow(row)
            count += 1
            
            if numLines > 100 and (count % (numLines / 100)) == 0:
                utils.log("[%s] done parsing %s" % \
                    (self, utils.getStatusStr(count, numLines)))
                time.sleep(0.1)
        
        f.close()
        self._output.put(StopIteration)
        
        utils.log("[%s] finished parsing %d entities (filtered %d)" % (self, count, self.numFiltered))
    
    def _parseRow(self, row):
        retain_result = self._filter(row)
        
        if not retain_result:
            self.numFiltered += 1
            return
        
        entity = Entity()
        entity.subcategory = self.subcategories[0]
        
        if isinstance(retain_result, dict):
            for col, value in retain_result.iteritems():
                if value is not None:
                    entity[col] = value
        
        for k in row:
            if k not in self._columnMap:
                continue
            
            k2 = self._columnMap[k]
            if k2 is None:
                continue
            
            value = row[k]
            entity[k2] = row[k]
        
        utils.log(entity.title)
        self._output.put(entity)
    
    def _filter(self, row):
        return True
    
    def _get_cmd_results(self, k, v):
        if isinstance(v, basestring):
            v = "'%s'" % v
        
        cmd = 'SELECT * FROM %s WHERE %s=%s' % (self.table, k, v)
        return self.execute(cmd)
    
    def _format_result(self, result, transform=False):
        if result is not None:
            cols = self.table_format.cols
            if not transform:
                ret = { }
                for col in cols:
                    index = cols[col].index
                    ret[col] = result[index]
                
                result = AttributeDict(ret)
            else:
                entity = Entity()
                
                col_map = {
                    'name' : 'title', 
                    'collection_id' : 'aid', 
                    'song_id' : 'aid', 
                    'artist_id' : 'aid', 
                    'movie_id' : 'aid', 
                }
                
                for col in cols:
                    index = cols[col].index
                    if col in col_map:
                        col2 = col_map[col]
                    else:
                        col2 = col
                    
                    try:
                        entity[col2] = result[index]
                    except:
                        pass
                
                result = entity
        
        return result
    
    def get_row(self, k, v, transform=False):
        result = self._get_cmd_results(k, v).fetchone()
        
        return self._format_result(result, transform=transform)
    
    def get_rows(self, k, v, transform=False):
        results = self._get_cmd_results(k, v).fetchall()
        
        if results is None:
            return []
        
        for i in xrange(len(results)):
            results[i] = self._format_result(results[i], transform=transform)
        
        return results

