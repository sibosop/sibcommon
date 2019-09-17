#!/usr/bin/env python
import os
import sys
home = os.environ['HOME']
proj = home+"GitProjects/iAltar"
sys.path.append(proj+"/iAltar")
sys.path.append(proj+"/config")
sys.path.append(proj+"/common")
sys.path.append(proj+"/server")
from py_bing_search import PyBingImageSearch
import time
import urllib
import httplib
import json
import requests

debug=True

headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': '883e1d2b72b743f8aad86451b97c91df',
}

def getUrls(choices):
  choices[0]=choices[0].replace(" ","+")
  choices[1]=choices[1].replace(" ","+")
  urls=None
  search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
  search_term = "%s %s"%(choices[0],choices[1]) 
  params = {
      # Request parameters
      'q': search_term,
      "license": "public",
      'count': '50',
      'offset': '0',
      'mkt': 'en-us',
      'safeSearch': 'Moderate',
      'imageType' : "photo"
  }
  if debug: print "params:", params
  response = requests.get(search_url, headers=headers, params=params)
  print "raise for status"
  response.raise_for_status()
  seach_results = response.json() 
  print "loading from json"
  data = json.loads(search_results)
  print "%s"%data
  return urls

if __name__ == '__main__':
  import words
  urls=getUrls(words.getWords())
  if urls == None:
    print "Bing Error"
    exit(1)
  if len(urls) == 0:
    print "no urls!"
  for i in urls:
    print "full:",i['full']
    print "thumb:",i['thumb']
