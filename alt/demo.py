from platform.utils import lazyProperty

class Foo(object):
    @lazyProperty
    def bar(self):
        print "running property"
        def foo():
            return 5
        return foo
        
