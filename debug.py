#!/usr/bin/env python
import inspect
from singleton import Singleton


class Debug(object):
  __metaclass__ = Singleton
  def __init__(self,modlist=[]):
    self.mods = []
    self.enable(modlist)
    
  def enable(self,names):
    for name in names:
      if name not in self.mods:
        self.mods.append(name)
      
  def disable(self,names):
    for name in names:
      if name in self.mods:
        self.mods.remove(name)
      
  def p(self,msg):
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    
    if mod.__name__ in self.mods:
      print ('[%s] %s' % (mod.__name__, msg))