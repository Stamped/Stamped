json_attribs      File.expand_path(File.join(File.dirname(__FILE__), "node.json"))
cookbook_path     File.expand_path(File.join(File.dirname(__FILE__), "cookbooks"))
log_level         :info
#file_store_path   File.join(File.dirname(__FILE__), '..')
#file_cache_path   File.join(File.dirname(__FILE__), '..')

Chef::Log::Formatter.show_time = false

print "\n"
print "cookbook_path: '#{cookbook_path}'\n"
print "json_attribs:  '#{json_attribs}'\n"
print "\n"

