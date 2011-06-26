
sudo yum install -y ant
sudo mkdir /var/lib/cassandra
sudo chown `whoami` /var/lib/cassandra/
sudo mkdir /var/log/cassandra
sudo chown `whoami` /var/log/cassandra/
mkdir /var/lib/cassandra/commitlog /var/lib/cassandra/data
sudo mkdir /mnt/cassandra
sudo chown `whoami` /mnt/cassandra/
mkdir /mnt/cassandra/commitlog /mnt/cassandra/data /mnt/cassandra/logs
echo "/mnt/cassandra/logs /var/log/cassandra    none bind" | sudo -E tee -a /etc/fstab
echo "/mnt/cassandra/logs /var/lib/cassandra/commitlog    none bind" | sudo -E tee -a /etc/fstab
echo "/mnt/cassandra/logs /var/lib/cassandra/data    none bind" | sudo -E tee -a /etc/fstab
sudo mount /var/log/cassandra/
sudo mount /var/lib/cassandra/commitlog/
sudo mount /var/lib/cassandra/data/
wget -q http://www.apache.org/dist/cassandra/0.8.0/apache-cassandra-0.8.0-bin.tar.gz
tar -zxf apache-cassandra-0.8.0-bin.tar.gz
echo "export CASSANDRA_HOME=~/apache-cassandra-0.8.0" | sudo -E tee -a ~/.bashrc
rm apache-cassandra-0.8.0-bin.tar.gz 
# mv ~/cassandra.yaml ~/apache-cassandra-0.8.0/conf
cd ~/apache-cassandra-0.8.0/
