#!/usr/bin/env python
import csv
import os
import sys
import glob
from utils import print_dbg
from singleton import Singleton
from specs import Specs
import mido
import threading

class Event(object):
  def __init__(self):
    self.eventName = None
    self.num = 0
    self.value = 0
    self.callback = self.defaultCallback
    
  def defaultCallback(self,event):
    print_dbg("default event callback %s"%event)
      
  def __str__(self):
    return "event %s num %s value %s"%(self.eventName,self.num,self.value)
    
class MidiHandler(threading.Thread):
  __metaclass__ = Singleton
  def __init__(self,mapperList):
    super(MidiHandler,self).__init__()
    spec = Specs().s
    mido.set_backend(spec["midiBackEnd"])
    self.controlMap = []
    self.noteMap = []
    self.inputs = []
    self.outputs = []
    self.name = "MidiHandler"
    self.running = True
    for n in mapperList:
      desc = spec[n]
      self.inputs.append(mido.open_input(desc['inPort']))  
      self.outputs.append(mido.open_output(desc['outPort']))
      for i in range(0,128):
        self.controlMap.append(self.findEvent(i,desc['controls']))
        self.noteMap.append(self.findEvent(i,desc['notes']))
        
    self.rtMap = {
      'clock' : self.nop
      ,'stop' : self.nop
      ,'start' : self.nop
      ,'songpos' : self.nop
      ,'continue' : self.nop
      ,'control_change': self.control_change
      ,'note_on' : self.note_on
      ,'note_off' : self.nop
      ,'pitchwheel' : self.nop
    }
    
  def register(self,eventName,callback):
    for e in self.controlMap:
      if e.eventName == eventName:
        e.callback = callback
        return
    for e in self.NoteMap:
      if e.eventName == eventName:
        e.callback = callback
            
  def findEvent(self,num,desc):
    rval = Event();
    for k in desc.keys():
      min = desc[k][0]
      if len (desc[k]) == 2:
        max = desc[k][1]
      else:
        max = min
      if num in range(min,max+1):
        rval.event = k
        rval.num = num-min
        break
    return rval
    
  
  def control_change(self,msg):
    ev = self.controlMap[msg.control]
    ev.value = msg.value
    ev.callback(ev)
      
  def note_on(self,msg):
    ev = self.noteMap[msg.note]
    if ev.eventName != None:
      ev.value = msg.velocity
      ev.callback(ev)
  
  def mapRt(self,name,callback):
    self.rtMap[name] = callback
  
  def nop(msg):
    print_dgb("%s: ignoring %s"%(name,msg))
    
  def run(self):
    print("%s starting"%self.name)
    while self.running:
      for msg in mido.ports.multi_receive(self.inputs):
        self.rtMap[msg.type](msg)
  
      
    
  