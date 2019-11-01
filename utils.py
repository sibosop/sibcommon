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
  hosts = Hosts().getHostIps()
  for ip in hosts:
    music = Hots().getAttr(ip,'music')
    if music['player']:
      Hosts().sendToHost(ip,hmcmd)
  for h in hosts:
    if music['enaled']:
      Hosts().sendToHost(ip,hscmd)
  return 0
  
def doHaltSound(ip):
  hscmd = { 'cmd' : 'HaltSound', 'args' : [""] }
  Hosts().sendToHost(h['ip'],hscmd)

def doStartMusic(cmd):
  smcmd = { 'cmd' : 'StartMusic', 'args' : [""] }
  hosts = Hosts().getHostIps()
  for ip in hosts:
    music = Hosts().getAttr(ip,'music')
    if music['enabled']:
      Hosts().sendToHost(ip,smcmd)
  return 0

def doMute(pip,mip,flag):
  mcmd = { 'cmd' : 'Mute', 'args' : {'ip' : mip, 'mute' : flag } }
  Hosts().sendToHost(pip,mcmd)
  hscmd = { 'cmd' : 'HaltSound', 'args' : [""] }
  Hosts().sendToHost(mip,hscmd)
  
def sysex_to_data(sysex):
  data = [None] * len(sysex)
  cnt2 = 0
  bits = 0
  for cnt in range(0,len(sysex)):
    if ((cnt % 8) == 0):
      bits = sysex[cnt]
    else:
      data[cnt2] = sysex[cnt] | ((bits & 1) << 7)
      cnt2 += 1
      bits >>= 1
  return data[0:cnt2]

def data_to_sysex(data):
  sysex = [0]
  idx = 0
  cnt7 = 0

  for x in data:
      c = x & 0x7F
      msb = x >> 7
      sysex[idx] |= msb << cnt7
      sysex += [c]

      if cnt7 == 6:
          idx += 8
          sysex += [0]
          cnt7 = 0
      else:
          cnt7 += 1

  if cnt7 == 0:
      sysex.pop()
      
  return sysex
