#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

def parseAddress(row):
    addr = ''
    
    if 'address' in row and row['address'] is not None and len(row['address']) > 0:
        addr = row['address']
    else:
        return None
    
    if 'address_extended' in row and row['address_extended'] is not None and len(row['address_extended']) > 0:
        addr = addr + ' ' + row['address_extended']
    
    if 'locality' in row and row['locality'] is not None and len(row['locality']) > 0:
        addr = addr + ', ' + row['locality']
    
    if 'region' in row and row['region'] is not None and len(row['region']) > 0:
        addr = addr + ' ' + row['region']
    
    if 'postcode' in row and row['postcode'] is not None and len(row['postcode']) > 0:
        addr = addr + ', ' + row['postcode']
    
    return addr

