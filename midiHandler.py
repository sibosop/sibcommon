#!/usr/bin/env python
import csv
import os
import sys
import glob
from utils import print_dbg
from singleton import Singleton
from specs import Specs
import mido

class Event(object):
  def __init__(self):
    self.eventName = None
    self.num = 0
    self.value = 0
    self.callback = None
      
  def __str__(self):
    return "event %s num %s value %s"%(self.eventName,self.num,self.value)

class EventMapper():
  def __init__(self,desc):
    self.controlMap = []
    self.noteMap = []
    self.rtMap = []
    for i in range(0,128):
      self.controlMap.append(self.findEvent(i,desc['controls'])))
      self.noteMap.append
    
  def register(self,eventName,callback):
    for e in self.emap:
      if e.eventName == eventName:
        e.callback = callback 
  
  def findEvent(self,controlNum,desc):
    rval = Event();
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
    
class MidiHandler():
  __metaclass__ = Singleton
  def __init__(self,mapperList)
    spec = Specs().s
    mido.set_backend(s["midiBackEnd"])
    self.ctrlMap = []
    self.noteMap = []
    self.realTimeMap = []
    self.inputs = {}
    self.outputs = {}
    for n in mapperList:
      desc = spec[n]
      self.inputs[n] = mido.open_input(desc['inPort'])  
      self.ouputs[n] = mdio.open_output(desc['outPort'])
      spec = Specs()[n]
      if len(m['controls'].keys() != 0:
        em = EventMapper()
        
  