
from pynode.resources.package import PythonPackage

env.includeRecipe("virtualenv")

path = env.config.node.path
env.cookbooks.virtualenv.VirtualEnv(path) #, site_packages=False)

env.includeRecipe("pip")
#env.includeRecipe("libevent")

for package in env.config.node.python.requirements:
    env.cookbooks.pip.PipPackage(package, virtualenv=path)

