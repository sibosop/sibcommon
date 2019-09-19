#!/usr/bin/env python
import syslog
import os
import sys
from subprocess import CalledProcessError, check_output

def upgrade():
  try:
    print("DOING UPGRADE current dir %s"%os.getcwd())
    cmd = ['git','pull','origin','master']
    print("upgrade: %s"%(cmd))
    output = check_output(cmd)
    cmd = ['git','submodule','update']
    print("upgrade: %s"%(cmd))
    output = check_output(cmd)
    print("upgrade: %s"%output)
  except Exception, e:
    print("upgrade error: "+repr(e))


