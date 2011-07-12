#!/usr/bin/env python

from setuptools import setup, find_packages

import os
execfile(os.path.join('pynode', 'version.py'))

setup(
    name = 'pynode',
    version = VERSION,
    description = 'PyNode is a light-weight Python configuration management framework influenced by Chef', 
    author = 'Travis Fischer',
    author_email = 'travis@stamped.com',
    url = 'http://www.stamped.com/pynode/',
    packages = find_packages(),
    test_suite = "tests", 
    entry_points = {
        "console_scripts": [
            "pynode = pynode.PyNode:main",
        ],
    },
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires = [
        'jinja2', 
        'virtualenv', 
        'pip', 
    ],
)
