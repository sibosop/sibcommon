#!/usr/bin/env python
import threading
from Queue import Queue
import time
import sys
import os

import time
import urllib2
import words
import random
import json

from singleton import Singleton
from debug import Debug
from hosts import Hosts


class RecogOutput(threading.Thread):
  __metaclass__ = Singleton
  def __init__(self):
    super(RecogOutput,self).__init__()
    self.name = "RecogOutput"
    self.queue = Queue()
    recog = Hosts().getLocalAttr('recog')
    self.chokeTime = recog['chokeTime']
    self.listMax = recog['listMax']
    
  def run(self):
    print("starting: "+self.name)
    list = []
    changed = False
    seq = []
    hosts = Hosts().getHosts()
    needsVoice = False
    for ip in Hosts().getHostIps():
      recog = Hosts().getAttr(ip,"recog")
      if recog['enabled'] and recog['phrase']:
        phr = Hosts().getAttr(ip,"phase")
        if phr[voice]:
          needsVoice = True
        Debug().p("%s found recog phrase:"%(self.name,ip))
        seq.append(ip)
      
    while True:
      try:
        input = self.queue.get()
        Debug().p("%s got %s"%(self.name, input))
        if input == "__stop__":
          print("%s stopping"%(self.name))
          break
          
        if input not in list:
          list.append(input)
          if len(list) > self.listMax:
            del list[0]
          changed = True

        if changed:
          changed = False
          print(self.name+": "+str(list))
          sendString = ""
          for w in list:
            sendString += " " + w
          if len(seq) != 0:
            phraseArgs = {}
            phraseArgs['phrase'] = sendString
            if needsVoice:
              try:
                lang = random.choice(Specs().s['langList'])
                file=textSpeaker.makeSpeakFile(sendString,lang)
                if file is None:
                  print("Make Speak File error, skipping")
                else:
                  with open(file,"rb") as sf:
                    phraseArgs['phraseData'] = base64.b64encode(sf.read())
                  os.unlink(file)
              except Exception, e:
                print("getting voice data error: %s"%s)
            for ip in seq:
              phr = Hosts().getAttr(ip,'phrase')
              args
              if phr['voice']:
                try:
                  lang = random.choice(Specs().s['langList'])
                  file=textSpeaker.makeSpeakFile("%s %s"%(choices[0],choices[1]),lang)
                  if file is None:
                    print("Make Speak File error, skipping")
                  else:
                    with open(file,"rb") as sf:
                      phraseArgs['phraseData'] = base64.b64encode(sf.read())
                    os.unlink(file)
                except Exception, e:
                  print("getting voice data error: %s"%s)
        if self.chokeTime == 0:
          pass
        else:
          time.sleep(self.chokeTime)
      except Exception as e:
        print("%s Error: %s"%(self.name,repr(e)));
      
          

  def get(self):
    return self.queue.get()

  
