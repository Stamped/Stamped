
import logs

class Fail(Exception):
    pass

class StampedHTTPError(Exception):
    def __init__(self, msg, code, desc=None):
        Exception.__init__(self, msg)
        self.code = code
        self.msg  = msg
        self.desc = desc

class SchemaTypeError(TypeError):
    def __init__(self, msg=None, desc=None):
        TypeError.__init__(self, msg)
        self.msg  = msg
        self.desc = desc

class SchemaKeyError(KeyError):
    def __init__(self, msg=None, desc=None):
        KeyError.__init__(self, msg)
        self.msg  = msg
        self.desc = desc

class SchemaValidationError(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc

class StampedPermissionsErrorInsufficientPrivilegesError(Exception):
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

