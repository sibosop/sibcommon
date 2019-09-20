#!/usr/bin/env python
import os
import sys
import pygame
import sys
import time
import os
import wave
import audioop
import re
from gtts import gTTS
from pydub import AudioSegment
from hosts import Hosts
from debug import Debug
from specs import Specs
from utils import internetOn


def convertSampleRate(fname):
  spf = wave.open(fname, 'rb')
  channels = spf.getnchannels()
  width = spf.getsampwidth()
  rate=spf.getframerate()
  signal = spf.readframes(-1)

  Debug().p("convertSampleRate"
    + " rate:"+str(rate)
    + " channels:"+str(channels)
    + " width:"+str(width)
    )

  converted = audioop.ratecv(signal,2,1,rate,44100,None)
  wf = wave.open(fname, 'wb')
  wf.setnchannels(channels)
  wf.setsampwidth(width)
  wf.setframerate(44100)
  wf.writeframes(converted[0])
  wf.close()


def makeSpeakFile(line,language=''):
  rval = None 
  if language == '':
    language  = 'en-us'
  Debug().p("make speak file:"+line+" lang:"+str(language))
  try:
    fnameRoot = "%s/%s"%(Specs().s['tmpdir'],re.sub('\W+','_',line))
    if internetOn() and language != "es":
      Debug().p("speak: internet on using gTTS");
      Debug().p("playText line:"+line)
      fname = fnameRoot + ".mp3"
      Debug().p("speak:"+fname)
      tts1=gTTS(text=line,lang=language)
      Debug().p("tts1:%s"%tts1)
      tts1.save(fname)
      Debug().p("speak:"+fname)
      sound = AudioSegment.from_mp3(fname)
      os.unlink(fname)
      fname = fnameRoot + ".wav"
      Debug().p("speak:"+fname)
      sound.export(fname, format="wav")
      rval = fname
    else:
      print("speak: internet off using espeak");
      fname = fnameRoot + ".wav"
      Debug().p("speak:"+fname)
      os.system("espeak -w "+fname+" '"+line+"'")
      rval = fname
    convertSampleRate(rval)
  except Exception as e:
    print("speak error: "+ str(e))
    rval = None
  return rval


if __name__ == '__main__':
  os.environ['DISPLAY']=":0.0"
  os.chdir(os.path.dirname(sys.argv[0]))
  os.chdir("..") # sigh: get to default app path
  Debug(["__main__"])
  Specs("%s/%s"%("speclib","commontest.json"))
  print "%s"%makeSpeakFile("fuck everything")
  
