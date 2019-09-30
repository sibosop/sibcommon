#!/usr/bin/env python
import os
import sys
import pygame
import time
from hosts import Hosts
from debug import Debug
from specs import Specs
from singleton import Singleton



class Display(object):
  __metaclass__ = Singleton
  def __init__(self):
    self.screen=None
    self.myFont=None
    self.FilterDot = True
    self.name="Display"
    pygame.mouse.set_visible(False);
    self.lineLen = Specs().s['lineLen']
    isRaspberry = True
    if Specs().s['noHosts']:
      fontSize = Specs().s["fontSize"]
      isRasberry = Specs().s['hostType'] == "raspberry"
    else:
      fontSize = Hosts().getLocalAttr('fontSize')
      isRaspberry = Hosts().getLocalAttr("hostType") == "raspberry"
    if isRaspberry:
      self.screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
    else:
      self.screen = pygame.display.set_mode([800,480]);
    fontFile = Specs().s['fontFile']
    Debug().p("%s: setting font to %s size %d"%(self.name,fontFile,fontSize))
    self.myFont = pygame.font.Font("%s/%s"%("speclib",fontFile), fontSize)
    print("display image setup done")

  def image(self,img):
    try:
      image = pygame.image.load(img);
    except:
      print("Display can't render "+img)
      splash = "%s"%(Specs().s['splashImg'])
      image = pygame.image.load(splash)
      return False
    ws=self.screen.get_width()
    hs=self.screen.get_height()
    rs = float(ws)/float(hs)
    wi = image.get_width()
    hi = image.get_height()
    ri = float(wi)/float(hi)
    dw = 0
    dh = 0
    if  wi < (ws/2) and hi < (hs/2):
      print("doing half scale:"+img)
      simage = pygame.transform.scale2x(image)
    else:
      if rs > ri:
        dw = wi * (float(hs)/float(hi))
        dh = hs
      else:
        dw = ws
        dh = hi * (float(ws)/float(wi))

      try:
        print("doing smooth scale:"+img)
        simage = pygame.transform.smoothscale(image,(int(dw),int(dh)))
      except:
        print("smoothscale failed doing normal scale for:"+img)
        simage = pygame.transform.scale(image,(int(dw),int(dh)))

    xoffset = (ws - simage.get_width()) / 2
    yoffset = (hs - simage.get_height()) / 2
    Debug().p("displayImage ws:"+str(ws) 
            + " hs:"+str(hs) 
            + " rs:"+str(rs)
            +"  wi:"+str(wi) 
            + " hi:"+str(hi) 
            + " ri:"+str(ri) 
            + " dw:"+str(dw) 
            + " dh:"+str(dh) 
            + " xoffset:"+str(xoffset) 
            + " yoffset:"+str(yoffset) 
            )
    self.screen.fill((0,0,0))
    self.screen.blit(simage,(xoffset,yoffset)) 
    pygame.display.flip() 
    return True

  def text(self,text):
    lines = []
    Debug().p("%s: text type %s"%(self.name,type(text)))
    if type(text) == str or type(text) == unicode:
      Debug().p("%s: converting %s to array"%(self.name,text))
      if self.FilterDot:
        text=text.replace("."," ")
      text=text.strip()
      words=text.split()
      r = ""
      for w in words:
        if (len(w) + len(r)) < self.lineLen:
          r += w + " "
        else:
          lines.append(r)
          r = w + " "
      lines.append(r)
      lines = lines[0:4]
    else:
      for l in text:
        lines.append(l)
    i = 0
    self.screen.fill((0,0,0))
    labels = []
    maxWidth = 0
    maxHeight = 0
    for l in lines:
      label = self.myFont.render(l, 1, (255,255,0))
      w = label.get_width()
      h = label.get_height()
      maxWidth = max(w,maxWidth)
      maxHeight = max(h,maxHeight)
      labels.append(label)
      
    numLabels = len(labels)
    wordRect = pygame.Surface((maxWidth,(maxHeight*numLabels)-4))

    i = 0
    for l in labels:
      h = l.get_height()
      w = l.get_width()
      offset = (wordRect.get_width() - w)/2
      wordRect.blit(l,(offset,i*h))
      i += 1
    sx = (self.screen.get_width() - wordRect.get_width()) / 2
    sy = (self.screen.get_height() - wordRect.get_height()) / 2
    self.screen.blit(wordRect,(sx,sy))
    pygame.display.flip() 

if __name__ == '__main__':
    os.environ['DISPLAY']=":0.0"
    os.chdir(os.path.dirname(sys.argv[0]))
    os.chdir("..") # sigh: get to default app path
    Debug(["__main__"])
    Specs("%s/%s"%("speclib","poem.json"))
    pygame.init()
    Display().image(sys.argv[1])
    time.sleep(5)
    Display().text(["foo","bar"])
    time.sleep(5)
    Display().text("what a friend we have in bezos. The Bastard")
    time.sleep(5)
    
	
