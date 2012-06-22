#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import logs

class Fail(Exception):
    pass

class StampedHTTPError(Exception):
    def __init__(self, code, kind=None, msg=None):
        Exception.__init__(self, msg)
        self.code = code
        self.msg  = msg
        self.kind = kind
        
        if msg is not None:
            logs.warning(msg)

# Schema Exceptions

class SchemaTypeError(TypeError):
    def __init__(self, msg=None, desc=None):
        TypeError.__init__(self, msg)
        self.msg  = msg
        self.desc = desc

        if msg is not None:
            logs.warning(msg)

class SchemaKeyError(KeyError):
    def __init__(self, msg=None, desc=None):
        KeyError.__init__(self, msg)
        self.msg  = msg
        self.desc = desc

        if msg is not None:
            logs.warning(msg)

class SchemaValidationError(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc

        if msg is not None:
            logs.warning(msg)

# Basic Stamped Exceptions

class StampedPermissionsError(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc
        
        if msg is not None:
            logs.warning(msg)

class StampedIllegalActionError(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc
        
        if msg is not None:
            logs.warning(msg)

class StampedInputError(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc
        
        if msg is not None:
            logs.warning(msg)

class StampedUnavailableError(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc
        
        if msg is not None:
            logs.warning(msg)

class StampedDuplicationError(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc
        
        if msg is not None:
            logs.warning(msg)

class StampedAuthError(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc
        
        if msg is not None:
            logs.warning(msg)

# Specific Stamped Exceptions

class StampedLinkedAccountExistsError(StampedIllegalActionError):
    def __init__(self, msg=None):
        StampedIllegalActionError.__init__(self, msg)

class StampedInvalidPasswordError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)

class StampedInvalidScreenNameError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)

class StampedInvalidEmailError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)

class StampedInvalidClientError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)

class StampedInvalidCredentialsError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)

class StampedDuplicateEmailError(StampedDuplicationError):
    def __init__(self, msg=None):
        StampedDuplicationError.__init__(self, msg)

class StampedDuplicateScreenNameError(StampedDuplicationError):
    def __init__(self, msg=None):
        StampedDuplicationError.__init__(self, msg)


# Third Party Stamped Exceptions

class StampedThirdPartyError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)

class StampedThirdPartyInvalidCredentialsError(StampedInvalidCredentialsError):
    def __init__(self, msg=None):
        StampedInvalidCredentialsError.__init__(self, msg)
