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

# Global configuration variables
NODES_PER_ZONE = 3             # Define number of nodes to create in each
                               # zone.  GCE typically has two zones per region
                               # so this would create a 6 node C* cluster

MAX_NODES = 9                  # Prevents excessive number of nodes to be
                               # created.  If NODES_PER_ZONE * number_of_zones
                               # is > than MAX_NODES, the script will raise an
                               # error and exit.  GCE typically has 2 zones per
                               # region (e.g. NODES_PER_ZONE * 2 < MAX_NODES)

NODE_PREFIX = "cassnode"       # All nodenames begin with this string.  This is
                               # how the scripts determine what nodes belong to
                               # the C* cluster.

MACHINE_TYPE = "n1-standard-1" # The machine type used for all cluster nodes

API_VERSION = "v1"             # GCE API version

WAIT_MAX = 10                  # Max wait-iterations for startup-script, the
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

VERBOSE = False                # Eat gcutil's stdout/stderr unless True. If
                               # debugging script issues, set this to True
                               # and re-run the scripts
#############################################################################

# Moving below configuration block since the startup script only
# works on Debian and was only tested with Wheezy images.
IMAGE = "debian-7"

import subprocess
import os
import sys

if VERBOSE:
  NULL = None
else:
  NULL = open(os.devnull, "w")
BE = BaseException

# See above - if the GCE_USERNAME is not set, attempt to grab it from the
# local user's environment. This username will be used to execute 'gsutil'
# on the new GCE instances to fetch the JRE installer from the defined
# GCS_BUCKET.
if not GCE_USERNAME:
    GCE_USERNAME = (os.getenv('USER')
            or os.getenv('LOGNAME')
            or os.getenv('HOME').split(os.sep)[-1])
    if not GCE_USERNAME:
        raise BE("Must set GCE_USERNAME in tools/common.py")

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
            stderr=NULL).split('\n')[1:-1]
    for line in csv:
        # name,zone,status,network-ip,external-ip
        p = line.split(',')
        zone = p[1]
        if zone in cluster:
            cluster[zone].append({'name':p[0], 'ip':p[3], 'zone':zone})
        else:
            cluster[zone] = [{'name':p[0], 'ip':p[3], 'zone':zone}]
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
            image_path = path 
    return image_path
