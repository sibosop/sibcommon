#!/usr/bin/env python
import inspect
from singleton import Singleton


class Debug(object):
  __metaclass__ = Singleton
  def __init__(self,modlist=[]):
    self.tlist = {}
    self.enable(modlist)
    
    
  def enable(self,names):
    for name in names:
      self.tlist[name] = True
        
      
  def disable(self,names):
    for name in names:
      self.tlist[name] = False
      
  def p(self,msg):
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    
    
    try:
      if self.tlist[mod.__name__ ]:
        print ('[%s] %s' % (mod.__name__, msg))
    except KeyError:
      self.tlist[mod.__name__] = False
      
      
if __name__ == "__main__":
  Debug([])
  Debug().p("shouldn't show")
  Debug().enable(["__main__"])
  Debug().p("should show")
  Debug().disable(["__main__"])
  Debug().p("shouldn't show")