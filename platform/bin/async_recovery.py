import Globals

import re
import pprint
import datetime
import sys

import tasks.Tasks
import pprint

file_path = sys.argv[1]

f = open(file_path)

data = {}
lines = f.readlines()
for line in lines:
    match = re.match(r'.+ ((api|enrich)::\w+): ({.+}):.*\r\n', line)
    if match is not None:
        task_name = match.group(1)
        key = match.group(2)
        raw_string = match.group(3)
        try:
            payload = eval(raw_string)
            li = data.setdefault(key,[])
            li.append((task_name, payload))
        except Exception as e:
            print raw_string
            # preview_match = re.match(r'.+\((<StampPreview ({.+})>),\).+', raw_string)
            # print e 
            # print preview_match.group(1), preview_match.group(2)



for queue, v in data.items():
    for key, payload in v:
        pass
        # tasks.Tasks.call(queue, key, payload)

m = {}
for queue, v in data.items():
    for key, payload in v:
        value = m.setdefault(key, 0)
        m[key] =  value + 1

pprint.pprint(m)

# pprint.pprint(data)