#!/usr/bin/env bash

if [ "$#" -eq 1 ]
then
    node=$1
else
    echo "Description:"
    echo "   runs mongo on the given db0"
    echo ""
    echo "Usage:"
    echo "   $0 node-name"
    exit 1
fi

dns=`./get_dns_by_node_name.py $node`
echo "dns:   $dns"

mongo "$dns"

