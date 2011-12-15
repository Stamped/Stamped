#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import datetime, gzip, httplib, json, logging, os, sys, pickle, string, threading, time, re
import htmlentitydefs, traceback, urllib, urllib2
import aws, logs, math, random, boto

from boto.ec2.connection import EC2Connection
from subprocess          import Popen, PIPE
from functools           import wraps
from BeautifulSoup       import BeautifulSoup
from StringIO            import StringIO

def shell(cmd, customEnv=None):
    pp = Popen(cmd, shell=True, stdout=PIPE, env=customEnv)
    delay = 0.01
    
    """
    while pp.returncode is None:
        time.sleep(delay)
        delay *= 2
        if delay > 1:
            delay = 1
        
        log(pp.poll())
    """
    
    output = pp.stdout.read().strip()
    status = pp.wait()
    
    return (output, status)

def shell2(cmd, *args, **kwargs):
    pp = Popen(cmd, args, kwargs)
    output = pp.stdout.read().strip()
    status = pp.wait()
    
    return (output, status)

def shell3(cmd, customEnv=None):
    pp = Popen(cmd, shell=True)
    status = pp.wait()
    
    return status

def lazyProperty(undecorated):
    name = '_' + undecorated.__name__
    @property
    @wraps(undecorated)
    def decorated(self):
        try:
            return getattr(self, name)
        except AttributeError:
            v = undecorated(self)
            setattr(self, name, v)
            return v
    return decorated

def log(s=""):
    s = _formatLog(s) + "\n"
    
    logs.debug(s)
    sys.stderr.write(s)
    sys.stdout.flush()
    sys.stderr.flush()

def logRaw(s, includeFormat=False):
    if includeFormat:
        s = _formatLog(s)
    
    sys.stderr.write(s)
    sys.stdout.flush()
    sys.stderr.flush()

def _formatLog(s):
    try:
        return "[%s] %s" % (threading.currentThread().getName(), normalize(s, strict=True))
    except:
        return "[%s] __error__ printout" % (threading.currentThread().getName(), )

def write(filename, content):
    f = open(filename, "w")
    f.write(content)
    f.close()

def getFormattedException():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    f = traceback.format_exception(exc_type, exc_value, exc_traceback)
    return string.joinfields(f, '')

def printException():
    """
        Simple debug utility to print a stack trace.
    """
    #traceback.print_exc()
    
    #traceback.print_exception(exc_type, exc_value, exc_traceback,
    #                          limit=8, file=sys.stderr)
    logs.warning(getFormattedException())

def resolvePath(path):
    if "." in path and not os.path.exists(path):
        pkg  = __import__(path, {}, {}, path)
        path = os.path.dirname(os.path.abspath(pkg.__file__))
    
    return os.path.abspath(path)

def getFuncName(offset=0):
    import inspect
    return inspect.stack()[1 + offset][3]

def getPythonConfigFile(path, pickled=False, jsonPickled=False):
    if os.path.exists(path):
        with open(path, "rb") as fp:
            source = fp.read()
        
        if pickled:
            return AttributeDict(pickle.loads(source))
        elif jsonPickled:
            return AttributeDict(json.loads(source))
        else:
            return AttributeDict(eval(source))
    else:
        return AttributeDict()

def getenv(var, default=None):
    value = os.getenv(var)
    
    if value is None or value == "":
        if default:
            return default
        else:
            raise Exception("error: environment variable '%s' not set!" % var)
    
    return value

class AttributeDict(object):
    def __init__(self, *args, **kwargs):
        d = kwargs
        if args:
            d = args[0]
        super(AttributeDict, self).__setattr__("_dict", d)
    
    def __setattr__(self, name, value):
        self[name] = value
    
    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        #elif name == "_dict":
        #   return object.__getattribute__(self, name)
        
        try:
            return self[name]
        except KeyError:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))
    
    def __setitem__(self, name, value):
        self._dict[name] = self._convert_value(value)

    def __getitem__(self, name):
        return self._convert_value(self._dict[name])

    def _convert_value(self, value):
        if isinstance(value, dict) and not isinstance(value, AttributeDict):
            return AttributeDict(value)
        
        return value

    def copy(self):
        return self.__class__(self._dict.copy())

    def update(self, *args, **kwargs):
        self._dict.update(*args, **kwargs)

    def items(self):
        return self._dict.items()

    def values(self):
        return self._dict.values()

    def keys(self):
        return self._dict.keys()

    def pop(self, *args, **kwargs):
        return self._dict.pop(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self._dict.get(*args, **kwargs)

    def __repr__(self):
        return self._dict.__repr__()

    def __unicode__(self):
        return self._dict.__unicode__()

    def __str__(self):
        return self._dict.__str__()

    def __iter__(self):
        return self._dict.__iter__()

    def __getstate__(self):
        return self._dict

    def __setstate__(self, state):
        super(AttributeDict, self).__setattr__("_dict", state)

class Singleton(object):
    __instance = None
    
    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        
        return cls.__instance

from collections import MutableMapping
from itertools import izip_longest as _zip_longest

class OrderedDict(dict, MutableMapping):
    """
        Dictionary which respects order of item insertion / removal.
        Return an instance of a dict subclass, supporting the usual :class:`dict`
        methods.  An *OrderedDict* is a dict that remembers the order that keys
        were first inserted. If a new entry overwrites an existing entry, the
        original insertion position is left unchanged.  Deleting an entry and
        reinserting it will move it to the end.
        
        Taken from current draft of <a href=http://www.python.org/dev/peps/pep-0372/>
        PEP 372: Adding an ordered dictionary to collections</a>
    """
    
    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        if not hasattr(self, '_keys'):
            self._keys = []
        self.update(*args, **kwds)

    def clear(self):
        del self._keys[:]
        dict.clear(self)

    def __setitem__(self, key, value):
        if key not in self:
            self._keys.append(key)
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._keys.remove(key)

    def __iter__(self):
        return iter(self._keys)

    def __reversed__(self):
        return reversed(self._keys)

    def popitem(self):
        if not self:
            raise KeyError('dictionary is empty')
        key = self._keys.pop()
        value = dict.pop(self, key)
        return key, value

    def __reduce__(self):
        items = [[k, self[k]] for k in self]
        inst_dict = vars(self).copy()
        inst_dict.pop('_keys', None)
        return (self.__class__, (items,), inst_dict)

    setdefault = MutableMapping.setdefault
    update = MutableMapping.update
    pop = MutableMapping.pop
    keys = MutableMapping.keys
    values = MutableMapping.values
    items = MutableMapping.items

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self.items()))

    def copy(self):
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def __eq__(self, other):
        if isinstance(other, OrderedDict):
            return all(p==q for p, q in  _zip_longest(self.items(), other.items()))
        return dict.__eq__(self, other)

def getFile(url, request=None, params=None):
    """
        Wrapper around urllib2.urlopen(url).read(), which attempts to increase 
        the success rate by sidestepping server-side issues and usage limits by
        retrying unsuccessful attempts with increasing delays between retries, 
        capped at a maximum possibly delay, after which the request will simply
        fail and propagate any exceptions normally.
    """
    
    maxDelay = 64
    delay = 0.5
    data = None
    request = None
    
    if request is None:
        if params is not None and isinstance(params, dict):
            params = urllib.urlencode(params)
        
        request = urllib2.Request(url, params)
        request.add_header('Accept-encoding', 'gzip')
    
    while True:
        try:
            response = urllib2.urlopen(request)
            data = response.read()
            break
        except urllib2.HTTPError, e:
            #log("'%s' fetching url '%s'" % (str(e), url))
            #printException()
            
            # reraise the exception if the request resulted in an HTTP client 4xx error code, 
            # since it was a problem with the url / headers and retrying most likely won't 
            # solve the problem.
            if e.code >= 400 and e.code < 500:
                raise
            
            # if delay is already too large, request will likely not complete successfully, 
            # so propagate the error and return.
            if delay > maxDelay:
                raise
        except (ValueError, IOError, httplib.BadStatusLine) as e:
            #log("Error '%s' fetching url '%s'" % (str(e), url))
            #printException()
            
            # if delay is already too large, request will likely not complete successfully, 
            # so propagate the error and return.
            if delay > maxDelay:
                raise
        except Exception, e:
            print type(e)
            log("[utils] Unexpected Error '%s' fetching url '%s'" % (str(e), url))
            if delay > maxDelay:
                raise
        
        # encountered error fetching document. delay for a bit and try again
        #log("Attempting to recover with delay of %d" % delay)
        
        # put the current thread to sleep for a bit, increase the delay, 
        # and retry the request
        time.sleep(delay)
        delay *= 2
    
    if response.info().get('Content-Encoding') == 'gzip':
        #data = zlib.decompress(data)
        buf = StringIO(data)
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
        buf.close()
    
    if hasattr(response, 'fp') and hasattr(response.fp, '_sock') and hasattr(response.fp._sock, 'recv'):
        response.fp._sock.recv = None
    
    response.close()
    # return the successfully downloaded file
    return data

def getSoup(url, opener=None):
    """ downloads and returns the BeautifulSoup parsed version of the file at the given url """
    return BeautifulSoup(getFile(url, opener))

def createEnum(*sequential, **named):
    return dict(zip(sequential, range(len(sequential))), **named)

def count(container):
    """
        utility to count the number of items in the given container, whether it 
        be a concrete data type or an iterator. think of this function as len()
        but for either a built-in container type or an iterator.
    """
    
    try:
        return len(container)
    except:
        # count the number of elements in a generator expression
        return sum(1 for item in container)

def removeNonAscii(s):
    return "".join(ch for ch in s if ord(ch) < 128)

def normalize(s, strict=False):
    """ 
        Attempts to normalize the given value. If it is a string, this includes 
        escaping html codes and possibly removing non-ascii characters.
    """
    
    try:
        if isinstance(s, basestring):
            # replace html escape sequences with their unicode equivalents
            if '&' in s and ';' in s:
                for name in htmlentitydefs.name2codepoint:
                    escape_seq = '&%s;' % name
                    
                    while True:
                        l = s.lower().find(escape_seq)
                        if l < 0:
                            break
                        
                        if name == 'lsquo' or name == 'rsquo':
                            # simplify unicode single quotes to use the ascii apostrophe character
                            val = "'"
                        else:
                            val = unichr(htmlentitydefs.name2codepoint[name])
                        
                        s = u"%s%s%s" % (s[:l], val, s[l+len(escape_seq):])
            
            # handle &#xxxx;
            escape_seq = '&#'
            while True:
                l = s.find(escape_seq)
                if l < 0:
                    break
                
                m = s.find(';', l)
                if m < 0 or m <= l + 2:
                    break
                
                try:
                    val = unichr(int(s[l + 2 : m]))
                except ValueError:
                    try:
                        val = unichr(int(s[l + 3 : m]))
                    except ValueError:
                        break
                
                s = u"%s%s%s" % (s[:l], val, s[m + 1:])
        
        if strict and isinstance(s, unicode):
            s = removeNonAscii(s.encode("utf-8"))
    except Exception as e:
        printException()
        log(e)
    
    return s

def numEntitiesToStr(numEntities):
    if numEntities == 1:
        return 'entity'
    else:
        return 'entities'

def getStatusStr(count, maxCount):
    return "%d%% (%d / %d)" % (round((100.0 * count) / max(1, maxCount)), count, maxCount)

def abstract(func):
    """ marks the target function as abstract """
    
    def wrapper(*__args, **__kwargs):
        raise NotImplementedError('Missing required %s() method' % func.__name__)
    
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__  = func.__doc__
    
    return wrapper

def getInstance(name):
    """ returns the AWS instance associated with the stackName.nodeName (e.g., peach.db0) """
    
    name = name.lower()
    
    try:
        if '.' in name:
            inputStackName, inputNodeName = name.split('.')
        else:
            inputStackName, inputNodeName = name, None
    except ValueError:
        return None
    
    conn = EC2Connection(aws.AWS_ACCESS_KEY_ID, aws.AWS_SECRET_KEY)
    reservations = conn.get_all_instances()
    
    for reservation in reservations:
        for instance in reservation.instances:
            if instance.state != 'running' or not hasattr(instance, 'tags'):
                continue
            
            if 'stack' in instance.tags:
                stackName = instance.tags['stack']
                
                if stackName is None or stackName.lower() == inputStackName:
                    if not inputNodeName or \
                        ('name' in instance.tags and instance.tags['name'].lower() == inputNodeName):
                        return instance
    
    return None

def is_ec2():
    """ returns whether or not this python program is running on EC2 """
    
    return os.path.exists("/proc/xen") and os.path.exists("/etc/ec2_version")

def init_db_config(conf):
    """ initializes MongoDB with proper host configuration """
    
    if ':' in conf:
        host, port = conf.split(':')
        port = int(port)
    else:
        host, port = (conf, 27017)
        
        if '.' in conf and not conf.endswith('.com'):
            # attempt to resolve the (possible) semantic EC2 instance name to 
            # a valid DNS name or associated IP address
            instance = getInstance(conf)
            
            if instance:
                if is_ec2():
                    host = instance.private_dns_name
                else:
                    host = instance.public_dns_name
    
    config = {
        'mongodb' : {
            'host' : host, 
            'port' : port, 
        }
    }
    
    # TODO: there is a Python oddity that needs some investigation, where, depending on 
    # where and when the MongoDBConfig Singleton is imported, it'll register as the same 
    # instance that AMongoCollection knows about or not. For now, as a workaround, just 
    # import it multiple ways and initialize the config with both possible import paths.
    from api.db.mongodb.AMongoCollection import MongoDBConfig
    cfg = MongoDBConfig.getInstance()
    cfg.config = AttributeDict(config)
    
    from db.mongodb.AMongoCollection import MongoDBConfig as MongoDBConfig2
    cfg2 = MongoDBConfig2.getInstance()
    cfg2.config = AttributeDict(config)
    
    return config

def is_func(obj):
    return hasattr(obj, '__call__')

def get_spherical_distance(latLng1, latLng2):
    try:
        # convert latitude and longitude to spherical coordinates in radians
        degrees_to_radians = math.pi / 180.0
        
        # phi = 90 - latitude
        phi1 = (90.0 - latLng1[0]) * degrees_to_radians
        phi2 = (90.0 - latLng2[0]) * degrees_to_radians
        
        # theta = longitude
        theta1 = latLng1[1] * degrees_to_radians
        theta2 = latLng2[1] * degrees_to_radians
        
        # compute distance from spherical coordinates
        cos = (math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) + 
               math.cos(phi1) * math.cos(phi2))
        arc = math.acos(cos)
        
        # multiply arc by the earth's radius in your desired units to get length
        return arc
    except:
        return -1

def validate_email(email):
    # Taken from Django validators.py
    email_re = re.compile(
        R"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        R'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
        R')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain

    try:
        if email_re.match(email):
            return True
        raise
    except:
        return False

def validate_screen_name(screen_name):
    screen_name_re = re.compile("^[\w-]{1,20}$", re.IGNORECASE)
    
    try:
        if screen_name_re.match(screen_name):
            return True
        raise
    except:
        return False

def validate_hex_color(color):
    color_re = re.compile("^[0-9a-f]{3}(?:[0-9a-f]{3})?$", re.IGNORECASE)
    
    try:
        if color_re.match(color):
            return True
        raise
    except:
        return False

def getNumLines(f):
    numLines = 0
    bufferSize = 1024 * 1024
    read_f = f.read # loop optimization
    
    buf = read_f(bufferSize)
    while buf:
        numLines += buf.count('\n')
        buf = read_f(bufferSize)
    
    f.seek(0)
    return numLines

def sampleCDF(cdf, item_func=lambda i: i):
    total = 0.0
    
    for item in cdf:
        total += item_func(item)
    
    x = random.random() * total
    i = 0
    for item in cdf:
        x -= item_func(item)
        
        if x <= 0:
            return i
        
        i += 1
    
    return i - 1

def sendEmail(msg, **kwargs):
    if not validate_email(msg['to']):
        msg = "Invalid email address"
        logs.warning(msg)
        raise Exception(msg)
    
    format = kwargs.pop('format', 'text')
    
    try:
        ses = boto.connect_ses(aws.AWS_ACCESS_KEY_ID, aws.AWS_SECRET_KEY)
        ses.send_email(msg['from'], msg['subject'], msg['body'], msg['to'], format=format)
    except Exception as e:
        logs.warning('EMAIL FAILED: %s' % msg)
        logs.warning(e)

    return True

def parseTemplate(src, params):
    try:
        from jinja2 import Template
    except ImportError:
        print "error installing Jinja2"
        raise
    
    source = src.read()
    template = Template(source)
    return template.render(params)

def runMongoCommand(mongo_cmd, db='stamped', verbose=False):
    from api.db.mongodb.AMongoCollection import MongoDBConfig
    
    cmd_template = "mongo --quiet %s:%s/%s --eval 'printjson(%s);'"
    cfg = MongoDBConfig.getInstance()
    cmd = cmd_template % (cfg.host, cfg.port, db, mongo_cmd)
    
    if verbose:
        log(cmd)
    
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.temp.sh')
    
    f=open(path, 'w')
    f.write(cmd)
    f.close()
    os.system('chmod +x %s' % path)
    
    cmd = '/bin/bash -c %s' % path
    ret = shell(cmd)
    
    try:
        return json.loads(ret[0])
    except ValueError:
        return ret[0]

def get_basic_stats(collection, key):
    """
        Returns the mean, standard deviation, max, and min values for the key 
        across the given collection.
    """
    
    max_value = None
    min_value = None
    total = 0
    
    for item in collection:
        value = item[key]
        total += value
        
        if max_value is None or value > max_value:
            max_value = value
        
        if min_value is None or value < min_value:
            min_value = value
    
    count = max(1, len(collection))
    avg   = total / float(count)
    
    total = 0
    for item in collection:
        diff = item[key] - avg
        total += diff * diff
    
    std   = math.sqrt(total / float(max(count - 1, 1)))
    
    return {
        'avg' : round_float(avg, 4), 
        'std' : round_float(std, 4), 
        'min' : round_float(min_value, 4), 
        'max' : round_float(max_value, 4), 
    }

def round_float(f, n):
    """ Truncates/pads a float f to n decimal places without rounding """
    try:
        slen = len('%.*f' % (n, f))
        return str(f)[:slen]
    except:
        return 0

def get_modified_time(filename):
    return datetime.datetime.fromtimestamp(os.path.getmtime(filename))

