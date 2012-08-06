#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import os, utils

from servers.web2.core.templatetags.stamped_tags import global_handlebars_template_library

def process_templates(output_path, target=None):
    library   = global_handlebars_template_library()
    templates = library.templates
    
    scripts   = []
    indent    = "    "
    
    if target is None:
        target_templates = sorted(templates.keys())
    else:
        target_templates = []
        
        for template in target:
            if template not in templates:
                template = template.split('.')[0]
            
            assert template in templates
            target_templates.append(template)
    
    for template in target_templates:
        path, source = templates[template]
        path_comment = "<!-- %s -->" % os.path.basename(path)
        
        indented_source = '\n'.join("%s%s" % (indent, line) for line in source.split('\n'))
        indented_source = "%s%s" % (indent, indented_source.strip())
        
        wrapper = "%s\n<script id='%s' type='text/html' class='handlebars-template'>\n%s\n</script>\n" % \
                  (path_comment, template, indented_source)
        
        scripts.append(wrapper)
    
    # TODO: optionally use r.js to optimize / minify each individual script
    output = '\n'.join(scripts)
    with open(output_path, 'w') as f:
        f.write(output)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', type=str, default='templates/templates.generated.html')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-t', '--template', action='append', default=[])
    args = parser.parse_args()
    
    process_templates(args.output, args.template)

