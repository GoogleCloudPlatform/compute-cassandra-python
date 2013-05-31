echo 'deb http://debian.datastax.com/community stable main' >> /etc/apt/sources.list
curl -sL http://debian.datastax.com/debian/repo_key | /usr/bin/apt-key add - >/dev/null
apt-get -y -qq update
apt-get -y -qq upgrade
apt-get -y -qq install dsc12
service cassandra stop
rm -rf /var/lib/cassandra/*
apt-get -y -qq install icedtea-7-plugin openjdk-7-jdk openjdk-7-jre openjdk-7-jre-headless
update-java-alternatives -s java-1.7.0-openjdk-amd64

CONF=/etc/cassandra/cassandra.yaml
intip=$(ifconfig eth0 | grep "inet addr:" | awk '{print $2}' | cut -d: -f2)

sed -i "s|^cluster_name: 'Test Cluster'$|cluster_name: 'GCECassandraCluster'|" $CONF
sed -i "s|^listen_address: localhost$|listen_address: ${intip}|" $CONF
sed -i "s|^rpc_address: localhost$|rpc_address: 0.0.0.0|" $CONF
sed -i "s|^# num_tokens: 256$|num_tokens: 256|" $CONF
sed -i "s|^endpoint_snitch: SimpleSnitch$|endpoint_snitch: PropertyFileSnitch|" $CONF
touch /tmp/cassandra_startup_script_complete
