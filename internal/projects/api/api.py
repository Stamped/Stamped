#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import sys, thread
import MySQLdb
import Entity

# import specific databases
from db.mysql.MySQLEntityDB import MySQLEntityDB






def main():
    MySQLEntityDB().addEntity(1)
   

# where all the magic starts
if __name__ == '__main__':
    main()
