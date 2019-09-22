#!/usr/bin/env python
import os
import sys
import pygame
import time
import threading

from specs import Specs
from singleton import Singleton
from debug import Debug
import Queue


class Watchdog(threading.Thread):
  __metaclass__ = Singleton
  def __init__(self):
    super(Watchdog,self).__init__()
    self.wdLock = threading.Lock()
    self.name = "WatchDog"
    self.tlist = {}
    self.timeoutInterval = Specs().s['watchdogTimeout']
    self.queue = Queue.Queue()
    
  def feed(self,t):
    self.wdLock.acquire()
    self.tlist[t] = time.time()
    self.wdLock.release()

  def add(self,t):
    Debug().p ("%s adding %s"%(self.name,t.name))
    self.feed(t)

  def run (self):
    while True:
      try:
        msg = self.queue.get_nowait()
        if msg == "__stop__":
          print("%s stopping"%self.name)
          return
      except Queue.Empty:
        pass
      
      c = time.time()
      for k in self.tlist.keys():
        self.wdLock.acquire()
        tflag = c - self.tlist[k] > self.timeoutInterval
        self.wdLock.release()
        if tflag:
          print ("%s: %s has timed out"%(self.name,k.name))
          os._exit(1)
      time.sleep(.1)


if __name__ == '__main__':
  os.environ['DISPLAY']=":0.0"
  os.chdir(os.path.dirname(sys.argv[0]))
  os.chdir("..") # sigh: get to default app path
  Specs("%s/%s"%("speclib","commontest.json"))
  class Test (threading.Thread):
    def __init__(self,num):
      super(Test,self).__init__()
      self.name = "test thread %d"%num
      Watchdog().add(self)

    def run(self):
      print "thread %s starting"%self.name
      for i in range(4):
        print ("feeding watchdog")
        Watchdog().feed(self)
        time.sleep(1)
      count = 0
      while (True):
        print ("waiting for dog %d"%count)
        count = count + 1
        time.sleep(1)
        

  wd = Watchdog()
  wd.setDaemon(True)
  wd.start()
  test = Test(1)
  test.setDaemon(True)
  test.start()
  while True:
    time.sleep(5)



