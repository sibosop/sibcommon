#!/usr/bin/env python
import os
import sys
import mido
import singleton
from utils import print_dbg
from specs import Specs

class ControllerEvent(object):
  def __init__(self):
    self.eventName = None
    self.num = 0
    self.value = 0
    self.callback = None
      
  def __str__(self):
    return "event %s num %s value %s"%(self.event,self.num,self.value)

class Controller():
  __metaclass__ = singleton.Singleton
  def __init__(self,name):
    self.emap = []
    for i in range(0,128):
      self.emap.append(self.findEvent(i,Specs().s[name]))
      
  def register(self,eventName,callback):
    for e in self.emap:
      if e.eventName == eventName:
        e.callback = callback 
    
  def findEvent(self,controlNum,desc):
    rval = ControllerEvent();
    for k in desc.keys():
      min = desc[k][0]
      if len (desc[k]) == 2:
        max = desc[k][1]
      else:
        max = min
      if controlNum in range(min,max+1):
        rval.event = k
        rval.num = controlNum-min
        break
    return rval
    
  
