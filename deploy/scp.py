#!/usr/bin/env bash

if [ "$#" -eq 2 ]
then
    user="ubuntu"
    node=$1
    path=$2
    echo "defaulting to user $user"
elif [ "$#" -eq 3 ]
then
    user=$1
    node=$2
    path=$3
else
    echo "Description:"
    echo "   scp's a file from an EC2 instance"
    echo ""
    echo "Usage:"
    echo "   $0 node-name path OR $0 user node-name path"
    exit 1
fi

echo "user: $user"
echo "node: $node"
echo "path: $path"

dns=`./get_dns_by_node_name.py $node`
echo "dns:  $dns"

scp -i 'keys/test-keypair' "$user@$dns:$path" .

