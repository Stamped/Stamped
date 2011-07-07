#!/usr/bin/env python

__author__ = "Richard Crowley, Kevin Palms"
__version__ = "0.0.0"
__copyright__ = "Copyright 2011 DevStructure"
__license__ = "TODO"

"""
Modified from Crowley's tools for creating CloudFormation templates.

http://devstructure.github.com/python-cloudformation/python-cloudformation.7.html
https://github.com/devstructure/python-cloudformation#readme

COPYRIGHT:
    Copyright 2011 DevStructure. All rights reserved.
    
    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:
    
        1.  Redistributions of source code must retain the above copyright
            notice, this list of conditions and the following disclaimer.
    
        2.  Redistributions in binary form must reproduce the above
            copyright notice, this list of conditions and the following
            disclaimer in the documentation and/or other materials provided
            with the distribution.
    
    THIS SOFTWARE IS PROVIDED BY DEVSTRUCTURE ``AS IS'' AND ANY EXPRESS
    OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL DEVSTRUCTURE OR CONTRIBUTORS BE LIABLE
    FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
    THE POSSIBILITY OF SUCH DAMAGE.
    
    The views and conclusions contained in the software and documentation
    are those of the authors and should not be interpreted as representing
    official policies, either expressed or implied, of DevStructure.

"""

from collections import defaultdict
import json

def _dict_property(name):
    """
    Return a property that gets and sets the given dictionary item.
    """
    def get(self):
        return self[name]
    def set(self, value):
        self[name] = value
    return property(get, set)
    
def EncodeUserData(string):
    data = []
    for line in string.split('\n'):
        data.append(line)
        data.append("\n")
    return data
    
def AddWaitHandle(handle):
    data = ["\n"]
    data.append("curl -X PUT -H 'Content-Type:' --data-binary '{\"Status\": \"SUCCESS\", \"Reason\": \"Instance is ready\", \"UniqueId\": \"stamped\", \"Data\": \"Done\"}' \"")
    data.append({"Ref": handle})
    data.append("\"\n")
    return data

class Template(defaultdict):
    """
    A CloudFormation template.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize a neverending tree of Template objects.
        """
        super(self.__class__, self).__init__(*args, **kwargs)
        self.default_factory = lambda: self.__class__(self.__class__)
        self.user_data = []

    # Shortcuts to the typical keys in a Template template.
    Description = _dict_property('Description')
    Mappings = _dict_property('Mappings')
    Outputs = _dict_property('Outputs')
    Parameters = _dict_property('Parameters')
    Resources = _dict_property('Resources')

    def add(self, key, *args, **kwargs):
        """
        Add an item to this CloudFormation template.  This is typically
        called on non-root Template objects, for example

            t.Parameters.add(...)

        to add an item to the Parameters object.
        """
        self[key] = self.__class__(*args, **kwargs)

    def dumps(self, pretty=True):
        """
        Return a string representation of this CloudFormation template.
        """
        self['AWSTemplateFormatVersion'] = '2010-09-09'
        
        f = open('stamped-cloudformation-dev.template', 'w')
        json.dump(self, f, indent=2, sort_keys=True)
        f.close()
        
        print json.JSONEncoder(indent=2, sort_keys=True).encode(self)
