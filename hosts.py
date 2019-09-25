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
from netifaces import interfaces, ifaddresses, AF_INET


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
    self.localHost = None
    self.findLocalHost()
    
      
  def findLocalHost(self):
    self.localHost = None
    #ipList = subprocess.check_output(["hostname","-I"]).split()
    ipList = []
    for interface in interfaces():
          for i in ifaddresses(interface):
            Debug().p("interface type %d"%i)
            for link in ifaddresses(interface)[i]:
              ipList.append(link['addr'])
    for ip in ipList:
      for h in self.hosts:
        Debug().p("checking ip %s against %s"%(h['ip'],ip))
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
    if not self.getAttr(ip,"hasServer"):
      print("sendToHost skipping %s: it is not a server"%ip)
      return
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
      print("ip %s:%s"%(ip,e))
    except Exception,e:
      print("ip %s:%s"%(ip,e))
      

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
      
  def isLocalHost(self,ip):
    return self.localHost == ip

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

if __name__ == '__main__':
    os.environ['DISPLAY']=":0.0"
    os.chdir(os.path.dirname(sys.argv[0]))
    os.chdir("..") # sigh: get to default app path
    Debug(["__main__"])
    Specs("%s/%s"%("speclib","piano.json"))
    print(Hosts().isLocalHost("none"))
