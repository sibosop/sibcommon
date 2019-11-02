#!/usr/bin/env python
import threading
from Queue import Queue
import time
from debug import Debug
from recogOutput import RecogOutput
from display import Display
from hosts import Hosts


class RecogAnalyzer(threading.Thread):
  def __init__(self,output):
    super(RecogAnalyzer,self).__init__()
    self.name = "RecogAnalyzer"
    self.queue = Queue()
    recog = Hosts().getLocalAttr("recog")
    self.chooseLen=recog['chooseLen']
    self.chooseSize=recog['chooseSize']
    self.output = output
    self.choices = []

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
          if w not in self.choices:
            self.choices.append(w)
          while len(self.choices) > self.chooseSize:
            self.choices = self.choices[1:]
            Debug().p("%s choices %s"%(self.name,self.choices))
          self.output.queue.put(self.choices)


  


  
