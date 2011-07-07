#Virtualenv setup

=begin
directory "/sites/" do
    owner node[:user]
    group node[:user]
    mode 0775
end

virtualenv "/sites/stamped" do
    owner node[:user]
    group node[:user]
    mode 0775
end

directory "/sites/stamped/run" do
    owner node[:user]
    group node[:user]
    mode 0775
end

git "/sites/stamped/" do
  repository "git://github.com/Stamped/Stamped.git"
  reference "HEAD"
  user node[:user]
  group node[:user]
  action :sync
end

script "Install Requirements" do
  interpreter "bash"
  user node[:user]
  group node[:user]
  code <<-EOH
  /sites/stamped/bin/pip install -r /sites/stamped/internal/build/deploy/requirements.txt
  EOH
end

# Gunicorn setup
service "stamped-gunicorn" do
    provider Chef::Provider::Service::Upstart
    enabled true
    running true
    supports :restart => true, :reload => true, :status => true
    action [:enable, :start]
end

service "stamped-celery" do
    provider Chef::Provider::Service::Upstart
    enabled true
    running true
    supports :restart => true, :reload => true, :status => true
    action [:enable, :start]
end

cookbook_file "/etc/init/stamped-gunicorn.conf" do
    source "gunicorn.conf"
    owner "root"
    group "root"
    mode 0644
    notifies :restart, resources(:service => "stamped-gunicorn")
end

cookbook_file "/etc/init/stamped-celery.conf" do
    source "celery.conf"
    owner "root"
    group "root"
    mode 0644
    notifies :restart, resources(:service => "stamped-celery")
end
=end

cookbook_file "/home/#{node[:user]}/.bash_profile" do
    source "bash_profile"
    owner node[:user]
    group node[:user]
    mode 0755
end

