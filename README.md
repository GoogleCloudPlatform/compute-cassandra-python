## compute-cassandra-python

This repository is intended to be a guideline for setting up a basic working
Cassandra cluster utilizing Google Compute Engine resources.

This material was developed using Cassandra 1.2.5, Debian Wheezy images,
Python 2.7, and the OpenJDK 7 JRE (see Java below) available through the
official Debian repository.

## Overview

[Cassandra](http://cassandra.apache.org) is an open-source
[NoSQL](http://en.wikipedia.org/wiki/Nosql) data store.  It is designed
primarily to provide a robust fault tolerant distributed and decentralized
data store that is highly durable and scalable.  It provides a SQL-like
interface but is *not* equivalent with a traditional relational,
ACID-compliant database like MySQL or PostgreSQL.  To learn much more about
Cassandra, you can also reference the material published by Datastax on their
[resources page](http://www.datastax.com/resources).  This guide was developed
using Datastax's [Community Edition](http://www.datastax.com/docs/quick_start/cassandra_quickstart) for Debian.


Google Compute Engine (GCE) is a very good match for Cassandra users.  Some of
GCE's features that make it a great fit are:

* Distinct geographic regions within Europe and North America
* Separate zones within a region to provide fault-tolerance within a region
* Ability to scale up/down be adding and removing compute resources
* A variety of compute machine types for standard or high memory/CPU needs
* Bring up instances with a custom startup script
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

### A note about Java

This guide intentionally uses OpenJDK 7.  At first glance, just about all
documentation existing today advises that Cassandra 1.x be run using a
proprietary JVM, at version 1.6.  However, after doing a bit more
[digging](http://comments.gmane.org/gmane.comp.db.cassandra.devel/7504), the
development community is pushing for OpenJDK 7 for Cassandra 2.x.  Other
post by committers have suggested trying OpenJDK 7 and reporting bugs.  Since
this guide is not intended to be a production deployment guide, it made
sense to further the cause.

If readers do wish to use an alternate JVM with this guide, the included
scripts can fairly easily be tweaked (e.g. minor edits to
`tools/startup_script.sh` and `tools/create_cluster.py`).

## Default (weak) Cluster Settings

Since this guide is intended as a non-production cluster, it uses a standard
machine `n1-standard-1` type and *scratch disks* only.  Production clusters
would probably use more powerful machines, persistent disks, and possibly more
nodes depending on usage.

The default settings for this guide live in `tools/common.py`.  You can make
changes to the number of nodes in the cluster, machine type, image, and
nodename prefix by editing these default global variables.

## One-time Setup

1. Check out the repository or save and upack a ZIP file of the repository.
```
$ git clone https://github.com/GoogleCloudPlatform/compute-cassandra-python.git
$ cd compute-cassandra-python
```

1. Set up authorization.  Please make sure to specify your *Project ID* (and
not the project name or number).  Your Project ID can be found in the
[API Console](https://code.google.com/apis/console/) dashboard.
```
$ cd compute-cassandra-python
$ ./tools/auth.py <project_id>
```
You will be prompted to open a URL in your browser.  You may need to log in
with your Google credentials if you haven't already.  Click the "Allow access"
button.  Next copy/paste the verification code in your terminal.  This will
cache authorization information into your `$HOME/.gcutil_auth` file.

1. Networking firewall rules. If you want to access the cluster over its
external ephemeral IP's, you should consider opening up port 9160 for the
Thrift protocol and 9042 for CQL clients.  By default, internal IP traffic
is open so no other rules should be necessary.  You can open these ports with
the following:

    ```
    $ ./tools/firewall.py open
    ```

## Creating the Cluster

1. Create the new cluster using the provided script.

    ```
    $ ./tools/create_cluster.py
    ```

1. Go get a cup of tea (or other libation to
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
    => Ensuring startup scripts are complete
    *** warning: startup script not complete on node cassnode-b-2, sleeping 20 seconds
    *** warning: startup script not complete on node cassnode-b-1, sleeping 20 seconds
    --> Completion file exists on node cassnode-b-0
    --> Completion file exists on node cassnode-a-0
    *** warning: startup script not complete on node cassnode-a-2, sleeping 20 seconds
    --> Completion file exists on node cassnode-a-1
    *** warning: startup script not complete on node cassnode-b-2, sleeping 20 seconds
    --> Completion file exists on node cassnode-b-1
    *** warning: startup script not complete on node cassnode-a-2, sleeping 20 seconds
    *** warning: startup script not complete on node cassnode-b-2, sleeping 20 seconds
    *** warning: startup script not complete on node cassnode-a-2, sleeping 20 seconds
    --> Completion file exists on node cassnode-b-2
    *** warning: startup script not complete on node cassnode-a-2, sleeping 20 seconds
    *** warning: startup script not complete on node cassnode-a-2, sleeping 20 seconds
    *** warning: startup script not complete on node cassnode-a-2, sleeping 20 seconds
    --> Completion file exists on node cassnode-a-2
    => Adding SEED nodes to cassandra configs
    => Updating Snitch file on nodes
    => Starting cassandra cluster SEED nodes
    --> Attempting to start cassandra on node cassnode-b-2 UP
    --> Attempting to start cassandra on node cassnode-a-0 UP
    => Starting cassandra cluster non-SEED nodes
    --> Attempting to start cassandra on node cassnode-b-1 UP
    --> Attempting to start cassandra on node cassnode-b-0 UP
    --> Attempting to start cassandra on node cassnode-a-2 UP
    --> Attempting to start cassandra on node cassnode-a-1 UP
    => Cassandra cluster is up and running on all nodes
    => Sleeping 60 seconds to give nodes time to join cluster
    => Output from node cassnode-b-2 and 'nodetool status'
    Datacenter: ZONE1
    =================
    Status=Up/Down
    |/ State=Normal/Leaving/Joining/Moving
    --  Address         Load       Tokens  Owns (effective)  Host ID                               Rack
    UN  10.240.205.20   92.62 KB   256     18.3%             8fc829de-65c9-4b43-ab6f-f58c65932366  RAC1
    UN  10.240.194.246  85.26 KB   256     16.1%             aae9d759-2c3c-47a4-981f-43506b449433  RAC1
    UN  10.240.205.228  109.85 KB  256     17.1%             eeaa960d-c1d7-4e46-8d43-fee54dce2b03  RAC1
    Datacenter: ZONE2
    =================
    Status=Up/Down
    |/ State=Normal/Leaving/Joining/Moving
    --  Address         Load       Tokens  Owns (effective)  Host ID                               Rack
    UN  10.240.221.31   71.83 KB   256     16.3%             904d64bd-ce95-4dd7-900e-2441a604f6f7  RAC1
    UN  10.240.89.53    98.73 KB   256     16.1%             3d0c0953-acc9-4b3e-9062-17792b4d4c1a  RAC1
    UN  10.240.169.136  98.74 KB   256     16.1%             9ca89253-59aa-4639-9959-b719f0465b5b  RAC1
    ```

### So what just happened?

1. The first thing the script does is to find a US-based region that has at
least two zones in that region also in the UP state (e.g. not under a
maintenance window).  In the output above, the script selects zones
`us-central1-a` and `us-central1-b` in region `us-central1`.
1. Next, the script creates 3 `n1-standard-1` instances running `debian-7`
in each zone.  The nodename is computed by using the last 3-characters of the
zone name appended to the NAME_PREFIX defined in `tools/common.py`.
1. When an instance is created, a custom script is executed by using GCE's
metadata feature.  The commands to be executed on a newly created instance
can be found in `tools/startup_script.sh`.  The last command in this script
is to create an empty file in a specific location.  The
`tools/create_cluster.py` iterates through the nodes and checks to see if
that marker file has been created and sleeps between each check.  Once all
nodes possess the marker file, the script continues.
1. Next, each node needs a few of its Cassandra configuration files updated.
The script selects one node from each zone to act as a SEED node.  Each
node's `/etc/cassandra/cassandra.yaml` file is updated with the IP addresses
of the SEED nodes.
1. This guide uses mutliple zones and therefore a custom PropertyFileSnitch
is generated with the IP addressess of all nodes in the cluster.  This data
is written to each node's `/etc/cassandra/cassandra-topology.properties`
file.
1. Next, the Cassandra service is started on the two SEED nodes.  In the
example above, this was `cassnode-b-2` and `cassnode-a-0` which were randomly
chosen.  The remaining non-SEED nodes are then also brought up.
1. Finally, the script pauses for a minute to ensure all nodes have had a
chance to discover each other and exchange data via the gossip protocol.  To
verify that the Cassandra cluster is actually running, the `nodetool status`
command is run against a random node in the cluster.  Ideally, you will see
an entry for all 6 nodes in the cluster, 3 per zone.

## Destroying the cluster

There is a script that will delete all nodes with names starting with the
NAME_PREFIX.  You can use this to purge the cluster if something goes wrong
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
  $ ./tools/firewall.py close
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
a demo keyspace.  For instance,

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
Note that the nodenames were manually added to better illustrate the data
distribution across zones.  Recall that in these examples, the replication
factor was set to 2 for each zone implying that data exists in two nodes in 
each zone.

  ```
  $ gcutil ssh --zone us-central1-a cassnode-a-2
  $ nodetool getendpoints demo characters name
  10.240.221.31   # cassnode-a-0
  10.240.89.53    # cassnode-a-2
  10.240.194.246  # cassnode-b-1
  10.240.205.20   # cassnode-b-2
  $ nodetool getendpoints demo characters appearances
  10.240.221.31   # cassnode-a-0
  10.240.169.136  # cassnode-a-1
  10.240.205.228  # cassnode-b-0
  10.240.194.246  # cassnode-b-1
  ```
## Debugging / Troubleshooting

The first thing you can try is to edit `tools/common.py` and change the
VERBOSE value to `True`.  When you re-run a script with that enabled, you
will see all of the standard output and error messages from `gcutil`.

In order to understand what's going on with a cluster deployment with these
scripts, you will likely need to either use the web console and check the
instance's serial output or SSH into the instance and monitor log files.  In
addition to standard log files, two that you should observe are:

* `/var/log/startupscript.log` - Log for metadata startup-script
* `/var/log/cassandra/output.log` - Cassandra log

Note that these scripts were *not* tested on a Windows system.  Some effort
was put into using platform-safe commands (e.g. `os.path.sep`).  But it was
only tested on both Linux and Mac.  Since these scripts only rely on `python`
and `gcutil`, they *should* work on Windows also.

## Conclusion

This guide was meant to give you the basic tools to bring up a small
Cassandra cluster for further education and evaluation.  The scripts should
be fairly straight forward to understand or tweak for your own experiments.

In summary, this guide showed that Google's Compute Engine is a good fit
for Cassandra deployments by,

* Taking advantage of mutliple zones within a region
* Metadata hooks to customize your instanes when they are created
* The (under the hood) capabilities of `gcutil` to easily manage your instances
* The ease with which a Cassandra cluster can be created and destroyed

## Contributing changes

* See [CONTRIB.md](https://github.com/GoogleCloudPlatform/compute-cassandra-python/blob/master/CONTRIB.md)

## Licensing

* See [LICENSE](https://github.com/GoogleCloudPlatform/compute-cassandra-python/blob/master/LICENSE)
