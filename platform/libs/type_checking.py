#!/usr/bin/env python

"""
Type-checking decorators that attempt to make Python a reasonable language.
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'arg', 'varargs', 'kwarg', 'varkwargs', 'returns',
            'Fn', 'Any', 'Number', 'IterableOf', 'ListOf', 'SetOf', 'DictOf', 'AnyOf' ]

import Globals
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import namedtuple
import functools
import numbers
import types

class TypeMatcher(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def matches_instance(self, instance):
        pass

    @abstractproperty
    def description(self):
        pass


class SimpleTypeMatcher(TypeMatcher):
    def __init__(self, class_object):
        super(SimpleTypeMatcher, self).__init__()
        self.__class_object = class_object

    def matches_instance(self, instance):
        return isinstance(instance, self.__class_object)

    @property
    def description(self):
        return 'isinstance(%s)' % self.__class_object


NoneMatcher = SimpleTypeMatcher(types.NoneType)
Fn = SimpleTypeMatcher(types.FunctionType)
Any = SimpleTypeMatcher(object)
Number = SimpleTypeMatcher(numbers.Number)


def get_type_matcher(type_matcher_arg):
    if type_matcher_arg is None:
        return NoneMatcher
    if isinstance(type_matcher_arg, type):
        type_matcher_arg = SimpleTypeMatcher(type_matcher_arg)
    return type_matcher_arg


class IterableOfTypeMatcher(TypeMatcher):
    def __init__(self, element_matcher, iterable_type=None):
        super(IterableOfTypeMatcher, self).__init__()
        self.__element_matcher = get_type_matcher(element_matcher)
        self.__iterable_type = iterable_type

    def matches_instance(self, instance):
        if self.__iterable_type is not None and not isinstance(instance, self.__iterable_type):
            return False
        try:
            return all(self.__element_matcher.matches_instance(item) for item in instance)
        except TypeError:
            return False

    @property
    def description(self):
        if self.__iterable_type is not None:
            return 'isinstance(%s) containing instances matching (%s)' % (
                self.__iterable_type, self.__element_matcher.description
            )
        else:
            return 'is container of instances matching (%s)' % self.__element_matcher.description


IterableOf = IterableOfTypeMatcher
ListOf = lambda x : IterableOfTypeMatcher(x, list)
SetOf = lambda x : IterableOfTypeMatcher(x, set)
# Not bothering with tuples because contents are more commonly heterogeneous.


class DictTypeMatcher(TypeMatcher):
    def __init__(self, key_type, val_type):
        super(DictTypeMatcher, self).__init__()
        self.__key_type_matcher = get_type_matcher(key_type)
        self.__val_type_matcher = get_type_matcher(val_type)

    def matches_instance(self, instance):
        return (isinstance(instance, dict) and
                all(self.__key_type_matcher.matches_instance(key) for key in instance.keys()) and
                all(self.__val_type_matcher.matches_instance(val) for val in instance.values()))

    @property
    def description(self):
        return 'is dict where each key matches (%s) and each value matches (%s)' % (
            self.__key_type_matcher.description,
            self.__val_type_matcher.description
        )

DictOf = lambda key, val : DictTypeMatcher(key, val)


class ManyTypesMatcher(TypeMatcher):
    def __init__(self, *matchers):
        super(ManyTypesMatcher, self).__init__()
        self.__matchers = matchers

    def matches_instance(self, instance):
        return any(matcher.matches_instance(instance) for matcher in self.__matchers)

    @property
    def description(self):
        return 'any of: [%s]' % ', '.join('<%s>' % matcher.description for matcher in self.__matchers)


def AnyOf(*matchers):
    return ManyTypesMatcher(*[get_type_matcher(m) for m in matchers])


ArgMatcher = namedtuple('ArgMatcher', ['name', 'required', 'type_matcher'])


class ArgsMatchingFunction(object):
    """
    Wrapper around a function that adds argument type-checking.
    TODO: Also extend the python docstring with the arg type information. If we do this we will also want to encapsulate
          return information in this.
    TODO: Consider checking user input against function.func_code details.
    """

    # A set of enums clarifying the order in which we expect to see the decorators.
    TOKEN_ARG = 1
    TOKEN_KWARG = 2
    TOKEN_VARARGS = 3
    TOKEN_VARKWARGS = 4
    TOKEN_END = 5

    def __init__(self, function):
        self.__function = function
        self.__arg_matchers = []
        # Does this function take a generic *args array?
        self.__varargs = False
        # Does this function take a generic **kwargs dict?
        self.__varkwargs = False

        self.__matchers_by_name = {}
        # When the decorators are typed in order, they are executed from last to first, so we expect to handle the
        # arguments backwards.
        self.__last_token_seen = self.TOKEN_END


    def __call__(self, *args, **kwargs):
        self.check_matches_call(args, kwargs)
        return self.__function(*args, **kwargs)

    @property
    def func_name(self):
        return self.__function.func_name

    def add_matcher(self, matcher):
        self.__arg_matchers.insert(0, matcher)
        curr_token = self.TOKEN_ARG if matcher.required else self.TOKEN_KWARG
        if curr_token > self.__last_token_seen:
            raise Exception('Incorrect ordering of type checking decorators for function %s' % self.func_name)
        self.__last_token_seen = curr_token

        if matcher.name in self.__matchers_by_name:
            raise Exception('Naming conflict in arguments to function %s' % self.func_name)
        self.__matchers_by_name[matcher.name] = matcher

    def add_varargs(self, type_matcher=Any):
        curr_token = self.TOKEN_VARARGS
        if curr_token >= self.__last_token_seen:
            raise Exception('Incorrect ordering of type checking decorators for function %s' % self.func_name)
        self.__last_token_seen = curr_token
        self.__varargs = True
        self.__varargs_matcher = type_matcher

    def add_varkwargs(self, type_matcher=Any):
        curr_token = self.TOKEN_VARKWARGS
        if curr_token >= self.__last_token_seen:
            raise Exception('Incorrect ordering of type checking decorators for function %s' % self.func_name)
        self.__last_token_seen = curr_token
        self.__varkwargs = True
        self.__varkwargs_matcher = type_matcher

    def check_matches_call(self, args, kwargs):
        matchers_to_args = {}
        varargs = []
        varkwargs = {}
        for (position, arg) in enumerate(args):
            if len(self.__arg_matchers) <= position:
                if self.__varargs:
                    # We're at the end of our arg matchers, and there's a varargs parameter consuming the extra.
                    varargs.append(arg)
                else:
                    raise TypeError('Too many positional arguments passed to call to %s' % self.func_name)
            else:
                matchers_to_args[self.__arg_matchers[position]] = arg

        for (name, arg) in kwargs.items():
            if name not in self.__matchers_by_name:
                if self.__varkwargs:
                    varkwargs[name] = arg
                else:
                    raise TypeError('Unexpected keyword arg %s=%s passed to %s()' % (
                        name, arg, self.func_name
                    ))
            else:
                matcher = self.__matchers_by_name[name]
                if matcher in matchers_to_args:
                    raise TypeError('%s() got multiple values for keyword argument %s' % (
                        self.func_name, name
                    ))
                matchers_to_args[matcher] = arg

        for (matcher, arg) in matchers_to_args.items():
            # Accept None everywhere.
            if arg is not None and not matcher.type_matcher.matches_instance(arg):
                raise TypeError('In call to %s(), argument %s=%s fails to meet expectation: %s' % (
                    self.func_name, matcher.name, arg, matcher.type_matcher.description
                ))

        for vararg in varargs:
            if not self.__varargs_matcher.matches_instance(vararg):
                raise TypeError('In call to %s(), vararg (%s) does not meet expectation: %s' % (
                    self.func_name, vararg, self.__varargs_matcher.description
                ))

        for (kwarg_key, kwarg_val) in varkwargs.items():
            if not self.__varkwargs_matcher.matches_instance(kwarg_val):
                raise TypeError('In call to %s(), varkwarg (%s=%s) does not meet expectation: %s' % (
                    self.func_name, kwarg_key, kwarg_val, self.__varkwargs_matcher.description
                ))

        # The interpreter will catch this if the decorators are in sync with the function definition, but we do it here
        # just in case they're not.
        for matcher in self.__arg_matchers:
            if matcher.required and matcher not in matchers_to_args:
                raise TypeError('In call to %s(), required arg %s is not supplied!' % (
                    self.func_name, matcher.name
                ))


disable_type_checking = False

def get_args_matching_function(func):
    if isinstance(func, types.FunctionType):
        func = ArgsMatchingFunction(func)
    return func

def arg(name, type_matcher, description=''):
    type_matcher = get_type_matcher(type_matcher)

    def decorator(func):
        if disable_type_checking:
            return func

        func = get_args_matching_function(func)
        func.add_matcher(ArgMatcher(name, True, type_matcher))

        return func
    return decorator

def varargs(type_matcher=Any, description=None):
    type_matcher = get_type_matcher(type_matcher)

    def decorator(func):
        if disable_type_checking:
            return func

        func = get_args_matching_function(func)
        func.add_varargs(type_matcher)
        return func
    return decorator

def kwarg(name, type_matcher, description=''):
    type_matcher = get_type_matcher(type_matcher)

    def decorator(func):
        if disable_type_checking:
            return func

        func = get_args_matching_function(func)
        func.add_matcher(ArgMatcher(name, False, type_matcher))

        return func
    return decorator

def varkwargs(type_matcher=Any, description=None):
    type_matcher = get_type_matcher(type_matcher)

    def decorator(func):
        if disable_type_checking:
            return func

        func = get_args_matching_function(func)
        func.add_varkwargs(type_matcher)
        return func
    return decorator

def returns(type_matcher, description=''):
    type_matcher = get_type_matcher(type_matcher)

    def decorator(func):
        if disable_type_checking:
            return func

        @functools.wraps(func)
        def decorated(*args, **kwargs):
            result = func(*args, **kwargs)
            if not type_matcher.matches_instance(result):
                raise TypeError('Result of function %s is < %s >; does not match rule: %s' % (
                    func.func_name, result, type_matcher.description
                ))
            return result
        return decorated
    return decorator



if __name__ == '__main__':
    def print_exception(fn, *args, **kwargs):
        try:
            fn(*args, **kwargs)
        except Exception as e:
            print e

    @arg('s', basestring, 'string to repeat')
    @arg('n', int, 'num times to repeat string s')
    @kwarg('sep', basestring, 'separator')
    @returns(basestring)
    def repeat_string_n_times(s, n, sep=''):
        return sep.join([s] * n)

    print repeat_string_n_times('a', 2)
    print repeat_string_n_times('b', 3, ' ')
    print repeat_string_n_times(sep='-', s='c', n=4)
    print_exception(repeat_string_n_times, 'abc', 1.5)
    print_exception(repeat_string_n_times)
    print_exception(repeat_string_n_times, 1.5, 'abc')

    @arg('counts', DictOf(basestring, int), 'counts of words thus far, to be updated')
    @arg('text', AnyOf(basestring, ListOf(basestring)), 'text to count words in')
    @kwarg('is_stop_word', Fn, 'indicates which words we should not bother counting')
    @returns(DictOf(basestring, int))
    def count_additional_words(counts, text, is_stop_word=lambda x:False):
        if isinstance(text, basestring):
            text = text.split()
        for word in text:
            if not is_stop_word(word):
                counts[word] = counts.get(word, 0) + 1
        return counts

    print count_additional_words({}, 'hello world')
    print count_additional_words(text='hello to the world', is_stop_word=lambda x: x in ['the', 'to'], counts={'a':2})
    print_exception(count_additional_words, {1:2}, 'hello world')
    print_exception(count_additional_words, {'a':'b'}, 'hello world')

    @kwarg('remove_dupes', bool, 'if true, dupes are not included in the result')
    @varargs(list, 'lists to be concatenated')
    @returns(list)
    def concatenate_lists(remove_dupes=False, *lists):
        result = []
        for list in lists:
            if not remove_dupes:
                result += list
            else:
                for el in list:
                    if el not in result:
                        result.append(el)
        return result

    print concatenate_lists(False, ['a'], ['b', 'c'])
    print concatenate_lists()

    @kwarg('strict', bool, 'If false, we also allow any value to be missing')
    @varargs(DictOf(basestring, Any))
    @varkwargs()
    @returns(bool)
    def check_dict_values(strict=False, *dicts, **required_values):
        for dct in dicts:
            for (key, val) in required_values.items():
                if key not in dct and strict:
                    return False
                if key in dct and val != dct[key]:
                    return False
        return True

    check_dict_values(False, {}, {'a':1}, {'b':2}, a=1, b=2)
    check_dict_values(True, {}, {'a':None}, {'23':object()}, a=1, b=2)

    @varkwargs(int)
    def weird_fn(**kwargs):
        result = ''
        for (name, val) in kwargs.items():
            result += name * val
        return result

    print weird_fn(a=1, b=2, c=3)
    print_exception(weird_fn, a=1, b=2, c=3.4)