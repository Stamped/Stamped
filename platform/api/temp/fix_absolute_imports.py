from __future__ import unicode_literals

import re
from sys import argv

pattern = re.compile('from __future__ import (.*)')

with open(argv[1]) as f:
    lines = [line for line in f]

for i, line in enumerate(lines):
    match = pattern.match(line)
    if match:
        imports = set([item.strip() for item in match.group(1).split(',')])
        imports.add('absolute_import')
        lines[i] = 'from __future__ import ' + ', '.join(sorted(imports)) + '\n'
        break
else:
    for i, line in enumerate(lines):
        if not line.startswith('#'):
            lines.insert(i, 'from __future__ import absolute_import\n')
            break

with open(argv[1], 'w') as f:
    f.writelines(lines)
