#!/usr/bin/env python
import os
import sys
home = os.environ['HOME']
proj = home+"GitProjects/iAltar"
sys.path.append(proj+"/iAltar")
sys.path.append(proj+"/config")
sys.path.append(proj+"/common")
sys.path.append(proj+"/server")
import pygame
import time
import host
import config


debug = True

screen=None
setupDone=False
myFont=None

def setup():
  global screen
  global setupDone
  global myFont
  if setupDone:
      return
  pygame.init()
  pygame.mouse.set_visible(False);
  fontSize = host.getLocalAttr('fontSize')
  fontFile = config.specs['fontFile']
  print("seting font to %s %d"%(fontFile,fontSize))
  myFont = pygame.font.Font("%s/%s/%s"%(home,config.specs['fontDir'],fontFile), fontSize)
  if host.getLocalAttr("isRaspberry"):
    screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
  else:
    screen = pygame.display.set_mode([800,480]);
  setupDone=True
  print("display image setup done")

def displayImage(img):
  global screen
  global setupDone
  setup()
  try:
    image = pygame.image.load(img);
  except:
    print("display Image can't render "+img)
    splash = "%s/%s"%(home,config.specs['splashImg'])
    image = pygame.image.load(splash)
    return False
  ws=screen.get_width()
  hs=screen.get_height()
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
  if debug: print("displayImage ws:"+str(ws) 
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
  screen.fill((0,0,0))
  screen.blit(simage,(xoffset,yoffset)) 
  pygame.display.flip() 
  return True



def printText(text):
    global screen
    global myFont
    # render text
    if len(text) < 2:
        print "display image bad text format"
        return
    lineSpacing = config.specs['textlineSpacing']
    label1 = myFont.render(text[0], 1, (255,255,0))
    label2 = myFont.render(text[1], 1, (255,255,0))
    maxWidth = max(label1.get_width(),label2.get_width())
    maxHeight = label1.get_height() + label2.get_height() + lineSpacing 
    wordRect = pygame.Surface((maxWidth,maxHeight))
    screen.fill((0,0,0));
    if maxWidth == label1.get_width():
        wordRect.blit(label1, (0, 0))
        offset = (maxWidth - label2.get_width()) / 2
        wordRect.blit(label2, (offset, label1.get_height() + lineSpacing))
    else:
        offset = (maxWidth - label1.get_width()) / 2
        wordRect.blit(label1, (offset, 0))
        wordRect.blit(label2, (0, label1.get_height() + lineSpacing))

    wx = (screen.get_width() - wordRect.get_width()) / 2
    if wx < 0: 
        wx = 0
    wy = (screen.get_height() - wordRect.get_height()) / 2
    if wy < 0:
        wy = 0
    screen.blit(wordRect,(wx,wy)) 
    pygame.display.flip() 

if __name__ == '__main__':
    displayImage(sys.argv[1])
    time.sleep(5)
    
	
