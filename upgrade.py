#!/usr/bin/env python
import syslog
import os
import sys
from threadMgr import ThreadMgr
from subprocess import CalledProcessError, check_output

def upgrade():
  try:
    print("DOING UPGRADE")
    ThreadMgr().stopAll()
    cmd = ['git','pull','origin','master']
    print("upgrade: %s"%(cmd))
    output = check_output(cmd)
    print("upgrade: %s"%(output))
    cmd = ['git','-C','sibcommon','pull','origin','master']
    print("upgrade: %s"%(cmd))
    output = check_output(cmd)
    print("upgrade: %s"%(output))
    cmd = ['git','-C','speclib','pull','origin','master']
    output = check_output(cmd)
    print("upgrade: %s"%(output))
  except Exception, e:
    print("upgrade error: "+repr(e))


