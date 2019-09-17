#!/usr/bin/env python
import os
home = os.environ['HOME']
proj = "%s/%s"%(home,"GitProjects/iAltar")
import sys
sys.path.append(proj+"/common")
sys.path.append(proj+"/config")
import syslog
import subprocess
import threading
import host
import RPi.GPIO as GPIO
import time

class ShutdownThread(threading.Thread):
  def __init__(self):
    super(ShutdownThread,self).__init__()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    self.hosts = host.getHosts()
    self.name = "Shutdown Thread"

  def doShutdown(self):
    print "%s doing shutdown"%self.name
    for h in self.hosts:
      if host.isLocalHost(h['ip']):
        print"%s skipping localhost shutdown for %s"%(self.name,h['ip'])
      else:
        try:
          print "%s calling shutdown for: %s"%(self.name,h['ip'])
          host.sendToHost(h['ip'],{'cmd' : 'Poweroff', 'args' : [""] })
        except:
          print "%s ignoring shutdown error for %s"%(self.name,h)
    print "%s shutting down"%self.name
    subprocess.check_output(["sudo","poweroff"])

  def run(self):
    print "%s starting"%self.name
    while GPIO.input(16):
      time.sleep(1)
      continue
    self.doShutdown()
