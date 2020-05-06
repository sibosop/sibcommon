#!/usr/bin/env python
import os
import sys
import random
import time
from specs import Specs
from debug import Debug
from singleton import Singleton

class Words(object):
  __metaclass__ = Singleton
  def __init__(self):
    self.name = "Words"
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
    Debug().p("%s: tests: %s %s"%(self.name,tests[0],tests[1]))
    Debug().p("%s: %s %s"%(self.name,tests[0],tests[0][-2:]))
    if tests[0][-2:] == "ly":
      Debug().p("%s: swaping %s and %s"%(self.name,tests[0],tests[1]))
      tmp = tests[0]
      tests[0] = tests[1]
      tests[1] = tmp
    return tests

if __name__ == '__main__':
  os.environ['DISPLAY']=":0.0"
  os.chdir(os.path.dirname(sys.argv[0]))
  os.chdir("..") # sigh: get to default app path
  Debug(["__main__"])
  Specs("%s/%s"%("speclib","commontest.json"))
  choices = Words().getWords()
  print (choices)
  choices = Words().getWords()
  print (choices)
  choices = Words().getWords()
  print (choices)
