#!/usr/bin/env python
import urllib2
import os
  
def internetOn():
  try:
    urllib2.urlopen('http://216.58.192.142', timeout=1)
    return True
  except urllib2.URLError as err: 
    return False
    
def mkpath(path):
  try: 
    os.makedirs(path)
  except OSError:
    if not os.path.isdir(path):
      raise
  return path