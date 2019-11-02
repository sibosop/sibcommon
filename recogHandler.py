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
    self.recog = [None,None]
    self.threads=[]
    self.phraseIps = []
    for ip in Hosts().getHostIps():
      recog = Hosts().getAttr(ip,'recog')
      if recog['enabled'] and recog['phrase']:
        self.phraseIps.append(ip)
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
    for t in self.threads:
      ThreadMgr().start(t)
      
  def getRecog(self,cmd):
    Debug().p("starting recog")
    recog = {}
    recog['status'] = "ok"
    recog['recog'] = self.recog
    return json.dumps(recog)
    
  def startRecog(self,cmd):
    Debug().p("starting recog")
    self.queue.put("__start__")
    return Hosts.jsonStatus("ok")
    
  def haltRecog(self,cmd):
    Debug().p("halting recog")
    self.queue.put("__halt__")
    return Hosts.jsonStatus("ok")
    
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
        self.recog = msg
        Debug().p("%s got recog: %s"%(self.name,self.recog))
        cmd = { 'cmd' : "Phrase", 'args' : {"phrase" : self.recog}}
        for ip in self.phraseIps:
          Debug().p("%s: ip %s sending %s"%(self.name,ip,cmd))
          Hosts().sendToHost(ip,cmd)
          
          
        
        
    print("%s: stopping"%self.name)
    self.doHalt()
    