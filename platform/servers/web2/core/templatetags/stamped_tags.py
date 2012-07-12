#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import logs, os, pystache, utils, pybars

from servers.web2.core.templatetags.handlebars_template_helpers import *

from subprocess import Popen, PIPE
from pprint     import pformat
from django     import template

register = template.Library()

__global_mustache_template_library = None
def global_mustache_template_library():
    global __global_mustache_template_library
    
    if __global_mustache_template_library is None:
        __global_mustache_template_library = MustacheTemplateLibrary()
    
    return __global_mustache_template_library

__global_handlebars_template_library = None
def global_handlebars_template_library():
    global __global_handlebars_template_library
    
    if __global_handlebars_template_library is None:
        __global_handlebars_template_library = HandlebarsTemplateLibrary()
    
    return __global_handlebars_template_library

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
        logs.debug("[%s] loaded %d custom templates" % (self, len(self.templates)))
    
    def render(self, template_name, context):
        return self._renderer.render(self.templates[template_name][1], context)
    
    def __str__(self):
        return self.__class__.__name__

class HandlebarsTemplateLibrary(object):
    
    """
        Container for all custom handlebars templates used in this django project.
    """
    
    def __init__(self):
        path = os.path.abspath(os.path.dirname(__file__))
        root = os.path.dirname(os.path.dirname(path))
        name = os.path.join(root, 'templates')
        
        self._load_templates(name)
        self._renderer = pybars.Compiler()
        self._compiled = {}
        self._partials = {}
        
        for k, v in self.templates.iteritems():
            path, source = v
            source = unicode(source)
            
            try:
                compiled = self._renderer.compile(source)
                
                self._compiled[k] = compiled
                self._partials[k] = compiled
            except Exception, e:
                logs.warn("[%s] template compiler error (%s): %s" % (self, path, e))
                raise
            
            #def m(n, k):
            #    logs.warn("[%s] MISSING: '%s' '%s'" % (n, k))
            #self._renderer.register_helper('helperMissing', m)
            try:
                pass
                #def helper(items, options):
                #    return compiled(items)
                
                #self._renderer.register_helper(k, compiled)
            except Exception, e:
                logs.warn("[%s] template register helper error (%s): %s" % (self, path, e))
                raise
    
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
        
        #logs.debug("[%s] loaded %d custom templates" % (self, len(self.templates)))
    
    def render(self, template_name, context):
        pad = "-" * 20
        pad = "%s %s(%s) %s" % (pad, self, template_name, pad)
        
        def helper_wrapper(helper):
            def _(*args, **kwargs):
                return helper(template_name, pad, *args, **kwargs)
            
            return _
        
        helpers = dict(
            helperMissing=helper_wrapper(missing), 
            user_profile_image=helper_wrapper(user_profile_image), 
            entity_image=helper_wrapper(entity_image), 
            debug=helper_wrapper(debug)
        )
        
        return self._compiled[template_name](context, helpers=helpers, partials=self._partials)
    
    def __str__(self):
        return self.__class__.__name__


class CustomCSSTemplateLibrary(object):
    
    """
        Container for all custom handlebars templated less css files used in this 
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
        logs.debug("[%s] loaded %d custom templates" % (self, len(self.templates)))
    
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

def custom_template(parser, token, template_library):
    try:
        parts = token.split_contents()
        context_variable = None
        
        if len(parts) == 2:
            tag_name, template_name = parts
        elif len(parts) == 3:
            tag_name, template_name, context_variable = parts
        else:
            raise ValueError
    except ValueError:
        raise template.TemplateSyntaxError("%r tag invalid arguments" % token.contents.split())
    
    for s in [ '"', '"' ]:
        if (template_name.startswith(s) and template_name.endswith(s)):
            template_name = template_name[len(s):-len(s)]
            break
    
    if (template_name not in template_library.templates):
        raise template.TemplateDoesNotExist("%r '%s' not found" % (template_name, 
                                                                   token.contents.split()[0]));
    
    return CustomTemplateNode(template_name, template_library, context_variable)

@register.tag
def mustache_template(parser, token):
    """
        Defines a custom tag for the django templating engine called 'mustache_template' 
        which accepts exactly one parameter, the name of the custom template to render 
        in the context of the current django templating context.
    """
    
    return custom_template(parser, token, global_mustache_template_library())

@register.tag
def handlebars_template(parser, token):
    """
        Defines a custom tag for the django templating engine called 'handlebars_template' 
        which accepts exactly one parameter, the name of the custom template to render 
        in the context of the current django templating context.
    """
    
    return custom_template(parser, token, global_handlebars_template_library())

@register.tag
def custom_css(parser, token):
    """
        Defines inline customizable css for the django templating engine called 'custom_css' 
        which accepts exactly one parameter, the name of the custom less template to render 
        in the context of the current django templating context.
    """
    
    try:
        parts = token.split_contents()
        context_variable = None
        
        if len(parts) == 2:
            tag_name, template_name = parts
        elif len(parts) == 3:
            tag_name, template_name, context_variable = parts
        else:
            raise ValueError
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly one argument" % token.contents.split()[0])
    
    for s in [ '"', '"' ]:
        if (template_name.startswith(s) and template_name.endswith(s)):
            template_name = template_name[len(s):-len(s)]
            break
    
    library = global_custom_css_template_library()
    if (template_name not in library.templates):
        raise template.TemplateDoesNotExist("%r '%s' not found" % (template_name, token.contents.split()[0]));
    
    return CustomCSSNode(template_name, library, context_variable)

@register.filter
def split(s, delimiter):
    return s.split(delimiter)

@register.filter
def split0(s, delimiter):
    return s.split(delimiter)[0]

@register.filter
def split1(s, delimiter):
    return s.split(delimiter)[1]

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
    
    def __init__(self, name, library, context_variable=None):
        AStampedNode.__init__(self)
        self._name = name
        self._library = library
        
        if context_variable is not None:
            self._context_variable = template.Variable(context_variable)
        else:
            self._context_variable = None
    
    def render(self, context):
        try:
            if self._context_variable is None:
                context_dict = self._simplify_context(context)
            else:
                context_dict = self._context_variable.resolve(context)
            
            result = unicode(self._library.render(self._name, context_dict))
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
    
    def __init__(self, name, library, context_variable=None):
        AStampedNode.__init__(self)
        
        self._name = name
        self._library = library
        
        if context_variable is not None:
            self._context_variable = template.Variable(context_variable)
        else:
            self._context_variable = None
    
    def render(self, context):
        try:
            if self._context_variable is None:
                context_dict = self._simplify_context(context)
            else:
                context_dict = self._context_variable.resolve(context)
            
            result = self._library.render(self._name, context_dict)
            if len(result.strip()) == 0:
                logs.warn("%s.render warning empty result (%s)" % (self, self._name))
            
            return result
        except Exception, e:
            logs.warn("%s.render error (%s): %s" % (self, self._name, e))
            logs.warn(utils.getFormattedException())
            
            return ''

