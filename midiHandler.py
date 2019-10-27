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
#





class MidiPortHandler(object):
  def __init__(self,iname,oname):
    self.name = iname
    self.iport = mido.open_input(iname)
    self.oport = mido.open_output(oname)
    self.rtMap = {
      'clock' : self.nop
      ,'stop' : self.nop
      ,'start' : self.nop
      ,'songpos' : self.nop
      ,'continue' : self.nop
      ,'control_change': self.nop
      ,'note_on' : self.nop
      ,'note_off' : self.nop
      ,'pitchwheel' : self.nop
      ,'sysex' : self.nop
    }
  def rtRegister(self,rt,callback):
    self.rtMap[rt] = callback
      
  def nop(self,msg):
    Debug().p("%s: ignoring %s"%(self.name,msg))
    
  def sendSysex(self,sysex):
    self.oport.send(mido.Message('sysex',data=sysex))
    
class MidiHandler(threading.Thread):
  __metaclass__ = Singleton
  def __init__(self):
    super(MidiHandler,self).__init__()
    spec = Specs().s
    self.midiSpec = Hosts().getLocalAttr('midi')
    mido.set_backend(self.midiSpec['backend']) 
    self.name = "MidiHandler"
    self.running = True
    self.queue = Queue.Queue()
    self.portHandlers = []
    
  def addPortHandler(self,p):
    p.outport = mido.open_output
    self.portHandlers.append(p)
      
  def run(self):
    print("%s starting"%self.name)
    for d in self.midiSpec['devices']:
      if d['id'] == 'nano':
        from nanoPlayer import NanoPlayer
        NanoPlayer(d)
      
    while self.running:
      try:
        msg = self.queue.get_nowait()
        if msg == "__stop__":
          break
      except Queue.Empty:
        pass
        
      #for msg in mido.ports.multi_receive(self.inputs):
        #self.rtMap[msg.type](msg)
      for p in self.portHandlers:
        msg = p.iport.poll()
        if msg is not None:
          p.rtMap[msg.type](msg)
          
          
  
      
    
  