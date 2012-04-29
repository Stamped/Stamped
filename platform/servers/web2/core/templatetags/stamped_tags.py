#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import logs, os, pystache, utils

from pprint import pformat
from django import template

register = template.Library()

__global_template_library = None
def global_custom_template_library():
    global __global_template_library
    
    if __global_template_library is None:
        __global_template_library = MustacheTemplateLibrary()
    
    return __global_template_library

class MustacheTemplateLibrary(object):
    
    """
        Container for all custom mustache templates used in this django project.
    """
    
    def __init__(self):
        path = os.path.abspath(os.path.dirname(__file__))
        root = os.path.dirname(os.path.dirname(path))
        name = os.path.join(root, 'html')
        
        self._load_templates(name)
        self._renderer = pystache.Renderer(partials=self.partials)
    
    def _load_templates(self, directory):
        self.templates = {}
        suffix = '.template.html'
        
        for template in sorted(os.listdir(directory)):
            if not template.endswith(suffix):
                continue
            
            path = os.path.join(directory, template)
            with open(path, 'r') as f:
                text = f.read()
            
            name = template[:-len(suffix)]
            self.templates[name] = (path, text)
        
        self.partials = dict(((k, v[1]) for k, v in self.templates.iteritems()))
        logs.info("[%s] loaded %d custom templates" % (self, len(self.templates)))
    
    def render(self, template_name, context):
        return self._renderer.render(self.templates[template_name][1], context)
    
    def __str__(self):
        return self.__class__.__name__

@register.tag
def custom_template(parser, token):
    """
        Defines a custom tag for the django templating engine called 'custom_template' 
        which accepts exactly one parameter, the name of the custom template to render 
        in the context of the current django templating context.
    """
    
    try:
        tag_name, template_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly one argument" % token.contents.split()[0])
    
    for s in [ '"', '"' ]:
        if (template_name.startswith(s) and template_name.endswith(s)):
            template_name = template_name[len(s):-len(s)]
            break
    
    library = global_custom_template_library()
    if (template_name not in library.templates):
        raise template.TemplateDoesNotExist("%r '%s' not found" % (template_name, token.contents.split()[0]));
    
    return CustomTemplateNode(template_name, library)

class CustomTemplateNode(template.Node):
    """
        Defines the renderer (e.g., View in MVC) for our custom_template tag, 
        which renders custom templates w.r.t. django's current templating 
        context.
    """
    
    def __init__(self, template_name, library):
        self._template_name = template_name
        self._library       = library
    
    def render(self, context):
        try:
            context_dict = {}
            
            # convert django context object to a normal python dict for ease of 
            # use / interop with the custom template library's renderer.
            for d in context:
                for k, v in d.iteritems():
                    if k not in context_dict:
                        context_dict[k] = v
            
            result = self._library.render(self._template_name, context_dict)
            if len(result.strip()) == 0:
                logs.warn("CustomTemplateNode.render warning empty result (%s)" % self._template_name)
            
            return result
        except Exception, e:
            logs.warn("CustomTemplateNode.render error (%s): %s" % (self._template_name, e))
            logs.warn(utils.getFormattedException())
            
            return ''

