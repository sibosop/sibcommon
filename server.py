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

from utils import print_dbg
from singleton import Singleton


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
    
    print_dbg("Post: %s"%str(post_body))
    status = Server().cmdHandler(json.loads(post_body))
    self.send_response(200)
    self.end_headers()
    self.wfile.write(status)
    s = json.loads(status)
    print_dbg("handle cmd: %s"%s);
    if s['status'] == "poweroff":
      Server.doExit(3)
    if s['status'] == "reboot":
      Server.doExit(4)
    if s['status'] == "stop":
      Server.doExit(5)
    return


class Server(threading.Thread):
  __metaclass__ = Singleton
  def __init__(self,port):
    super(Server,self).__init__()
    host = subprocess.check_output(["hostname","-I"]).split();
    self.host = host[0]
    self.port = port
    self.name = "ServerThread: %s:%d"%(self.host,port)
    print("%s"%(self.name))
    self.server = ThreadedHTTPServer((self.host, self.port), MyHandler)

    self.commandTable = {
      'Upgrade' : Server.doUpgrade
      ,'Poweroff' : Server.doPoweroff
      ,'Reboot' : Server.doReboot
    }
  @staticmethod
  def doExit(num):
    print "Doing Exit with %d"%num
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(num)

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
    print_dbg("%s handling cmd: %s"%(self.name,cmd['cmd']))
    if cmd['cmd'] not in self.commandTable.keys():
      return Hosts.jsonStatus("%s: %s not implemented"%(self.name,cmd['cmd']),False)
    status = self.commandTable[cmd['cmd']](cmd['args'])
    return status
    

  def registerCommand(self,cmd,callback):
    print_dbg("%s: registering command %s"%(self.name,cmd))
    self.commandTable[cmd] = callback

  def run(self):
    print "%s starting server"%(self.name)
    self.server.serve_forever()
    print("shouldn't get here");

  

