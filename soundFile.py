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
from utils import print_dbg
from singleton import Singleton
from specs import Specs

class SoundFile(object):
  __metaclass__ = Singleton
  def __init__(self):
    self.baseTime = time.time()
    self.listMutex=threading.Lock()
    self.maxEvents = 2
    self.collections = []
    self.currentCollection = ""
    self.timeout = 0
    self.rootDir = ""
    self.currentCollection = ""
    for d in Specs().s['collections']:
        self.collections.append(d)
  
    print_dbg(self.collections)
    self.currentCollection = self.collections.pop(0)
    print_dbg("currentCollection: %s"%self.currentCollection['name'])

    self.timeout = time.time() + self.currentCollection['time']

      
  def testBumpCollection(self):
    print_dbg("testBumpCollection time %d timeout %d"%(time.time(),self.timeout))
    if time.time() > self.timeout:
      print_dbg("testBumpCollection timeout passed")
      if len(self.collections) == 0:
        return False
    
      self.currentCollection = self.collections.pop(0)
      print_dbg("new current collection %s"%self.currentCollection['name'])
      self.timeout = time.time() + self.currentCollection['time']
      print_dbg("new timeout %d"%self.timeout)
    return True
  
  def getSoundEntry(self):
    keys = Specs().s[self.currentCollection['list']]
    print_dbg("collection-list %s - %s number of keys %d"%(self.currentCollection['name'],self.currentCollection['list'],len(keys)))
    done = False
    choices = 0
    numChoices = Specs().s['maxEvents']
    print_dbg("collection: %s number of choices: %d max Events: %d"%(self.currentCollection['name'],self.maxEvents,numChoices))
    rval = []
    while len(rval) < numChoices:
      choice = random.randint(0,len(keys)-1)
      print_dbg("rval %s"%rval)
      if keys[choice]['name'] in rval:
        continue
      rval.append(keys[choice])
    return rval
  


