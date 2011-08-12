#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import gzip, httplib, json, logging, os, sys, pickle, threading, time, traceback, urllib2
from subprocess import Popen, PIPE
from functools import wraps
from BeautifulSoup import BeautifulSoup
from StringIO import StringIO
import htmlentitydefs

def shell(cmd, customEnv=None):
    pp = Popen(cmd, shell=True, stdout=PIPE, env=customEnv)
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

def log(s):
    print _formatLog(s)
    sys.stdout.flush()
    sys.stderr.flush()

def logRaw(s, includeFormat=False):
    if includeFormat:
        s = _formatLog(s)
    
    sys.stdout.write(s)
    sys.stdout.flush()
    sys.stderr.flush()

def _formatLog(s):
    try:
        return "[%s] %s" % (threading.currentThread().getName(), normalize2(s))
    except:
        return "[%s] __error__ printout" % (threading.currentThread().getName(), )

def write(filename, content):
    f = open(filename, "w")
    f.write(content)
    f.close()

def printException():
    """
        Simple debug utility to print a stack trace.
    """
    traceback.print_exc()

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

def getFile(url, opener=None):
    """
        Wrapper around urllib2.urlopen(url).read(), which attempts to increase 
        the success rate by sidestepping server-side issues and usage limits by
        retrying unsuccessful attempts with increasing delays between retries, 
        capped at a maximum possibly delay, after which the request will simply
        fail and propagate any exceptions normally.
    """
    
    maxDelay = 64
    delay = 0.5
    html = None
    request = None
    
    if opener is None:
        opener  = urllib2.urlopen
        request = urllib2.Request(url)
        request.add_header('Accept-encoding', 'gzip')
    
    if request is None:
        request = url
    
    while True:
        try:
            response = urllib2.urlopen(request)
            html = response.read()
            break
        except urllib2.HTTPError, e:
            #log("'%s' fetching url '%s'" % (str(e), url))
            
            # reraise the exception if the request resulted in an HTTP client 4xx error code, 
            # since it was a problem with the url / headers and retrying most likely won't 
            # solve the problem.
            if e.code >= 400 and e.code < 500:
                raise
            
            # if delay is already too large, request will likely not complete successfully, 
            # so propagate the error and return.
            if delay > maxDelay:
                raise
        except IOError, httplib.BadStatusLine:
            #log("Error '%s' fetching url '%s'" % (str(e), url))
            
            # if delay is already too large, request will likely not complete successfully, 
            # so propagate the error and return.
            if delay > maxDelay:
                raise
        except Exception, e:
            log("Unexpected Error '%s' fetching url '%s'" % (str(e), url))
            printException()
            raise
        
        # encountered error GETing document. delay for a bit and try again
        #log("Attempting to recover with delay of %d" % delay)
        
        # put the current thread to sleep for a bit, increase the delay, 
        # and retry the request
        time.sleep(delay)
        delay *= 2
    
    if response.info().get('Content-Encoding') == 'gzip':
        #html = zlib.decompress(html)
        buf = StringIO(html)
        f = gzip.GzipFile(fileobj=buf)
        html = f.read()
        buf.close()
    
    # return the successfully parsed html
    return html

def getSoup(url, opener=None):
    return BeautifulSoup(getFile(url, opener))

def createEnum(*sequential, **named):
    return dict(zip(sequential, range(len(sequential))), **named)

def count(container):
    try:
        return len(container)
    except:
        # count the number of elements in a generator expression
        return sum(1 for item in container)

def removeNonAscii(s):
    return "".join(ch for ch in s if ord(ch) < 128)

def normalize2(s):
    try:
        if isinstance(s, basestring):
            # replace html escape sequences with their unicode equivalents
            if '&' in s and ';' in s:
                for name in htmlentitydefs.name2codepoint:
                    escape_seq = '&%s;' % name
                    
                    while True:
                        l = s.find(escape_seq)
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
                
                val = unichr(int(s[l + 2 : m]))
                s = u"%s%s%s" % (s[:l], val, s[m + 1:])
        if isinstance(s, unicode):
            s = removeNonAscii(s.encode("utf-8"))
    except Exception as e:
        utils.printException()
        utils.log(e)
    
    return s

def normalize(s):
    try:
        if isinstance(s, basestring):
            # replace html escape sequences with their unicode equivalents
            if '&' in s and ';' in s:
                for name in htmlentitydefs.name2codepoint:
                    escape_seq = '&%s;' % name
                    
                    while True:
                        l = s.find(escape_seq)
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
                
                val = unichr(int(s[l + 2 : m]))
                s = u"%s%s%s" % (s[:l], val, s[m + 1:])
        elif isinstance(s, unicode):
            s = removeNonAscii(s.encode("utf-8"))
    except Exception as e:
        utils.printException()
        utils.log(e)
    
    return s

def numEntitiesToStr(numEntities):
    if numEntities == 1:
        return 'entity'
    else:
        return 'entities'

def getStatusStr(count, maxCount):
    return "%d%% (%d / %d)" % (round((100.0 * count) / max(1, maxCount)), count, maxCount)

def abstract(func):
    def wrapper(*__args, **__kwargs):
        raise NotImplementedError('Missing required %s() method' % func.__name__)
    
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__  = func.__doc__
    
    return wrapper

