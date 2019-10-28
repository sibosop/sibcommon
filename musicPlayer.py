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
from server import Server
import Queue

class MusicBlock(object):
  def __init__(self):
    self.mute = False

class MusicPlayer(threading.Thread):
  def __init__(self,defaultCollection="playerCollection"):
    super(MusicPlayer,self).__init__()
    self.done = False
    self.name= "MusicPlayer"
    self.running = None
    self.mutex = threading.Lock()
    self.queue = Queue.Queue()
    self.collection = defaultCollection
    self.waitTime = None
    self.musicBlocks = {}
    for h in Hosts().getHosts():
      if h['hasMusic']:
        self.musicBlocks[h['ip']] = MusicBlock()
        
    SoundFile().setCurrentCollection(self.collection)
    if Hosts().getLocalAttr("hasServer"):
      Server().register({"HaltMusic" : self.haltMusic
                          ,"StartMusic" : self.startMusic
                          ,"Mute" : self.mute 
                        }) 
    
    
  def stop(self):
    Debug().p("%s: stop request"%self.name)
    self.setRunning(False)
    
  def mute(self,args):
    self.musicBlocks[args['ip']].mute = args['mute']
    return Hosts.jsonStatus(str(args))
    
  def haltMusic(self,cmd):
    self.queue.put("__halt__")
    return Hosts.jsonStatus(str(cmd))
  
  def startMusic(self,cmd):
    self.queue.put("__start__")
    return Hosts.jsonStatus(str(cmd))
    
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
    
  def checkMsg(self):
    rval = False
    try:
      msg = self.queue.get(timeout=self.waitTime)
      if msg == "__stop__":
        self.stop()
      elif msg == "__halt__":
        Debug().p("%s halting"%self.name)
        self.waitTime = None
      elif msg == "__start__":
        Debug().p("%s starting"%self.name)
        self.waitTime = .1
      rval = True
    except Queue.Empty:
      pass
    return rval
    
  def doExit(self):
      print ("%s done"%self.name)
      for t in SoundTrackManager().eventThreads:
        t.stop()
      self.done = True
      
  def run(self):
    print("%s starting"%self.name)
    self.setRunning(SoundFile().testBumpCollection())
    loop = Specs().s['musicLoop']
    while self.isRunning():
      if self.checkMsg():
        continue
      entry = SoundFile().getSoundEntry()
      Debug().p("player choosing %s"%entry)
      count = 0
      if self.musicBlocks[Hosts().getLocalHost()].mute:
        Debug().p("%s local %s mute so ignoring"%(self.name,Hosts().getLocalHost()))
      else:
        for t in SoundTrackManager().eventThreads:
          choice = random.choice(entry)
          Debug().p("sending  %s request to %s"%(choice,t.name))
          t.setCurrentSound(choice)
      for ip in self.musicBlocks.keys():
        if Hosts().isLocalHost(ip):
          Debug().p("%s: ignoring %s"%(self.name,ip))
          continue
        if self.musicBlocks[ip].mute:
          Debug().p("%s: ignoring muted %s %s"%(self.name,ip,self.musicBlocks[ip].mute))
          continue
        try:
          url = "http://"+ip+":8080"
          Debug().p("%s: url: %s"%(self.name,url))
          cmd = { 'cmd' : "Sound" ,'args' : choice }
          req = urllib2.Request(url
                  ,json.dumps(cmd),{'Content-Type': 'application/json'})
          timeout = 1
          f = urllib2.urlopen(req,None,timeout)
          test = f.read()
          Debug().p("%s: got response:%s"%(self.name,test))
        except urllib2.URLError as ve:
          Debug().p("%s: got URLError %s on ip:%s"%(self.name,ve,ip))
          continue
        except Exception as e:
          print("%s got exception %s"%(self.name,e))
          continue
      self.waitTime = random.randint(Specs().s['minChange'],Specs().s['maxChange'])
      Debug().p("next change: %d"%self.waitTime)
      #Debug().p("number busy channels %d"%n
      if SoundFile().testBumpCollection() is False:
        print "waiting for channels to be done"
        n = pygame.mixer.get_busy()
        while n != 0:
          n = pygame.mixer.get_busy()
          print "number busy channels",n
          if self.checkMsg( ):
            continue
        if loop:
          SoundFile().setCurrentCollection(self.collection)
        else:
          self.SetRunning(false)
    self.doExit()     
    
