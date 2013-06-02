#!/usr/bin/env    python
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

"""Script to set up authentication via gcutil.

Make sure to pass in the "Project ID" and not the project name or number.
"""

import subprocess
import sys
import os

if len(sys.argv) != 2:
    print "Usage: auth.py project_id"
    sys.exit(1)

retval = subprocess.call(["gcutil", "auth", "--project=%s" % (sys.argv[1])])

if retval != 0:
    print "Error authenticating, please try again"
    sys.exit(retval)

# Silently cache the project id to avoid repeatedly passing in an extra arg.
null = open(os.devnull, "w")
_ = subprocess.call(["gcutil", "getproject", "--project=%s" % (sys.argv[1]),
        "--cache_flag_values"], stdout=null, stderr=null)
