from __future__ import absolute_import
import os, sys

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base)

sys.path.append(os.path.join(base, "api"))

import stamped
