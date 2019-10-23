#!/usr/bin/env python
import urllib2
import os
from hosts import Hosts
  
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
  
  
def doHaltMusic(cmd):
  hmcmd = { 'cmd' : 'HaltMusic', 'args' : [""] }
  hscmd = { 'cmd' : 'HaltSound', 'args' : [""] }
  hosts = Hosts().getHosts()
  for h in hosts:
    if h['hasMusicPlayer']:
      Hosts().sendToHost(h['ip'],hmcmd)
  for h in hosts:
    if h['hasMusic']:
      Hosts().sendToHost(h['ip'],hscmd)
  return 0

def doStartMusic(cmd):
  smcmd = { 'cmd' : 'StartMusic', 'args' : [""] }
  hosts = Hosts().getHosts()
  for h in hosts:
    if h['hasMusicPlayer']:
      Hosts().sendToHost(h['ip'],smcmd)
  return 0
