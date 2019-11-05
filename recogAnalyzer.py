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
    self.running = True
    self.choices = []

  def run(self):
    print("starting: "+self.name)
    while self.running:
      result = self.queue.get()
      if type(result) == str:
        if result == "__stop__":
          print("%s: stopping"%(self.name))
          self.running = False
        continue
      # Once the transcription has settled, the first result will contain the
      # is_final result. The other results will be for subsequent portions of
      # the audio.
      Debug().p('Final: %s'%(result.is_final))
      Debug().p('Stability: %f'%(result.stability))
      # The alternatives are ordered from most likely to least.
      alternatives = result.alternatives
      for alternative in alternatives:
        Display().text(alternative.transcript)
        if result.is_final:
          Debug().p('Confidence: %f'%(alternative.confidence))
          Debug().p('Transcript: %s'%(alternative.transcript))
          args = {"final" : alternative.transcript, "search" : ['search','string']}
          self.output.queue.put(args)


  
