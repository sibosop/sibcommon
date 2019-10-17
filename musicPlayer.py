#!/usr/bin/env python

import threading
import time
import subprocess
import glob
import random
import json
import os
import sys
import traceback
import urllib2
from soundFile import SoundFile
import pygame
from debug import Debug
from soundTrack import SoundTrackManager
from specs import Specs
from hosts import Hosts
import Queue


class MusicPlayer(threading.Thread):
  def __init__(self):
    super(MusicPlayer,self).__init__()
    self.done = False
    self.name= "MusicPlayer"
    self.running = None
    self.mutex = threading.Lock()
    self.queue = Queue.Queue()
    
    
  def stop(self):
    print_dbg("%s: stop request"%self.name)
    self.setRunning(False)
    
  def setRunning(self,flag):
    self.mutex.acquire()
    self.running = flag
    self.mutex.release()
    return flag
    
  def isRunning(self):
    self.mutex.acquire()
    flag = self.running
    self.mutex.release()
    return flag
    
  def checkStop(self):
    try:
      msg = self.queue.get(timeout=1)
      if msg == "__stop__":
        self.doExit()
        return True
    except Queue.Empty:
      pass
    return False
    
  def doExit(self):
      print ("%s done"%self.name)
      for t in SoundTrackManager().eventThreads:
        t.stop()
      self.done = True
      
  def run(self):
    print("%s starting"%self.name)
    stime = time.time()
    self.setRunning(SoundFile().testBumpCollection())
    loop = Specs().s['musicLoop']
    while self.isRunning():
      if self.checkStop():
        return
        
      if time.time() > stime:
        entry = SoundFile().getSoundEntry()
        Debug().p("player choosing %s"%entry)
        count = 0
        for t in SoundTrackManager().eventThreads:
          choice = random.choice(entry)
          Debug().p("sending  %s request to %s"%(choice,t.name))
          t.setCurrentSound(choice)
        for h in Hosts().getHosts():
          ip = h['ip']
          if Hosts().isLocalHost(ip):
            Debug().p("%s: ignoring %s"%(self.name,ip))
            continue
          if h['hasMusic']:
            try:
              url = "http://"+ip+":8080"
              Debug().p("%s: url: %s"%(self.name,url))
              cmd = { 'cmd' : "Sound" ,'args' : choice }
              req = urllib2.Request(url
                      ,json.dumps(cmd),{'Content-Type': 'application/json'})
              timeout = 4
              f = urllib2.urlopen(req,None,timeout)
              test = f.read()
              Debug().p("%s: got response:%s"%(self.name,test))
            except urllib2.URLError as ve:
              Debug().p("%s: got URLError %s on ip:%s"%(self.name,ve,ip))
              continue
            except Exception as e:
              print("%s got exception %s"%(self.name,e))
              continue
        offset = random.randint(Specs().s['minChange'],Specs().s['maxChange'])
        stime = time.time() + offset
        #Debug().p("next change: %d"%offset)
        n = pygame.mixer.get_busy()
        #Debug().p("number busy channels %d"%n
      if SoundFile().testBumpCollection() is False:
        print "waiting for channels to be done"
        n = -1
        while n != 0:
          n = pygame.mixer.get_busy()
          print "number busy channels",n
          if self.checkStop():
            return
        if loop:
          SoundFile().reset()
        else:
          self.SetRunning(false)
    self.doExit()     
    
