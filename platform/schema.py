#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import copy
import pprint
import logs
import utils

class SchemaException(Exception):
    pass

class SchemaMeta(type):
    def __new__(cls, name, bases, attrs):
        flag = 'setSchema' in attrs
        result = type.__new__(cls, name, bases, attrs)
        result._preSetSchema()
        if flag:
            result.setSchema()
        result._postSetSchema()
        return result

_propertyKey            = 'property'
_propertyListKey        = 'property_list'
_nestedPropertyKey      = 'nested_property'
_nestedPropertyListKey  = 'nested_property_list'

_typeKey                = 'type'
_kindKey                = 'kind'
_castKey                = 'cast'

class Schema(object):
    __metaclass__ = SchemaMeta

    def __init__(self):
        self.__properties = {}
        self.__required_count = 0

    @classmethod
    def _preSetSchema(cls):
        cls._propertyInfo = {}
        for c in cls.__mro__:
            if hasattr(c, '_propertyInfo'):
                for k,v in c._propertyInfo.items():
                # TODO: do check for valid python identifier string
                    #r'^[_a-zA-Z][_a-zA-Z0-9]*$'
                    if k in cls._propertyInfo:
                        cur = cls._propertyInfo[k]
                        if cur != v:
                            raise SchemaException('duplicate property with different definition %s' % (k,))
                    cls._propertyInfo[k] = v
                    # print("added %s to %s", k, cls)

    @classmethod
    def _postSetSchema(cls):
        cls._required_fields   = set()

        properties = cls._propertyInfo
        for name, info in properties.items():
            kind = info[_kindKey]
            t = info[_typeKey]
            if info['required']:
                cls._required_fields.add(name)

    @classmethod
    def setSchema(cls):
        pass

    @classmethod
    def __addProperty(cls, t, name, kind, **kwargs):
        if not isinstance(name, basestring):
            raise SchemaException('property names must be basestrings, got %s' % (name,))
        if kind is None:
            raise SchemaException('kind must not be none for property %s' %(name,))
        if name in cls._propertyInfo:
            raise SchemaException('duplicate property %s' % (name,))
        if t == _nestedPropertyKey or t == _nestedPropertyListKey:
            if not issubclass(kind, Schema):
                raise SchemaException('nested properties must be Schemas not %s' % (kind,))
        kwargs[_kindKey] = kind
        kwargs[_typeKey] = t
        # Set default cast
        if 'cast' not in kwargs:
            if kind == bool:
                def __castBool(x):
                    if x is None:
                        return None 
                    if x in set([True, 'true', 'True', 1]):
                        return True 
                    if x in set([False, 'false', 'False', 0]):
                        return False
                    raise Exception("Cannot cast %s as bool" % x)
                kwargs['cast'] = __castBool
            elif kind == int:
                kwargs['cast'] = lambda x: int(x) if x is not None else None
            elif kind == float:
                kwargs['cast'] = lambda x: float(x) if x is not None else None
            elif kind == basestring:
                kwargs['cast'] = lambda x: unicode(x) if x is not None else None
        cls._propertyInfo[name] = kwargs

    def __getattr__(self, name):
        # Special case
        if name in set(['_Schema__required_count', '__class__', '_Schema__properties']):
            return object.__getattribute__(self, name)

        if self.__required_count < len(self.__class__._required_fields):
            logs.info('Object: %s' % pprint.pformat(self))
            logs.info('Required: %s' % self.__class__._required_fields)
            raise SchemaException('Invalid access, required properties not set')
        if name in self.__class__._propertyInfo:
            info = self.__class__._propertyInfo[name]
            if self.__required_count < len(self.__class__._required_fields):
                raise SchemaException('Invalid access, required properties not set')
            else:
                if name in self.__properties:
                    return self.__properties[name]
                else:
                    return None
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        # print(self.__class__._propertyInfo)
        if name in self.__class__._propertyInfo:
            info = self.__class__._propertyInfo[name]
            kind = info[_kindKey]

            # Apply cast.  If we have a propertyList or nestedPropList, apply to all items
            cast = info.get(_castKey, None)
            if cast is not None:
                t = info[_typeKey]
                if t in [_propertyKey, _nestedPropertyKey]:
                    value = cast(value)
                else:
                    value = tuple([ cast(v) for v in value])


            if value is None:
                if name in self.__class__._required_fields:
                    # Decrement __required_count if required
                    if name in self.__properties and self.__properties[name] is not None:
                        self.__required_count -= 1
                self.__properties[name] = None
            else:
                t = info[_typeKey]
                # Check if t is a scalar value or a list
                if t == _propertyKey or t == _nestedPropertyKey:
                    if isinstance(value, kind):
                        # Success!
                        if name in self.__class__._required_fields:
                            # Increment __required_count if required
                            if name not in self.__properties or self.__properties[name] is None:
                                self.__required_count += 1
                        self.__properties[name] = value
                    else:
                        raise SchemaException('Bad type for field "%s" and value %s, should be "%s"' % (name, value, kind))
                else:
                    valid = True
                    for item in value:
                        if not isinstance(item, kind):
                            raise SchemaException('Bad type for field "%s" and value %s, should be "%s"' % (name, value, kind))
                    if name in self.__class__._required_fields:
                        # Increment __required_count if required
                        if name not in self.__properties or self.__properties[name] is None:
                            self.__required_count += 1
                    self.__properties[name] = value
        else:
            if not name.startswith('_Schema__') and not name.startswith('__'):
                logs.warning('Setting non-schema field "%s"' % (name))
                raise AttributeError('SETTING NON-SCHEMA FIELD "%s"' % name)
            object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name in self.__class__._propertyInfo:
            if name in self.__properties:
                if name in self.__class__._required_fields:
                    # Decrement __required_count if required
                    if name in self.__properties and self.__properties[name] is not None:
                        self.__required_count -= 1
                del self.__properties[name]
        else:
            object.__delattr__(self, name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            for k, v in self.__properties.items():
                if k in other.__properties:
                    v2 = other.__properties[k]
                    if v2 != v:
                        return False
                else:
                    return False
                return True
        else:
            return False

    def __str__(self):
        return '[%s %s]' % (self.__class__, self.dataExport())

    def __unicode__(self):
        return u'[%s %s]' % (self.__class__, self.dataExport())

    def dataExport(self):
        properties = {}
        for k,v in self.__properties.items():
            info = self.__class__._propertyInfo[k]
            t = info[_typeKey]
            if t == _propertyKey:
                properties[k] = copy.deepcopy(v)
            elif t == _nestedPropertyKey:
                properties[k] = v.dataExport()
            elif t == _propertyListKey:
                if v is None:
                    properties[k] = None
                else:
                    properties[k] = tuple([ copy.deepcopy(v2) for v2 in v])
            else:
                if v is None:
                    properties[k] = None 
                else:
                    properties[k] = tuple([ v2.dataExport() for v2 in v])
        return properties

    def dataImport(self, properties, **kwargs):
        overflow = kwargs.pop('overflow', False)
        if isinstance(properties, Schema):
            raise Exception("Invalid data type: cannot import schema object")
        try:
            for k, v in properties.items():
                try:
                    if v is None:
                        self.__setattr__(k, None)
                        continue

                    p = self.__class__._propertyInfo[k]
                    if p[_typeKey] == _nestedPropertyKey:
                        if k in self.__properties:
                            nested = self.__properties[k]
                        else:
                            nested = p[_kindKey]()
                        nested.dataImport(v)
                        self.__setattr__(k, nested)

                    elif p[_typeKey] == _nestedPropertyListKey and v is not None:
                        l = tuple(v)
                        nestedKind = p[_kindKey]
                        nestedPropList = tuple([nestedKind().dataImport(item) for item in l])
                        self.__setattr__(k, nestedPropList)
                    else:
                        self.__setattr__(k, v)
                except (AttributeError, KeyError):
                    if not overflow:
                        logs.warning("AttributeError: %s (%s)" % (k, self.__class__.__name__))
                        raise
        except Exception as e:
            logs.warning(e)
            raise
        return self

    @classmethod
    def addProperty(cls, name, kind, required=False):
        cls.__addProperty(_propertyKey, name, kind, required=required)

    @classmethod
    def addPropertyList(cls, name, kind, required=False):
        cls.__addProperty(_propertyListKey, name, kind, required=required)

    @classmethod
    def addNestedProperty(cls, name, kind, required=False):
        cls.__addProperty(_nestedPropertyKey, name, kind, required=required)

    @classmethod
    def addNestedPropertyList(cls, name, kind, required=False):
        cls.__addProperty(_nestedPropertyListKey, name, kind, required=required)
