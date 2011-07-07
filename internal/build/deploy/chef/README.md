Assuming you have ruby, rubygems, and chef + prerequisites installed, and the chef bin dir is in your path, you can run the solo version of chef locally from this directory via the command:
    sudo chef-solo -c solo.rb

Note that the sudo is required. If you want more detailed logging output, run:
    sudo chef-solo -l debug -c solo.rb

