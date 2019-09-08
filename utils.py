#!/usr/bin/env python
import urllib2

debug = False

def setDebug(flag):
  global debug
  debug = flag

def print_dbg(msg):
  if debug: print(msg)
  
def internetOn():
  try:
    urllib2.urlopen('http://216.58.192.142', timeout=1)
    return True
  except urllib2.URLError as err: 
    return False
    

  