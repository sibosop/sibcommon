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
from recogOutput import RecogOutput
import threading
from singleton import Singleton
import Queue
from threadMgr import ThreadMgr

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
      })
    self.threads=[]
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
    ro = RecogOutput()
    ra = RecogAnalyzer(ro)
    rc = Recog(ra)
    rec = Recorder(rc)
    self.threads.append(ro)
    self.threads.append(ra)
    self.threads.append(rc)
    self.threads.append(rec)
    for t in self.threads:
      ThreadMgr().start(t)
      
    
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
      if msg == "__stop__":
        self.running = False
      elif msg == "__halt__":
        self.doHalt()
      elif msg == "__start__":
        self.doStart()
        
    print("%s: stopping"%self.name)
    self.doHalt()
    