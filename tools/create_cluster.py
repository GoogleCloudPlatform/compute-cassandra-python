#!/usr/bin/env    python
# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Script to start up a demo Cassandra cluster on Google Compute Engine."""

import os
import time

# Read in global config variables
mydir = os.path.dirname(os.path.realpath(__file__))
common = mydir + os.path.sep + "common.py"
execfile(common, globals())


# Find a US region with at least two UP zones.
def find_zones():
    """Find a US region with at least two UP zones."""
    print("=> Finding suitable region, selecting zones:"),
    regions = subprocess.check_output(["gcutil", "--service_version",
            API_VERSION, "--format", "names", "listregions", "--filter",
            "name eq 'us.*'"], stderr=NULL).split('\n')[0:-1]
    for region in regions:
        zones = subprocess.check_output(["gcutil", "--service_version",
                API_VERSION, "--format", "names", "listzones", "--filter",
                "status eq UP", "--filter", "name eq '%s.*'" % region],
                stderr=NULL).split('\n')[0:-1]
        if len(zones) > 1:
            print(zones)
            return zones
    raise BE("Error: No suitable US regions found with 2+ zones")

# Create all nodes synchronously
def create_nodes(zones):
    """Create all nodes synchronously."""
    print("=> Creating %d '%s' '%s' nodes" % (NODES_PER_ZONE*len(zones),
            IMAGE, MACHINE_TYPE))
    script = "startup-script:" + os.path.dirname(os.path.realpath(__file__))
    script += os.path.sep + "startup_script.sh"

    imgPath = get_image_path()
    if imgPath is None:
        raise BE("Error: No matching IMAGE for '%s'" % IMAGE)
    img = "https://www.googleapis.com/compute/%s/%s" % (API_VERSION, imgPath)

    for zone in zones:
        for i in range(NODES_PER_ZONE):
            nodename = "%s-%s-%d" % (NODE_PREFIX, zone[-1:], i)

            r = subprocess.call(["gcutil",
                    "--service_version=%s" % API_VERSION,
                    "addinstance", nodename, "--zone=%s" % zone,
                    "--machine_type=%s" % MACHINE_TYPE, "--network=default",
                    "--external_ip_address=ephemeral",
                    "--image=%s" % img, "--persistent_boot_disk=false",
                    "--synchronous_mode", "--metadata_from_file=%s" % script],
                    stdout=NULL, stderr=NULL)
            if r != 0:
                raise BE("Error: could not create node %s" % nodename)
            print("--> Node %s created" % nodename)


# Update the SEED list on each node.
def add_seeds(cluster):
    """Update the SEED list on each node."""
    print("=> Adding SEED nodes to cassandra configs")
    # Select first node from each zone as a SEED node.
    seed_ips = []
    seed_data = []
    for z in cluster.keys():
        seed_node = cluster[z][0]
        seed_ips.append(seed_node['ip'])
        seed_data.append(seed_node)

    # Update each node's cassandra.yaml file
    for z in cluster.keys():
        for node in cluster[z]:
            sed = "sudo sed -i 's|seeds: \\\"127.0.0.1\\\""
            sed += "|seeds: 127.0.0.1,%s|'" % ",".join(seed_ips)
            sed += " /etc/cassandra/cassandra.yaml"
            _ = subprocess.call(["gcutil",
                    "--service_version=%s" % API_VERSION, "ssh",
                    "--zone=%s" % z, node['name'], sed],
                    stdout=NULL, stderr=NULL)
    return seed_data


# Write the PropertyFileSnitch on each node.
def add_snitch(cluster):
    """Write the PropertyFileSnitch on each node."""
    print("=> Updating Snitch file on nodes")
    # Craft the PropertyFileSnitch file
    i=1
    contents = [
        "# Auto-generated topology snitch during cluster turn-up", "#",
        "# Cassandra node private IP=Datacenter:Rack", "#", ""
    ]
    for z in cluster.keys():
        contents.append("# Zone \"%s\" => ZONE%d" % (z, i))
        for node in cluster[z]:
            contents.append("%s=ZONE%d:RAC1" % (node['ip'], i))
        i+=1
        contents.append("")
    contents.append("# default for unknown hosts")
    contents.append("default=ZONE1:RAC1")
    topo_file = "sudo bash -c"
    topo_file += " 'cat <<EOF>/etc/cassandra/cassandra-topology.properties\n"
    topo_file += "\n".join(contents)
    topo_file += "\nEOF'\n"
 
    for z in cluster.keys():
        for node in cluster[z]:
            _ = subprocess.call(["gcutil",
                    "--service_version=%s" % API_VERSION, "ssh",
                    "--zone=%s" % z, node['name'], topo_file],
                    stdout=NULL, stderr=NULL)


# Check to make sure startup-script completion file exists.
def check_script_complete(cluster):
    """Check to make sure startup-script completion file exists."""
    print("=> Ensuring startup scripts are complete")
    num_nodes = 0
    for z in cluster.keys():
        num_nodes += len(cluster[z])

    nodes_done = []
    tries=0
    secs = 20
    max_tries = WAIT_MAX * 60 / secs
    while tries < max_tries:
        for z in cluster.keys():
            for node in cluster[z]:
                if node['name'] not in nodes_done:
                    done = subprocess.call(["gcutil",
                            "--service_version=%s" % API_VERSION, "ssh",
                            "--zone=%s" % z, node['name'],
                            "ls /tmp/cassandra_startup_script_complete"],
                            stdout=NULL, stderr=NULL)
                    if done == 0:
                        nodes_done.append(node['name'])
                        print("--> Completion file found on %s" % node['name'])
                    else:
                        print("*** warning: startup script not found on node"),
                        print("%s, sleeping %d secs" % (node['name'], secs))
                        time.sleep(secs)
        tries += 1
    if len(nodes_done) != num_nodes:
        raise BE("Error: Cluster could not be configured correctly")


# Cleanly start up Cassandra on specified node
def node_start_cassandra(zone, nodename):
    """Cleanly start up Cassandra on specified node"""
    status = "notok"
    tries = 0
    print("--> Attempting to start cassandra on node %s" % nodename),
    while status != "ok" and tries < 5:
        r = subprocess.call(["gcutil", "--service_version=%s" % API_VERSION,
                "ssh", "--zone=%s" % zone, nodename,
                "sudo service cassandra stop"], stdout=NULL, stderr=NULL)
        r = subprocess.call(["gcutil", "--service_version=%s" % API_VERSION,
                "ssh", "--zone=%s" % zone, nodename,
                "sudo rm /var/run/cassandra.pid"], stdout=NULL, stderr=NULL)
        r = subprocess.call(["gcutil", "--service_version=%s" % API_VERSION,
                "ssh", "--zone=%s" % zone, nodename,
                "sudo rm -rf /var/lib/cassandra/*"], stdout=NULL, stderr=NULL)
        r = subprocess.call(["gcutil", "--service_version=%s" % API_VERSION,
                "ssh", "--zone=%s" % zone,nodename,
                "sudo service cassandra start"], stdout=NULL, stderr=NULL)
        r = subprocess.call(["gcutil", "--service_version=%s" % API_VERSION,
                "ssh", "--zone=%s" % zone,nodename,
                "ls /var/run/cassandra.pid"], stdout=NULL, stderr=NULL)
        if r == 0:
            status = "ok"
            print("UP")
            break
        tries += 1
        print("."),
    if status == "notok":
        print("FAILED")
        raise BE("Error: cassandra failing to start on node %s" % nodename)


# Bring up cassandra on cluster nodes, SEEDs first
def start_cluster(seed_data, cluster):
    """Bring up cassandra on cluster nodes, SEEDs first"""
    # Start SEED nodes first.
    print("=> Starting cassandra cluster SEED nodes")
    started_nodes = []
    for node in seed_data:
        node_start_cassandra(node['zone'], node['name'])
        started_nodes.append(node['name'])

    # Start remaining non-seed nodes.
    print("=> Starting cassandra cluster non-SEED nodes")
    for z in cluster.keys():
        for node in cluster[z]:
            if node['name'] not in started_nodes:
                node_start_cassandra(z, node['name'])


# Display cluster status by running 'nodetool status' on a node
def verify_cluster(cluster):
    """Display cluster status by running 'nodetool status' on a node"""
    keys = cluster.keys()
    zone = keys[0]
    nodename = cluster[zone][0]['name']
    status = subprocess.check_output(["gcutil",
            "--service_version=%s" % API_VERSION, "ssh",
            "--zone=%s" % zone, nodename, "nodetool status"], stderr=NULL)
    print("=> Output from node %s and 'nodetool status'" % nodename)
    print(status)


def main():
    # Find a suitable US region with more than a single UP zone.
    zones = find_zones()
    # Make sure we don't exceed MAX_NODES.
    if NODES_PER_ZONE * len(zones) > MAX_NODES:
        raise BE("Error: MAX_NODES exceeded. Too many zones: %s" % str(zones))

    # Create the nodes and poll for startup scripts to complete.
    create_nodes(zones)
    cluster = get_cluster()
    check_script_complete(cluster)

    # Identify SEED nodes and update config files.
    seed_data = add_seeds(cluster)
    add_snitch(cluster)

    # Bring up the cluster and give it a minute for nodes to join.
    start_cluster(seed_data, cluster)
    print("=> Cassandra cluster is up and running on all nodes")
    print("=> Sleeping 60 seconds to give nodes time to join cluster")
    time.sleep(60)

    # Run nodetool status on a node and display output.
    verify_cluster(cluster)


if __name__ == '__main__':
    main()
