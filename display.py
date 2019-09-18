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
    pygame.mouse.set_visible(False);
    fontSize = Hosts().getLocalAttr('fontSize')
    fontFile = Specs().s['fontFile']
    print("seting font to %s %d"%(fontFile,fontSize))
    self.myFont = pygame.font.Font("%s/%s"%("speclib",fontFile), fontSize)
    if Hosts().getLocalAttr("hostType") == "raspberry":
      self.screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
    else:
      self.screen = pygame.display.set_mode([800,480]);
    print("display image setup done")

  def image(self,img):
    try:
      image = pygame.image.load(img);
    except:
      print("Display can't render "+img)
      splash = "%s/%s"%(Specs.s['splashImg'])
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
      # render text
      if len(text) < 2:
          print "display image bad text format"
          return
      lineSpacing = Specs().s['textlineSpacing']
      label1 = self.myFont.render(text[0], 1, (255,255,0))
      label2 = self.myFont.render(text[1], 1, (255,255,0))
      maxWidth = max(label1.get_width(),label2.get_width())
      maxHeight = label1.get_height() + label2.get_height() + lineSpacing 
      wordRect = pygame.Surface((maxWidth,maxHeight))
      self.screen.fill((0,0,0));
      if maxWidth == label1.get_width():
          wordRect.blit(label1, (0, 0))
          offset = (maxWidth - label2.get_width()) / 2
          wordRect.blit(label2, (offset, label1.get_height() + lineSpacing))
      else:
          offset = (maxWidth - label1.get_width()) / 2
          wordRect.blit(label1, (offset, 0))
          wordRect.blit(label2, (0, label1.get_height() + lineSpacing))

      wx = (self.screen.get_width() - wordRect.get_width()) / 2
      if wx < 0: 
          wx = 0
      wy = (self.screen.get_height() - wordRect.get_height()) / 2
      if wy < 0:
          wy = 0
      self.screen.blit(wordRect,(wx,wy)) 
      pygame.display.flip() 

if __name__ == '__main__':
    os.environ['DISPLAY']=":0.0"
    os.chdir(os.path.dirname(sys.argv[0]))
    os.chdir("..") # sigh: get to default app path
    Debug(["__main__"])
    Specs("%s/%s"%("speclib","commontest.json"))
    pygame.init()
    Display().image(sys.argv[1])
    time.sleep(5)
    Display().text(["foo","bar"])
    time.sleep(5)
    
	
