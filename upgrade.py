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
<<<<<<< HEAD
    cmd = ['git','-C','sibcommon','pull','origin','master']
    print("upgrade: %s"%(cmd))
    output = check_output(cmd)
    cmd = ['git','-C','speclib','pull','origin','master']
=======
>>>>>>> 3bf942522f18b57d2be9038c6922deea87c06541
    print("upgrade: %s"%(cmd))
    os.chdir("../speclib")
    output = check_output(cmd)
<<<<<<< HEAD
=======
    print("upgrade: %s"%output)
    os.chdir("..")
>>>>>>> 3bf942522f18b57d2be9038c6922deea87c06541
  except Exception, e:
    print("upgrade error: "+repr(e))


