#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import os, sys, virtualenv, Utils
import pip.commands.install
from optparse import OptionParser

class PyNode(object):
    def __init__(self, configFile):
        self.configFile = configFile
    
    @Utils.lazyProperty
    def config(self):
        configFilePath = self._resolvePath(self.configFile)
        
        with open(configFilePath, "rb") as fp:
            source = fp.read()
        
        cfg = eval(source)
        if not 'path' in cfg:
            cfg['path'] = "/pynode/%s" % cfg['name']
        
        return cfg
    
    def init(self):
        if not 'path' in self.config or not self._createVirtualEnv(self.config['path']):
            return False
        
        if 'python' in self.config and 'requirements' in self.config['python']:
            if not self._installPackages(self.config['python']['requirements']):
                return False
        
        if 'cookbooks' in self.config and not self._importCookbooks(self.config['cookbook_path'], self.config['cookbooks']):
            return False
        
        return True
    
    def _createVirtualEnv(self, path):
        if not os.path.exists(path):
            os.makedirs(path, 0755)
        
        virtualenv.create_environment(path)
        Utils.log("Installed virtualenv '%s'" % path)
        
        return True
    
    def _installPackages(self, packages):
        if len(packages) <= 0:
            return
        
        Utils.logRaw("Installing %d python packages..." % len(packages), True)
        
        try:
            command = pip.commands.install.InstallCommand()
            opts, args = command.parser.parse_args()
            
            # TBD, why do we have to run the next part here twice before actual install
            requirement_set = command.run(opts, packages)
            requirement_set = command.run(opts, packages)
            requirement_set.install(opts)
        except Exception as e:
            Utils.log("Error installing python packages with pip")
            Utils.printException()
            return False
        
        Utils.logRaw("done!\n")
        
        # ensure packages installed successfully by importing them one at a time
        success = True
        for package in packages:
            try:
                importExec = "import %s" % package
                exec importExec in { }
                Utils.log("Installed python package '%s'" % package)
            except ImportError as e:
                success = False
                Utils.log("Error installing package '%s'" % package)
        
        return success
    
    def _importCookbooks(self, cookbookPath, cookbooks):
        logArgs = (len(cookbooks), self._getCookbookStr(len(cookbooks)))
        Utils.log("Importing %d %s..." % logArgs)
        
        if not isinstance(cookbookPath, (tuple, list)):
            cookbookPath = [ cookbookPath ]
        
        success = True
        for cookbook in cookbooks:
            importedCookbook = False
            
            for path in cookbookPath:
                completePath = os.path.join(path, cookbook)
                
                if os.path.exists(completePath) and os.path.isdir(completePath):
                    try:
                        # !!!TODO!!!
                        # importing pollutes the local / global namespace!
                        # want to have isolated import with exec in { }
                        importExec = "import " + path + "." + cookbook
                        test = { }
                        exec importExec in test
                        Utils.log("Imported '%s' cookbook from '%s'" % (cookbook, completePath))
                        importedCookbook = True
                        break
                    except ImportError as e:
                        Utils.log("Error importing cookbook %s from '%s'" % (cookbook, completePath))
                        Utils.printException()
            
            if not importedCookbook:
                Utils.log("Error: could not import cookbook %s" % (cookbook, ))
                success = False
        
        if success:
            Utils.log("Imported %d %s successfully!" % logArgs)
        
        return success
    
    def _resolvePath(self, path):
        if "." in path and not os.path.exists(path):
            pkg  = __import__(path, {}, {}, path)
            path = os.path.abspath(pkg.__file__)
        
        return os.path.abspath(path)
    
    def _getCookbookStr(self, count):
        if count == 1:
            return "cookbook"
        else:
            return "cookbooks"

def parseCommandLine():
    usage   = "Usage: %prog [options] configfile"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        print "Error: must provide a single config file"
        parser.print_help()
        return None
    else:
        options.config = args[0]
    
    return options

def main():
    options = parseCommandLine()
    if options is None:
        return
    
    node = PyNode(options.config)
    node.init()

# where all the magic starts
if __name__ == '__main__':
    main()

