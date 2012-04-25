#!/usr/bin/env bash

user="ubuntu"
node=$1
coll=${*:2}

echo "Imports a collections from the mongodb instance running on the given semantic node (e.g., peach.db1)."
echo "usage: $0 node collection+"
echo "example: $0 peach.db1 stamps users"
echo ""
echo "user: $user"
echo "node: $node"
echo "coll: $coll"

dns=`./get_dns_by_node_name.py $node`
echo "dns:  $dns"
mkdir -p .temp

echo ""
echo "exporting and downloading..."

for c in $coll
do
    cmd="mongoexport -d stamped -c $c -o $c"
    ssh -o StrictHostKeyChecking=no -i 'keys/test-keypair' "$user@$dns" "$cmd"
    scp -i 'keys/test-keypair' "$user@$dns:/home/ubuntu/$c" .temp
done

echo ""
echo "importing..."
for c in $coll
do
    mongoimport --drop -d stamped -c $c .temp/$c
done

