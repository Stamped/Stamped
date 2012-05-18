#!/usr/bin/env python
"""
Base classes for structured, type/field checked data representation that parallels common built in Python types.

TODO, add pickling compatibility
TODO, evaluate use of single underscore attributes. -Landon
TODO, consider changing the parent attribute to a weakref, which would only require small and transparent modifications. -Landon
"""
__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import copy, logs, pprint, weakref

from datetime   import datetime
from utils      import normalize
from errors     import *


# adding generic validation for email, username, etc. on a per-element basis
# isSet consistency
# 
# user updates info; set existing value to empty
# empty strings
#
# exporting sparse version which ignores isSet and just returns if it's an actual, concrete value
# remove unused arguments and complexity from schema

# required set None value or not?
# derived values
# default values

class SchemaElement(object):
    
    """
The goal of the Schema class is to create a wrapper that allows for certain 
constraints to easily be applied to a structured set of data, ensuring that 
anything within the wrapper is valid and complete. Additionally, it is designed 
to allow for easy reformatting of data, with the hope of centralizing any 
transformations in order to minimize variations across structures. 

The class is built out of SchemaElement blocks. Each SchemaElement can be set 
to a specific value; it will then guarantee that the value meets any constrains 
placed on it.

These constraints include:

* Type          The type that the value can be. This currently includes 
                basestring, bool, int, long, float, and datetime. It does not 
                include dict or list unless set by a Schema or SchemaList, 
                respectively. Note that this constraint is mandatory and must
                be set.

* Required      Require that the value be set (i.e. is not None).

* Default       Set the default value. This also ensures that the value is 
                never None, i.e. the value is always set to default instead 
                of None. 

* Case          Set a specific case for the value. Accepted values are "upper", 
                "lower", and "mixed". If "lower", for example, the lowercase 
                value of the string will be stored. Note that this only applies 
                to basestring types only.

Additionally, a SchemaElement has the following attributes and functions:

* value         Returns the value of the element.

* isSet         Returns a boolean denoting if the value has been set or not.
                This is primarily used when you want to know if a None value 
                is overwriting a previous value or if it is still the default.

* validate      Check to see if any problems exist within the element. This 
                does not need to be called manually, and is called after a
                new value is set.

* setElement    Set the value of the element.

Note that a SchemaElement by iteslf cannot be directly compared to a normal
object with the same value. For example, if 'element' is a SchemaElement with
the value set to "abc", then:

    element != str("abc")

However, the element can easily be converted into its value:

    str(element) == str("abc")

    element.value == str("abc")

Additionally, if the element is contained within a Schema or SchemaList and is
derived that way, it will automatically return the value and not the 
SchemaElement:

    schema['element'] == str("abc")

Given that SchemaElements are only intended to be used within an additional 
wrapper (Schemas and SchemaLists), however, this should not be a common 
situation.

"""
    def __init__(self, requiredType, **kwargs):
        self._name          = None
        self._data          = None
        self._isSet         = False
        self._parent        = None
        self._requiredType  = self._setType(requiredType)
        self._required      = kwargs.pop('required', False)
        self._overflow      = kwargs.pop('overflow', False)
        self._default       = kwargs.pop('default', None)
        self._case          = self._setCase(kwargs.pop('case', None))
        self._normalize     = kwargs.pop('normalize', True)
        
        if self._default != None:
            self.setElement('[default]', self._default)
        
        self._setDerivative(kwargs.pop('derivedFrom', None), \
                            kwargs.pop('derivedFn', None))
    
    def __str__(self):
        return str(self.value)
    
    def __len__(self):
        if self._data == None:
            return 0
        return len(self._data)
    
    # Properties
    
    @property
    def value(self):
        return self._data
    
    @property
    def isSet(self):
        return self._isSet
    
    @property
    def name(self):
        return self._name
    
    # Private Functions

    def setIsSet(self, isSet):
        self._isSet = isSet
        # We should use weakref to avoid garbage collection, but not working in Python 2.6 :(
        if self._parent != None and isSet:
            self._parent.setIsSet(isSet)
    
    def _setType(self, requiredType):
        allowed = [basestring, bool, int, long, float, dict, list, datetime]
        if requiredType in allowed:
            return requiredType
        msg = "Invalid Type (%s)" % requiredType
        logs.warning(msg)
        raise SchemaTypeError(msg)

    def _setInt(self, number):
        if number == None:
            return None
        return int(number)

    def _setCase(self, case):
        if case in ['upper', 'lower', 'mixed']:
            return case
        return None

    def _clearElement(self):
        self._data = None
        self.setIsSet(False)

    def _setDerivative(self, derivedFrom, derivedFn):
        if derivedFrom != None or derivedFn != None:
            self._derivedFrom   = derivedFrom
            self._derivedFn     = derivedFn
        else:
            self._derivedFrom   = None
            self._derivedFn     = None

    # Public Functions

    def validate(self):
        if self.value == None and self._required == True:
            msg = "Required field empty (%s) parent type: %s" % (self._name, type(self._parent))
            logs.warning(msg)
            raise SchemaValidationError(msg)
        
        if self._data != None \
            and not isinstance(self._data, self._requiredType):
            msg = "Incorrect type (%s)" % self._name
            logs.warning(msg)
            raise SchemaKeyError(msg)
        
        return True
    
    def setElement(self, name, value):
        try:
            msg = "Set Element Failed (%s)" % name

            # Convert empty strings
            ### TODO: Do we want this functionality?
            # if value == '':
            #     value = None

            if value == None and self._default != None:
                value = self._default

            # Type checking
            if value != None and not isinstance(value, self._requiredType):

                if isinstance(value, dict):
                    msg = "Cannot set dictionary as value (%s)" % name
                    logs.warning(msg)
                    raise SchemaTypeError(msg)
                elif isinstance(value, list):
                    msg = "Cannot set list as value (%s)" % value
                    logs.warning(msg)
                    raise SchemaTypeError(msg)
                elif self._requiredType == bool:
                    b = str(value).lower()
                    if b == 'true' or b == '1':
                        value = True
                    elif b == 'false' or b == '0':
                        value = False
                elif self._requiredType == basestring:
                    value = str(value)
                elif self._requiredType == float:
                    value = float(value)
                elif self._requiredType == int:
                    value = int(value)

                if not isinstance(value, self._requiredType):
                    msg = "Incorrect type (%s)" % name
                    logs.warning(msg)
                    raise SchemaKeyError(msg)
            
            # Case
            if self._case:
                if self._case == 'upper':
                    value = str(value).upper()
                elif self._case == 'lower':
                    value = str(value).lower()
            
            if self._normalize:
                value = normalize(value)
            
            self._name  = name
            self._data  = value
            self.setIsSet(True)
            self.validate()
        except:
            logs.warning(msg)
            raise

class SchemaList(SchemaElement):

    """
A SchemaList is a special type of SchemaElement that contains multiple 
SchemaElements of the same type. It is, not surprisingly, designed to mimic
a standard Python list in functionality. Like a normal list, it can hold any
number of values; however, unlike a normal list, it cannot hold different 
types of elements (e.g. it cannot have both a basestring and a float). 

A SchemaList has all of the typical Python list functions:

* append
* insert
* extend
* remove
* pop
* index
* count
* sort
* reverse

It also includes:

* value         Returns the value of the element. This includes the values of
                any child elements, e.g. all inner SchemaElements are returned
                with the value.

* isSet         Inherited from SchemaElement.

* validate      Check to see if any problems exist within the list. This is
                called automatically whenever the list is modified. 

* setElement    Inherited from SchemaElement. Sets the SchemaList to a given
                list.

* importData    Bulk import data. This can also be called during instantiation,
                e.g. a = SchemaList(data). Unlike setElement, this appends the
                data onto the list and does not overwrite any existing data.

Finally, a SchemaList can take an additional parameter for parsing data during
import. This is the "delimiter", and allows you to pass a formatted string and
have the SchemaList automatically parse the variable into the list elements.

Note that a SchemaList by itself cannot be directly compared to a normal list.
Instead, the contents of the SchemaList should be compared to the contents of
the normal list. This can most easily be accomplished by comparing the value 
of the SchemaList to the list:

    schemaList != [1, 2, 3]

    schemaList.value == [1, 2, 3]

"""
    def __init__(self, element, **kwargs):
        SchemaElement.__init__(self, list, **kwargs)
        self._element       = element
        self._data          = []
        self._delimiter     = kwargs.pop('delimiter', None)

    def __len__(self):
        return len(self._data)
    
    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, item):
        self._data[key] = self._import(item)
        self.validate()
    
    def __delitem__(self, key):
        del(self._data[key])
        self.validate()

    # Properties

    @property
    def value(self):
        ret = []
        for item in self._data:
            ret.append(item.value)
        return ret

    # Private Functions

    def _import(self, item):
        element = self._element
        if isinstance(item, SchemaElement):
            return item

        elif isinstance(element, Schema) or isinstance(element, SchemaList):
            newSchemaItem = copy.deepcopy(element)
            newSchemaItem._overflow = self._overflow
            newSchemaItem.importData(item)
            return newSchemaItem

        elif isinstance(element, SchemaElement):
            newSchemaElement = copy.deepcopy(element)
            newSchemaElement.setElement('e', item)
            return newSchemaElement

        else:
            msg = "Invalid List Element (%s)" % element
            logs.warning(msg)
            raise SchemaTypeError(msg)

    # List Functions

    def append(self, item):
        self._data.append(self._import(item))
        self.setIsSet(True)

    def insert(self, position, item):
        self._data.insert(position, self._import(item))
        self.setIsSet(True)

    def extend(self, items):
        data = []
        for item in items:
            data.append(self._import(item))
        self._data.extend(data)
        self.setIsSet(True)

    def remove(self, item):
        return self._data.remove(self._import(item))
    
    def pop(self, i=-1):
        return self._data.pop(i).value

    def index(self, item):
        if isinstance(item, SchemaElement):
            item = item.value
        return self.value.index(item)

    def count(self, item):
        if isinstance(item, SchemaElement):
            item = item.value
        return self.value.count(item)

    def sort(self):
        self._data.sort()
    
    def reverse(self):
        self._data.reverse()

    # Public Functions

    def importData(self, data):
        # Make sure there's something to import
        if data == None or len(data) == 0:
            return

        # Use delimiter if set and if data not already a list
        if self._delimiter != None and isinstance(data, basestring):
            try:
                data = data.split(self._delimiter)
            except:
                msg = "Invalid Delimiter for Data (%s)" % data
                logs.warning(msg)
                raise SchemaValidationError(msg)

        # Ensure that data is a valid list
        if not isinstance(data, list):
            msg = "Incorrect List Input (%s)" % data
            logs.warning(msg)
            raise SchemaTypeError(msg)

        data = copy.copy(data)

        # Ensure that element is set properly
        if not isinstance(self._element, SchemaElement):
            msg = "Invalid List Element (%s)" % self._element
            logs.warning(msg)
            raise SchemaTypeError(msg)
        element = self._element

        # Append data
        for item in data:
            self.append(item)

        self.setIsSet(True)

    def validate(self):
        if len(self._data) == 0 and self._required == True:
            msg = "Required List Empty (%s)" % self._name
            logs.warning(msg)
            raise SchemaValidationError(msg)

        for item in self._data:
            if not isinstance(item, SchemaElement):
                msg = "Invalid List Element (%s)" % self._element
                logs.warning(msg)
                raise SchemaTypeError(msg)
            item.validate()

    def setElement(self, name, value):
        self._data = []
        self._name = name
        self.importData(value)

class Schema(SchemaElement):

    """
A Schema is a second variety of the SchemaElement class that contains multiple 
SchemaElements in a dictionary-style format. Similar to how a SchemaList mimics
a Python list, a Schema mimics a generic Python dictionary. 

By definition, a Schema will have a SchemaElement set as the value of every
sub-key. Although chaining can occur (e.g. a Schema within a Schema), the sub-
value must be a SchemaElement. (It can also be a SchemaList, but there too, the
value of every item in the SchemaList must be a SchemaElement). 

To query a Schema, classic dictionary notation can be used:

    schema['item'] == 1

    schema['items']['item'] == 'abc'

Dot notation can also be used:

    schema.item == 1

    schema.items.item == 'abc'

If a raw SchemaElement is returned, it will always be returned as the value 
(instead of the object). Conversely, if a Schema or a SchemaList is returned,
it will be the object and not the value. To obtain the value you can access 
the value property:

    schema != {'a': 1}

    schema.value == {'a': 1}

The following attributes and functions are available to a Schema:

* value         Returns the value of the element. This includes the values of
                any child elements, e.g. all inner Schemas and SchemaElements
                are returned as their values.

* validate      Check to see if any problems exist within the list. This is
                called automatically whenever the Schema is modified.

* setElement    Set the Schema to use a specific set of data.

* importData    Bulk import data. This can also be called during instantiation,
                e.g. a = Schema(data). Note that this attempts to _merge_ the
                data and not completely replace it; if an element is set within
                the Schema that is not overwritten by the new data, it will 
                remain. To overwrite all existing data, use setElement().

* exportFields  Export an explicitly defined list of fields. This allows for
                the user to specify certain fields that they want to use in
                order to construct a new Schema or a specific dictionary.

* exportSparse  Export only fields that have been set (i.e. where isSet==True). 
                This allows for the user to export only data that has been
                incrementally changed. It is primarily useful for updates.

* setSchema     This function must be implemented and called on any sub-classes
                of the Schema. This is used to define the elements of the
                Schema.

* getDataAsDict Deprecated - use value instead.

Finally, when importing new data into a Schema, you can pass it the parameter
"overflow=True". This will override the default behavior for unrecognized
fields in data import, and will discard them instead of failing. This is useful
when not all fields are expected to match, but should not be used as a first
resort.

"""
    
    def __init__(self, data=None, **kwargs):
        SchemaElement.__init__(self, dict, **kwargs)
        self._elements = {}
        
        if data is None and kwargs is not None:
            kwargs.pop('required', False)
            kwargs.pop('overflow', False)
            kwargs.pop('default', None)
            kwargs.pop('case', None)
            kwargs.pop('normalize', True)
            kwargs.pop('derivedFrom', None)
            kwargs.pop('derivedFn', None)
            
            if len(kwargs) > 0:
                data = kwargs
        
        self.setSchema()
        self.importData(data)
    
    def __setattr__(self, name, value):
        # Will work for mangled private variables too
        if name[:1] == '_':
            object.__setattr__(self, name, value)
        
        elif isinstance(value, SchemaElement):
            try:
                self._elements[name] = value
                self._elements[name]._name = name
                self._elements[name]._parent = self
            except:
                msg = "Cannot Add Element (%s)" % name
                logs.warning(msg)
                raise SchemaKeyError(msg)
        
        else:
            if name in self._elements:
                self._elements[name].setElement(name, value)
            else:
                try:
                    if len(self._contents(name)) == 1:
                        for k, v in self._elements.iteritems():
                            if isinstance(v, Schema) and 1 == len(v._contents(name)):
                                v[name] = value
                                v.setIsSet(True)
                        
                        return
                except:
                    pass
                
                msg = "Cannot Set Element (%s)" % name
                #logs.warning(msg)
                raise SchemaKeyError(msg)
    
    def __setitem__(self, key, value):
        self.__setattr__(key, value)
    
    def __delattr__(self, key):
        self.__setattr__(key, None)
    
    def __delitem__(self, key):
        self.__setattr__(key, None)
    
    def __getattr__(self, name):
        if name[:1] == '_':
            return SchemaElement.__getattr__(self, name)
        
        def _returnOutput(item):
            if isinstance(item, Schema) or isinstance(item, SchemaList):
                item._parent = self
                return item
            return item.value
        
        if name in self._elements:
            return _returnOutput(self._elements[name])
        
        try:
            result = self._contents(name)
            if len(result) != 1:
                raise
            return _returnOutput(result[0])
        except:
            msg = "Cannot Get Element (%s)" % name
            logs.warning(msg)
            raise SchemaKeyError(msg)

    def __getitem__(self, key):
        return self.__getattr__(key)
    
    def __len__(self):
        return len(self._elements)
    
    def __iter__(self):
        return self.value.__iter__()
    
    def __contains__(self, item):
        ret = self._contents(item)
        
        if len(ret) == 1:
            return ret[0]._isSet
        elif len(ret) == 0:
            return False
        else:
            msg = "Multiple Keys Exist (%s)" % item
            logs.warning(msg)
            raise SchemaKeyError(msg)
    
    # Properties
    
    @property
    def value(self):
        ret = {}
        for k, v in self._elements.iteritems():
            if v.isSet:
                ret[k] = v.value
        
        return ret

    # Private Functions

    def _importData(self, data, **kwargs):
        # Wipe all contents if not set in data
        clear = kwargs.pop('clear', True)
        
        if isinstance(data, Schema):
            data = data.value
        
        if not isinstance(data, dict) and data != None:
            msg = "Invalid Type (data=%s) (type=%s)" % (data, type(data))
            logs.warning(msg)
            logs.warning("Schema: %s" % self)
            raise SchemaTypeError(msg)
        
        ret = {}
        data = copy.copy(data)
        derivatives = []
        
        for k, v in self._elements.iteritems():
            item  = None
            isSet = False
            
            if data != None and k in data:
                item  = data.pop(k)
                isSet = True
            
            # Dictionary or List
            if isinstance(v, Schema) or isinstance(v, SchemaList):
                v._overflow = self._overflow

                if item == None:
                    if v._required == True:
                        path = None
                        try:
                            path = self.name
                            parent = self._parent
                            while parent is not None:
                                path = '%s > %s' % (parent.name, path)
                                parent = parent._parent
                        except:
                            pass
                        msg = "Missing Nested Element (%s, %s)" % (path, k)
                        logs.warning(msg)
                        raise SchemaValidationError(msg)
                
                if clear:
                    if item is not None:
                        v.setElement(k, item)
                    elif isinstance(v, SchemaList):
                        v._data = []
                    else:
                        v.setSchema()
                else:
                    v.importData(item)
            
            # Value
            elif isinstance(v, SchemaElement):
                if isSet:
                    v.setElement(k, item)
                elif v._derivedFrom != None:
                    # Wait until everything else has been set
                    derivatives.append(v)
                elif clear:
                    v._clearElement()
                else:
                    v.validate()
            
            else:
                msg = "Unrecognized Element (%s)" % k
                logs.warning(msg)
                raise SchemaTypeError(msg)
        
        # Attempt to set any derivative values
        for element in derivatives:
            try:
                inputValue = self._elements[element._derivedFrom].value
                element.setElement(element._name, \
                                    element._derivedFn(inputValue))
            except:
                msg = "Unable to derive (%s)" % element._name
                logs.warning(msg)
                raise SchemaValidationError(msg)
        
        # Fail if excess data exists
        if data != None and len(data) > 0 and self._overflow == False:
            msg = "Unknown Field: %s" % data
            logs.warning(msg)
            raise SchemaValidationError(msg)
        
        self.setIsSet(True)
    
    def _contents(self, item):
        output = []
        if item in self._elements:
            output.append(self._elements[item])
        
        for k, v in self._elements.iteritems():
            if isinstance(v, Schema):
                output.extend(v._contents(item))
        
        return output
    
    # Public Functions
    
    def validate(self):
        if len(self._elements) == 0 and self._required == True:
            msg = "Required Schema Empty (%s)" % self._name
            logs.warning(msg)
            raise SchemaValidationError(msg)
        
        for k, v in self._elements.iteritems():
            if v.isSet:
                v.validate()
    
    def setElement(self, name, data):
        self._name = name
        self._importData(data, clear=True)
        self.setIsSet(True)
    
    def importData(self, data, overflow=None):
        """
        when overflow is true, we ignore any extra attributes not defined in the target
        """
        if data == None: # or len(data) == 0:
            return
        
        if overflow == None:
            overflow = self._overflow
        
        # Preserve state of self._overflow
        _overflow = self._overflow
        try:
            self._overflow = overflow
            self._importData(data, clear=False)
            self._overflow = _overflow
        except:
            self._overflow = _overflow
            raise
    
    def removeElement(self, name):
        del(self._elements[name])
    
    def exportSparse(self):
        ret = {}
        for k, v in self._elements.iteritems():
            if isinstance(v, Schema):
                data = v.exportSparse()
                if len(data) > 0:
                    ret[k] = data
            elif isinstance(v, SchemaList):
                if len(v) > 0:
                    ret[k] = v.value
            elif isinstance(v, SchemaElement):
                # if v.isSet == True:
                if v.value != None:
                    ret[k] = v.value
            else:
                msg = "Unrecognized Element (%s)" % k
                logs.warning(msg)
                raise SchemaTypeError(msg)
        return ret
    
    def setSchema(self):
        raise NotImplementedError
    
    def importSchema(self, schema):
        try:
            self.importData(schema.value, overflow=True)
            return self
        except:
            msg = "Conversion failed (Define in subclass?)"
            logs.warning(msg)
            raise SchemaValidationError(msg)
    
    def exportSchema(self, schema):
        try:
            schema.importData(self.value, overflow=True)
            return schema
        except:
            msg = "Conversion failed (Define in subclass?)"
            logs.warning(msg)
            raise SchemaValidationError(msg)
    
    # DEPRECATED
    
    def getDataAsDict(self):
        return self.value
    
    def __str__(self):
        return pprint.pformat(self.value)

