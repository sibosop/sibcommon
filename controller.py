#!/usr/bin/env python
import os
import sys
import mido
import singleton
from utils import print_dbg

class ControllerEvent(object):
  def __init__(self):
    self.event = None
    self.num = 0
    self.value = 0
    self.callback = None
      
  def __str__(self):
    return "event %s num %s value %s"%(self.event,self.num,self.value)

class Controller(object):
  _metaclass_ = singleton.Singleton
  def __init__(self,inPort,outPort,desc):
    mido.set_backend('mido.backends.rtmidi')
    self.midiIn = mido.open_input(inPort)
    self.midiOut = mido.open_output(outPort)
    self.emap = []
    for i in range(0,128):
      self.emap.append(self.findEvent(i,desc))
      
  def register(self,event,callback):
    for e in self.emap:
      if e.event == event:
        e.callback = callback 
  
  def run(self):
    while True:
      msg = self.midiIn.receive();
      print_dbg("type: %s control %d value %d"%(msg.type,msg.control,msg.value))
      rval = self.emap[msg.control]
      if rval.callback is not None:
        rval.value = msg.value
        rval.callback(rval)
    
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
      
    
    
  def close(self):
    self.midiIn.close()
    self.midiOut.close()

