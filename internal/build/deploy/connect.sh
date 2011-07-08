#!/usr/bin/env bash

if [ "$#" -eq 1 ]
then
    user="ubuntu"
    stack=$1
    echo "defaulting to user $user"
elif [ "$#" -eq 2 ]
then
    user=$1
    stack=$2
else
    echo "Description:"
    echo "   ssh's into an active AWS instance denoted by the given stack-name"
    echo ""
    echo "Usage:"
    echo "   $0 stack-name OR $0 user stack-name"
    exit 1
fi

echo "user:  $user"
echo "stack: $stack"

dns=`./get_dns_by_stack_name.py $stack`
echo "dns:   $dns"

ssh -i 'keys/test-keypair' "$user@$dns"

