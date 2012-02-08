#!/usr/bin/env bash

user="ubuntu"
node=$1
coll=$2

echo "user: $user"
echo "node: $node"
echo "coll: $coll"

dns=`./get_dns_by_node_name.py $node`
echo "dns:  $dns"

cmd="mongoexport -d stamped -c $coll -o $coll"
ssh -o StrictHostKeyChecking=no -i 'keys/test-keypair' "$user@$dns" "$cmd"

mkdir -p .temp
scp -i 'keys/test-keypair' "$user@$dns:/home/ubuntu/$coll" .temp

mongoimport --drop -d stamped -c $coll .temp/$coll

