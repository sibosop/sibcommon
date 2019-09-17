#!/usr/bin/env python
import os
import sys
home = os.environ['HOME']
proj = home+"/GitProjects/iAltar"
sys.path.append(proj+"/iAltar")
sys.path.append(proj+"/config")
sys.path.append(proj+"/common")
sys.path.append(proj+"/server")
import random
import time
import config

debug=False

lines = []
wordList = None
wordDir = None
global init
init=False


def initWords():
  if debug: print "init words"
  config.load()
  random.seed(time.time())
  wordList = config.specs['wordList']
  wordDir= "%s/%s"%(home,config.specs['fontDir'])
  for w in wordList:
    f = open(wordDir+"/"+w,"r")
    for l in f.read().split('\n'):
      lines.append(l)
  init=True


#@profile
def getWords():
  global init
  if init==False:
    initWords()
    init=True
  tests=[]
  for i in range(0,2):
    n = random.randint(0,len(lines)-1)
    tests.append(lines[n])
  if debug: print "tests:",tests[0],tests[1] #,tests[2]
  if debug: print "%s %s"%(tests[0],tests[0][-2:])
  if tests[0][-2:] == "ly":
    if debug: print "swaping %s and %s"%(tests[0],tests[1])
    tmp = tests[0]
    tests[0] = tests[1]
    tests[1] = tmp
  return tests

if __name__ == '__main__':
  choices = getWords()
  print choices
  choices = getWords()
  print choices
  choices = getWords()
  print choices
