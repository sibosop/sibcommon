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
from singleton import Singleton


class PhraseHandler(object):
  __metaclass__ = Singleton
  def __init__(self):
    super(phraseThread,self).__init__()
    self.name = "PhraseHandler"
    print("starting: %s"%self.name)
    Watchdog().add(self)
    self.hasDisplay = Hosts().getLocalAttr("hasDisplay")
    self.displayType = Hosts().getLocalAttr("displayType")
    self.hasVoice = Hosts().getLocalAttr("hasVoice")
    self.queue = Queue.Queue()

  def setPhrase(self,args):
    print("%s setting phrase to %s"%(name,args['phrase']))
    self.queue.put(args)
    return Host().jsonStatus("ok")
  
  def run(self):
    print "%s starting"%self.name
    splash = Specs().s['splashImg']
    if self.hasDisplay:
      print("%s displaying f:%s"%(name,splash))
      Display().image(splash)
    while True:
      Watchdog().feed(self)
      p = self.queue.get()
      print("%s Displaying Phrase %s"%(self.name,p['phrase']))
      if self.hasDisplay and self.displayType == "Phrase":
        Display().text(p['phrase'])
      if self.hasVoice:
        Voice().sendPhrase(p)

