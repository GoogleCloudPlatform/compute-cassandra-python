# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Common global variables and functions
NODES_PER_ZONE = 3             # likely a 6-node cluster
MAX_NODES = 9                  # upper limit on node count
NODE_PREFIX = "cassnode"       # all nodenames begin with this
IMAGE = "debian-7"             # either debian-6, debian-7, or centos-6
MACHINE_TYPE = "n1-standard-1" # basic machine type
API_VERSION = "v1beta15"       # GCE API version
WAIT_MAX = 10                  # max wait iterations for startup-scripts
VERBOSE = False                # eat gcutil's stdout/stderr unless True
#############################################################################
import subprocess
import os
import sys

if VERBOSE:
  NULL = None
else:
  NULL = open(os.devnull, "w")
BE = BaseException

# Internal data structure for the cluster is a dict by 'zone', with a list
# of dicts containing 'name' and 'ip'
# Essentially looks for any instances that have a name that starts
# with NODE_PREFIX
# e.g.
# cluster['us-central1-a'] = [
#     {'name': 'cassnode-a-0', 'ip': '192.168.72.3', 'zone': 'us-central1-a'},
#     {'name': 'cassnode-a-1', 'ip': '192.168.112.9', 'zone': 'us-central1-a'}
# ]
def get_cluster():
    """Return the program data structure of a cluster"""
    cluster = {}
    pattern = "name eq '%s.*'" % NODE_PREFIX
    csv = subprocess.check_output(["gcutil",
            "--service_version=%s" % API_VERSION, "--format=csv",
            "listinstances", "--filter=%s" % pattern],
            stderr=NULL).split('\n')
    for line in csv:
        p = line.split(',')
        if p[0].startswith(NODE_PREFIX):
            zone = p[7].split('/')[-1]
            if cluster.has_key(zone):
                cluster[zone].append({'name':p[0], 'ip':p[4], 'zone':zone})
            else:
                cluster[zone] = [{'name':p[0], 'ip':p[4], 'zone':zone}]
    return cluster

# Return the image URL that matches IMAGE defined above
def get_image_path():
    """Return the image URL that matches IMAGE"""
    image_path = None
    csv = subprocess.check_output(["gcutil",
        "--service_version=%s" % API_VERSION, "--format=csv", "listimages",
        "--filter", "status eq READY"], stderr=NULL).split('\n')[1:-1]
    for line in csv:
        path = line.split(',')[0]
        name = path.split('/')[-1]
        if name.startswith(IMAGE):
            image_path = name 
    return image_path
