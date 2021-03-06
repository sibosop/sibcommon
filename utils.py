#!/usr/bin/env python
import urllib2
import os
from hosts import Hosts
from debug import Debug
from asoundConfig import setVolume



  
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
  
def doSetSearch(search):
  cmd = { 'cmd' : "Search", 'args' : {'type' : search}}
  for ip in Hosts().getHostIps():
    iAltar = Hosts().getAttr(ip,'iAltar')
    if iAltar['enabled'] and iAltar['player']:
      Hosts().sendToHost(ip,cmd)
  
  

def sendVoiceMsg(cmdStr):
  cmd = { 'cmd' : cmdStr, 'args' : [""] }
  for ip in Hosts().getHostIps():
    phrase = Hosts().getAttr(ip,'phrase')
    if phrase['enabled'] and phrase['voice']:
        Hosts().sendToHost(ip,cmd)
  return 0
  
def doStartVoice(cmd):
  return sendVoiceMsg('StartVoice')
   
def doHaltVoice(cmd):
  return sendVoiceMsg('HaltVoice')
  
def sendRecogMsg(cmdStr):
  cmd = { 'cmd' : cmdStr, 'args' : [""] }
  rval = ""
  for ip in Hosts().getHostIps():
    recog = Hosts().getAttr(ip,'recog')
    if recog['enabled'] and recog['engine']:
        rval = Hosts().sendToHost(ip,cmd)
  return rval
  
def doPoweroff(cmdStr):
  cmd = { 'cmd' : 'Poweroff', 'args' : [""] }
  lh = Hosts().getLocalHost()
  for ip in Hosts().getHostIps():
    if ip == lh:
      continue
    if Hosts().getAttr(ip,'hasServer'):
      Hosts().sendToHost(ip,cmd)
  if Hosts().getLocalAttr('hasServer'):
    Hosts().sendToHost(lh,cmd)
  return 0  
  
def doStartRecog(cmd):
  return sendRecogMsg('StartRecog')
   
def doHaltRecog(cmd):
  return sendRecogMsg('HaltRecog')

def doGetRecog(cmd):
  return sendRecogMsg('GetRecog')
 
  
def doHaltMusic(cmd):
  hmcmd = { 'cmd' : 'HaltMusic', 'args' : [""] }
  hscmd = { 'cmd' : 'HaltSound', 'args' : [""] }
  hosts = Hosts().getHostIps()
  for ip in hosts:
    music = Hosts().getAttr(ip,'music')
    Debug().p("Test Halt for ip %s music: %s"%(ip,music))
    if music['enabled'] and music['player']:
      Hosts().sendToHost(ip,hmcmd)
      Debug().p("Halt Player for ip %s music: %s"%(ip,music))
    if music['enabled']:
      Debug().p("Halt Music for ip %s music: %s"%(ip,music))
      Hosts().sendToHost(ip,hscmd)
  return 0

def doSetVolume(val):
  vcmd = { 'cmd' : 'Volume', 'args' : {'value' : val}}
  for ip in Hosts().getHostIps():
    if ip == Hosts().getLocalHost():
      setVolume(val)
      continue
    Hosts().sendToHost(ip,vcmd)

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
