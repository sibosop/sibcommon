#!/usr/bin/env python
import sys
import os
import argparse
import platform
import subprocess
import traceback
home = os.environ['HOME']
import sys
import urllib2
from singleton import Singleton
from specs import Specs
from utils import print_dbg


class Hosts(object):
  __metaclass__ = Singleton
  def __init__(self):
    self.names = []
    self.timeout = 2
    self.hosts = Specs().s['hosts']
    for a in self.hosts:
      if 'name' in a:
        self.names.append(a['name'])

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
      print_dgb("cmd json: %s"%json.dumps(cmd))
      req = urllib2.Request(url
              ,json.dumps(cmd),{'Content-Type': 'application/json'})
      f = urllib2.urlopen(req,None,timeout)
      test = f.read()
      print_dbg("got response: %s"%test)
    except Exception, e:
        traceback.print_exc()
      

  def sendWithSubnet(self,ip,cmd):
    for i in ip:
      h = "%s.%d"%(Specs().s['subnet'],i)
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
    
  def jsonStatus(self,s):
    d = {}
    d['status'] = s
    return json.dumps(d) 
     
  def sendToWordServer(self,ip,cmd): 
    print_dbg("send to word server")
    rval = True
    port = Specs().s['wordServerPort']
    try:
      #url = "http://"+ip + ":" + str(port) + "/"+cmd
      url = "http://%s:%d/%s"%(ip,port,cmd)
      print_dbg("send to word server: %s"%url)
      req = urllib2.Request(url)
      f = urllib2.urlopen(req,None,timeout)
      rval = f.read()
      print_dbg("got response: %s"%rval)  
    except Exception as e:
      print("host send error: %s"%str(e))
      rval = jsonStatus("408")
    return rval
      
  def isLocalHost(self,ip):
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

  def getLocalHost(self):
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
    rval = self.getHost(self.getLocalHost())[a]
    print_dbg("Get Local Attr %s: %s"%(a,rval))
    return rval

