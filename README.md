![status: inactive](https://img.shields.io/badge/status-inactive-red.svg)

This project is no longer actively developed or maintained.  

For more information about Cassandra on Compute Engine, refer to our [solutions page](https://cloud.google.com/solutions/cassandra/).

## compute-cassandra-python

This repository is intended to be a guideline for setting up a basic working
Cassandra cluster utilizing Google Compute Engine resources.

This material was developed using Cassandra 2.0.4, Debian-7 Wheezy images,
Python 2.7, and the Oracle&#174; Java Runtime Engine (JRE) v1.7.

## Overview

[Cassandra](http://cassandra.apache.org) is an open-source
[NoSQL](http://en.wikipedia.org/wiki/Nosql) data store.  It is designed
primarily to provide a robust fault tolerant distributed and decentralized
data store that is highly durable and scalable.  It provides the Cassandra
Query Language (CQL) tool which is SQL-like language for querying a
Cassandra cluster.  Although CQL has many similarities to SQL, there are
some fundamental differences.  CQL adheres to the Cassandra data model and
architecture so some operations and clauses (such as joins and subclauses) are
not available.  To learn much more about Cassandra and CQL, you can also
reference the material published by Datastax on their
[resources page](http://www.datastax.com/resources).  This guide was developed
using Datastax's
[Community Edition](http://www.datastax.com/documentation/gettingstarted/index.html?pagename=docs&version=quick_start&file=quickstart#getting_started/gettingStartedDeb_t.html)
for Debian.

Google Compute Engine (GCE) is a very good match for Cassandra users.  Some of
GCE's features that make it a great fit are:

* Distinct geographic regions within Europe and North America
* Separate zones within a region to provide fault-tolerance within a region
* Ability to scale up/down by adding and removing compute resources
* A variety of compute machine types for standard or high memory/CPU needs
* A Metadata service to store common configuration information or bring up
  instances with a custom startup script
* Persistent disks to preserve and share data between restarts and/or machines

There is a lot to consider when getting ready to deploy a Cassandra cluster in
production.  This guide is intended to provide a starting point to learn more
about GCE and Cassandra by deploying a small cluster in a single region across
multiple zones.  It does not address issues such as security, managing a
production cluster, or performance tuning.  The documentation provided by
Datastax goes into much more detail about planning production Cassandra
clusters.

### Prerequisites

This guide assumes you have registered a
[Google Cloud Platform](https://cloud.google.com/) account and have enabled
both the Google Compute Engine and Google Cloud Storage services.  It also
assumes you have installed the `gcutil` and `gsutil` command-line utilities
bundled with the [Google Cloud SDK](https://developers.google.com/cloud/sdk/).
Lastly, you will need a system with [`python`](http://www.python.org/) (at
least 2.7) installed if you would like to use the provided scripts for
deploying the example cluster.

### Java&#174;

Datastax highly recommends against using the OpenJDK environment that is
available in Debian Linux.  This guide was therefore developed using the
Oracle Java Runtime Engine (JRE) 1.7.  If you intend to run the scripts
included in this guide, you will first need to download the correct version
from Oracle.

The scripts were developed using the `jre-7u51-linux-x64.tar.gz` package.
You will likely need to agree to Oracle's Binary Code License Agreement
(and perhaps even create an Oracle account) before you will be able to
download the file.  Once downloaded, be sure to remember the location of the
file.

## Default (weak) Cluster Settings

Since this guide is intended as a non-production cluster, it uses a standard
machine `n1-standard-1` type.  Production clusters would likely need more
powerful machines, additional persistent disks, and possibly more nodes
depending on usage.

The default settings for this guide live in `tools/common.py`.  You can make
changes to the number of nodes in the cluster, machine type, and
nodename prefix by editing these default global variables.  The relevant
section of the file looks like:
  ```
# Global configuration variables
NODES_PER_ZONE = 3             # define number of nodes to create in each
                               # zone.  GCE typically has two zones per region
                               # so this would create a 6 node C* cluster

MAX_NODES = 9                  # prevents excessive number of nodes to be
                               # created.  if NODES_PER_ZONE * number_of_zones
                               # is > than MAX_NODES, the script will raise an
                               # error and exit.  GCE typically has 2 zones per
                               # region (e.g. NODES_PER_ZONE * 2 < MAX_NODES)

NODE_PREFIX = "cassnode"       # all nodenames begin with this string.  This is
                               # how the scripts determine what nodes belong to
                               # the C* cluster.

MACHINE_TYPE = "n1-standard-1" # the machine type used for all cluster nodes

API_VERSION = "v1"             # GCE API version

WAIT_MAX = 10                  # max wait-iterations for startup-script, the
                               # delay between each iteration is 20 seconds

SCOPES = "userinfo-email,compute-rw,storage-full" # Scopes set to match same    
                               # default scopes as Cloud Console                
                                                                                
GCE_USERNAME = ""              # Use this to override the local environment.    
                               # This username must exist on the newly created  
                               # GCE instances in order to fetch the JRE        
                               # install file from GCS                          
                                                                                
GCS_BUCKET = "mybucket"        # Specify bucket housing JRE7 install file       
JRE7_INSTALL = "jre-7u51-linux-x64.tar.gz" # Basenamne of downloaded JRE file   
JRE7_VERSION = "jre1.7.0_51"   # Path version string of extracted JRE           
                                                                                
VERBOSE = False                # eat gcutil's stdout/stderr unless True, if
                               # debugging script issues, set this to True
                               # and re-run the scripts
#############################################################################
  ```

## One-time Setup

1. Check out this repository or save and upack a ZIP file of this repository.

  ```
  $ git clone https://github.com/GoogleCloudPlatform/compute-cassandra-python.git
  $ cd compute-cassandra-python
  ```

1. Set up authorization. After downloading the Google Cloud SDK, unpack it and
execute the included `install.sh` script. You can set up authorization and
setting the default Project ID with:

  ```
  $ gcloud auth login
  ```

Your browser will either load up a permission authorization page or a URL will
be generated that you need to load in a browser. You will need to log in
with your Google credentials if you haven't already and click the "Allow
access" button. You may need to copy/paste the verification code in your
terminal. You will also be prompted to enter your default Project ID.

1. Networking firewall rules. If you want to access the cluster over its
external ephemeral IP addresses, you should consider opening up port 9160 
for the Thrift protocol and 9042 for CQL clients.  By default, internal IP 
traffic is open so no other rules should be necessary.  You can open these 
ports with the following comment (assuming you want to use the 'default' 
network):

  ```
  $ gcutil addfirewall cassandra-rule --allowed="tcp:9042,tcp:9160" --network="default" --description="Allow external Cassandra Thrift/CQL connections"
  ```

1. Upload the JRE install file to a Google Cloud Storage bucket. After you
have downloaded the JRE 1.7 install file, you will need to upload it to a
Google Cloud Storage bucket. Make sure to update `tools/common.py`  to specify
your bucket name and adjust the JRE7 variables if needed. The `gsutil` utility
is included in the Cloud SDK. Create a bucket and upload the JRE with:

  ```
  $ gsutil mb gs://mybucket
  $ gsutil cp jre-7u51-linu-x64.tar.gz gs://mybucket
  ```

## Creating the Cluster

1. Create the new cluster using the provided script.

    ```
    $ ./tools/create_cluster.py
    ```

1. Go get a cup of tea (or other libation to the prophet
[Cassandra](http://en.wikipedia.org/wiki/Cassandra)). This will take
around 10 minutes.  Assuming the script completes with no errors, you
will see something similar to:

    ```
    => Finding suitable region, selecting zones: ['us-central1-a', 'us-central1-b']
    => Creating 6 'debian-7' 'n1-standard-1' nodes
    --> Node cassnode-a-0 created
    --> Node cassnode-a-1 created
    --> Node cassnode-a-2 created
    --> Node cassnode-b-0 created
    --> Node cassnode-b-1 created
    --> Node cassnode-b-2 created
    => Uploading JRE install file to each cluster node: . . . . . . done.
    => Uploading and running configure script on nodes: . . . . . . done.
    => Starting cassandra cluster on SEED nodes
    --> Attempting to start cassandra on node cassnode-b-1 UP
    --> Attempting to start cassandra on node cassnode-a-2 UP
    => Starting cassandra cluster non-SEED nodes
    --> Attempting to start cassandra on node cassnode-b-0 UP
    --> Attempting to start cassandra on node cassnode-b-2 UP
    --> Attempting to start cassandra on node cassnode-a-1 UP
    --> Attempting to start cassandra on node cassnode-a-0 UP
    => Cassandra cluster is up and running on all nodes
    => Sleeping 30 seconds to give nodes time to join cluster
    => Output from node cassnode-b-1 and 'nodetool status'
    Datacenter: ZONE1
    =================
    Status=Up/Down
    |/ State=Normal/Leaving/Joining/Moving
    --  Address         Load       Tokens   Owns (effective)  Host ID                               Rack
    UN  10.240.101.202  97.38 KB   256      15.6%             557db8f8-5fc1-4575-bc80-d4f9c855690a  RAC1
    UN  10.240.160.88   97.38 KB   256      17.9%             45c00bb9-b4da-45de-86fc-97f020998336  RAC1
    UN  10.240.155.155  103.42 KB  256      16.9%             bbc373ed-0259-46c1-a3b3-177d2383526a  RAC1
    Datacenter: ZONE2
    =================
    Status=Up/Down
    |/ State=Normal/Leaving/Joining/Moving
    --  Address         Load       Tokens   Owns (effective)  Host ID                               Rack
    UN  10.240.115.159  97.2 KB    256      15.8%             04cec381-00f1-4e0b-8be4-82c062743bf7  RAC1
    UN  10.240.191.62   83.37 KB   256      17.5%             2ea44ff3-8b18-4c22-a0a5-8836ffaf9362  RAC1
    UN  10.240.116.10   98.77 KB   256      16.3%             5ecd834e-a253-4ec7-b9sb-d46efb655f02  RAC1
    ```

### So what just happened?

1. The first thing the script does is to find a US-based region that has at
least two zones in that region also in the UP state. In the output above, the
script selects zones `us-central1-a` and `us-central1-b` in region
`us-central1`.
1. Next, the script creates 3 `n1-standard-1` instances running `debian-7`
in each zone.  The nodename is computed by concatenating the NODE_PREFIX
defined in `tools/common.py`, a dash, the zone designator, another dash,
and an incrementing integer (e.g. `cassnode-a-0`, `cassnode-a-1`, ...).
1. Now that each node in the cluster is up and running, the script then
uses some of that node information to create a customized install script
based on the included `tools/node_config_tmpl` file and saves that to
`tools/node_config_tmpl.sh`.
1. Next, the generated install script, `tools/node_config_tmpl.sh` executes
on each node in the cluster.  The install script handles updating Debian
packages, installing Cassandra, setting up the Cassandra configuration files,
fetching the JRE install file from Google Cloud Storage and installing it.
1. The Cassandra service is started on two SEED nodes, one in each
zone.  In the example above, this was `cassnode-a-2` and `cassnode-b-1` which
were randomly chosen.  The remaining non-SEED nodes are then also brought up.
1. Finally, the script pauses to ensure all nodes have had a chance to
discover each other and exchange data via the gossip protocol.  To verify that
the Cassandra cluster is actually running, the `nodetool status` command is
run against a random node in the cluster.  Ideally, you will see an entry for
all 6 nodes in the cluster, 3 per zone.

## Destroying the cluster

There is a script that will delete all nodes with names starting with the
NODE_PREFIX.  You can use this to purge the cluster if something goes wrong
and you want to start over, or if you're done with the guide and don't want to
be charged for running instances.  It will list out the matching instances
and prompt you before actually deleting the cluster.

Note that all data will be permanently deleted. The script intentionally
deletes the persistent disks leaving nothing behind. The script also does not
gracefully shutdown the Cassandra service or otherwise check for active usage.
  ```
  $ ./tools/destroy_cluster.py
  ```

Once the cluster is down, you may also want to delete the firewall rule
that allows external Thrift/CQL communication.  You can do that with:
  ```
  $ gcutil deletefirewall cassandra-rule
  ```

### Keeping your disks

Since the cluster uses persistent disks, you may just want to terminate the
running instances without deleting the persistent disks. Then at a later time,
you can create new instances and re-use the same disks. This is a great cost
savings technique if you'd like to tinker with the cluster once in a while
over an extended time period without having to rebuild it from scratch each
time. However, there are no included scripts to support this technique but
you can use either `gcutil` or the Cloud Console to terminate instances
without deleting their disks.

## CQL: Getting Started

It's beyond the scope of this guide to create a real Cassandra schema,
but here are a few commands that will demonstrate that your cluster is 
functional.

Start by SSH'ing into one of your cluster nodes, for example:

  ```
  $ gcutil ssh --zone us-central1-a cassnode-a-2
  ```

Once logged in, fire up the included python-based CQL interpreter and create
a demo keyspace.  In the example below, a keyspace is created with the
`NetworkTopologyStrategy` class with a data replication factor of 2 for each
zone.  A few informational commands show some the keyspace's properties and
a snippet of the token distribution.  For instance,

  ```
  $ cqlsh
  Connected to GCECassandraCluster at localhost:9160.
  [cqlsh 4.1.0 | Cassandra 2.0.4 | CQL spec 3.1.1 | Thrift protocol 19.39.0]
  Use HELP for help.
  cqlsh> create keyspace demo with replication =
     ... {'class': 'NetworkTopologyStrategy', 'ZONE1': 2, 'ZONE2': 2};
  cqlsh> describe keyspace demo;

  CREATE KEYSPACE demo WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'ZONE2': '2',
    'ZONE1': '2'
  };
  cqlsh> use demo;
  cqlsh:demo> describe cluster;

  Cluster: GCECassandraCluster
  Partitioner: Murmur3Partitioner
  Snitch: PropertyFileSnitch

  Range ownership:
                     8312226922118728182  [10.240.169.136, 10.240.205.20, 10.240.221.31, 10.240.194.246]
                     2398506559789756293  [10.240.169.136, 10.240.194.246, 10.240.221.31, 10.240.205.20]
                    -6687625507946491144  [10.240.221.31, 10.240.89.53, 10.240.205.228, 10.240.205.20]
                     -890208907273719943  [10.240.205.20, 10.240.89.53, 10.240.194.246, 10.240.169.136]
  [snip]

  ```

Next, you can create a few tables and insert some sample data.

  ```
  cqlsh:demo> create table characters (
          ...   name text primary key,
          ...   type text,
          ...   description text,
          ...   appearances set<text>
          ... );
  cqlsh:demo> insert into characters (name,type,description,appearances) values
          ... ('Bilbo Baggins', 'Hobbit', 'The main character in "The Hobbit"',
          ... {'The Hobbit', 'The Fellowship of the Ring',
          ... 'The Return of the King', 'Unfinished Tales'});
  cqlsh:demo> insert into characters (name,type,description,appearances) values
          ... ('Frodo Baggins', 'Hobbit', 'A main character in the LotR',
          ... {'The Fellowship of the Ring', 'The Two Towers',
          ... 'The Return of the King', 'The Silmarillion',
          ... 'Unfinished Tales'});
  cqlsh:demo> insert into characters (name,type,description,appearances) values
          ... ('Gimli', 'Dwarf', 'A main character in the LotR',
          ... {'The Fellowship of the Ring', 'The Two Towers',
          ... 'The Return of the King', 'Unfinished Tales'});
  cqlsh:demo> insert into characters (name,type,description,appearances) values
          ... ('Legolas', 'Elf', 'A main character in the LotR',
          ... {'The Fellowship of the Ring', 'The Two Towers',
          ... 'The Return of the King'});

  cqlsh:demo> select name, appearances from characters where type = 'Hobbit';
  Bad Request: No indexed columns present in by-columns clause with Equal operator

  cqlsh:demo> create index type_idx on characters(type);

  cqlsh:demo> select name, appearances from characters where type = 'Hobbit';
   name          | appearances
  ---------------+----------------------------------------------------------------------------------------------------------
   Bilbo Baggins |                       {The Fellowship of the Ring, The Hobbit, The Return of the King, Unfinished Tales}
   Frodo Baggins | {The Fellowship of the Ring, The Return of the King, The Silmarillion, The Two Towers, Unfinished Tales}
  cqlsh:demo> quit;
  ```

Now you can use `nodetool` to take a look at a how the data is distributed.
Note that the nodenames were manually added to the output as comments to
better illustrate the data distribution across zones.  Recall that in these
examples, the replication factor was set to 2 for each zone implying that
data exists in two nodes in each zone.

  ```
  $ gcutil ssh --zone us-central1-a cassnode-b-1
  $ nodetool getendpoints demo characters name
  10.240.101.202  # cassnode-a-0
  10.240.155.155  # cassnode-a-2
  10.240.191.62   # cassnode-b-1
  10.240.116.10   # cassnode-b-2
  $ nodetool getendpoints demo characters appearances
  10.240.101.202  # cassnode-a-0
  10.240.160.88   # cassnode-a-1
  10.240.115.159  # cassnode-b-0
  10.240.191.62   # cassnode-b-1
  ```
## Debugging / Troubleshooting

1. Enable extra command-line output by toggling the VERBOSE variable to `True`
in the `tools/common.py` file. When you re-run a script with that enabled, you
will see all of the standard output and error messages from `gcutil` and
the instance commands.

1. In order to understand what's going on with a cluster deployment with these
scripts, you will likely need to either use the web console and check the
instance's serial output or SSH into the instance and monitor log files.  In
addition to standard Linux log files, you may need to consult the Cassandra
log files, especially:
 * `/var/log/cassandra/system.log` - Cassandra log

1. Ensure that your firewall rule is enabled so that the Cassandra nodes
are accessible by both Thrift and CQL protocols.

1. If you are having problems with Cassandra, then you can look for help on
mailing lists, forums, Stack Overflow, or IRC.  In other words, if the nodes
have all been  created and Cassandra started successfully (as verfied
with the `nodetool status` output) but you are not able to execute CQL
commands properly, then you'll likely need more detailed Cassandra help.

## Conclusion

This guide was meant to give you the basic tools to bring up a small
Cassandra cluster for further education and evaluation.  The scripts should
be fairly straightforward to understand or tweak for your own experiments.

In summary, this guide showed that Google's Compute Engine is a good fit
for Cassandra deployments by:

* Taking advantage of mutliple zones within a region
* The (under the hood) capabilities of `gcutil` to easily manage your instances
* The ease with which a Cassandra cluster can be created and destroyed

### Extending this guide

This guide did not take advantage of a powerful GCE feature that allows a
newly created instance to execute a
[startup-script](https://developers.google.com/compute/docs/howtos/startupscript).
Rather, the scripts in this guide invoked `gcutil ssh` to execute the
post-boot `tools/node_config_tmpl.sh` node configuration script.

So a great next step would be to utilize the GCE startup script feature.
Using this feature, additional Cassandra nodes could quickly and easily be
created and automatically configured as soon as they finished booting.
This could be accomplished by,

 * Updating the `tools/node_configure_tmpl` script to be executed as a
   Metadata startup-script.
 * As nodes are created/destroyed, use the
   [Metadata service](https://developers.google.com/compute/docs/metadata) to
   store SEED IP addresses and a newly computed PropertyFileSnitch file
   contents.
 * Lastly, the startup-script could pull down the updated PropertyFileSnitch
   and fire up the Cassandra service.  New nodes would automatically join the
   Cassandra cluster via the gossip protocol and begin replicating data.

## Contributing changes

* See [CONTRIB.md](https://github.com/GoogleCloudPlatform/compute-cassandra-python/blob/master/CONTRIB.md)

## Licensing

* See [LICENSE](https://github.com/GoogleCloudPlatform/compute-cassandra-python/blob/master/LICENSE)

## Credits

* Oracle and Java are registered trademarks of Oracle and/or its affiliates.
  Other names may be trademarks of their respective owners
