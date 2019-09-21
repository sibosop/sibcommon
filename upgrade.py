#!/usr/bin/env python
import syslog
import os
import sys
from subprocess import CalledProcessError, check_output

def upgrade():
  try:
    print("DOING UPGRADE")
    cmd = ['git','pull','origin','master']
    os.chdir("sibcommon")
    output = check_output(cmd)
    cmd = ['git','-C','sibcommon','pull','origin','master']
    print("upgrade: %s"%(cmd))
    output = check_output(cmd)
    cmd = ['git','-C','speclib','pull','origin','master']
  except Exception, e:
    print("upgrade error: "+repr(e))


