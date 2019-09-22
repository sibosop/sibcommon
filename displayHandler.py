#!/usr/bin/env python
import os
import sys
import json
import base64
import shutil
import threading
import glob
import time
import random
import Queue

from watchdog import Watchdog
from specs import Specs
from debug import Debug
from hosts import Hosts
from utils import mkpath
from singleton import Singleton
from server import Server
from display import Display

class DisplayHandler(threading.Thread):
  __metaclass__ = Singleton
  def __init__(self):
    super(DisplayHandler,self).__init__()
    self.name = "DisplayHandler"
    print("starting: %s"%self.name)
    Watchdog().add(self)
    self.currentId = None
    self.queue = Queue.Queue()
    if Hosts().getLocalAttr('hasServer'):
      Server().register({
        'AddImage' : self.addImage
        ,'RmCacheDir' : self.rmCacheDir
        ,'SetImageDir' : self.setImageDir
        ,'ClearCache' : self.clearCache
      })
      
    
  def setImageDir(self,args):
    rval = "ok"
    id = args[0]
    path = self.getCacheDir(id)
    self.queue.put(path)
    print("SetImageDir to %s: %s"%(path,rval))
    return Hosts.jsonStatus(rval)
    
  def addImage(self,args):
    id = args['id']
    imgData = args['imgData']
    if self.currentId is None or self.currentId != id:
      self.currentId = id
    print("addImage currentId: %d"%self.currentId)
    path = self.getCacheDir(self.currentId)
    for d in imgData:
      file = path + "/%s"%d['name']
      print("---name: %s"%file)
      with open(file, 'wb') as f:
        f.write(base64.b64decode(d['img']))
    return Hosts.jsonStatus("ok");
  
  @staticmethod 
  def getCacheDir(id):
    path = "%s/%d"%(DisplayHandler.getImageCache(),id)
    return mkpath(path)
    
  @staticmethod 
  def getCacheDir(id):
    path = DisplayHandler.getImageCache()+"/%d"%id
    return mkpath(path)
  
  @staticmethod 
  def rmCacheDir(args):
    rval = "ok"
    id = args[0]
    path = DisplayHandler.getCacheDir(id)
    try:
      shutil.rmtree(path)
    except OSError as e:
      rval = "Error: %s - %s." % (e.filename, e.strerror)
    print("rmCacheDir: path %s %s"%(path,rval))
    return Hosts.jsonStatus(rval)
    
  @staticmethod
  def getImageCache():
    path = "%s/imageCache"%(Specs().s['tmpdir'])
    return mkpath(path)
  
  @staticmethod 
  def clearCache(args):
    path = DisplayHandler.getImageCache()
    for f in os.listdir(path):
      try:
        r = path+"/%s"%f
        print("rm: %s"%r)
        shutil.rmtree(path)
      except OSError as e:
        rval = "Error: %s - %s." % (e.filename, e.strerror)
    return Hosts.jsonStatus("ok")
  

  def run(self):
    print ("%s starting"%self.name)
    afiles = []
    (minTime,maxTime) = Specs().s["displayTimeRange"]
    lastImageDir=""
    imageIndex=0
    splash = Specs().s['splashImg']
    print("displaying f:%s"%splash)
    Display().image(splash)
    ts = None
    while True:
      Watchdog().feed(self)
      try:
        path = self.queue.get(timeout=ts)
      except Queue.Empty:
        path = lastImageDir
        
      if path == "__stop__":
        print("%s is stopping"%self.name)
        break
        
      print("%s: path %s lastImageDir %s"%(self.name,path,lastImageDir))
      if path != lastImageDir:
        print("%s reseting imageIndex"%self.name)
        imageIndex = 0
        lastImageDir = path
        if len(afiles) == 0:
          print("empty image file. waiting")
          ts = 1
          continue
      afiles=glob.glob(path+"/*.jpg")
      numFiles = len(afiles)
      if numFiles == 0:
        print("%s directory empty!!"%self.name)
        print("displaying f:%s"%splash)
        Display().image(splash)
        ts = 1
        continue
      print("imageIndex %d len afiles %d"%(imageIndex,numFiles))
      if imageIndex >= numFiles:
        print("resetting imageIndex");
        imageIndex = 0
      f = afiles[imageIndex]
      imageIndex += 1
      print("displaying f:%s"%f)
      if Display().image(f) == False:
        print "skipping bad images:%s"%f
        ts = .1
        continue
      ts = (random.random() * (maxTime - minTime)) + minTime
      print("next display %f"%ts)
      

      

    



