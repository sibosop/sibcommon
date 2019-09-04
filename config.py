#!/usr/bin/env python
import os
home = os.environ['HOME']
import json
import urllib2
from threading import Lock
from utils import print_dbg
mutex = Lock()
specs = None
specDir = None


def includeFiles():
  global specs
  global specDir
  if 'include' not in specs:
    return
  if debug: print "config: doing include"
  for f in specs['include']:
    path="%s/%s.json"%(specDir,f)
    print_dbg("adding %s to specs"%path)
    with open(path) as sf:
      tmp = json.load(sf)
    specs.update(tmp)


def load(specPath):
  global specs
  if specs:
    return specs
  specDir = os.path.dirname(specPath)
  print_dbg("config: specPath%s"%specPath)
  with open(specPath) as f:
    specs = json.load(f)
  includeFiles()
  print_dbg("%s"%(specs))
  return specs
  
  
def internetOn():
  try:
    urllib2.urlopen('http://216.58.192.142', timeout=1)
    return True
  except urllib2.URLError as err: 
    return False
    


if __name__ == '__main__':
  load();
