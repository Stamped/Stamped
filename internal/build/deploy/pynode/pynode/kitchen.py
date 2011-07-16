#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import os, utils
from utils import AttributeDict, OrderedDict
from cookbook import Cookbook
from environment import Environment
from errors import Fail

class Kitchen(Environment):
    
    def __init__(self):
        self._running = False
        super(Kitchen, self).__init__()
    
    def reset(self):
        super(Kitchen, self).reset()
        
        if hasattr(self, '_running') and self._running:
            raise Fail("Error can't reset Kitchen while it is running")
        
        self._sourced_recipes  = set()
        self._included_recipes = OrderedDict()
        self.cookbooks = AttributeDict()
        self._cookbookPaths = [ ]
        self._running = False
    
    def run(self):
        recipes = ""
        
        for k, v in self._included_recipes.iteritems():
            name = k
            (cookbook, recipe) = v
            
            recipes += "%s : %s(%s); " % (name, cookbook, recipe)
        
        utils.log("Kitchen is up and running...")
        utils.log("   recipes       (%d): %s" % (len(self._included_recipes), recipes))
        utils.log("   cookbook_path (%d): %s" % (len(self._cookbookPaths), str(self._cookbookPaths)))
        
        self._running = True
        self._preRun()
        
        super(Kitchen, self).run()
        
        self._postRun()
        self._running = False
        
        utils.log("Kitchen finished processing all recipes successfully!")
    
    def includeRecipe(self, *args):
        for name in args:
            if name in self._included_recipes:
                continue
            
            try:
                cookbook, recipe = name.split('.')
            except ValueError:
                cookbook, recipe = name, "default"
            
            try:
                cookbook = self.cookbooks[cookbook]
            except KeyError:
                try:
                    self._loadCookbook(cookbook)
                    cookbook = self.cookbooks[cookbook]
                except ImportError as e:
                    utils.log("Error: unable to find cookbook for recipe '%s'" % name)
                    raise e
            
            self._included_recipes[name] = (cookbook, recipe)
            
            if self._running:
                self._sourceRecipe(cookbook, recipe)
    
    def addCookbookPath(self, *args):
        for origPath in args:
            path = utils.resolvePath(origPath)
            
            self._cookbookPaths.append((origPath, path))
    
    def _registerCookbook(self, cookbook):
        #utils.log("Registering cookbook %s" % (cookbook, ))
        self.updateConfig(dict((k, v.get('default')) for k, v in cookbook.config.items()), False)
        self.cookbooks[cookbook.name] = cookbook
    
    def _loadCookbook(self, *args, **kwargs):
        for name in args:
            cookbook = None
            
            for origpath, path in reversed(self._cookbookPaths):
                fullpath = os.path.join(path, name)
                if not os.path.exists(fullpath):
                    continue
                
                cookbook = Cookbook.loadFromPath(name, fullpath)
                break
            
            if not cookbook:
                raise ImportError("Cookbook %s not found" % name)
            
            self._registerCookbook(cookbook)
    
    def _sourceRecipe(self, cookbook, recipe):
        name = "%s.%s" % (cookbook.name, recipe)
        if name in self._sourced_recipes:
            return
        
        utils.log("Sourcing recipe '%s' in cookbook '%s'" % (recipe, cookbook.name))
        
        self._sourced_recipes.add(name)
        cookbook.loader(self)
        
        rc = cookbook.getRecipe(recipe)
        globs = { 'env': self }
        
        with self:
            exec compile(rc, name, 'exec') in globs
    
    def _preRun(self):
        for name in self._included_recipes:
            (cookbook, recipe) = self._included_recipes[name]
            self._sourceRecipe(cookbook, recipe)
    
    def _postRun(self):
        pass
    
    def __getstate__(self):
        state = super(Kitchen, self).__getstate__()
        
        state.update(
            cookbookPaths   = [ x[0] for x in self.cookbookPaths ],
            includedRecipes = self.includedRecipes, 
        )
        
        return state
    
    def __setstate__(self, state):
        super(Kitchen, self).__setstate__(state)
        
        for path in state['cookbookPaths']:
            self.addCookbookPath(path)
        
        for recipe in state['includedRecipes']:
            self.includeRecipe(recipe)

