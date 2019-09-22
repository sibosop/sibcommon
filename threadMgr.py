#!/usr/bin/env python

from singleton import Singleton
import time

class ThreadMgr(object):
  __metaclass__ = Singleton
  def __init__(self):
    self.tlist = {}
    self.name = "ThreadMgr"
    self.daemon = False
  
  def start(self,t):
    self.tlist[t.name] = t
    t.setDaemon(self.daemon)
    t.start()
    
  def stop(self,t):
    if t.isAlive():
      print("%s: stopping %s"%(self.name,t.name))
      t.queue.put("__stop__")
      errorCnt = 5
      while t.isAlive() and errorCnt != 0:
        if not self.daemon:
          t.join(5)
        else:
          time.sleep(2)
          
        if t.isAlive():
          print ("%s: waiting for %s to stop count %d"%(self.name,t.name,errorCnt))
          errorCnt = errorCnt - 1
        else:
          print ("%s: thread stopped %s"%(self.name,t.name))
    else:
      print("%s: thread %s already dead"%(self.name,t.name))
    del self.tlist[t.name]
      
  def stopByName(self,n):
    try:
      self.stop(self.tlist[n])
    except NameError:
      print("%s: thread %s isn't managed"%(self.name,n))
      
  def stopAll(self):
    for k in self.tlist.keys():
      self.stop(self.tlist[k])
  