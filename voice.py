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


class Voice(threading.Thread):
  __metaclass__ = Singleton
  def __init__(self):
    super(Voice,self).__init__()
    self.name = "Voice"
    self.queue = Queue.Queue()
    self.voiceMinVol=.7
  
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
    while True:
      reps = 0
      if random.randint(0,1) == 0:
        reps = random.randint(2,4)
      else:
        reps = 1
      Debug().p("reps on next: %d"%reps)
      for i in range(reps):
        l = (random.random()*(voiceMaxVol-self.voiceMinVol))+self.voiceMinVol
        r = (random.random()*(voiceMaxVol-self.voiceMinVol))+self.voiceMinVol
        try:
          vt = self.queue.get(timeout=ts)
          Debug().p("voice track change")
        except Queue.Empty:
          pass
        playSound(vt,l,r)
        if reps > 1:
          ts = random.random()
        else:
          ts = random.randint(5,10)
          
          

