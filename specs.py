#!/usr/bin/env python
import os
import json
from debug import Debug
from singleton import Singleton

class Specs(object):
  __metaclass__ = Singleton

  def __init__(self,specPath):
    self.s = None
    self.specDir = os.path.dirname(specPath)
    Debug().p("Specs: specPath%s"%specPath)
    with open(specPath) as f:
      self.s = json.load(f)
    if 'include' in self.s:
      Debug().p("Specs: doing include")
      for f in self.s['include']:
        path="%s/%s.json"%(specDir,f)
        Debug().p("adding %s to specs"%path)
        with open(path) as sf:
          tmp = json.load(sf)
        self.s.update(tmp)
    Debug().p("%s"%(self.s))
  

