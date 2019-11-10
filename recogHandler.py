#!/usr/bin/env python
import os
import sys
from debug import Debug
from singleton import Singleton
from hosts import Hosts
from server import Server
from display import Display
from recorder import Recorder
from recog import Recog
from recogAnalyzer import RecogAnalyzer
import threading
from singleton import Singleton
import Queue
from threadMgr import ThreadMgr
import json
from specs import Specs
import random
from textSpeaker import makeSpeakData

class RecogHandler(threading.Thread):
  __metaclass__ = Singleton
  def __init__(self):
    super(RecogHandler,self).__init__()
    self.name = "RecogHandler"
    print("starting: %s"%self.name)
    self.queue = Queue.Queue()
    if Hosts().getLocalAttr('hasServer'):
      Server().register({
        'StartRecog' : self.startRecog
        ,'HaltRecog' : self.haltRecog
        ,'GetRecog' : self.getRecog
      })
    self.threads=[]
    self.finalIps = []
    self.searchIps = []
    for ip in Hosts().getHostIps():
      recog = Hosts().getAttr(ip,'recog')
      if recog['enabled'] and recog['phrase'] == "final":
        Debug().p("%s ip %s wants final phrase"%(self.name,ip))
        self.finalIps.append(ip)
      if recog['enabled'] and recog['phrase'] == "search":
        Debug().p("%s ip %s wants search phrase"%(self.name,ip))
        self.searchIps.append(ip)
    self.running = True
    Display().text("Recog not Running")
      
  def doHalt(self):
    Debug().p("%s do Halt")
    if len(self.threads) != 0:
      for t in self.threads:
        ThreadMgr().stop(t)
        del t
      self.threads = []  
    Display().text("Recog not Running")
    
  def doStart(self):
    Debug().p("%s do Start")
    self.doHalt()
    ra = RecogAnalyzer(self)
    rc = Recog(ra)
    rec = Recorder(rc)
    self.threads.append(ra)
    self.threads.append(rc)
    self.threads.append(rec)
    self.recog = []
    for t in self.threads:
      ThreadMgr().start(t)
    Display().text("Recog Running")
      
  def getRecog(self,cmd):
    Debug().p("getting recog")
    msg = {}
    msg['status'] = "ok"
    msg['recog'] = ["",""]
    if len(self.threads) != 0:
      msg['recog'] = self.recog
    rval =  json.dumps(msg)
    self.recog = ["",""]
    return rval
    
    
  def startRecog(self,cmd):
    Debug().p("starting recog")
    self.queue.put("__start__")
    return Hosts.jsonStatus("ok")
    
  def haltRecog(self,cmd):
    Debug().p("halting recog")
    self.queue.put("__halt__")
    return Hosts.jsonStatus("ok")
  
  def sendPhrase(self,ip,text):
    lang = random.choice(Specs().s['langList'])
    phr = Hosts().getAttr(ip,'phrase')
    args = {}
    args["phrase"] = text
    if phr['voice']:
      args["phraseData"] = makeSpeakData("%s %s"%(text[0],text[1]),lang)
    else:
      args["phraseData"] = "" 
    cmd = { 'cmd' : "Phrase", 'args' : args}
    Debug().p("%s: ip %s sending %s"%(self.name,ip,args['phrase'])) 
    Hosts().sendToHost(ip,cmd)
    
  def run(self):
    print("%s: starting thread"%self.name)
    while self.running:
      msg = self.queue.get()
      if type(msg) is str:
        if msg == "__stop__":
          self.running = False
        elif msg == "__halt__":
          self.doHalt()
        elif msg == "__start__":
          self.doStart()
      else:
        #Debug().p("%s got recog: %s"%(self.name,msg))
        for ip in self.searchIps:
          c = 0
          text =""
          for w in msg['search']:
            if len(w) != 0:
              c+=1
          if c == 2:
            self.sendPhrase(ip,msg['search'])
            self.recog = msg['search']
            
        for ip in self.finalIps:
          #Debug().p("%s: ip %s sending %s"%(self.name,ip,cmd))
          self.sendPhrase(ip,msg['final'])
          
          
        
        
    print("%s: stopping"%self.name)
    self.doHalt()
    
