#!/usr/bin/env bash

if [ "$#" -eq 2 ]
then
    user="ubuntu"
    stack=$1
    tag=$2
    echo "defaulting to user $user"
elif [ "$#" -eq 3 ]
then
    user=$1
    stack=$2
    tag=$3
else
    echo "Description:"
    echo "   ssh's into an active AWS instance denoted by the given stack-name"
    echo ""
    echo "Usage:"
    echo "   $0 stack-name family-tag OR $0 user stack-name family-tag"
    exit 1
fi

echo "user:  $user"
echo "stack: $stack"
echo "tag:   $tag"

dns=`./get_dns_by_stack_name.py -t $tag $stack`
echo "dns:   $dns"

ssh -o StrictHostKeyChecking=no -i 'keys/test-keypair' "$user@$dns"

