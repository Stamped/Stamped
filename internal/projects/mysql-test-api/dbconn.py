#!/usr/bin/env python

import MySQLdb

class DatabaseConnection:

    def connect(self):
        return MySQLdb.connect(user='root',db='stamped_api')