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
Script to set up firewall rules via gcutil.
"""

import subprocess
import sys
from os import devnull

def usage():
  print "Usage: firewall.py [add|delete]"
  sys.exit(1)

if len(sys.argv) != 2: usage()

# assumes you're using the 'default' network
null = open(devnull, "w")

if sys.argv[1].lower() == "add":
  ret = subprocess.call(["gcutil", "addfirewall",
    "--allowed", "tcp:9160", "--network", "default",
    "--description", "Allow all incoming to Cassandra Thrift port",
    "cassandra"], stdout=null, stderr=null)
elif sys.argv[1].lower() == "delete":
  ret = subprocess.call(["gcutil", "deletefirewall", "--force",
    "cassandra"], stdout=null, stderr=null)
else:
  usage()

if ret != 0:
  print "Error setting firewall rule, please try again"
  sys.exit(ret)
