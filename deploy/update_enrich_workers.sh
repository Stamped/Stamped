
stack="bowser"

for ((i = 5; i < 10; ++i)); do
    node="$stack.work-enrich$i"
    echo "Updating node: $node"
    dns=`./get_dns_by_node_name.py $node`
    ssh -o StrictHostKeyChecking=no -i 'keys/test-keypair' "ubuntu@$dns" -x "cd /stamped/stamped && sudo git pull && sudo restart celeryd"
done
