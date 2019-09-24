#!/usr/bin/env python
import serial
import os
import sys
from debug import Debug
from singleton import Singleton
from specs import Specs

class Panel(object):
  __metaclass__ = Singleton
  def __init__(self):
    self.name = "Panel"
    self.ser = None
    brightness = Specs().s['panelBrightness']
    contrast = Specs().s['panelContrast']
    if self.hasPanel():
      self.ser = serial.Serial('/dev/ttyUSB0', 9600)
      self.ser.write(bytearray([0xfe,0x53,brightness]))
      self.ser.write(bytearray([0xfe,0x52,contrast]))

  def hasPanel(self):
    path = Specs().s['panelDev']
    if os.path.exists(path):
      print("%s Located usb serial device at %s"%(self.name,path))
      return True
    print("%s No usb serial device at %s"%(self.name,path))
    return False;

  def clear(self):
    self.ser.write(bytearray([0xfe,0x51]))

  def setRow(self,r):
    val = 0
    if ( r == 1 ):
      val = 0x40
    self.ser.write(bytearray([0xfe,0x45,val]))

  def printText(self,t):
    self.clear()
    Debug().p("%s panel 0 %s len %s"%(self.name,t[0],len(t[0])))
    self.ser.write('{0: ^16}'.format(t[0]).upper())
    Debug().p("%s panel 1 %s len %s"%(self.name,t[1],len(t[1])))
    self.setRow(1)
    self.ser.write('{0: ^16}'.format(t[1]).upper())

if __name__ == '__main__':
    os.environ['DISPLAY']=":0.0"
    os.chdir(os.path.dirname(sys.argv[0]))
    os.chdir("..") # sigh: get to default app path
    Debug(["__main__"])
    Specs("%s/%s"%("speclib","piano.json"))
    Panel().printText(["panel","test"])
