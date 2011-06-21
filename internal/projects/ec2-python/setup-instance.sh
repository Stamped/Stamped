# Install git
echo '>>>>>>>>> Install & Configure Git'
sudo yum -y install git

git config --global user.name "Stamped Bot"
git config --global user.email "devbot@stamped.com"

# Test GitHub Connection
echo '>>>>>>>>> Add GitHub as host'
ssh -o StrictHostKeyChecking=no git@github.com
# Warning: not most secure method (bypasses check of IP address)

# Grab repo
echo '>>>>>>>>> Clone Repo'
git clone git@github.com:Stamped/Stamped.git stamped

# Install MySQL
echo '>>>>>>>>> Install & Configure MySQL'
sudo yum install -y xfsprogs mysql-server

echo "/dev/sda1 /vol xfs noatime 0 0" | sudo tee -a /etc/fstab
sudo mkdir -m 400 /vol

sudo /etc/init.d/mysqld stop

sudo mkdir /vol/etc /vol/lib /vol/log
sudo mv /etc/mysql     /vol/etc/
sudo mv /var/lib/mysql /vol/lib/
sudo mv /var/log/mysql /vol/log/
sudo mkdir /etc/mysql
sudo mkdir /var/lib/mysql
sudo mkdir /var/log/mysql

echo "/vol/etc/mysql /etc/mysql     none bind" | sudo tee -a /etc/fstab
sudo mount /etc/mysql
echo "/vol/lib/mysql /var/lib/mysql none bind" | sudo tee -a /etc/fstab
sudo mount /var/lib/mysql
echo "/vol/log/mysql /var/log/mysql none bind" | sudo tee -a /etc/fstab
sudo mount /var/log/mysql

sudo /etc/init.d/mysqld start

# Python
echo '>>>>>>>>> Setup MySQL API'
sudo yum -y install MySQL-python
python /home/ec2-user/stamped/internal/projects/mysql-test-api/mysql-api.py --setup

# Complete
echo '>>>>>>>>> Done!'
