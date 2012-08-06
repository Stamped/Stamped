from __future__ import absolute_import
import os

import sys

import re

lines = sys.stdin.readlines()

for line in lines:
	match = re.match(r'(\d+) .+ Worker.py .+', line)
	if match is not None:
		pid = match.group(1)
		os.system('kill %s' % pid)