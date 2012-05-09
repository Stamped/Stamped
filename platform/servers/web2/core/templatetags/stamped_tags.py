#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import logs, os, pystache, utils

from subprocess import Popen, PIPE
from pprint     import pformat
from django     import template

register = template.Library()

__global_template_library = None
def global_custom_template_library():
    global __global_template_library
    
    if __global_template_library is None:
        __global_template_library = MustacheTemplateLibrary()
    
    return __global_template_library

__global_css_template_library = None
def global_custom_css_template_library():
    global __global_css_template_library
    
    if __global_css_template_library is None:
        __global_css_template_library = CustomCSSTemplateLibrary()
    
    return __global_css_template_library

class MustacheTemplateLibrary(object):
    
    """
        Container for all custom mustache templates used in this django project.
    """
    
    def __init__(self):
        path = os.path.abspath(os.path.dirname(__file__))
        root = os.path.dirname(os.path.dirname(path))
        name = os.path.join(root, 'templates')
        
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

class CustomCSSTemplateLibrary(object):
    
    """
        Container for all custom mustache templated less css files used in this 
        django project.
    """
    
    def __init__(self):
        path = os.path.abspath(os.path.dirname(__file__))
        root = os.path.dirname(os.path.dirname(path))
        name = os.path.join(os.path.join(root, 'assets'), 'css')
        
        self._load_templates(name)
        self._renderer = pystache.Renderer(partials=self.partials)
    
    def _load_templates(self, root):
        self.templates = {}
        suffix = '.less.template'
        
        for directory, subdirs, filenames in os.walk(root):
            for filename in filenames:
                if not filename.endswith(suffix):
                    continue
                
                path = os.path.join(directory, filename)
                with open(path, 'r') as f:
                    text = f.read()
                
                name = filename[:-len(suffix)]
                self.templates[name] = (path, text)
        
        self.partials = dict(((k, v[1]) for k, v in self.templates.iteritems()))
        logs.info("[%s] loaded %d custom templates" % (self, len(self.templates)))
    
    def render(self, template_name, context):
        less    = self._renderer.render(self.templates[template_name][1], context)
        proxy   = ".%s.less" % template_name
        
        if utils.is_ec2():
            prog = "/stamped/node/node_modules/less/bin/lessc"
        else:
            prog = "lessc"
        
        cmd     = "%s %s" % (prog, proxy)
        
        with open(proxy, 'w') as fp:
            fp.write(less)
            fp.close()
        
        pp      = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        output  = pp.stdout.read().strip()
        error   = pp.stderr.read().strip()
        status  = pp.wait()
        
        if 0 != status:
            raise Exception("lessc error %d: %s\n%s" % (status, output, error))
        
        return output
    
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
        tag_name, less_css_template_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly one argument" % token.contents.split()[0])
    
    for s in [ '"', '"' ]:
        if (less_css_template_name.startswith(s) and less_css_template_name.endswith(s)):
            less_css_template_name = less_css_template_name[len(s):-len(s)]
            break
    
    library = global_custom_template_library()
    if (less_css_template_name not in library.templates):
        raise template.TemplateDoesNotExist("%r '%s' not found" % (less_css_template_name, 
                                                                   token.contents.split()[0]));
    
    return CustomTemplateNode(less_css_template_name, library)

@register.tag
def custom_css(parser, token):
    """
        Defines inline customizable css for the django templating engine called 'custom_css' 
        which accepts exactly one parameter, the name of the custom less template to render 
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
    
    library = global_custom_css_template_library()
    if (template_name not in library.templates):
        raise template.TemplateDoesNotExist("%r '%s' not found" % (template_name, token.contents.split()[0]));
    
    return CustomCSSNode(template_name, library)

class AStampedNode(template.Node):
    
    def _simplify_context(self, context):
        context_dict = {}
        
        # convert django context object to a normal python dict for ease of 
        # use / interop with the custom template library's renderer.
        for d in context:
            for k, v in d.iteritems():
                if k not in context_dict:
                    context_dict[k] = v
        
        return context_dict
    
    def __str__(self):
        return self.__class__.__name__

class CustomTemplateNode(AStampedNode):
    """
        Defines the renderer (e.g., View in MVC) for our custom_template tag, 
        which renders custom templates w.r.t. django's current templating 
        context.
    """
    
    def __init__(self, name, library):
        AStampedNode.__init__(self)
        self._name = name
        self._library = library
    
    def render(self, context):
        try:
            context_dict = self._simplify_context(context)
            
            result = self._library.render(self._name, context_dict)
            if len(result.strip()) == 0:
                logs.warn("%s.render warning empty result (%s)" % (self, self._name))
            
            return result
        except Exception, e:
            logs.warn("%s.render error (%s): %s" % (self, self._name, e))
            logs.warn(utils.getFormattedException())
            
            return ''

class CustomCSSNode(AStampedNode):
    """
        Defines the renderer (e.g., View in MVC) for our custom_css tag, which 
        renders custom less css templates w.r.t. django's current templating 
        context.
    """
    
    def __init__(self, name, library):
        AStampedNode.__init__(self)
        
        self._name = name
        self._library = library
    
    def render(self, context):
        try:
            context_dict = self._simplify_context(context)
            
            result = self._library.render(self._name, context_dict)
            if len(result.strip()) == 0:
                logs.warn("%s.render warning empty result (%s)" % (self, self._name))
            
            return result
        except Exception, e:
            logs.warn("%s.render error (%s): %s" % (self, self._name, e))
            logs.warn(utils.getFormattedException())
            
            return ''

