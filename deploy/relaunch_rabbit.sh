
stack=$1

node="$stack.mon0"
echo "Relaunching rabbitmq on node: $node"
dns=`./get_dns_by_node_name.py $node`
ssh -o StrictHostKeyChecking=no -i 'keys/test-keypair' "ubuntu@$dns" -x sudo restart rabbitmq-server

for ((i = 5; i < 10; ++i)); do
    node="$stack.work-enrich$i"
    echo "Relaunching celeryd on node: $node"
    dns=`./get_dns_by_node_name.py $node`
    ssh -o StrictHostKeyChecking=no -i 'keys/test-keypair' "ubuntu@$dns" -x sudo restart celeryd
done

for ((i = 0; i < 4; ++i)); do
    node="$stack.work-api$i"
    echo "Relaunching celeryd on node: $node"
    dns=`./get_dns_by_node_name.py $node`
    ssh -o StrictHostKeyChecking=no -i 'keys/test-keypair' "ubuntu@$dns" -x sudo restart celeryd
done

