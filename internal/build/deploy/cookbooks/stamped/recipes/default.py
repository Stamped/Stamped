
from pynode.resources import Service

env.includeRecipe("virtualenv")

path = env.config.node.path
env.cookbooks.virtualenv.VirtualEnv(path) #, site_packages=False)

env.includeRecipe("pip")
env.includeRecipe("libevent")

for package in env.config.node.python.requirements:
    env.cookbooks.pip.PipPackage(package, virtualenv=path)

activate = env.config.node.path + "/bin/activate"
python = env.config.node.path + "/bin/python"
site = env.config.node.wsgi_app
wsgi_log = env.config.node.wsgi_log

Service(name="wsgi_app", 
        start_cmd="source %s && %s %s >& %s&" % (activate, python, site, wsgi_log))

