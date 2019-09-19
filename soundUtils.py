#!/usr/bin/env python
import pygame
import os
from debug import Debug
import numpy as np

def playSound(sound,l,r):
  eventChan = None
  eventChan=pygame.mixer.find_channel()
  if eventChan is None:
    pygame.mixer.set_num_channels(pygame.mixer.get_num_channels()+1);
    eventChan=pygame.mixer.find_channel()
  Debug().p("busy channels: %d"%getBusyChannels())
  Debug().p("l: %s r %s"%(str(l),str(r)))
  eventChan.set_volume(l,r)
  eventChan.play(sound)
  eventChan.set_endevent()

def getBusyChannels():
  count = 0
  for i in range(pygame.mixer.get_num_channels()):
    if pygame.mixer.Channel(i).get_busy():
      count +=1
  return count

def playFile(path):
  Debug().p("playing %s"%path)
  sound = pygame.mixer.Sound(file=path)
  playSound(sound,.5,.5)

def doJpent():
  speedChangeMax = specs.specs['speedChangeMax']
  speedChangeMin = specs.specs['speedChangeMin']
  rval = ((speedChangeMax-speedChangeMin) 
                        * random.random()) + speedChangeMin
  Debug().p("doJpent")
  return rval

def speedx(sound, factor):
  rval = None
  Debug().p("speedx factor: %s"%factor)
  sound_array = pygame.sndarray.array(sound)
  """ Multiplies the sound's speed by some `factor` """
  indices = np.round( np.arange(0, len(sound_array), factor) )
  indices = indices[indices < len(sound_array)].astype(int)
  rval = pygame.sndarray.make_sound(sound_array[ indices.astype(int) ])
  return rval