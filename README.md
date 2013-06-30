## compute-cassandra-python

This repository is intended to be a guideline for setting up a basic working
Cassandra cluster utilizing Google Compute Engine resources.

This material was developed using Cassandra 1.2.5, Debian Wheezy images,
Python 2.7, and the Oracle&#174; Java Runtime Engine (JRE) v1.6.

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
[Community Edition](http://www.datastax.com/documentation/gettingstarted/getting_started/gettingStartedDeb_t.html)
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
[Google Cloud Platform](https://cloud.google.com/) account and have added the
Google Compute Engine service.  It also assumes you have installed
[`gcutil`](https://developers.google.com/compute/docs/gcutil/), the
command-line utility used to manage Google Compute Engine resources.  Lastly,
you will need a system with [`python`](http://www.python.org/) (at least 2.7)
installed if you would like to use the provided scripts for deploying the
example cluster.

### Java&#174; Setup

Datastax highly recommends against using the OpenJDK environment that is
available in Debian Linux.  This guide was therefore developed using the
Oracle Java Runtime Engine (JRE) 1.6.  If you intend to run the scripts
included in this guide, you will first need to download the correct version
from Oracle.  Save the file to the same computer that you will be using to
run the setup scripts used in this guide.

The scripts were developed using the `jre-6u45-linux-x64.bin` package.  You
will be able to download the same file by visiting the "previous versions"
section for [Oracle's SE Runtime Environment](http://goo.gl/TEuy0).  You
will likely need to agree to Oracle's Binary Code License Agreement
(and perhaps even create an Oracle account) before you will be able to
download the file.

Once downloaded, be sure to remember the location of the file.  You will
need to provide the full pathname to the `tools/create_cluster.py` script.

## Default (weak) Cluster Settings

Since this guide is intended as a non-production cluster, it uses a standard
machine `n1-standard-1` type and *scratch disks* only.  Production clusters
would likely need more powerful machines, persistent disks, and possibly more
nodes depending on usage.

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

API_VERSION = "v1beta15"       # GCE API version

WAIT_MAX = 10                  # max wait-iterations for startup-script, the
                               # delay between each iteration is 20 seconds

JRE6_VERSION = "jre1.6.0_45"   # path version string of extracted JRE
JRE6_INSTALL = "jre-6u45-linux-x64.bin" # basenamne of downloaded JRE file

VERBOSE = False                # eat gcutil's stdout/stderr unless True, if
                               # debugging script issues, set this to True
                               # and re-run the scripts
#############################################################################
  ```

## One-time Setup

1. Check out the repository or save and upack a ZIP file of the repository.
```
$ git clone https://github.com/GoogleCloudPlatform/compute-cassandra-python.git
$ cd compute-cassandra-python
```

1. Set up authorization.  Please make sure to specify your *Project ID* (not
the project name or number).  To find your Project ID, log into the 
[Cloud Console](https://cloud.google.com/console/) and look in the upper
left corner under your project.  Once you have your Project ID, run the
following command to authenticate:
  ```
  $ gcutil auth --project_id=YOUR_PROJECT_ID
  ```
You will be prompted to open a URL in your browser.  You may need to log in
with your Google credentials if you haven't already.  Click the "Allow access"
button.  Next, copy/paste the verification code in your terminal.  Then run
the following command to cache your Project ID for so the included scripts
can reference your Project ID:
  ```
  $ gcutil getproject --project_id=YOUR_PROJECT_ID --cache_flag_values
  ```

1. Networking firewall rules. If you want to access the cluster over its
external ephemeral IP addresses, you should consider opening up port 9160 
for the Thrift protocol and 9042 for CQL clients.  By default, internal IP 
traffic is open so no other rules should be necessary.  You can open these 
ports with the following comment (assuming you want to use the 'default' 
network):
    ```
    $ gcutil addfirewall cassandra-rule --allowed="tcp:9042,tcp:9160" --network="default" --description="Allow external Cassandra Thrift/CQL connections"
    ```

## Creating the Cluster

1. As stated above in the Java section, please make sure you have downloaded
`jre-6u45-linux-x64.bin` and saved the file locally.

1. Create the new cluster using the provided script.

    ```
    $ ./tools/create_cluster.py path/to/jre-6u45-linux-x64.bin
    ```

1. Go get a cup of tea (or other libation to the prophet
[Cassandra](http://en.wikipedia.org/wiki/Cassandra)). This will take
upwards of 10 minutes.  Assuming the script completes with no errors, you
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
    => Sleeping 60 seconds to give nodes time to join cluster
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
least two zones in that region also in the UP state (e.g. not under a
maintenance window).  In the output above, the script selects zones
`us-central1-a` and `us-central1-b` in region `us-central1`.
1. Next, the script creates 3 `n1-standard-1` instances running `debian-7`
in each zone.  The nodename is computed by concatenating the NODE_PREFIX
defined in `tools/common.py`, a dash, the zone designator, another dash,
and an incrementing integer (e.g. `cassnode-a-0`, `cassnode-a-1`, ...).
1. The script then uses the `gcutil push` feature to upload the JRE file to
each node in the cluster.
1. Now that each node in the cluster is up and running, the script then
uses some of that node information to create a customized install script
based on the included `tools/node_config_tmpl` file and saves that to
`tools/node_config_tmpl.sh`.
1. Next, the generated install script, `tools/node_config_tmpl.sh` executes
on each node in the cluster.  The install script handles updating Debian
packages, installing Cassandra, setting up the Cassandra configuration files,
and installing the JRE that was uploaded to each node.
1. The Cassandra service is started on two SEED nodes, one in each
zone.  In the example above, this was `cassnode-a-2` and `cassnode-b-1` which
were randomly chosen.  The remaining non-SEED nodes are then also brought up.
1. Finally, the script pauses for a minute to ensure all nodes have had a
chance to discover each other and exchange data via the gossip protocol.  To
verify that the Cassandra cluster is actually running, the `nodetool status`
command is run against a random node in the cluster.  Ideally, you will see
an entry for all 6 nodes in the cluster, 3 per zone.

## Destroying the cluster

There is a script that will delete all nodes with names starting with the
NODE_PREFIX.  You can use this to purge the cluster if something goes wrong
and want to start over, or if you're done with the guide and don't want to
be charged for running instances.  It will list out the matching instances
and prompt you before actually deleting the cluster.

Note that all data will be permanently deleted (recall that these instances
are only using *scratch disks*).  The script does not gracefully shutdown
the Cassandra service or otherwise check for active usage.

  ```
  $ ./tools/destroy_cluster.py
  ```

Once the cluster is down, you may also want to delete the firewall rule
that allows external Thrift/CQL communication.  You can do that with:

  ```
  $ gcutil deletefirewall cassandra-rule
  ```

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
  [cqlsh 3.0.2 | Cassandra 1.2.5 | CQL spec 3.0.0 | Thrift protocol 19.36.0]
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
  $ gcutil ssh --zone us-central1-a cassnode-a-2
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

1. Make sure that you cached your Project ID with `gcutil` as stated in the
One-time Setup section above.  The scripts assume that the Project ID has
been cached and will likely fail unless you've cached your Project ID.

1. Enable extra command-line output by toggling the VERBOSE variable to `True`
in the `tools/common.py` file. When you re-run a script with that enabled, you
will see all of the standard output and error messages from `gcutil`.

1. In order to understand what's going on with a cluster deployment with these
scripts, you will likely need to either use the web console and check the
instance's serial output or SSH into the instance and monitor log files.  In
addition to standard Linux log files, you may need to consult the Cassandra
log files, especially:
 * `/var/log/cassandra/output.log` - Cassandra log

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

### Extending this guide with Metadata startup scripts

This guide did not take advantage of a powerful GCE feature that allows a
newly created instance to execute a
[startup-script](https://developers.google.com/compute/docs/howtos/startupscript).
Rather, the scripts in this guide invoked `gcutil ssh` to execute the
post-boot `tools/node_config_tmpl.sh` node configuration script.

So a great next step would be to utilize the GCE startup script feature.
Using this feature, additional Cassandra nodes could quickly and easily be
created and automatically configured as soon as they finished booting.
This could be accomplished by,

 * Pre-download the Oracle JRE and upload it to a bucket in
   [Google Cloud Storage](https://cloud.google.com/products/cloud-storage)
   (GCS) after agreeing to the licensing terms.
 * Modify the `tools/node_configure_tmpl` script to be executed as a Metadata
   startup-script.
 * Modify the startup-script to download the Oracle JRE from the GCS bucket.
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
