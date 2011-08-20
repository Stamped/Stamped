
class Fail(Exception):
    pass

class InvalidArgument(Exception):
    pass

class StampedHTTPError(Exception):
	def __init__(self, msg, code, desc=None):
		Exception.__init__(self, msg)
		self.code = code
		self.msg = msg
		self.desc = desc

class InvalidState(Exception):
    pass

class SchemaTypeError(TypeError):
	def __init__(self, msg=None, desc=None):
		TypeError.__init__(self, msg)
		self.msg = msg
		self.desc = desc

class SchemaKeyError(KeyError):
	def __init__(self, msg=None, desc=None):
		KeyError.__init__(self, msg)
		self.msg = msg
		self.desc = desc

class SchemaValidationError(Exception):
	def __init__(self, msg=None, desc=None):
		Exception.__init__(self, msg)
		self.msg = msg
		self.desc = desc
