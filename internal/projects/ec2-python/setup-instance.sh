# Install git
echo '>>>>>>>>> Install and configure git'
sudo yum -y install git

git config --global user.name "Stamped Bot"
git config --global user.email "devbot@stamped.com"

# Test GitHub connection
echo '>>>>>>>>> Add GitHub as host'
ssh -o StrictHostKeyChecking=no git@github.com
# Warning: not most secure method (bypasses check of IP address)

# Grab repo
echo '>>>>>>>>> Clone repo'
git clone git@github.com:Stamped/Stamped.git stamped

# Complete
echo '>>>>>>>>> Completed setup'
