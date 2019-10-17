#!/usr/bin/env python
import csv
import os
import sys
import glob
from debug import Debug
from singleton import Singleton
from specs import Specs
import mido
import threading
import Queue
from hosts import Hosts

class Event(object):
  def __init__(self):
    self.eventName = None
    self.num = 0
    self.value = 0
    self.callback = self.defaultCallback
    
  def defaultCallback(self,event):
    Debug().p("default event callback %s"%event)
      
  def __str__(self):
    return "event %s num %s value %s"%(self.eventName,self.num,self.value)
    
class MidiHandler(threading.Thread):
  __metaclass__ = Singleton
  def __init__(self):
    super(MidiHandler,self).__init__()
    spec = Specs().s
    hostSpec = Hosts().getLocalAttr('midi')
    mapperList = hostSpec['devices']
    mido.set_backend(hostSpec['backend'])
    self.controlMap = []
    self.noteMap = []
    self.inputs = []
    self.outputs = []
    self.name = "MidiHandler"
    self.running = True
    for n in mapperList:
      desc = spec[n['id']]
      if n['inPort']:
        self.inputs.append(mido.open_input(n['inPort']))
      if  n['outPort']:
        self.outputs.append(mido.open_output(n['outPort']))
      for i in range(0,128):
        self.controlMap.append(self.findEvent(i,desc['controls']))
        self.noteMap.append(self.findEvent(i,desc['notes']))
    self.queue = Queue.Queue()
    
    
        
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
        Debug().p("found %s %d"%(k,num))
        rval.eventName = k
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
      try:
        msg = self.queue.get_nowait()
        if msg == "__stop__":
          break
      except Queue.Empty:
        pass
        
      #for msg in mido.ports.multi_receive(self.inputs):
        #self.rtMap[msg.type](msg)
      for i in self.inputs:
        msg = i.poll()
        if msg is not None:
          self.rtMap[msg.type](msg)
          
          
  
      
    
  