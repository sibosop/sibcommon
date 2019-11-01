#!/usr/bin/env python
import os
import sys
from debug import Debug
from singleton import Singleton
from hosts import Hosts
from mido import open_output
from mido import Message
from utils import doStartMusic
from utils import doHaltMusic
from utils import doHaltSound
from utils import doMute
from utils import sysex_to_data
from utils import data_to_sysex
from midiHandler import MidiPortHandler
from midiHandler import MidiHandler
from specs import Specs

class ControlBlock(object):
  def __init__(self,ip):
    self.ip = ip
    self.slider = 0
    self.pot = 0

class RtEvent(object):
  def __init__(self):
    self.eventName = None
    self.num = 0
    self.value = 0
    self.callback = self.defaultCallback
    
  def defaultCallback(self,event):
    Debug().p("default event callback %s"%event)
      
  def __str__(self):
    return "event %s num %s value %s callback %s"%(self.eventName,self.num,self.value,self.callback)


class NanoPlayer(object):
  __metaclass__ = Singleton
  sceneReq = [0x42,0x40,0x00,0x01,0x13,0x00,0x1F,0x10,0x00]
  togLocs = [17,23]
  transTogs = [307]
  def __init__(self,device):
    self.name = "%sPlayer"%device['id']
    desc = Specs().s[device['id']]
    iph = MidiPortHandler(device["inPort"],device['outPort'])
    iph.rtRegister("control_change",self.control_change)
    iph.rtRegister("sysex",self.sysex)
    MidiHandler().addPortHandler(iph)
    self.outport = iph.oport
    self.controlMap = []
    for i in range(0,128):
      self.controlMap.append(self.findEvent(i,desc['controls']))
    self.controlBlocks = [-1] * 8
    self.playerIps = []
    for h in Hosts().getHosts():
      if h['nanoId'] != -1:
        self.controlBlocks[h['nanoId']] = ControlBlock(h['ip'])
        Debug().p("%s added nano id %d for host %s"%(self.name,h['nanoId'],h['ip']))
      music = h['music']
      if music['enabled'] and music['player']:
        Debug().p("%s added added music player host %s"%(self.name,h['ip']))
        self.playerIps.append(h['ip'])
        
    self.register("slider", self.doSlider)
    self.register("pot", self.doPot)
    self.register("solo", self.doSolo)
    self.register("start", self.doStart)
    self.register("stop", self.doStop)
    self.register("begin", self.doBegin)
    self.register("end", self.doEnd)
    self.register("record", self.doRecord)
    self.register("cycle", self.doCycle)
    self.register("mute", self.doMute)
    self.register("prevTrack", self.doPrevTrack)
    self.register("nextTrack", self.doNextTrack)
    self.register("setMark", self.doSetMark)
    self.register("prevMark", self.doPrevMark)
    self.register("nextMark", self.doNextMark)
    self.register("recordSelect", self.doRecordSelect)
    self.register("recordSelect", self.doRecordSelect)
    self.setupState = "RequestSceneData"
    self.scene = None
    
    self.sendSysex(NanoPlayer.sceneReq)
    
    
  def sendSysex(self,sysex):
    Debug().p("sending sysex: %s"%sysex)
    self.outport.send(Message('sysex',data=sysex))
      
  def sysex(self,msg):
    Debug().p("sysex got msg %s"%msg)
    if self.setupState == "RequestSceneData":
      self.scene = sysex_to_data(msg.data[12:])
      for y in range(0,8):
        for x in NanoPlayer.togLocs:
          self.scene[x+(y*31)] = 1
      for x in NanoPlayer.transTogs:
        self.scene[x] = 1
      retData = data_to_sysex(self.scene)
      header = []
      for c in range(0,12):
        header.append(msg.data[c])
      for rd in retData:
        header.append(rd)
      self.sendSysex(header)
      self.setupState = "ConfigDataSent"
    elif self.setupState == "ConfigDataSent":
      if msg.data[7] != 35:
        print("MIDI ERROR: config did not succeed")
      self.setupState == None
    elif self.setupState == None:
      Debug().p("%s unexepected sysex message: %s"%(self.name,msg))
    
    
    
  def control_change(self,msg):
    ev = self.controlMap[msg.control]
    #Debug().p("%s got %s ev %s"%(self.name,msg,ev))
    ev.value = msg.value
    ev.callback(ev)
      
  def note_on(self,msg):
    ev = self.noteMap[msg.note]
    if ev.eventName != None:
      ev.value = msg.velocity
      ev.callback(ev)
        
  def findEvent(self,num,desc):
    rval = RtEvent();
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
     
  def register(self,eventName,callback):
    for e in self.controlMap:
      if e.eventName == eventName:
        Debug().p("register %s to %s"%(eventName,callback))
        e.callback = callback
      
  def doSlider(self,msg):
    Debug().p("%s slider %s"%(self.name,msg))
    self.controlBlocks[msg.num].slider = msg.value
    return
  def doPot(self,msg):
    Debug().p("%s Pot %s"%(self.name,msg))
    self.controlBlocks[msg.num].pot = msg.value
    return
  
    
  def doStart(self,msg):
    Debug().p("%s Start %s"%(self.name,msg))
    if msg.value == 127:
      doStartMusic("")
    else:
      doHaltMusic("")
    return
    
  def doStop(self,msg):
    Debug().p("%s Stop %s"%(self.name,msg))
    
    return
    
  def doBegin(self,msg):
    Debug().p("%s Begin %s"%(self.name,msg))
    return
  def doEnd(self,msg):
    Debug().p("%s End %s"%(self.name,msg))
    return
  def doRecord(self,msg):
    Debug().p("%s Record %s"%(self.name,msg))
    return
  def doCycle(self,msg):
    Debug().p("%s Cycle %s"%(self.name,msg))
    return
  def doSolo(self,msg):
    Debug().p("%s Solo %s"%(self.name,msg))
    cb = self.controlBlocks[msg.num]
    return
    
  def doMute(self,msg):
    Debug().p("%s Mute %s"%(self.name,msg))
    cb = self.controlBlocks[msg.num]
    for ip in self.playerIps:
      doMute(ip,cb.ip,msg.value == 127)
    return
  def doPrevTrack(self,msg):
    Debug().p("%s PrevTrack %s"%(self.name,msg))
    return
  def doNextTrack(self,msg):
    Debug().p("%s NextTrack %s"%(self.name,msg))
    return
  def doSetMark(self,msg):
    Debug().p("%s SetMark %s"%(self.name,msg))
    return
  def doPrevMark(self,msg):
    Debug().p("%s PrevMark %s"%(self.name,msg))
    return
  def doNextMark(self,msg):
    Debug().p("%s NextMark %s"%(self.name,msg))
    return
  def doRecordSelect(self,msg):
    Debug().p("%s RecordSelect %s"%(self.name,msg))
    return
    