#!/usr/bin/env python
import os
import sys
home = os.environ['HOME']
proj = home+"GitProjects/iAltar"
sys.path.append(proj+"/iAltar")
sys.path.append(proj+"/config")
sys.path.append(proj+"/common")
import json
import config
import threading
import host
import time
import displayImage
import watchdog
import textSpeaker
import voice

phraseMutex = threading.Lock()
phrase = {}

name = "Phrase Handler"
def setPhrase(args):
  global phrase
  p = args
  print("%s setting phrase to %s"%(name,p['phrase']))
  phraseMutex.acquire()
  phrase=p
  phraseMutex.release()
  return host.jsonStatus("ok")

def getPhrase():
  global phrase
  rval = []
  phraseMutex.acquire()
  rval = phrase
  phraseMutex.release()
  return rval

class phraseThread(threading.Thread):
  def __init__(self,watchdog):
    super(phraseThread,self).__init__()
    self.name = "phraseThread"
    print("starting: %s"%self.name)
    self.watchdog = watchdog
    self.watchdog.add(self)
    self.hasDisplay = host.getLocalAttr("hasDisplay")
    self.displayType = host.getLocalAttr("displayType")
    self.hasVoice = host.getLocalAttr("hasVoice")

  def run(self):
    print "%s starting"%self.name
    lastPhrase = {}
    splash = "%s/%s"%(home,config.specs['splashImg'])
    if self.hasDisplay:
      print("%s displaying f:%s"%(name,splash))
      displayImage.displayImage(splash)
    while True:
      self.watchdog.feed(self)
      p = getPhrase()
      if p != lastPhrase:
        print("%s Displaying Phrase %s"%(self.name,p['phrase']))
        if self.hasDisplay and self.displayType == "Phrase":
            displayImage.printText(p['phrase'])
        if self.hasVoice:
          voice.sendPhrase(p)
        lastPhrase = p
      time.sleep(1)

