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
from soundFile import SoundFile
import pygame
from utils import print_dbg
from soundTrack import SoundTrackManager
from specs import Specs
from hosts import Hosts

class MusicPlayer(threading.Thread):
  def __init__(self):
    super(MusicPlayer,self).__init__()
    self.done = False
    self.name= "MusicPlayer"
    self.running = None
    self.mutex = threading.Lock()
    
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
  def run(self):
    print("%s starting"%self.name)
    stime = time.time()
    self.setRunning(SoundFile().testBumpCollection())
    while self.isRunning():
      #print_dbg("%s: time %s stime %s"%(self.name,time.time(),stime))
      if time.time() > stime:
        entry = SoundFile().getSoundEntry()
        print_dbg("player choosing %s"%entry)
        count = 0
        for t in SoundTrackManager().eventThreads:
          choice = random.choice(entry)
          print_dbg("sending  %s request to %s"%(choice,t.name))
          t.setCurrentSound(choice)
        for h in Hosts().getHosts():
          ip = h['ip']
          if Hosts.isLocalHost(ip):
            print_dbg("%s: ignoring %s"%(self.name,ip))
            continue
          if h['hasMusic']:
            try:
              url = "http://"+ip+":8080"
              if debug: syslog.syslog("url:"+url)
              cmd = { 'cmd' : "Sound" ,'args' : choice }
              req = urllib2.Request(url
                      ,json.dumps(cmd),{'Content-Type': 'application/json'})
              timeout = 4
              f = urllib2.urlopen(req,None,timeout)
              test = f.read()
              if debug: syslog.syslog("got response:"+test)
            except Exception,u:
              print("%s skipping on error on url %s: %s"%(self.name,url,u))
              continue
        offset = random.randint(Specs().s['minChange'],Specs().s['maxChange'])
        stime = time.time() + offset
        #print_dbg("next change: %d"%offset)
        n = pygame.mixer.get_busy()
        #print_dbg("number busy channels %d"%n)
      time.sleep(1)
      self.setRunning(SoundFile().testBumpCollection())
    print ("%s done"%self.name)
    self.done = True
        
    for t in SoundTrackManager().eventThreads:
      t.stop()
    
