#!/usr/bin/env python
import pygame
import os
import threading
import random
import time
import Queue


import singleton
from specs import Specs
from utils import print_dbg
from soundUtils import speedx,playSound
from soundFile import SoundFile

class SoundTrackManager(object):
  __metaclass__ = singleton.Singleton
  def __init__(self,rootDir):
    self.rootDir = rootDir
    self.buffers = {}
    self.currentSound = {'file':""}
    self.octaves = [0.25,0.5,1.0,2.0,4.0]
    self.ecount = 0
    self.eventThreads=[]
    self.makeBuffers()
    
    self.changeNumSoundThreads(Specs().s['numThreads'])
    self.tunings = {}
    for k in Specs().s['tunings'].keys():
      self.tunings[k] = []
      for t in Specs().s['tunings'][k]:
        num,den = t.split("/")
        self.tunings[k].append(float(num)/float(den))
    
    
  def makeBuffers(self):
    for l in Specs().s['collections']:
      print_dbg ("l: %s"%l)
      for f in Specs().s[l['list']]:
        print_dbg("f: %s"%f['name'])
        try:
          path = self.rootDir + '/' + f['name']
          buffer = pygame.mixer.Sound(file=path)
          self.buffers[f['name']] = buffer
        except Exception as e:
          print "make Buffers:",e
          
  
  
  def startEventThread(self):
    print_dbg("startEventThread")
    self.ecount += 1
    t=soundTrack(self.ecount)
    self.eventThreads.append(t)
    self.eventThreads[-1].setDaemon(True)
    self.eventThreads[-1].start()

  def stopEventThread(self):
    print_dbg("stopEventThread")
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

  
  
  
class soundTrack(threading.Thread):
  def __init__(self,c):
    super(soundTrack,self).__init__()
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
    print_dbg("%s setting lRatio:%f rRation:%f"%(self.name,self.lRatio,self.rRatio))
    
  def getFactor(self,cs):
    print_dbg("getFactor on: %s"%cs)
  
    rval = 1.0
    if 'tuning' in cs.keys() and cs['tuning'] in Specs().s['tunings'].keys():
      ts = SoundTrackManager().tunings[cs['tuning']]
      tc = random.choice(ts)
      oc = random.choice(SoundTrackManager().octaves)
      print_dbg("tc: %f oc: %f"%(tc,oc))
      rval = tc * oc
    else:
      print_dbg("default tuning for cs: %s"%cs)
      speedChangeMax = Specs().s['speedChangeMax']
      speedChangeMin = Specs().s['speedChangeMin']
      rval = ((speedChangeMax-speedChangeMin) * random.random()) + speedChangeMin
    
    print_dbg("factor: %d"%rval)
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
    print("Sound Track:"+self.name)
    ts = None
    cs = None
    while self.isRunning():
      print_dbg("%s: timeout %s"%(self.name,ts))
      try:
        test = self.queue.get(timeout=ts)
      except Queue.Empty:
        test = cs
      cs = test
      file=""
      file = cs['name']
      #path = rootDir + '/' + file
      print_dbg("%s: playing: %s"%(self.name,file))
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
      print_dbg("%s: lVol %f rVol %f lRatio %f rRatio %f"%(self.name,lVol,rVol,self.lRatio,self.rRatio))
      event = {}
      event['vol'] = v
      event['factor'] = factor
      event['file'] = file
      print_dbg("Sound baseTime:%d"%SoundFile().baseTime)
      event['time'] = time.time() - SoundFile().baseTime
      self.playList['events'].append(event)
      playSound(sound,lVol,rVol)
      ts = random.randint(Specs().s['eventMin'],Specs().s['eventMax'])/1000.0;
      
      
    print("schlub thread " + self.name + " exiting")
    
