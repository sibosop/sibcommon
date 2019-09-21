#!/usr/bin/env python
import os
import sys
import json
import threading
import time
import Queue

from display import Display
from hosts import Hosts
from specs import Specs
from watchdog import Watchdog
import textSpeaker
from voice import Voice
from server import Server
from singleton import Singleton
from debug import Debug

class PhraseHandler(threading.Thread):
  __metaclass__ = Singleton
  def __init__(self):
    super(PhraseHandler,self).__init__()
    self.name = "PhraseHandler"
    print("starting: %s"%self.name)
    Watchdog().add(self)
    self.hasDisplay = Hosts().getLocalAttr("hasDisplay")
    self.displayType = Hosts().getLocalAttr("displayType")
    self.hasVoice = Hosts().getLocalAttr("hasVoice")
    self.queue = Queue.Queue()
    if Hosts().getLocalAttr("hasServer"):
      Server().register({'Phrase' : self.setPhrase})

  def setPhrase(self,args):
    Debug().p("%s setting phrase to %s"%(self.name,args['phrase']))
    self.queue.put(args)
    return Hosts().jsonStatus("ok")
  
  def run(self):
    print "%s starting"%self.name
    splash = Specs().s['splashImg']
    if self.hasDisplay:
      Debug().p("%s displaying f:%s"%(self.name,splash))
      Display().image(splash)
    while True:
      Watchdog().feed(self)
      p = self.queue.get()
      if type(p) == 'str' and p == "__stop__":
        print("%s stopping"%p.name)
        break
      Debug().p("%s Displaying Phrase %s"%(self.name,p['phrase']))
      if self.hasDisplay and self.displayType == "Phrase":
        Display().text(p['phrase'])
      if self.hasVoice:
        Voice().sendPhrase(p)

