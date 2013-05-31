#!/usr/bin/env  python
# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
"""

import subprocess
import os
import sys

# Read in global variables, edit
# the common.py file to change any
# global vars
mydir = os.path.dirname(os.path.realpath(__file__))
common = mydir + os.path.sep + "common.py"
execfile(common, globals())

# Find nodes that match our name prefix
def getNodes():
  nodes = []
  pattern = "name eq '%s.*'" % NODE_PREFIX
  csv = subprocess.check_output(["gcutil",
    "--service_version=%s" % API_VERSION, "--format=csv", "listinstances",
    "--filter=%s" % pattern]).split('\n')
  for line in csv:
    elements = line.split(',')
    if elements[0].startswith(NODE_PREFIX):
      nodes.append([elements[0], elements[7]])
  return nodes

# destroy the nodes
def destroyNodes(nodes):
  null = open(os.devnull, "w")
  for node in nodes:
    print "...deleting %s in zone %s" % (node[0], node[1])
    _ = subprocess.call(["gcutil",
      "--service_version=%s" % API_VERSION, "deleteinstance", "-f",
      "--zone=%s" % node[1], node[0]], stdout=null, stderr=null)
  null.close()


def main():
  nodes = getNodes()

  if not nodes:
    print "No nodes found matching NODE_PREFIX '%s'" % NODE_PREFIX
    sys.exit(0)

  print "*************************************************************"
  print "************************* WARNING ***************************"
  print "*************************************************************"
  print "You are about to delete ALL of the following instances.  This"
  print "operation can *NOT* be undone and ALL data will be lost."
  print ""
  for node in nodes:
    print "\t" + node[0] + " in zone " + node[1]
  answer = raw_input("\nAre you SURE you want to delete these nodes [y|N]? ")
  if answer.lower() not in ["y", "yes"]:
    print "Ok, nothing to do then."
    sys.exit(0)

  destroyNodes(nodes)
  print "Complete.  Nodes deleted."


if __name__ == '__main__':
  main()
