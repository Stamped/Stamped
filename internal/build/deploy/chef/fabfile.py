from fabric.api import env, local, run, sudo

env.user  = 'root'
env.hosts = ['204.232.205.196']

env.code_dir = '/sites/stamped'
env.virtualenv = '/sites/stamped'
env.rundir = '/sites/stamped/run'

env.chef_executable = '/var/lib/gems/1.8/bin/chef-solo'

def install_chef():
    sudo('apt-get update', pty=True)
    sudo('apt-get install -y git-core rubygems ruby ruby-dev', pty=True)
    sudo('gem install chef --no-ri --no-rdoc', pty=True)

def sync_config():
    local('rsync -av . %s@%s:/etc/chef' % (env.user, env.hosts[0]))

def update():
    sync_config()
    sudo('cd /etc/chef && %s' % env.chef_executable, pty=True)

def reload():
    "Reload the server."
    env.user = "docs"
    run("kill -HUP `cat %s/gunicorn.pid`" % env.rundir, pty=True)

def restart():
    "Restart (or just start) the server"
    sudo('restart stamped-gunicorn', pty=True)

