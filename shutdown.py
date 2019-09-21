#!/usr/bin/env python
import os
import syslog
import subprocess
import threading
import RPi.GPIO as GPIO
import time
from singleton import Singleton
from hosts import Hosts
import Queue

class Shutdown(threading.Thread):
  __metaclass__ = Singleton
  def __init__(self):
    super(Shutdown,self).__init__()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    self.hosts = Hosts().getHosts()
    self.name = "Shutdown Thread"
    self.queue = Queue.Queue()

  def doShutdown(self):
    print "%s doing shutdown"%self.name
    for h in self.hosts:
      if Hosts().isLocalHost(h['ip']):
        print"%s skipping localhost shutdown for %s"%(self.name,h['ip'])
      else:
        try:
          print "%s calling shutdown for: %s"%(self.name,h['ip'])
          Hosts().sendToHost(h['ip'],{'cmd' : 'Poweroff', 'args' : [""] })
        except:
          print "%s ignoring shutdown error for %s"%(self.name,h)
    print "%s shutting down"%self.name
    subprocess.check_output(["sudo","poweroff"])

  def run(self):
    print "%s starting"%self.name
    while GPIO.input(16):
      try:
        self.queue.get(timeout=1)
      except Queue.Empty:
        print("%s stopping"%self.name)
        return
      continue
    self.doShutdown()
