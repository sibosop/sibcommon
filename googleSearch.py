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
home = os.environ['HOME']
proj = home+"/GitProjects/iAltar"
sys.path.append(proj+"/iAltar")
sys.path.append(proj+"/config")
sys.path.append(proj+"/common")
sys.path.append(proj+"/server")
import pprint
import config
import time
import traceback
import sys
import apiclient

from apiclient.discovery import build

global initFlag
initFlag=False
debug=False
global creds
creds={}

def doSetup():
  global creds
  config.load()
  lines = open(config.specs['credFile']).read().split('\n')
  for l in lines:
    vars=l.split("=")
    if len(vars) == 2:
      creds[vars[0]]=vars[1]

  for k in creds.keys():
    if debug: print "key:",k,"value:",creds[k]
  

  
def getUrls(qs):
  global initFlag
  if initFlag==False:
    doSetup()
    initFlag=True
  images=[]
  index=0
  while len(images) < 15:
    # Build a service object for interacting with the API. Visit
    # the Google APIs Console <http://code.google.com/apis/console>
    # to get an API key for your own application.
    try:
      service = build("customsearch", "v1",
                developerKey=creds['key'])
      query = qs[0]+" "+qs[1]
      startReq = index * 10
      
      if debug: print "query:",query,"index:",startReq
      res=None
      start_time = time.time()
      if index == 0:
        res = service.cse().list(
            q=query,
            cx=creds['cx'],
            searchType='image',
            safe='off',
          ).execute()
      else:
        res = service.cse().list(
            q=query,
            cx=creds['cx'],
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
        if debug: print "rejecting too few items"
        return []

      #if debug: print "res:",res 
      for l in res['items']:
        if debug: print "link",l['link']
        relem={}
        relem['full']=l['link']
        relem['thumb']=l['image']['thumbnailLink']
        images.append(relem)
    
      index += 1
          
      if debug: pprint.pprint(res)

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
  import words
  urls=getUrls(words.getWords())
  if urls == None:
    print "Google Error"
    exit(1)
  if len(urls) == 0:
    print "no urls!"
  for i in urls:
    print "full:",i['full']
    print "thumb:",i['thumb']
