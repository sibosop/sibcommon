#!/usr/bin/env python
import os
import sys
home = os.environ['HOME']
proj = home+"GitProjects/iAltar"
sys.path.append(proj+"/iAltar")
sys.path.append(proj+"/config")
sys.path.append(proj+"/common")
sys.path.append(proj+"/server")
import glob
import random
import subprocess
import os
import sys
import time
import config
import DisplayHandler
import uuid

debug=True

global init
init=False
archives=[]

def clearArchive():
  cdir=DisplayHandler.getArchiveCache()
  files = glob.glob(cdir+"/*")
  for f in files:
    os.remove(f)
  return cdir

randList = []
randListIndex = 0
def getArchive():
  global init
  global randList
  global randListIndex
  adir=config.specs["archiveDir"]
  cdir=clearArchive()
  if init == False:
    if debug: print("init seed")
    random.seed()
    init=True
    for a in glob.glob(adir+"/*.tgz"):
      if False: print("a: %s"%a)
      archives.append(a)
      #n = random.randint(0,len(archives)-1)
    randList = random.sample(range(len(archives)),len(archives))
    randListIndex = 0
      
  try:  
    n = randList[randListIndex]
    randListIndex += 1
    if randListIndex == len(archives) :
      randListIndex = 0
      randList = random.sample(range(len(archives)),len(archives))
    if debug: print("n:"+str(n)+" archive:"+archives[n])
    cmd=["tar","xzf",archives[n],"-C",cdir]
    if debug: print( "cmd: %s"%cmd)
    subprocess.check_output(cmd)
  except subprocess.CalledProcessError, e:
    print("archive problem: "+', '.join(cmd)+str(e.output))
  images=[]
  choices=[]
  try:
    for a in glob.glob(cdir+"/*.jpg"):
      if debug: print("archive image %s"%a)
      images.append(a);
  except:
    e = sys.exc_info()[0]
    print("return from archive image append "+str(e))
  
  textName=cdir+"/"+config.specs['archiveTextName']
  if debug: print("textName %s"%textName)
  try:  
    with open(textName) as fp:
      for line in fp:
        if debug: print(line.rstrip())
        choices.append(line.rstrip())
  except:
    e = sys.exc_info()[0]
    print("choice name append "+str(e))

  return [images,choices]
  
def putArchive(choices):
  if config.specs['doArchive']:
    try:
      if debug: print "doing archive"
      tmpFile="%s/%s/%s"%(home,config.specs['tmpdir'],"tarFiles")
      adir=config.specs["archiveDir"]
      cdir=DisplayHandler.getArchiveCache()
      textName=cdir+"/"+config.specs['archiveTextName']
      cf=open(textName,"w")
      cf.write("%s\n"%choices[0])
      cf.write("%s\n"%choices[1])
      cf.close()
      afiles=glob.glob("%s/*.jpg"%cdir)
      tfiles=glob.glob("%s/*.lkp"%cdir)
      tf = open(tmpFile,"w")
      for file in afiles:
        if False: print "writing %s to %s"%(file,tmpFile)
        fb = os.path.basename(file)
        tf.write("%s\n"%fb)
      for file in tfiles:
        if False: print "writing %s to %s"%(file,tmpFile)
        fb = os.path.basename(file)
        tf.write("%s\n"%fb)
      tf.close()
      cmd = ["tar","-czf",adir+"/"+str(uuid.uuid4())+".tgz","-C",cdir,"-T",tmpFile]
      if debug: print "cmd %s"%cmd
      subprocess.check_output(cmd)
    except subprocess.CalledProcessError, e:
      print "Error %s"%(e)

if __name__ == '__main__':
  rval=getArchive()
  images=rval[0]
  choices=rval[1]
  for i in images:
    print i
  for i in choices:
    print i
