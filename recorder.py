#!/usr/bin/env python
import threading
from Queue import Queue
from Queue import Empty

import sys
import time
import os
import alsaaudio
import grpc
import asoundConfig
from debug import Debug
from recog import Recog



class Recorder(threading.Thread):
  def __init__(self,recog):
    super(Recorder,self).__init__()
    self.name = "Recorder Thread"
    self.queue = Queue()
    self.fileCount = 0
    self.hw = asoundConfig.getHw()
    self.inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, cardindex=int(self.hw['Mic']))
    self.inp.setchannels(1)
    self.inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    self.inp.setperiodsize(1600)
    self.loopCount = 1000
    self.recog = recog

  def run(self):
    print("starting: "+self.name)
    while True:
      try:
        msg = self.queue.get(False)
        if msg == "__stop__":
          print("%s: stopping"%self.name)
        break
      except Empty:
        pass
      loops = self.loopCount
      buff = bytes()
      while loops > 0:
        loops -= 1
        l, data = self.inp.read()
        if l < 0:
          print(self.name+" pipe error")
          continue
        if l:
          buff += data
        time.sleep(.001)
      loops = self.loopCount
      self.recog.queue.put(buff)
      Debug().p(self.name+" sending: "+str(len(buff)))

  def close(self):
    return

  
