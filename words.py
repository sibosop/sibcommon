#!/usr/bin/env python
import os
import sys
import random
import time
from specs import Specs
from utils import print_dbg
from singleton import Singleton

class Words(object):
  __metaclass__ = Singleton
  def __init__(self):
    wordList = Specs().s['wordList']
    wordDir=Specs().specDir
    self.lines = []
    for w in wordList:
      f = open(wordDir+"/"+w,"r")
      for l in f.read().split('\n'):
        self.lines.append(l)
        
  def getWords(self):
    tests=[]
    for i in range(0,2):
      n = random.randint(0,len(self.lines)-1)
      tests.append(self.lines[n])
    print_dbg("tests: %s %s"%(tests[0],tests[1]))
    print_dbg("%s %s"%(tests[0],tests[0][-2:]))
    if tests[0][-2:] == "ly":
      print_dbg("swaping %s and %s"%(tests[0],tests[1]))
      tmp = tests[0]
      tests[0] = tests[1]
      tests[1] = tmp
    return tests

if __name__ == '__main__':
  from utils import setDebug
  setDebug(True)
  os.environ['DISPLAY']=":0.0"
  os.chdir(os.path.dirname(sys.argv[0]))
  os.chdir("..") # sigh: get to default app path
  Specs("%s/%s"%("speclib","commontest.json"))
  choices = Words().getWords()
  print choices
  choices = Words().getWords()
  print choices
  choices = Words().getWords()
  print choices
