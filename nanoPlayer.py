#!/usr/bin/env python
import os
import sys
from debug import Debug
from singleton import Singleton
from hosts import Hosts
from midiHandler import MidiHandler
from utils import doStartMusic
from utils import doHaltMusic
from utils import doHaltSound
from utils import doMute

class ControlBlock(object):
  def __init__(self,ip):
    self.ip = ip
    self.slider = 0
    self.pot = 0

class NanoPlayer(object):
  __metaclass__ = Singleton
  def __init__(self):
    mh =  MidiHandler()
    self.name = "NanoPlayer"
    mh.register("slider", self.doSlider)
    mh.register("pot", self.doPot)
    mh.register("solo", self.doSolo)
    mh.register("start", self.doStart)
    mh.register("stop", self.doStop)
    mh.register("begin", self.doBegin)
    mh.register("end", self.doEnd)
    mh.register("record", self.doRecord)
    mh.register("cycle", self.doCycle)
    mh.register("mute", self.doMute)
    mh.register("prevTrack", self.doPrevTrack)
    mh.register("nextTrack", self.doNextTrack)
    mh.register("setMark", self.doSetMark)
    mh.register("prevMark", self.doPrevMark)
    mh.register("nextMark", self.doNextMark)
    mh.register("recordSelect", self.doRecordSelect)
    self.controlBlocks = [-1] * 8
    self.playerIps = []
    for h in Hosts().getHosts():
      if h['nanoId'] != -1:
        self.controlBlocks[h['nanoId']] = ControlBlock(h['ip'])
        Debug().p("%s added nano id %d for host %s"%(self.name,h['nanoId'],h['ip']))
      if h['hasMusicPlayer']:
        Debug().p("%s added added music player host %s"%(self.name,h['ip']))
        self.playerIps.append(h['ip'])
    
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
    if msg.value != 0:
      doStartMusic({'cmd' : 'StartMusic'})
    return
    
  def doStop(self,msg):
    Debug().p("%s Stop %s"%(self.name,msg))
    if msg.value != 0:
      doHaltMusic({'cmd' : 'HaltMusic'})
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
    for ip in self.playerIps:
      doMute(ip,cb.ip,False)
    return
    
  def doMute(self,msg):
    Debug().p("%s Mute %s"%(self.name,msg))
    cb = self.controlBlocks[msg.num]
    for ip in self.playerIps:
      doMute(ip,cb.ip,True)
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
    