#!/usr/bin/env python
import os
import json
from debug import Debug
from singleton import Singleton

class Specs(metaclass=Singleton):
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
        path="%s/%s.json"%(self.specDir,f)
        Debug().p("adding %s to specs"%path)
        tmp = {}
        with open(path) as sf:
          tmp = json.load(sf)
        for k in tmp.keys():
          if k not in self.s:
            self.s[k] = tmp[k]
          else:
            Debug().p("ignoring already set k %s"%k)
          
    Debug().p("%s"%(self.s))
  

