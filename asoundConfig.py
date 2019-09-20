#!/usr/bin/env python
import os
import sys
import traceback
home = os.environ['HOME']
from subprocess import CalledProcessError, check_output
micKey="MIC_CARD"
speakerKey="SPEAKER_CARD"
from debug import Debug
usbMic="USB-Audio - USB PnP Sound Device"

# various managling of the MINI plugs
defaultSpeakers = [
  {'search' : "bcm2835 - bcm2835 ALSA", 'name' : "MINI" }
  ,{'search' : "bcm2835_alsa - bcm2835 ALSA", 'name' : "MINI" }
  ]

speakerLookup = [ 
  {'search' : "USB-Audio - USB2.0 Device", 'name' : "HONK" }
  ,{'search' : "USB-Audio - USB Audio Device", 'name' : "JLAB" }
]


def getCardNum(line,key):
  rval=""
  Debug().p("line %s key %s"%(line,key))
  if line.find(key) != -1:
    Debug().p("found %s:%s"%(key,line))
    rval = line.split()[0].strip()
  return rval

hwInit = False
hw={}
def setSpeakerInfo(hw):
  Debug().p("set speak info:%s %s"%(hw['Speaker'],hw['SpeakerBrand']))
  cmdHdr = ["amixer", "-c",hw['Speaker']]
  try:
    cmd = cmdHdr[:]
    Debug().p(cmd)
    output = check_output(cmd)
    lines = output.split("\n");
    for l in lines:
      n = l.find("Limits: Playback") 
      if n != -1:
        vars = l.split()
        hw['min'] = vars[2]
        hw['max'] = vars[4]
  except CalledProcessError as e:
    traceback.print_exc()
    print(e.output)



def getHw():
  global hwInit
  global hw
  if hwInit is False:
    hw['Mic']="0"
    hw['Speaker']=-1
    cardPath = "/proc/asound/cards"
    with open(cardPath) as f:
      for line in f:
        t = getCardNum(line,usbMic)
        if t != "":
          hw['Mic'] = t
        for s in speakerLookup:
          t = getCardNum(line,s['search'])
          if t != "":
            hw['Speaker'] = t
            hw['SpeakerBrand']= s['name']

    if hw['Speaker'] == -1:
      with open(cardPath) as f:
        for line in f:
          for d in defaultSpeakers:
            t = getCardNum(line,d['search'])
            if t != "":
              hw['Speaker'] = t
              hw['SpeakerBrand'] = d['name']
              break

    #retrieve info about speaker
    setSpeakerInfo(hw)
    hwInit = True
  return hw 
  

def makeRc():
  path = "asoundrc.template"
  rcPath = home+"/.asoundrc"
  try:
    rc = open(rcPath,"w")
    hw = getHw()
    with open(path) as f:
      for line in f:
        if line.find(micKey) != -1:
          line = line.replace(micKey,hw['Mic'])
        elif line.find(speakerKey) != -1:
          line = line.replace(speakerKey,hw['Speaker'])
        Debug().p("writing line: %s"%line);
        rc.write(line)
  except Exception, e:
    traceback.print_exc()
    print("player error: %s"%repr(e))

# amixer -c 2 cset numid=3,name='PCM Playback Volume' 100
def setVolume(vol):
  if int(vol) >= 100 :
    vol = "100"
  hw=getHw()
  print("hw info %s"%hw)
  volRat = int(hw['max'])/100.0
  setVol = float(vol) * volRat
  setVol = int(round(setVol))
  print("max volume: %s rat: %f vol: %s SetVol %d"%(hw['max'],volRat,vol,setVol))
  cmdHdr = ["amixer", "-c",hw['Speaker']]
  try:
    cmd = cmdHdr[:]
    cmd.append("controls")
    output = check_output(cmd)
    lines = output.split("\n");
    for l in lines:
      if l.find("Volume") != -1:
        vars = l.split(",")
        cmd = cmdHdr[:]
        cmd.append("cset")  
        cmd.append(vars[0]+","+vars[2])
        cmd.append(str(setVol)) 
        Debug().p("vol: %s"%cmd)
        output = check_output(cmd)

  except CalledProcessError as e:
    traceback.print_exc()
    print(e.output)

def getVolume():
  vol = 666
  hw=getHw()
  print("max volume: %s"%hw['max'])
  volRat = float(hw['max'])/100.0
  print("max volume: %d vol: %f volRat: %f"%(hw['max'],vol,volRat))
  cmdHdr = ["amixer", "-c",hw['Speaker'],"cget","numid=3"]
  try:
    cmd = cmdHdr[:]
    output = check_output(cmd)
    lines = output.split("\n");
    for l in lines:
      if l.find(": values=") != -1: 
        var = l.split("=")
        var = var[1].split(",")
        vol=int(round(float(var[0])/volRat))

  except CalledProcessError as e:
    traceback.print_exc()
    print(e.output)

  return vol

if __name__ == '__main__':
  try:
    os.chdir(os.path.dirname(sys.argv[0]))
    Debug(['__main__'])
    makeRc()
    #setVolume(sys.argv[1])
    #print getVolume()
  except Exception, e:
     traceback.print_exc()
