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

"""
"""

import os

# Read in global variables, edit
# the common.py file to change any
# global vars
mydir = os.path.dirname(os.path.realpath(__file__))
common = mydir + os.path.sep + "common.py"
execfile(common, globals())


# Call deleteinstance on all nodes in cluster.
def destroy_nodes(cluster):
    """Call deleteinstance on all nodes in cluster."""
    for z in cluster.keys():
        for node in cluster[z]:
            print "...deleting node %s in zone %s" % (node['name'], node['zone'])
            _ = subprocess.call(["gcutil",
                    "--service_version=%s" % API_VERSION, "deleteinstance",
                    "-f", "--zone=%s" % node['zone'],
                    "--delete_boot_pd", node['name']],
                    stdout=NULL, stderr=NULL)


def main():
    # Find all nodes with names matching NODE_PREFIX.
    cluster = get_cluster()

    if not cluster:
        print "No nodes found matching NODE_PREFIX '%s'" % NODE_PREFIX
        sys.exit(0)

    print "*****************************************************************"
    print "*************************** WARNING *****************************"
    print "*****************************************************************"
    print "You are about to delete ALL of the following instances including."
    print "their boot disks.  This operation can *NOT* be undone and ALL"
    print "data will be lost."
    print ""
    for z in cluster.keys():
        print "=> Nodes for Zone '%s'" % z
        for node in cluster[z]:
            print "--> %s" % node['name']
    answer = raw_input(
        "\nAre you SURE you want to delete these nodes and their disks [y|N]? ")
    if answer.lower() not in ["y", "yes"]:
        print "Ok, nothing to do then."
        sys.exit(0)

    destroy_nodes(cluster)
    print "Complete.    Nodes and disks deleted."

if __name__ == '__main__':
    main()

