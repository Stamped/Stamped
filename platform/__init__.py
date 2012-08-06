from __future__ import absolute_import
"""
Primary Stamped Python module

Important Leaf Modules:

utils.py    : Utility functions and classes
logs.py     : Logging functions
schema.py   : Schema base classes for uniform and checked scalar, list, and dictionary representations.

Important Package Modules:

api         : Stamped API, application layer logic, database interfaces and implementations
alerts      : Push notifications, emails, low-importance
bin         : useful scripts
    logger.py   : query all logged API calls (local, Mongo-backed, and long-term logs)

crawler     :    crawl websites asynchronously, both lazy and pre-emptive
    NEEDS maintenance and improvement (Kevin, Travis)

keys        : certificates and cryptographic keys

libs        : 3rd party libraries, wrappers, and glue
    ec2_utils.py    : query all nodes in a given stack

servers     : Django webservers
    httpapi     : REST API
    web         : website

tasks       : Asynchronous tasks/messaging with Celery

tests       : Unit testing framework
    api         : test local stack
        main.py     : local test scipt
"""
