#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Assorted utility commands and classes
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import datetime, gzip, httplib, json, logging, os, pickle, re, string, sys
import htmlentitydefs, threading, time, traceback, urllib, urllib2
import keys.aws, logs, math, random, boto, bson
import libs.ec2_utils
import functools
import PIL, Image, ImageFile

from errors              import *
from boto.ec2.connection import EC2Connection
from subprocess          import Popen, PIPE
from functools           import wraps
from BeautifulSoup       import BeautifulSoup
from StringIO            import StringIO
from threading           import Lock
from gevent.pool         import Pool



class LoggingThreadPool(object):
    """
    Wrapper around gevent.pool.Pool that (a) logs any exceptions that show up in the spawned tasks and (b) ensures that
    log statements from the spawned tasks are attached to the current logging context.
    """
    def __init__(self, *args, **kwargs):
        self.__pool = Pool(*args, **kwargs)

    def spawn(self, fn, *args, **kwargs):
        def userFn():
            return fn(*args, **kwargs)

        currLoggingContext = logs.localData.loggingContext

        @functools.wraps(fn)
        def wrapperFn():
            try:
                return logs.runInOtherLoggingContext(userFn, currLoggingContext)
            except:
                logs.report()

        self.__pool.spawn(wrapperFn)

    def __getattr__(self, attr):
        return getattr(self.__pool, attr)


def shell(cmd, customEnv=None):
    pp = Popen(cmd, shell=True, stdout=PIPE, env=customEnv)
    """
    delay = 0.01
    
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

def is_running(cmd):
    return 0 == shell("ps -ef | grep '%s' | grep -v grep" % cmd)[1]

def lazyProperty(undecorated):
    name = '__lazyProperty_' + undecorated.__name__
    propertyLock = Lock()
    @property
    @wraps(undecorated)
    def decorated(self):
        try:
            pair = getattr(self, name)
        except AttributeError:
            with propertyLock:
                if hasattr(self, name):
                    pair = getattr(self, name)
                else:
                    pair = ([], Lock())
                    setattr(self, name, pair)
        closure, lock = pair
        if len(closure) == 0:
            with lock:
                if len(closure) == 0:
                    closure.append(undecorated(self))
        return closure[0]

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
        return normalize(str(s), strict=True)
    except Exception:
        return "[%s] __error__ printout" % (threading.currentThread().getName(), )
    
    """
    try:
        return "[%s] %s" % (threading.currentThread().getName(), normalize(s, strict=True))
    except:
        return "[%s] __error__ printout" % (threading.currentThread().getName(), )
    """

def logTask(task):
    # note: if isinstance(task, celery.result.EagerResult), then task was run locally / synchronously
    log("ASYNC: '%s' '%s' '%s' '%s'" % (type(task), task.ready(), task.successful(), task))

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
    
    setdefault  = MutableMapping.setdefault
    update      = MutableMapping.update
    pop         = MutableMapping.pop
    keys        = MutableMapping.keys
    values      = MutableMapping.values
    items       = MutableMapping.items
    
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

def getFile(url, request=None, params=None, logging=False):
    """
        Wrapper around urllib2.urlopen(url).read(), which attempts to increase 
        the success rate by sidestepping server-side issues and usage limits by
        retrying unsuccessful attempts with increasing delays between retries, 
        capped at a maximum possibly delay, after which the request will simply
        fail and propagate any exceptions normally.
    """
    
    maxDelay = 64
    delay    = 0.5
    data     = None
    request  = None
    
    if request is None:
        if params is not None and isinstance(params, dict):
            params = urllib.urlencode(params)
        
        request = urllib2.Request(url, params)
        request.add_header('Accept-encoding', 'gzip')
    
    while True:
        try:
            if logging:
                log(request.get_full_url())
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
                logs.warning("Failed: %s" % e)
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
        print 'wait %s' % delay
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
    """ marks the target function as abstract

    Consider replacing with functionality from the abc (Abstract Base Class) module.
    Specifically: 
    abc.ABCMeta - metaclass for abstract classes
    abc.abstractmethod - decorator for abstract methods
    abc.abstractproperty - decorator for abstract properties 
    """
    
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
    
    conn = EC2Connection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
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

def getDomain():
    if is_ec2():
        if libs.ec2_utils.is_prod_stack():
            return "https://api.stamped.com/v0/"
        return "https://dev.stamped.com/v0/"
    return "localhost:18000/v0/"



def get_db_config(config_desc):
    """ returns MongoDB host configuration """
    
    if ':' in config_desc:
        host, port = config_desc.split(':')
        port = int(port)
    else:
        host, port = (config_desc, 27017)
        
        if '.' in config_desc and not config_desc.endswith('.com'):
            # attempt to resolve the (possible) semantic EC2 instance name to 
            # a valid DNS name or associated IP address
            instance = getInstance(config_desc)
            
            if instance:
                if is_ec2():
                    host = instance.private_dns_name
                else:
                    host = instance.public_dns_name
    
    return host, port

def init_db_config(config_desc):
    """ initializes MongoDB with proper host configuration """
    
    host, port = get_db_config(config_desc)
    config = {
        'mongodb' : {
            'hosts' : [(host, port)],
        }
    }
    
    # TODO: there is a Python oddity that needs some investigation, where, depending on 
    # where and when the MongoDBConfig Singleton is imported, it'll register as the same 
    # instance that AMongoCollection knows about or not. For now, as a workaround, just 
    # import it multiple ways and initialize the config with both possible import paths.
    from api.db.mongodb.AMongoCollection import MongoDBConfig
    cfg = MongoDBConfig.getInstance()
    cfg.config = AttributeDict(config)
    
    from api.db.mongodb.AMongoCollection import MongoDBConfig as MongoDBConfig2
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

# email regex taken from Django validators.py
__email_re       = re.compile(
    R"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"               # dot-atom
    R'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    R')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)   # domain
__screen_name_re = re.compile("^[\w-]{1,20}$", re.IGNORECASE)
__color_re       = re.compile("^[0-9a-f]{3}(?:[0-9a-f]{3})?$", re.IGNORECASE)

def validate_email(email):

    # Source: http://data.iana.org/TLD/tlds-alpha-by-domain.txt
    # Version 2012012600, Last Updated Thu Jan 26 15:07:01 2012 UTC
    valid_suffixes = set(["AC", "AD", "AE", "AERO", "AF", "AG", "AI", "AL", "AM", "AN", "AO", "AQ", "AR", "ARPA", "AS", 
        "ASIA", "AT", "AU", "AW", "AX", "AZ", "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BIZ", "BJ", "BM", "BN", 
        "BO", "BR", "BS", "BT", "BV", "BW", "BY", "BZ", "CA", "CAT", "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL", 
        "CM", "CN", "CO", "COM", "COOP", "CR", "CU", "CV", "CW", "CX", "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ", 
        "EC", "EDU", "EE", "EG", "ER", "ES", "ET", "EU", "FI", "FJ", "FK", "FM", "FO", "FR", "GA", "GB", "GD", "GE", 
        "GF", "GG", "GH", "GI", "GL", "GM", "GN", "GOV", "GP", "GQ", "GR", "GS", "GT", "GU", "GW", "GY", "HK", "HM", 
        "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IM", "IN", "INFO", "INT", "IO", "IQ", "IR", "IS", "IT", "JE", "JM", 
        "JO", "JOBS", "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ", "LA", "LB", "LC", "LI", 
        "LK", "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MC", "MD", "ME", "MG", "MH", "MIL", "MK", "ML", "MM", "MN", 
        "MO", "MOBI", "MP", "MQ", "MR", "MS", "MT", "MU", "MUSEUM", "MV", "MW", "MX", "MY", "MZ", "NA", "NAME", "NC", 
        "NE", "NET", "NF", "NG", "NI", "NL", "NO", "NP", "NR", "NU", "NZ", "OM", "ORG", "PA", "PE", "PF", "PG", "PH", 
        "PK", "PL", "PM", "PN", "PR", "PRO", "PS", "PT", "PW", "PY", "QA", "RE", "RO", "RS", "RU", "RW", "SA", "SB", 
        "SC", "SD", "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "ST", "SU", "SV", "SX", "SY", 
        "SZ", "TC", "TD", "TEL", "TF", "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO", "TP", "TR", "TRAVEL", "TT", 
        "TV", "TW", "TZ", "UA", "UG", "UK", "US", "UY", "UZ", "VA", "VC", "VE", "VG", "VI", "VN", "VU", "WF", "WS", 
        "XN--0ZWM56D", "XN--11B5BS3A9AJ6G", "XN--3E0B707E", "XN--45BRJ9C", "XN--80AKHBYKNJ4F", "XN--90A3AC", 
        "XN--9T4B11YI5A", "XN--CLCHC0EA0B2G2A9GCD", "XN--DEBA0AD", "XN--FIQS8S", "XN--FIQZ9S", "XN--FPCRJ9C3D", 
        "XN--FZC2C9E2C", "XN--G6W251D", "XN--GECRJ9C", "XN--H2BRJ9C", "XN--HGBK6AJ7F53BBA", "XN--HLCJ6AYA9ESC7A", 
        "XN--J6W193G", "XN--JXALPDLP", "XN--KGBECHTV", "XN--KPRW13D", "XN--KPRY57D", "XN--LGBBAT1AD8J", "XN--MGBAAM7A8H", 
        "XN--MGBAYH7GPA", "XN--MGBBH1A71E", "XN--MGBC0A9AZCG", "XN--MGBERP4A5D4AR", "XN--O3CW4H", "XN--OGBPF8FL", 
        "XN--P1AI", "XN--PGBS0DH", "XN--S9BRJ9C", "XN--WGBH1C", "XN--WGBL6A", "XN--XKC2AL3HYE2A", "XN--XKC2DL3A5EE0H", 
        "XN--YFRO4I67O", "XN--YGBI2AMMX", "XN--ZCKZAH", "XXX", "YE", "YT", "ZA", "ZM", "ZW"])
    try:
        if __email_re.match(email):
            if email.split('.')[-1].upper() in valid_suffixes:
                return True
    except:
        pass
    
    return False

def validate_screen_name(screen_name):
    try:
        if __screen_name_re.match(screen_name) and isinstance(screen_name, basestring):
            return True
    except:
        pass
    
    return False

def validate_hex_color(color):
    try:
        if __color_re.match(color):
            return True
    except:
        pass
    
    return False



def validate_url(url):
    from django.core.validators import URLValidator
    from django.core.exceptions import ValidationError
    
    val = URLValidator(verify_exists=False)
    
    try:
        val(url)
    except ValidationError, e:
        return False
    
    return True

def getNumLines(f):
    bufferSize = 1024 * 1024
    numLines   = 0
    read_f     = f.read # loop optimization
    buf        = read_f(bufferSize)
    
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

def shuffle(array):
    l = len(array)
    o = range(l)
    a = range(l)
    
    for i in xrange(l):
        j = a.pop(random.randint(0, len(a) - 1))
        
        o[j] = array[i]
    
    return o

def sendEmail(msg, **kwargs):
    if not validate_email(msg['to']):
        msg = "Invalid email address"
        logs.warning(msg)
        raise Exception(msg)
    
    format = kwargs.pop('format', 'text')
    
    try:
        ses = boto.connect_ses(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
        ses.send_email(msg['from'], msg['subject'], msg['body'], msg['to'], format=format)
    except Exception as e:
        logs.warning('EMAIL FAILED: %s' % msg)
        logs.warning("Error: %s" % e)
    
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

def tryGetObjectId(string):
    """
        Attempts to parse the given string as a valid bson ObjectId (e.g., the 
        default underlying type for MongoDB _id's). Returns a valid ObjectId 
        instance or None if the given string could not be converted to a valid 
        ObjectId.
    """
    
    try:
        return bson.objectid.ObjectId(str(string))
    except Exception as e:
        return None

def generateUid():
    return str(bson.objectid.ObjectId())

def timestampFromUid(oid_str):
    return bson.objectid.ObjectId(oid_str).generation_time.replace(tzinfo=None)

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

def getFacebook(accessToken, path, params=None):
    if params is None:
        params = {}
    num_retries = 0
    max_retries = 5
    params['access_token'] = accessToken

    while True:
        try:
            baseurl = 'https://graph.facebook.com'
            encoded_params  = urllib.urlencode(params)
            url     = "%s%s?%s" % (baseurl, path, encoded_params)
            result  = json.load(urllib2.urlopen(url))
            
            if 'error' in result:
                if 'type' in result['error'] and result['error']['type'] == 'OAuthException':
                    # OAuth exception
                    raise
                raise
            
            return result
            
        except urllib2.HTTPError as e:
            logs.warning('Facebook API Error: %s' % e)
            num_retries += 1
            if num_retries > max_retries:
                if e.code == 400:
                    raise StampedInputError('Facebook API 400 Error')
                raise StampedUnavailableError('Facebook API Error')
                
            logs.info("Retrying (%s)" % (num_retries))
            time.sleep(0.5)

        except Exception as e:
            raise Exception('Error connecting to Facebook: %s' % e)

def getTwitter(url, key, secret, http_method="GET", post_body=None, http_headers=None):
    import libs.TwitterOAuth as TwitterOAuth
    
    TWITTER_CONSUMER_KEY    = 'kn1DLi7xqC6mb5PPwyXw'
    TWITTER_CONSUMER_SECRET = 'AdfyB0oMQqdImMYUif0jGdvJ8nUh6bR1ZKopbwiCmyU'
    
    consumer = TwitterOAuth.Consumer(key=TWITTER_CONSUMER_KEY, secret=TWITTER_CONSUMER_SECRET)
    token    = TwitterOAuth.Token(key=key, secret=secret)
    client   = TwitterOAuth.Client(consumer, token)
    
    resp, content = client.request(
        url,
        method=http_method,
        body=post_body,
        headers=http_headers,
        force_auth_header=True
    )
    
    return json.loads(content)

class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"

def getHeadRequest(url, maxDelay=2):
    """ 
        Robust HEAD request to ensure that the requested resource exists. Returns 
        the response object if the resource is accessible or None otherwise.
    """
    
    request  = HeadRequest(url)
    delay    = 0.5
    
    while True:
        try:
            return urllib2.urlopen(request)
        except urllib2.HTTPError, e:
            if e.code == 404:
                # Not found, return immediately
                return None
            elif e.code == 403:
                # Amazon returns 403s periodically -- worth another shot!
                pass
            elif e.code >= 400 and e.code < 500:
                # reraise the exception if the request resulted in any other 4xx error code, 
                # since it was a problem with the url / headers and retrying most likely won't 
                # solve the problem.
                logs.warning("Head request %s: (%s)" % (e.code, e))
                return None
        except (ValueError, IOError, httplib.BadStatusLine) as e:
            pass
        except Exception, e:
            logs.warning("Head request error: %s" % e)
            return None
        
        # if delay is already too large, request will likely not complete successfully, 
        # so propagate the error and return.
        if delay > maxDelay:
            return None
        
        # put the current thread to sleep for a bit, increase the delay, and retry the request
        time.sleep(delay)
        delay *= 2

def checkIfJpegResourceExists(url):
    return checkIfResourceExists(url, content_type='image/jpeg')

def get_input(msg="Continue %s? ", options=[('y', 'yes'), ('n', 'no'), ('a', 'abort'), ]):
    msg = msg % ("[%s]" % ", ".join(map(lambda o: "%s=%s" % (o[0], o[1]), options)))
    
    while True:
        answer = raw_input(msg).strip().lower()
        
        for option in options:
            if answer == option[0] or answer == option[1]:
                return option[0]
        
        print "invalid input"

def indentText(text, n):
    """ Takes a multi-line string of text and indents each line by n spaces. """

    lines    = text.split('\n')
    indent   = ' ' * n
    indented = [indent + line for line in lines]

    return '\n'.join(indented)

def basicNestedObjectToString(obj, wrapStrings=False):
    recurse = lambda o: basicNestedObjectToString(o, wrapStrings=wrapStrings)

    wrapperFn = str
    if wrapStrings:
        wrapperFn = json.dumps

    if isinstance(obj, unicode):
        return wrapperFn(obj.encode('utf-8'))
    
    if any(isinstance(obj, type_) for type_ in [basestring, int, float]):
        return wrapperFn(obj)
    
    if isinstance(obj, list):
        elementStrings = [indentText(recurse(element,), 2) + ',' for element in obj]
        return '[\n' + ('\n'.join(elementStrings)) + '\n]'
    
    if isinstance(obj, tuple):
        elementStrings = [indentText(recurse(element), 2) + ',' for element in obj]
        return '(\n' + ('\n'.join(elementStrings)) + '\n)'
    
    if isinstance(obj, dict):
        elementStrings = [indentText('%s : %s,' % (wrapperFn(key), recurse(value)), 2) for (key, value) in obj.items()]
        return '{\n' + ('\n'.join(elementStrings)) +'\n}'
    
    # TODO: should fallback to a simple str(obj)?
    raise Exception('Can\'t string-ify object of type: ' + type(obj))


def getImage(data):
    assert isinstance(data, basestring)
    
    io = StringIO(data)
    im = Image.open(io)
    
    return im

def getWebImage(url, desc=None):
    try:
        data = getFile(url)
    except urllib2.HTTPError:
        desc = ("%s " % desc if desc is not None else "")
        logs.warning("unable to download %simage from '%s'" % (url, desc))
        raise
    
    return getImage(data)

def getWebImageSize(url):
    try:
        data = getFile(url)
    except urllib2.HTTPError:
        logs.warning("Unable to download image: %s" % url)
        raise

    img = getImage(data)

    return img.size[0], img.size[1]


#Regexes for counting number of mentions and urls in a blurb or piece of text

mention_re = re.compile(r'(?<![a-zA-Z0-9_])@([a-zA-Z0-9+_]{1,20})(?![a-zA-Z0-9_])', re.IGNORECASE)
# URL regex taken from http://daringfireball.net/2010/07/improved_regex_for_matching_urls (via http://stackoverflow.com/questions/520031/whats-the-cleanest-way-to-extract-urls-from-a-string-using-python)
url_re          = re.compile(r"""((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.‌​][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))*))+(?:(([^\s()<>]+|(‌​([^\s()<>]+)))*)|[^\s`!()[]{};:'".,<>?«»“”‘’]))""", re.DOTALL)

def findMentions(text):
    mentionsIter = mention_re.finditer(text)
    mentions = []
    
    for mention in mentionsIter:
        mentions.append(mention)
    
    return mentions
    

def findUrls(text):
    urlsIter = url_re.finditer(text)
    urls = []
    
    for url in urlsIter:
        urls.append(url)
        
    return urls




