## compute-cassandra-python

This repository is intended to be a guideline to setting up a basic working Cassandra cluster utilizing Google Compute Engine resources.

This material was developed using Cassandra 1.2.4, Debian Wheezy images, and the OpenJDK 7 JRE available through the official Debian repository.

## Overview

[Cassandra](http://cassandra.apache.org) is an open-source [NoSQL](http://en.wikipedia.org/wiki/Nosql) data store.  It is designed primarily to provide a robust fault tolerant distributed and decentralized data store that is highly durable and scalable.  It provides a SQL-like interface but is *not* equivalent with a traditional relational database like MySQL or PostgreSQL.  To learn much more about Cassandra, you can also reference the material published by Datastax on their [resources page](http://www.datastax.com/resources).  This guide was also developed using Datastax's Community Edition.


Google Compute Engine (GCE) is a very good match for Cassandra users.  Some of GCE's features that make it a great fit are:

* Distinct geographic regions within Europe and North America
* Separate zones within a region to provide fault-tolerance within a region
* Ability to scale up/down be adding and removing compute resources when needed
* Persistent disks to preserve and share data between restarts and/or machines

There is a lot to consider when getting ready to deploy a Cassandra cluster in production.  This guide is intended to provide a starting point to learn more about GCE and Cassandra by deploying a small 6-node cluster in a single region across two zones.  It does not address issues such as security, scaling a running cluster, or performance tuning.  The documentation provided by Datastax goes into much more detail about planning production Cassandra clusters.

### Prerequisites

This guide assumes you have registered a [Google Cloud Platform](https://cloud.google.com/) account and have added the Google Compute Engine service.  It also assumes you have installed [`gcutil`](https://developers.google.com/compute/docs/gcutil/), the command-line utility used to manage Google Compute Engine resources.  Lastly, you will need a system with [`python`](http://www.python.org/) installed if you would like to use the provided scripts for deploying the example cluster.

## Project Setup, Installation, and Configuration
How do I, as a developer, start working on the project?

1. What dependencies does it have (where are they expressed) and how do I install them?
1. Can I see the project working before I change anything?

## Testing
How do I run the project's automated tests?

* Unit Tests

* Integration Tests

## Deploying

### How to setup the deployment environment

* Addons, packages, or other dependencies required for deployment.
* Required environment variables or credentials not included in git.
* Monitoring services and logging.

### How to deploy

## Troubleshooting & Useful Tools

### Examples of common tasks

> e.g.
> * How to make curl requests while authenticated via oauth.
> * How to monitor background jobs.
> * How to run the app through a proxy.

## Contributing changes

* See CONTRIB.md

## Licensing

* See LICENSE
