#!/usr/bin/env python
import os
import sys
import random
import threading
from soundUtils import playSound
from textSpeaker import makeSpeakFile
import time
import pygame
import base64
import Queue
from debug import Debug
from singleton import Singleton
from specs import Specs
from server import Server
from hosts import Hosts

class Voice(threading.Thread):
  __metaclass__ = Singleton
  def __init__(self):
    super(Voice,self).__init__()
    self.name = "Voice"
    self.queue = Queue.Queue()
    self.voiceMinVol=.7
    self.halted = True
    self.running = True
    if Hosts().getLocalAttr('hasServer'):
      Server().register({
        'StartVoice' : self.startVoice
        ,'HaltVoice' : self.haltVoice
      })
  def startVoice(self,cmd):
    self.queue.put("__start__")
    return Hosts.jsonStatus("ok")
    
  def haltVoice(self,cmd):
    self.queue.put("__halt__")
    return Hosts.jsonStatus("ok")
    
  def sendPhrase(self,args):
    p = args['phrase']
    speakText = p[0]+" "+p[1]
    file=None
    if 'phraseData' in args:
      Debug().p("decoding voice file data from args")
      file = "%s/%s_%s.mp3"%(Specs().s['tmpdir'],p[0],p[1])
      Debug().p("decoding to file %s"%file)
      with open(file, 'wb') as f:
        f.write(base64.b64decode(args['phraseData']))
    else:
      while file is None:
        lang = random.choice(config.specs['langList'])
        file=textSpeaker.makeSpeakFile(speakText,lang)
    Debug().p( "voice sound set to: %s"%file)
    voiceSound = pygame.mixer.Sound(file)
    self.queue.put(voiceSound)
    Debug().p("checkText unlinking: %s voiceSound: %s"%(file,voiceSound))
    os.unlink(file)
  
    
  def run(self):
    voiceMaxVol = Specs().s['voiceMaxVol']
    ts = None
    vt = None
    while self.running:
      try:
        msg = self.queue.get(timeout=ts)
        if type(msg) is str:
          if msg == "__stop__":
            print("%s stopping"%self.name)
            self.running = False
          elif msg == "__halt__":
            self.halted = True
            print("%s halting"%self.name)
            ts = None
          elif msg == "__start__":
            self.halted = False
            print("%s starting"%self.name)
            ts = .1
          continue
        Debug().p("voice track change")
        vt = msg
      except Queue.Empty:
        pass
      if vt==None or self.halted:
        continue
        
      reps = 0
      if random.randint(0,1) == 0:
        reps = random.randint(2,4)
      else:
        reps = 1
      Debug().p("reps on next: %d"%reps)
      for i in range(reps):
        l = (random.random()*(voiceMaxVol-self.voiceMinVol))+self.voiceMinVol
        r = (random.random()*(voiceMaxVol-self.voiceMinVol))+self.voiceMinVol
        playSound(vt,l,r)
        if reps > 1:
          ts = random.random()
        else:
          ts = random.randint(5,10)
          
          

