#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simple command-line example for Custom Search.

Command-line application that does a search.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import os
import sys
import pprint
import time
import traceback
import sys
import apiclient

from apiclient.discovery import build
from specs import Specs
from debug import Debug
from singleton import Singleton


class Search(object):
  __metaclass__ = Singleton
  
  def __init__(self):
    self.creds = {}
    lines = open(Specs().s['credFile']).read().split('\n')
    for l in lines:
      vars=l.split("=")
      if len(vars) == 2:
        self.creds[vars[0]]=vars[1]
    for k in self.creds.keys():
      Debug().p("key: %s value %s"%(k,self.creds[k]))
  

  
  def getUrls(self,qs):
    images=[]
    index=0
    while len(images) < 15:
      # Build a service object for interacting with the API. Visit
      # the Google APIs Console <http://code.google.com/apis/console>
      # to get an API key for your own application.
      try:
        service = build("customsearch", "v1",
                  developerKey=self.creds['key'])
        query = qs[0]+" "+qs[1]
        startReq = index * 10
      
        Debug().p ("query: %s index: %s"%(query,startReq))
        res=None
        start_time = time.time()
        if index == 0:
          res = service.cse().list(
              q=query,
              cx=self.creds['cx'],
              searchType='image',
              safe='off',
            ).execute()
        else:
          res = service.cse().list(
              q=query,
              cx=self.creds['cx'],
              searchType='image',
              start=int(startReq),
              safe='off',
            ).execute()
        elapsed_time = time.time() - start_time
        if 'error' in res:
          print "google responded with error message: ",pprint.pformat(res)
          time.sleep(60)
          return []
        tst= 'items' in res
        if tst==False or len(res['items']) < 10:
          Debug().p ("rejecting too few items")
          return []

        #Debug().p "res:",res 
        for l in res['items']:
          Debug().p ("link %s"%l['link'])
          relem={}
          relem['full']=l['link']
          relem['thumb']=l['image']['thumbnailLink']
          images.append(relem)
    
        index += 1
          
        Debug().p(res)

      except apiclient.errors.HttpError,e:
        print("google cse status:"+str(e.resp.status))
        if e.resp.status == 403:
          print("Google Quota Exceeded")
        return None
      
      except:
        print("google cse:"+str(sys.exc_info()[0]))
        return None 

    return images


if __name__ == '__main__':
  from words import Words
  os.environ['DISPLAY']=":0.0"
  os.chdir(os.path.dirname(sys.argv[0]))
  os.chdir("..") # sigh: get to default app path
  Debug(["__main__","words"])
  Specs("%s/%s"%("speclib","commontest.json"))
  urls=Search().getUrls(Words().getWords())
  if urls == None:
    print "Google Error"
    exit(1)
  if len(urls) == 0:
    print "no urls!"
  for i in urls:
    print "full:",i['full']
    print "thumb:",i['thumb']
