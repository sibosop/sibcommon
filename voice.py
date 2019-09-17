#!/usr/bin/env python
import os
import sys
home = os.environ['HOME']
proj = home+"GitProjects/iAltar"
sys.path.append(proj+"/iAltar")
sys.path.append(proj+"/config")
sys.path.append(proj+"/common")
sys.path.append(proj+"/server")
import random
import os
import threading
import soundTrack as st
import textSpeaker
import time
import config
import pygame
import base64

debug = True
debugFound = True
debugVoiceTrack = True

screen=None
myfont=None
count=0
voiceExt = ".wav"
voiceMutex=threading.Lock()
voiceSound = None
voiceChanged=False
voiceMinVol=.7

def sendPhrase(args):
  global voiceSound
  global voiceChanged
  p = args['phrase']
  speakText = p[0]+" "+p[1]
  file=None
  if 'phraseData' in args:
    print("decoding voice file data from args")
    file = "%s/%s/%s_%s.mp3"%(home,config.specs['tmpdir'],p[0],p[1])
    print("decoding to file %s"%file)
    with open(file, 'wb') as f:
      f.write(base64.b64decode(args['phraseData']))
  else:
    while file is None:
      lang = random.choice(config.specs['langList'])
      file=textSpeaker.makeSpeakFile(speakText,lang)
  print "voice sound set to: %s"%file
  voiceMutex.acquire()
  voiceSound = pygame.mixer.Sound(file)
  voiceChanged = True
  if st.backgroundCount != 0:
    st.backgroundCount -= 1
  voiceMutex.release()
  print("checkText unlinking:"+file+" voiceSound:"+str(voiceSound))
  os.unlink(file)

class VoiceThread(threading.Thread):
  def run(self):
    global voiceSound
    global voiceChanged
    voiceMaxVol = config.specs['voiceMaxVol'] 
    while True:
      voiceMutex.acquire()
      vt = voiceSound
      voiceMutex.release()
      if vt is None:
        print("check voice no voice")
        time.sleep(1)
      else:
        print("check voice found voice")
        reps = 0
        if random.randint(0,1) == 0:
          reps = random.randint(2,4)
        else:
          reps = 1
        if debugVoiceTrack:print("VoiceReadyEvent reps:"+str(reps))
        for i in range(reps):
          l = (random.random()*(voiceMaxVol-voiceMinVol))+voiceMinVol
          r = (random.random()*(voiceMaxVol-voiceMinVol))+voiceMinVol
          voiceMutex.acquire()
          st.playSound(vt,l,r)
          voiceMutex.release()
          if reps > 1:
            s = random.random()
            time.sleep(s)
        voiceTimeout = random.randint(5,10)
        if debugVoiceTrack: print("Next Voice:"+str(voiceTimeout));
        for i in range(voiceTimeout):
          voiceMutex.acquire()
          c = voiceChanged
          voiceChanged = False
          voiceMutex.release()
          if c:
            print("voiceSound changed")
            break;
          time.sleep(1)


