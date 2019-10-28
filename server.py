#!/usr/bin/env python
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import time
import os
import sys
import json
import subprocess
import urlparse
from hosts import Hosts

from debug import Debug
from singleton import Singleton
import upgrade
from asoundConfig import setVolume
from asoundConfig import getVolume


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ This class allows to handle requests in separated threads.
            No further content needed, don't touch this. """

class MyHandler(BaseHTTPRequestHandler):
  def do_HEAD(s):
    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()

  def log_message(self, format, *args):
    print("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))

  def do_POST(self):
    # Begin the response
    content_len = int(self.headers.getheader('content-length', 0))
    post_body = self.rfile.read(content_len)
    
    #Debug().p("Post: %s"%str(post_body))
    status = Server().cmdHandler(json.loads(post_body))
    self.send_response(200)
    self.end_headers()
    self.wfile.write(status)
    s = json.loads(status)
    Debug().p("handle cmd: %s"%s);
    if s['status'] == "poweroff":
      Server.doExit(3)
    if s['status'] == "reboot":
      Server.doExit(4)
    if s['status'] == "stop":
      Server.doExit(5)
    if s['status'] == "restart":
      Server.doExit(6)
    return


class Server(threading.Thread):
  __metaclass__ = Singleton
  def __init__(self,port):
    super(Server,self).__init__()
    self.host = Hosts().getLocalHost()
    self.port = port
    self.name = "ServerThread: %s:%d"%(self.host,port)
    print("%s"%(self.name))
    self.server = ThreadedHTTPServer((self.host, self.port), MyHandler)
    self.probeCallbacks = []

    self.commandTable = {
      'Poweroff' : Server.doPoweroff
      ,'Probe' : self.doProbe
      ,'Reboot' : Server.doReboot
      ,'Restart' : Server.doRestart
      ,'Stop' : Server.doStop
      ,'Upgrade' : Server.doUpgrade
      ,'Volume' : Server.setVolume
    }
    self.setProbe(Server.getVolume)
    
  def setProbe(self,cb):
    self.probeCallbacks.append(cb)
    
  @staticmethod
  def setVolume(args):
    return Hosts().jsonStatus(setVolume(args['value']))
  
  @staticmethod
  def getVolume():
    return{'Volume' : getVolume()}

  @staticmethod
  def doStop(args):
    return Hosts().jsonStatus("stop");

  @staticmethod
  def doRestart(args):
    return Hosts().jsonStatus("restart");
  
    
  @staticmethod
  def doExit(num):
    print ("Doing Exit with %d"%num)
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(num)
    
  def doProbe(self,args):
    state = {}
    state['status'] = "ok"
    attr = Hosts().getHost(Hosts().getLocalHost())
    for k in attr.keys():
      state[k]=attr[k]
    for cb in self.probeCallbacks:
      info = cb()
      for k in info.keys():
        state[k] = info[k]
        
    return json.dumps(state)

  @staticmethod
  def doUpgrade(cmd):
    upgrade.upgrade()
    print("returned from upgrade")
    return Hosts().jsonStatus("reboot")

  @staticmethod
  def doPoweroff(cmd):
    return Hosts().jsonStatus("poweroff");

  @staticmethod
  def doReboot(cmd):
    return Hosts().jsonStatus("reboot");

  def cmdHandler(self,cmd):
    Debug().p("%s handling cmd: %s"%(self.name,cmd['cmd']))
    if cmd['cmd'] not in self.commandTable.keys():
      return Hosts.jsonStatus("%s: %s not implemented"%(self.name,cmd['cmd']),False)
    status = self.commandTable[cmd['cmd']](cmd['args'])
    return status
    

  def register(self,cmds):
    Debug().p("%s: registering command %s"%(self.name,cmds))
    for k in cmds.keys():
      self.commandTable[k] = cmds[k]

  def run(self):
    print "%s starting server"%(self.name)
    self.server.serve_forever()
    print("shouldn't get here");

  


