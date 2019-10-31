#!/usr/bin/env python
import threading
from Queue import Queue
import time
from debug import Debug
from singleton import Singleton
from recogOutput import RecogOutput
from display import Display


class RecogAnalyzer(threading.Thread):
  __metaclass__ = Singleton
  def __init__(self):
    super(RecogAnalyzer,self).__init__()
    self.name = "RecogAnalyzer"
    self.queue = Queue()
    self.chooseLen=6

  def run(self):
    print("starting: "+self.name)
    while True:
      input = self.queue.get()
      if input == "__stop__":
        Debug().p("%s: stopping"%(self.name))
        break
      Debug().p(self.name+" got "+ input)
      Display().text(input)
      for w in input.split():
        Debug().p(self.name+"test:"+w)
        if len(w) > self.chooseLen:
          Debug().p(self.name+"CHOSE: "+w)
          RecogOutput().queue.put(w)


  


  
