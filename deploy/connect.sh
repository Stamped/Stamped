#!/usr/bin/env bash

if [ "$#" -eq 1 ]
then
    user="ubuntu"
    node=$1
    echo "defaulting to user $user"
elif [ "$#" -eq 2 ]
then
    user=$1
    node=$2
else
    echo "Description:"
    echo "   ssh's into an active AWS instance denoted by the given node-name (e.g., stack-name.instance-name)"
    echo ""
    echo "Usage:"
    echo "   $0 node-name OR $0 user node-name"
    exit 1
fi

echo "user: $user"
echo "node: $node"

dns=`./get_dns_by_node_name.py $node`
echo "dns:   $dns"

echo -n -e "\033]0;$node\007"
ssh -o StrictHostKeyChecking=no -i 'keys/test-keypair' "$user@$dns"
echo -n -e "\033]0;Terminal\007"

