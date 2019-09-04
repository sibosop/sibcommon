#!/usr/bin/env python
import os
import sys
home = os.environ['HOME']

debug = False

def setDebug(flag):
  global debug
  debug = flag

def print_dbg(msg):
  if debug: print(msg)