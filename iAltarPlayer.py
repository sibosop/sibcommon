#!/usr/bin/env python
import os
import sys
import threading
import time
import random
import base64
import json
import requests
import re
import urllib2
import datetime
import traceback
import ssl
import base64
from httplib import BadStatusLine

from textSpeaker import makeSpeakData
from archive import Archive
from imageHandler import ImageHandler
from specs import Specs
from hosts import Hosts
from phraseHandler import PhraseHandler
from googleSearch import Search
from watchdog import Watchdog
from words import Words
from singleton import Singleton
from debug import Debug
from server import Server
import Queue
from utils import doGetRecog


class iAltar(threading.Thread):
  __metaclass__ = Singleton
  def __init__(self):
    super(iAltar,self).__init__()
    self.name = "iAltarPlayer"
    print("starting: %s"%self.name)
    self.searchType = Specs().s['defaultSearchType'];
    print("%s: default search type: %s"%(self.name,self.searchType))
    Watchdog().add(self)
    if Hosts().getLocalAttr("hasServer"):
        Server().register({'Search' : self.setSearchType})
    self.queue = Queue.Queue()
    
    
    
  def setSearchType(self,args):
    self.searchType = args['type']
    Debug().p("%s set Search Type to %s"%(self.name,self.searchType))
    Archive().reset()
    return Hosts.jsonStatus("ok")

  @staticmethod
  def setImgData(fname):
    with open(fname,"rb") as ImageFile:
      d = {}
      d['name'] = os.path.basename(fname)
      d['img'] = base64.b64encode(ImageFile.read())
      return d
      
  @staticmethod
  def urlsToImages(urls):
    cdir = Archive().clearArchive()
    imageCount = 0
    images = []
    for url in urls:
      Debug().p( "url:%s"%url)
      imageTypes=['full','thumb']
      raw_img=None
      for t in imageTypes:
        try:
          Debug().p( "open image type: %s image: %s"%(t,url[t]))
          response=requests.get(url[t],timeout=20)
          raw_img = response.content
          break;
        except Exception as e:
          traceback.print_exc()
          print "return from exception for type %s url %s: %s"%(t,url[t],e)
          continue
      if raw_img != None:
        fname = "%s/urlimage%d.jpg"%(cdir,imageCount)
        imageCount += 1
        f = open(fname,"wb")
        f.write(raw_img)
        f.close()
        images.append(fname)
    return images
  
  def run(self):
    print("%s in run loop"%self.name)
    hosts = Hosts().getHosts()
    imageHosts = []
    phraseHosts = []
    lastCacheId = 0
    for h in hosts:
      ip = h['ip']
      if Hosts().isLocalHost(ip):
        ImageHandler.clearCache(None)
      else:
        Hosts().sendToHost(ip,{'cmd' : 'ClearCache' , 'args' : None});
      iAltar = Hosts().getAttr(ip,'iAltar')
      if iAltar['enabled']:
        if iAltar['image']:
          Debug().p("%s: display type for %s: image"%(self.name,ip))
          imageHosts.append(ip)
        if iAltar['phrase']:
          Debug().p("%s: wants phrase for %s: "%(self.name,ip))
          phraseHosts.append(ip)
    sleepTime = .001      
    while True:
      try:
        Debug().p("%s: sleeping %d"%(self.name,sleepTime))
        msg = self.queue.get(timeout=sleepTime)
        if msg == "__stop__":
          print("%s: stopping"%self.name)
        break
      except Queue.Empty:
        pass
      
      Watchdog().feed(self)
      cacheId = random.randint(10000,20000)
      images=[]
      choices=[]
      urls=[]
      if  self.searchType == 'Archive':
        [images,choices] = Archive().getArchive()
        for i in images:
          Debug().p("%s: image %s"%(self.name,i))
        for c in choices:
          Debug().p("%s: choice %s"%(self.name,c))
      elif self.searchType == 'Google':
        choices = []
        msg = doGetRecog('')
        if msg != "":
          test = json.loads(msg)
          Debug().p("%s got %s"%(self.name,test))
          if test['recog'] != ["",""]:
            choices = test['recog'] 
            Debug().p["%s choices from recog %s"%(self.name,choices)]
        if len(choices) == 0:
          choices = Words().getWords()
        urls = Search().getUrls(choices)
        if urls == None:
          Debug().p("%s Google Error switching to Archive"%self.name)
          self.searchType = "Archive"
          continue
        if len(urls) == 0:
          Debug().p("%s Nothing found try again"%self.name)
          continue
        images = self.urlsToImages(Search().getUrls(choices));
      else:
        Debug().p("%s unimplemented type %s switching to archive"%(self.name,searchType))
        self.searchType = 'Archive'
      if self.searchType != 'Archive':
        Archive().putArchive(choices)

      phraseArgs = {}
      if len(phraseHosts) != 0:
        phraseArgs['phrase'] = choices
        phraseArgs['phraseData'] = ""
        Debug().p("%s sending %s to %s"%(self.name,choices,ip))
        for ip in phraseHosts:
          phr = Hosts().getAttr(ip,'phrase')
          if phr['voice']:
            lang = random.choice(Specs().s['langList'])
            phraseArgs['phraseData'] = makeSpeakData("%s %s"%(choices[0],choices[1]),lang)
            
        #os.unlink(file.replace("mp3","wav"));
    

      if len(imageHosts) != 0:
        numImages = len(images)
        imagesPerHost = numImages/len(imageHosts)
        extraImages = numImages % len(imageHosts)
        extra = 0
        count = 0
        Debug().p(
              "%s numImages:%d imagesPerHost:%d extraImages:%d"
              %(self.name,numImages,imagesPerHost,extraImages))
        for ip in imageHosts:
          args = {}
          args['id'] = cacheId
          args['imgData'] = []
          for i in range(0,imagesPerHost):
            fname = images[i+count]
            args['imgData'].append(self.setImgData(fname))
          count += imagesPerHost
          if extra < extraImages:
            fname = images[count+extra]
            args['imgData'].append(self.setImgData(fname))
            extra += 1
          cmd = {'cmd' : "AddImage", 'args' : args}
          if Hosts().isLocalHost(ip):
            ImageHandler().addImage(args)
          else:
            Hosts().sendToHost(ip,cmd)


        for ip in imageHosts:
          args =[cacheId]
          if Hosts().isLocalHost(ip):
            ImageHandler().setImageDir(args)
          else:
            Hosts().sendToHost(ip,{'cmd' : 'SetImageDir' , 'args' : args});

        if lastCacheId != 0:
          for ip in imageHosts:
            args =[lastCacheId]
            if Hosts().isLocalHost(ip):
              ImageHandler.rmCacheDir(args)
            else:
              Hosts().sendToHost(ip,{'cmd' : 'RmCacheDir' , 'args' : args});
        lastCacheId = cacheId

      if len(phraseHosts) != 0:
        for ip in phraseHosts:
          if Hosts().isLocalHost(ip):
            PhraseHandler().setPhrase(phraseArgs)
          else:
            Hosts().sendToHost(ip,{'cmd' : 'Phrase' , 'args' : phraseArgs});
    
      sleepTime = Specs().s['iAltarSleepInterval']  
    
    
