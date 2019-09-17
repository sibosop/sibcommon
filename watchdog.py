#!/usr/bin/env python
import os
import sys
home = os.environ['HOME']
proj = home+"GitProjects/iAltar"
sys.path.append(proj+"/iAltar")
sys.path.append(proj+"/config")
sys.path.append(proj+"/common")
sys.path.append(proj+"/server")
import pygame
import time
import host
import config
import threading



class WatchdogThread(threading.Thread):
  def __init__(self):
    super(WatchdogThread,self).__init__()
    self.wdLock = threading.Lock()
    self.name = "WatchDog"
    self.tlist = {}
    self.timeoutInterval = config.specs['watchdogTimeout']

  def feed(self,t):
    self.wdLock.acquire()
    self.tlist[t] = time.time()
    self.wdLock.release()

  def add(self,t):
    print "%s adding %s"%(self.name,t.name)
    self.feed(t)

  def run (self):
    while True:
      c = time.time()
      for k in self.tlist.keys():
        self.wdLock.acquire()
        tflag = c - self.tlist[k] > self.timeoutInterval
        self.wdLock.release()
        if tflag:
          print "%s: %s has timed out"%(self.name,k.name)
          os._exit(1)
      time.sleep(.1)


if __name__ == '__main__':
  config.load()
  class Test (threading.Thread):
    def __init__(self,num,watchdog):
      super(Test,self).__init__()
      self.name = "test thread %d"%num
      self.wdList = {}
      self.watchDog = watchdog 
      self.watchDog.add(self)

    def run(self):
      print "thread %s starting"%self.name
      for i in range(4):
        print "feeding watchdog"
        self.watchDog.feed(self)
        time.sleep(1)
      while (True):
        print "waiting for dog"
        time.sleep(1)
        

  wd = WatchdogThread()
  wd.setDaemon(True)
  wd.start()
  test = Test(1,wd)
  test.setDaemon(True)
  test.start()
  while True:
    time.sleep(5)



