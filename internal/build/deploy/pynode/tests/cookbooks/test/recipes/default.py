
from kokki import *

# File("/tmp/kokki-test",
#     content = StaticFile("test/static.txt"))
#     # content = Template("test/test.j2"))

env._test = env.config.test.config2

"""
#for cookbook in env.config:
for item in env.config:
    from pprint import pprint
    pprint(item)
    pprint(env.config[item])
"""


