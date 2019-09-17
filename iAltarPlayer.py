#!/usr/bin/env python
import os
import sys
import threading
import time
import archive
import displayHandler
import random
from specs import Specs
from hosts import Hosts
import base64
import phraseHandler
import googleSearch
import words
import json
import requests
import re
import urllib2
import datetime
import traceback
import ssl
import watchdog
import base64
import textSpeaker


searchType=None

def setSearchType(t):
  global searchType
  searchType = t[0]
  archive.init = False;
  return host.jsonStatus("ok")

def setImgData(fname):
  with open(fname,"rb") as ImageFile:
    d = {}
    d['name'] = os.path.basename(fname)
    d['img'] = base64.b64encode(ImageFile.read())
  return d

def urlsToImages(urls):
  cdir = archive.clearArchive()
  imageCount = 0
  images = []
  for url in urls:
    if debug: print( "url:%s"%url)
    imageTypes=['full','thumb']
    raw_img=None
    for t in imageTypes:
      try:
        #startTime = time.time()
        if debug: print( "open image type:"+t+" image:",url[t] )
        response=requests.get(url[t],timeout=20)
        #req = urllib2.Request(url[t],headers={'User-Agent' : "Magic Browser"})
        #gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        #con = urllib2.urlopen( req, context=gcontext,timeout=20)
        raw_img = response.content
        #raw_img = urllib2.urlopen(images[imageIndex]).read()
        #if debug: print( "elapsed:"+str(time.time() - startTime))
        break;
      except Exception as e:
        print "return from exception for type %s url %s: %s"%(t,url[t],e)
        #print("elapsed:"+str(time.time() - startTime))
        #print(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        #print(traceback.format_exc())
        continue;
    if raw_img != None:
      fname = "%s/urlimage%d.jpg"%(cdir,imageCount)
      imageCount += 1
      f = open(fname,"wb")
      f.write(raw_img)
      f.close()
      images.append(fname)
  return images

debug=True
class masterThread(threading.Thread):
  def __init__(self,watchdog):
    super(masterThread,self).__init__()
    self.name = "masterThread"
    print("starting: %s"%self.name)
    global searchType
    searchType = config.specs['defaultSearchType'];
    print("%s: default search type: %s"%(self.name,searchType))
    self.watchdog = watchdog
    self.watchdog.add(self)

  def run(self):
    global searchType
    print("%s in run loop"%self.name)
    hosts = host.getHosts()
    imageHosts = []
    phraseHosts = []
    lastCacheId = 0
    for h in hosts:
      ip = h['ip']
      if host.isLocalHost(ip):
        DisplayHandler.clearCache(None)
      else:
        host.sendToHost(ip,{'cmd' : 'ClearCache' , 'args' : None});

      if host.getAttr(ip,'hasDisplay') and host.getAttr(ip,'displayType') == 'Image':
        print("%s: display type for %s: image"%(self.name,ip))
        imageHosts.append(ip)

      if host.getAttr(ip,'wantsPhrase'):
        print("%s: wants phrase for %s: "%(self.name,ip))
        phraseHosts.append(ip)

    while True:
      self.watchdog.feed(self)
      cacheId = random.randint(10000,20000)
      images=[]
      choices=[]
      urls=[]
      if searchType == 'Archive':
        [images,choices] = archive.getArchive()
        if debug:
          for i in images:
            print("%s: image %s"%(self.name,i))
          for c in choices:
            print("%s: choice %s"%(self.name,c))
      elif searchType == 'Google':
        choices = words.getWords()
        urls = googleSearch.getUrls(choices)
        if urls == None:
          print("%s Google Error switching to Archive"%self.name)
          searchType = "Archive"
          continue
        if len(urls) == 0:
          print("%s Nothing found try again"%self.name)
          continue
        images = urlsToImages(googleSearch.getUrls(choices));
      else:
        print("%s unimplemented type %s switching to archive"%(self.name,searchType))
        searchType = 'Archive'
      if searchType != 'Archive':
        archive.putArchive(choices)

      phraseArgs = {}
      if len(phraseHosts) != 0:
        phraseArgs['phrase'] = choices
        print("%s sending %s to %s"%(self.name,choices,ip))
        lang = random.choice(config.specs['langList'])
        file=textSpeaker.makeSpeakFile("%s %s"%(choices[0],choices[1]),lang)
        with open(file,"rb") as sf:
          phraseArgs['phraseData'] = base64.b64encode(sf.read())
        os.unlink(file)
        #os.unlink(file.replace("mp3","wav"));
    

      if len(imageHosts) != 0:
        numImages = len(images)
        imagesPerHost = numImages/len(imageHosts)
        extraImages = numImages % len(imageHosts)
        extra = 0
        count = 0
        print(
              "%s numImages:%d imagesPerHost:%d extraImages:%d"
              %(self.name,numImages,imagesPerHost,extraImages))
        for ip in imageHosts:
          args = {}
          args['id'] = cacheId
          args['imgData'] = []
          for i in range(0,imagesPerHost):
            fname = images[i+count]
            args['imgData'].append(setImgData(fname))
          count += imagesPerHost
          if extra < extraImages:
            fname = images[count+extra]
            args['imgData'].append(setImgData(fname))
            extra += 1
          cmd = {'cmd' : "AddImage", 'args' : args}
          if host.isLocalHost(ip):
            DisplayHandler.addImage(args)
          else:
            host.sendToHost(ip,cmd)


        for ip in imageHosts:
          args =[cacheId]
          if host.isLocalHost(ip):
            DisplayHandler.setImageDir(args)
          else:
            host.sendToHost(ip,{'cmd' : 'SetImageDir' , 'args' : args});

        if lastCacheId != 0:
          for ip in imageHosts:
            args =[lastCacheId]
            if host.isLocalHost(ip):
              DisplayHandler.rmCacheDir(args)
            else:
              host.sendToHost(ip,{'cmd' : 'RmCacheDir' , 'args' : args});
        lastCacheId = cacheId

      if len(phraseHosts) != 0:
        for ip in phraseHosts:
          if host.isLocalHost(ip):
            PhraseHandler.setPhrase(phraseArgs)
          else:
            host.sendToHost(ip,{'cmd' : 'Phrase' , 'args' : phraseArgs});
    
      sleepTime = config.specs['masterSleepInterval']  
      print("%s: sleeping %d"%(self.name,sleepTime))
      time.sleep(sleepTime)
    
