#!/usr/bin/env python
import os
import json
from utils import print_dbg
from singleton import Singleton

class Specs(object):
  __metaclass__ = Singleton

  def __init__(self,specPath):
    self.s = None
    self.specDir = os.path.dirname(specPath)
    print_dbg("Specs: specPath%s"%specPath)
    with open(specPath) as f:
      self.s = json.load(f)
    if 'include' not in self.s:
      return
    print_dbg("Specs: doing include")
    for f in self.s['include']:
      path="%s/%s.json"%(specDir,f)
      print_dbg("adding %s to specs"%path)
      with open(path) as sf:
        tmp = json.load(sf)
      self.s.update(tmp)
    print_dbg("%s"%(self.s))
  

