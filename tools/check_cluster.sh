#!/bin/sh

for zone in a b
do
  for node in 0 1 2
  do
    echo "****************************************************"
    echo "zone=us-central1-$zone, node=cassnode-$zone-$node"
    z=us-central1-$zone
    n=cassnode-$zone-$node
    #gcutil ssh --zone=$z $n 'grep seeds /etc/cassandra/cassandra.yaml'
    #gcutil ssh --zone=$z $n 'java -version 2>&1'
    #gcutil ssh --zone=$z $n 'sudo service cassandra start'
    gcutil ssh --zone=$z $n '/sbin/ifconfig eth0 | grep inet'
  done
done
