#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import os, utils

from core.templatetags.stamped_tags import global_custom_template_library

def process_templates(output_path):
    library   = global_custom_template_library()
    templates = library.templates
    
    scripts   = []
    indent    = "    "
    
    for template in sorted(templates.keys()):
        path, source = templates[template]
        path_comment = "<!-- %s -->" % os.path.basename(path)
        
        indented_source = '\n'.join("%s%s" % (indent, line) for line in source.split('\n'))
        indented_source = "%s%s" % (indent, indented_source.strip())
        
        wrapper = "%s\n<script id='%s' type='text/html' class='mustache-template'>\n%s\n</script>\n" % \
                  (path_comment, template, indented_source)
        
        scripts.append(wrapper)
    
    # TODO: optionally use r.js to optimize / minify each individual script
    output = '\n'.join(scripts)
    with open(output_path, 'w') as f:
        f.write(output)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', type=str, default='html/templates.generated.html')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    args = parser.parse_args()
    
    process_templates(args.output)

