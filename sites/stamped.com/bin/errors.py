
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