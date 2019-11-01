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
from panel import Panel


class PhraseHandler(threading.Thread):
  __metaclass__ = Singleton
  def __init__(self):
    super(PhraseHandler,self).__init__()
    self.name = "PhraseHandler"
    print("starting: %s"%self.name)
    Watchdog().add(self)
    self.phrase = Hosts().getLocalAttr("phrase")
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
    if self.phrase['image']:
      Debug().p("%s displaying f:%s"%(self.name,splash))
      Display().image(splash)
    while True:
      if Watchdog().isAlive():
        Watchdog().feed(self)
      p = self.queue.get()
      if type(p) is str and p == "__stop__":
        print("%s stopping"%self.name)
        break
      Debug().p("%s Displaying Phrase %s"%(self.name,p['phrase']))
      if self.phrase['image']:
        Display().text(p['phrase'])
      if self.phrase['voice']:
        if Voice().isAlive():
          Voice().sendPhrase(p)
        else:
          print("%s: %s is dead"%(self.name,Voice().name))
      if self.phrase['panel']:
        Panel().printText(p['phrase'])


