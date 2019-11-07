#!/usr/bin/env python
import threading
import Queue
import time
import syslog
import os
import io
import grpc
import traceback
from debug import Debug
from recogAnalyzer import RecogAnalyzer

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import warnings
warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")


class Recog(threading.Thread):
  def __init__(self,anal):
    super(Recog,self).__init__()
    self.name = "Recog Thread"
    self.queue = Queue.Queue()
    self.running = True
    self.anal = anal

  class dataStream(object):
    def __init__(self,recog):
      self.recog = recog
    
      Debug().p(self.recog.name+" in dataStream init")
    def __iter__(self):
      Debug().p(self.recog.name+" in dataStream iter")
      return self
    def next(self):
      Debug().p(self.recog.name+" in dataStream next")
      chunk = self.recog.queue.get()
      if type(chunk) is str and chunk == "__stop__":
        print("%s stopping"%self.recog.name)
        self.recog.running=false
        raise StopIteration
      Debug().p(self.recog.name+" got:" + str(len(chunk)))
      return chunk

  def run(self):
    syslog.syslog("starting: "+self.name)
    self.client = speech.SpeechClient()
    while self.running:
      stream = self.dataStream(self)
      #syslog.syslog(self.name+"for chunk in stream")
      #for chunk in stream:
      #  syslog.syslog(self.name+" chunk size:"+str(len(chunk)))
      requests = (types.StreamingRecognizeRequest(audio_content=chunk)
                  for chunk in stream)
      config = types.RecognitionConfig(
          encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16
          ,sample_rate_hertz=44100
          ,language_code='en-US'
          )
      streaming_config = types.StreamingRecognitionConfig(
                config=config
                ,interim_results=True
                )

      # streaming_recognize returns a generator.
      try:
        responses = self.client.streaming_recognize(streaming_config, requests)
        for response in responses:
          
          for result in response.results:
            self.anal.queue.put(result)
              
      except Exception as e:
        print("%s: exception %s"%(self.name,e))
        if str(e).find("iterating requests") == -1:
          traceback.print_exc()
        else:
          print ("%s: %s"%(self.name,e))
          self.running = False
          

  
  
