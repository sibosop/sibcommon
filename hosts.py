#!/usr/bin/env python
import sys
import os
import argparse
import platform
import subprocess
import traceback
import json
home = os.environ['HOME']
import sys
import urllib2
from singleton import Singleton
from specs import Specs
from debug import Debug

class Hosts(object):
  __metaclass__ = Singleton
  def __init__(self):
    self.timeout = 2
    default = Specs().s['host_defaults']
    hosts = Specs().s['hosts']
    self.hosts = []
    for h in hosts:
      host = {}
      for k in default.keys():
        host[k] = default[k]
      for k in h.keys():
        host[k] = h[k]
      self.hosts.append(host)
    self.findLocalHost()
    
      
  def findLocalHost(self):
    self.localHost = None
    ipList = subprocess.check_output(["hostname","-I"]).split()
    for ip in ipList:
      for h in self.hosts:
        if h['ip'] == ip:
          Debug().p("found local host: %s"%ip)
          self.localHost = ip
          break;

  def getHosts(self):
    return self.hosts
  
  def getHostIps(self):
    rval = []
    for h in self,hosts:
      rval.append(h['ip'])
    return rval

  def printHostList(self):
    print("Host list:")
    for h in self.hosts:
      print("\t%s"%h['ip'])

  def sendToMaster(self,cmd):
    for h in self.hosts:
      if h['isMaster']:
        self.sendToHost(h['ip'],cmd)
        break

  def sendByName(self,nameList,cmd):
    for n in nameList:
      for h in self.hosts:
        if h['name'] == n:
          self.sendToHost(h['ip'],cmd)
          break
        
  def sendToHost(self,ip,cmd):
    rval = True
    try:
      Debug().p("cmd %s"%cmd['cmd'])
      timeout = self.timeout
      if cmd['args'] is not None and 'timeout' in cmd['args']:
        print("timeout %d"%cmd['args']['timeout'])
        timeout = cmd['args']['timeout']
      Debug().p("send to host: %s %s timeout=%d"%(ip,cmd['cmd'],timeout))
      url = "http://"+ip+":8080"
      Debug().p("url: %s"%url)
      req = urllib2.Request(url
              ,json.dumps(cmd),{'Content-Type': 'application/json'})
      f = urllib2.urlopen(req,None,timeout)
      test = f.read()
      Debug().p("got response: %s"%test)
    except urllib2.URLError, e:
        Debug().p("ip %s:%s"%(ip,e))
      

  def sendWithSubnet(self,ip,cmd):
    for i in ip:
      h = "%s.%s"%(Specs().s['subnet'],i)
      self.sendToHost(h,cmd)

  def sendToHosts(self,cmd):
    save = None
    for h in self.hosts:
      ip = h['ip']
      if self.isLocalHost(ip):
        save = ip
      else:
        self.sendToHost(h['ip'],cmd)
    if save is not None:
      self.sendToHost(save,cmd)
    
  @staticmethod
  def jsonStatus(s,ok=True):
    d = {}
    d['ok'] = ok
    d['status'] = s
    return json.dumps(d) 
     
  @staticmethod
  def sendToWordServer(ip,cmd): 
    Debug().p("send to word server")
    rval = True
    port = Specs().s['wordServerPort']
    try:
      #url = "http://"+ip + ":" + str(port) + "/"+cmd
      url = "http://%s:%d/%s"%(ip,port,cmd)
      Debug().p("send to word server: %s"%url)
      req = urllib2.Request(url)
      f = urllib2.urlopen(req,None,self.timeout)
      rval = f.read()
      Debug().p("got response: %s"%rval)  
    except Exception as e:
      print("host send error: %s"%str(e))
      rval = jsonStatus("408")
    return rval
      
  @staticmethod
  def isLocalHost(ip):
    plats=platform.platform().split('-');
    if plats[0] == 'Darwin':
      return False
    myIp = subprocess.check_output(["hostname","-I"]).split()
    for i in myIp:
      Debug().p("isLocalHost: ip: %s myIp %s"%(ip,i))
      if i == ip:
        Debug().p("isLocalHost is True: %s"%ip)
        return True
    Debug().p("isLocalHost is False: %s"%ip)
    return False

  def getLocalHost(self):
    return self.localHost
  
  def getHost(self,ip):
    for h in self.hosts:
      if h['ip'] == ip:
        return h
    print("Can't find ip %s"%ip)
    return None
    
  def getAttr(self,ip,a):
    rval = self.getHost(ip)[a]
    Debug().p("Get Attr %s: %s"%(a,rval))
    return rval 
  
  def getLocalAttr(self,a):
    rval = self.getHost(self.getLocalHost())[a]
    Debug().p("Get Local Attr %s: %s"%(a,rval))
    return rval

