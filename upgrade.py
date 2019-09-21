#!/usr/bin/env python
import syslog
import os
import sys
from subprocess import CalledProcessError, check_output

def upgrade():
  try:
    print("DOING UPGRADE current dir %s"%os.getcwd())
    cmd = ['git','pull','origin','master']
    os.chdir("sibcommon")
    output = check_output(cmd)
    print("upgrade: %s"%(cmd))
    os.chdir("../speclib")
    output = check_output(cmd)
    print("upgrade: %s"%output)
    os.chdir("..")
  except Exception, e:
    print("upgrade error: "+repr(e))


