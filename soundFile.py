#!/usr/bin/env python
import collections
import csv
import os
import sys
import glob
import random
import syslog
import copy
import threading
import json
import shutil
import time
from debug import Debug
from singleton import Singleton
from specs import Specs

class SoundFile(metaclass=Singleton):
  def __init__(self):
    self.name="SoundFile"
    self.listMutex=threading.Lock()
    self.maxEvents = 2
    self.collections = {}
    self.currentCollection = None
    self.baseTime = time.time()
    self.index = 0
    self.timeout = 0
    self.rootDir = ""
    self.index = 0
    for k in Specs().s['collections']:
      print("k=%s"%k)
      self.collections[k] = []
      for d in Specs().s[k]:
        self.collections[k].append(d)
        Debug().p("key: %s collection %s"%(k,d))
  
  def setCurrentCollection(self,k=None):
    if k == None:
      k = Specs().s['collections'][0]
    self.currentCollection = k
    self.baseTime = time.time()
    self.timeout = 0
    self.rootDir = ""
    self.index = 0;
    self.timeout = self.collections[k][self.index]['time'] + time.time()
      
  def testBumpCollection(self):
    #Debug().p("testBumpCollection time %d timeout %d"%(time.time(),self.timeout))
    
    if time.time() > self.timeout:
      last = self.collections[self.currentCollection][self.index]
      Debug().p("testBumpCollection timeout passed")
      self.index += 1
      if len(self.collections[self.currentCollection]) == self.index:
        Debug().p("testBumpCollection for %s %s done"%(self.currentCollection,last))
        return False
      cur = self.collections[self.currentCollection][self.index]
      Debug().p("---------------------------------------------")
      Debug().p("NEW CURRENT COLLECTION %s"%cur['name'])
      Debug().p("---------------------------------------------")
      self.timeout = time.time() + cur['time']
      Debug().p("new timeout %d"%self.timeout)
    return True
    
  def goto(self,label):
    newIndex = 0;
    for k in self.collections[self.currentCollection]:
      print(k['name'])
      if (k['name'] == label):
        print("going to label", label, "newIndex", newIndex)
        self.baseTime = time.time()
        self.timeout = 0
        self.rootDir = ""
        self.index = newIndex;
        self.timeout = self.collections[self.currentCollection][self.index]['time'] + time.time()
        return True
      newIndex += 1
      
    return False
  
  def getSoundEntry(self):
    cur = self.collections[self.currentCollection][self.index]
    keys = Specs().s[cur['list']]
    Debug().p("collection-list %s - %s number of keys %d"%(cur['name'],cur['list'],len(keys)))
    done = False
    choices = 0
    numChoices = Specs().s['maxEvents']
    Debug().p("collection: %s number of choices: %d max Events: %d"%(cur['name'],self.maxEvents,numChoices))
    rval = []
    if len(keys) < numChoices:
      for k in keys:
        rval.append(k)
    else:
      while len(rval) < numChoices:
        choice = random.randint(0,len(keys)-1)
        if keys[choice] in rval:
          continue
        rval.append(keys[choice])
    Debug().p("%s: rval %s"%(self.name,rval))
    return rval
  



