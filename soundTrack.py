#!/usr/bin/env python
import pygame
import os
import threading
import random
import time
import Queue


import singleton
from specs import Specs
from debug import Debug
from soundUtils import speedx,playSound
from soundFile import SoundFile
from hosts import Hosts
from server import Server

class SoundTrackManager(object):
  __metaclass__ = singleton.Singleton
  def __init__(self,rootDir):
    self.rootDir = rootDir
    self.buffers = {}
    self.currentSound = {'file':""}
    self.octaves = [0.25,0.5,1.0,2.0,4.0]
    self.ecount = 0
    self.name = "SoundTrackManager"
    self.eventThreads=[]
    self.makeBuffers()
    if Hosts().getLocalAttr("hasServer"):
      Server().registerCommand("Sound",self.doSound)
    
    self.changeNumSoundThreads(Specs().s['numMusicThreads'])
    self.tunings = {}
    for k in Specs().s['tunings'].keys():
      self.tunings[k] = []
      for t in Specs().s['tunings'][k]:
        num,den = t.split("/")
        self.tunings[k].append(float(num)/float(den))
    
  def doSound(self,cmd):
    for t in self.eventThreads:
      t.setCurrentSound(cmd)
      return Hosts.jsonStatus(str(cmd))

  def makeBuffers(self):
    Debug().p("%s: makeBuffers"%self.name)
    for l in Specs().s['collections']:
      Debug().p ("l: %s"%l)
      for f in Specs().s[l['list']]:
        Debug().p("f: %s"%f['name'])
        if f['name'] in self.buffers:
          Debug().p("%s: skipping existing fname %s"%(self.name,f['name']))
        else:
          path = self.rootDir + '/' + f['name']
          buffer = pygame.mixer.Sound(file=path)
          self.buffers[f['name']] = buffer
          
          
  
  
  def startEventThread(self):
    Debug().p("startEventThread")
    self.ecount += 1
    t=soundTrack(self.ecount)
    self.eventThreads.append(t)
    self.eventThreads[-1].setDaemon(True)
    self.eventThreads[-1].start()

  def stopEventThread(self):
    Debug().p("stopEventThread")
    if len(self.eventThreads) != 0:
      t = self.eventThreads.pop()
      t.stop()
    else:
      print("trying to stop thread when list is empty")

  def changeNumSoundThreads(self,n):
    self.numEvents = n
    print("changing number of threads from "
                      +str(len(self.eventThreads))+ " to "+str(n))
    while len(self.eventThreads) != n:
      if len(self.eventThreads) < n:
        self.startEventThread()
      elif len(self.eventThreads) > n:
        self.stopEventThread()
  
    return True


  
  
  
class SoundTrack(threading.Thread):
  def __init__(self,c):
    super(SoundTrack,self).__init__()
    self.playList = {}
    self.playList['events'] = []
    self.runState = True
    self.name = "SoundTrack-"+str(c)
    self.num = c
    self.currentDir = os.getcwd()
    self.lRatio = .5
    self.rRatio = .5
    self.runMutex = threading.Lock()
    self.dirMutex = threading.Lock()
    self.queue = Queue.Queue()
    
  def setPanRatio(self):
    numEvents = len(SoundTrackManager().eventThreads)
    if numEvents <= 1:
      self.rRatio = .5
      self.lRatio = .5
    else:
      divs = 1.0 / float(numEvents-1)
      self.rRatio = float(self.num-1) * divs
      self.lRatio = 1.0 - self.rRatio
    Debug().p("%s setting lRatio:%f rRation:%f"%(self.name,self.lRatio,self.rRatio))
    
  def getFactor(self,cs):
    Debug().p("getFactor on: %s"%cs)
  
    rval = 1.0
    if 'tuning' in cs.keys() and cs['tuning'] in Specs().s['tunings'].keys():
      ts = SoundTrackManager().tunings[cs['tuning']]
      tc = random.choice(ts)
      oc = random.choice(SoundTrackManager().octaves)
      Debug().p("tc: %f oc: %f"%(tc,oc))
      rval = tc * oc
    else:
      Debug().p("default tuning for cs: %s"%cs)
      speedChangeMax = Specs().s['speedChangeMax']
      speedChangeMin = Specs().s['speedChangeMin']
      rval = ((speedChangeMax-speedChangeMin) * random.random()) + speedChangeMin
    
    Debug().p("factor: %d"%rval)
    return rval
    
  def setCurrentDir(self,dir):
    self.dirMutex.acquire()
    self.soundDir = dir
    self.dirMutex.release()
  
  def getCurrentDir(self):
    self.dirMutex.acquire()
    dir = self.soundDir
    self.dirMutex.release()
    return dir
    
  def setCurrentSound(self,cs):
    self.queue.put(cs)
    
  def isRunning(self):
    self.runMutex.acquire()
    rval = self.runState
    self.runMutex.release()
    return rval

  def stop(self):
    self.runMutex.acquire()
    self.runState = False
    self.runMutex.release()
    
    
  def run(self):
    print("%s starting"%self.name)
    ts = None
    cs = None
    while self.isRunning():
      Debug().p("%s: timeout %s"%(self.name,ts))
      try:
        test = self.queue.get(timeout=ts)
      except Queue.Empty:
        test = cs
      cs = test
      file=""
      file = cs['name']
      #path = rootDir + '/' + file
      Debug().p("%s: playing: %s"%(self.name,file))
      #sound = pygame.mixer.Sound(file=buffers[file])
      factor = self.getFactor(cs);
      sound = None
      nsound = speedx(SoundTrackManager().buffers[file],factor)
      if nsound is not None:
        sound = nsound
      else:
        sound = SoundTrackManager().buffers[file]
      v = random.uniform(Specs().s['soundMinVol'],Specs().s['soundMaxVol']);
      self.setPanRatio()
      lVol = v * self.lRatio
      rVol = v * self.rRatio
      Debug().p("%s: lVol %f rVol %f lRatio %f rRatio %f"%(self.name,lVol,rVol,self.lRatio,self.rRatio))
      event = {}
      event['vol'] = v
      event['factor'] = factor
      event['file'] = file
      Debug().p("Sound baseTime:%d"%SoundFile().baseTime)
      event['time'] = time.time() - SoundFile().baseTime
      self.playList['events'].append(event)
      playSound(sound,lVol,rVol)
      ts = random.randint(Specs().s['eventMin'],Specs().s['eventMax'])/1000.0;
      
      
    print("schlub thread " + self.name + " exiting")
    
