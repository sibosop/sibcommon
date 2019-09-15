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
from utils import print_dbg


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
      print_dbg("send to host: %s %s"%(ip,cmd))
      url = "http://"+ip+":8080"
      print_dbg("url: %s"%url)
      print_dbg("cmd json: %s"%json.dumps(cmd))
      req = urllib2.Request(url
              ,json.dumps(cmd),{'Content-Type': 'application/json'})
      f = urllib2.urlopen(req,None,self.timeout)
      test = f.read()
      print_dbg("got response: %s"%test)
    except Exception, e:
        traceback.print_exc()
      

  @staticmethod
  def sendWithSubnet(ip,cmd):
    for i in ip:
      h = "%s.%d"%(Specs().s['subnet'],i)
      sendToHost(h,cmd)

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
    print_dbg("send to word server")
    rval = True
    port = Specs().s['wordServerPort']
    try:
      #url = "http://"+ip + ":" + str(port) + "/"+cmd
      url = "http://%s:%d/%s"%(ip,port,cmd)
      print_dbg("send to word server: %s"%url)
      req = urllib2.Request(url)
      f = urllib2.urlopen(req,None,self.timeout)
      rval = f.read()
      print_dbg("got response: %s"%rval)  
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
      print_dbg("isLocalHost: ip: %s myIp %s"%(ip,i))
      if i == ip:
        print_dbg("isLocalHost is True: %s"%ip)
        return True
    print_dbg("isLocalHost is False: %s"%ip)
    return False

  @staticmethod
  def getLocalHost():
    subnet = Specs().s['subnet']
    ipList = subprocess.check_output(["hostname","-I"]).split()
    for ip in ipList:
      if subnet in ip:
        print_dbg("local host: %s"%ip)
        return ip
    return None
  
  def getHost(self,ip):
    for h in self.hosts:
      if h['ip'] == ip:
        return h
    print("Can't find ip %s"%ip)
    return None
    
  def getAttr(self,ip,a):
    rval = self.getHost(ip)[a]
    print_dbg("Get Attr %s: %s"%(a,rval))
    return rval 
  
  def getLocalAttr(self,a):
    rval = self.getHost(Hosts.getLocalHost())[a]
    print_dbg("Get Local Attr %s: %s"%(a,rval))
    return rval
