#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import datetime, os, pickle, sys, threading, traceback

from subprocess import Popen, PIPE
from functools  import wraps

def shell(cmd, customEnv=None):
    if customEnv:
        customEnv = dict(customEnv)
    
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
    if customEnv:
        customEnv = dict(customEnv)
    
    pp = Popen(cmd, shell=True, env=customEnv)
    status = pp.wait()
    
    return status

def scp(source, host, user, dest):
    cmd = 'scp -i keys/test-keypair -o StrictHostKeyChecking=no %s %s@%s:%s' % (source, user, host, dest)
    log(cmd)
    return Popen(cmd, shell=True).wait()

def runbg(host, user, cmd):
    assert not '"' in cmd
    ssh_cmd = 'ssh -i keys/test-keypair -f -o StrictHostKeyChecking=no %s@%s "%s"' % (user, host, cmd)
    log(ssh_cmd)
    return Popen(ssh_cmd, shell=True)

def lazy_property(undecorated):
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
    print _formatLog(s)

def logRaw(s, includeFormat=False):
    if includeFormat:
        s = _formatLog(s)
    
    sys.stdout.write(s)

def _formatLog(s):
    try:
        return "%s" % str(s)
    except Exception:
        return "__error__ printout"

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

def getPythonConfigFile(path, pickled=False):
    if os.path.exists(path):
        with open(path, "rb") as fp:
            source = fp.read()
        
        if pickled:
            return pickle.loads(source)
        else:
            return eval(source)
    else:
        return { }

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

def abstract(func):
    """ marks the target function as abstract """
    
    def wrapper(*__args, **__kwargs):
        raise NotImplementedError('Missing required %s() method' % func.__name__)
    
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__  = func.__doc__
    
    return wrapper

def get_input(msg="Continue %s? ", options=[('y', 'yes'), ('n', 'no'), ('a', 'abort'), ]):
    msg = msg % ("[%s]" % ", ".join(map(lambda o: "%s=%s" % (o[0], o[1]), options)))
    
    while True:
        answer = raw_input(msg).strip().lower()
        
        for option in options:
            if answer == option[0] or answer == option[1]:
                return option[0]
        
        print "invalid input"

def is_ec2():
    """ returns whether or not this python program is running on EC2 """
    
    return os.path.exists("/proc/xen") and os.path.exists("/etc/ec2_version")

def get_modified_time(filename):
    return datetime.datetime.fromtimestamp(os.path.getmtime(filename))

