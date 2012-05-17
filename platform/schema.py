#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import copy

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
                    if k in cls._propertyInfo:
                        cur = cls._propertyInfo[k]
                        if cur != v:
                            raise SchemaException('duplicate property with different definition %s' % (k,))
                    cls._propertyInfo[k] = v
                    # print("added %s to %s", k, cls)

    @classmethod
    def _postSetSchema(cls):
        cls._shortcuts         = {}
        cls._duplicates        = set()
        cls._required_fields   = set()

        properties = cls._propertyInfo
        for name, info in properties.items():
            kind = info[_kindKey]
            t = info[_typeKey]
            # set up for shortcuts for nested properties
            if t == _nestedPropertyKey and issubclass(kind, Schema):
                shortcuts = cls._shortcuts
                for shortcut, path in shortcuts:
                    # only consider shortcuts that don't conflict with local properties
                    if shortcut not in properties:
                        # ensure duplicates are added to duplicate set
                        if shortcut in cls.__shortcuts:
                            cls._duplicates.add(shortcut)
                        else:
                            # create shortcut path prefixed with property name
                            path = [name]
                            path.extend(shortcut)
                            cls._shortcuts[shortcut] = path
            if info['required']:
                cls._required_fields.add(name)
        for dup in cls._duplicates:
            del cls._duplicates[dup]

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
                    if x in set([True, 'true', 'True', 1]):
                        return True 
                    if x in set([False, 'false', 'False', 0]):
                        return False
                    raise Exception("Cannot cast %s as bool" % x)
                kwargs['cast'] = __castBool
            elif kind == int:
                kwargs['cast'] = lambda x: int(x)
            elif kind == float:
                kwargs['cast'] = lambda x: float(x)
            elif kind == basestring:
                kwargs['cast'] = lambda x: unicode(x)
        cls._propertyInfo[name] = kwargs

    def __shortcutHelper(self, name, create=False):
        path = self.__class__._shortcuts[name]
        cur = self
        for key in path[:-1]:
            next = cur.__getattr__(key)
            if next is None:
                if create:
                    info = self.__class__._propertyInfo[key]
                    kind = info[_kindKey]
                    next = kind()
                    cur.__setattr__(key, next)
                else:
                    return None
            cur = next
        return cur, path[-1]

    def __getattr__(self, name):
        if self.__required_count < len(self.__class__._required_fields):
            print 'Object: %s' % self
            print 'Required: %s' % self.__class__._required_fields
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
        elif name in self.__class__._duplicates:
            raise SchemaException('Duplicate shortcut used')
        elif name in self.__class__._shortcuts:
            last, lastKey = self.__shortcutHelper(name, create=False)
            if last is not None:
                return last.__getattr__(lastKey)
            else:
                return None
        else:
            object.__getattribute__(self, name)

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
        elif name in self.__class__._duplicates:
            raise SchemaException('Duplicate shortcut used')
        elif name in self.__class__._shortcuts:
            last, lastKey = self.__shortcutHelper(name, create=True)
            last.__setattr__(lastKey, value)
        else:
            object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name in self.__class__._propertyInfo:
            if name in self.__properties:
                if name in self.__class__._required_fields:
                    # Decrement __required_count if required
                    if name in self.__properties and self.__properties[name] is not None:
                        self.__required_count -= 1
                del self.__properties[name]
        elif name in self.__class__._duplicates:
            raise SchemaException('Duplicate shortcut used')
        elif name in self.__class__._shortcuts:
            last, lastKey = self.__shortcutHelper(name, create=False)
            if last is not None:
                last.__delattr__(lastKey)
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

    # def __contains__(self, item):
    #     for k, v in self.__properties.items():
    #         if item == k:
    #             return True 

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
                properties[k] = tuple([ copy.deepcopy(v2) for v2 in v])
            else:
                properties[k] = tuple([ v2.dataExport() for v2 in v])
        return properties

    def dataImport(self, properties, **kwargs):
        if isinstance(properties, Schema):
            raise Exception("Invalid data type: cannot import schema object")
        try:
            for k, v in properties.items():
                try:
                    p = self.__class__._propertyInfo[k]
                    if p[_typeKey] == _nestedPropertyKey:
                        if k in self.__properties:
                            nested = self.__properties[k]
                        else:
                            nested = p[_kindKey]()
                        nested.dataImport(v)
                        self.__setattr__(k, nested)

                    elif p[_typeKey] == _nestedPropertyListKey:
                        l = tuple(v)
                        nestedKind = p[_kindKey]
                        nestedPropList = tuple([nestedKind().dataImport(item) for item in l])
                        self.__setattr__(k, nestedPropList)
                    else:
                        self.__setattr__(k, v)
                except KeyError:
                    if kwargs.pop('overflow', False):
                        continue
        except Exception as e:
            print(e)
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
