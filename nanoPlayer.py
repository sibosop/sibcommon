#!/usr/bin/env python
import os
import sys
from debug import Debug
from singleton import Singleton
from hosts import Hosts
from midiHandler import MidiHandler


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
    
  def doSlider(self,msg):
    Debug().p("%s slider %s"%(self.name,msg))
    return
  def doPot(self,msg):
    Debug().p("%s Pot %s"%(self.name,msg))
    return
  def doSolo(self,msg):
    Debug().p("%s Solo %s"%(self.name,msg))
    return
  def doStart(self,msg):
    Debug().p("%s Start %s"%(self.name,msg))
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
  def doMute(self,msg):
    Debug().p("%s Mute %s"%(self.name,msg))
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
    