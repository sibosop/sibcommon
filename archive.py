#!/usr/bin/env python
import os
import sys
import traceback
import glob
import random
import subprocess
import os
import sys
import time
import uuid
from debug import Debug
from singleton import Singleton
from utils import mkpath
from specs import Specs

class Archive(object):
  __metaclass__ = Singleton
  def __init__(self):
    self.reset()

  def reset(self):
    self.cache = mkpath("%s/archiveCache"%(Specs().s['tmpdir']))
    self.adir=Specs().s["archiveDir"]
    Debug().p("archive dir %s"%self.adir)
    self.archives = []
    for a in glob.glob(self.adir+"/*.tgz"):
      #Debug().p("a: %s"%a)
      self.archives.append(a)
    self.randList = random.sample(range(len(self.archives)),len(self.archives))
    self.randListIndex = 0
    
  def getArchiveCache(self):
    return self.cache

  def clearArchive(self):
    files = glob.glob(self.cache+"/*")
    for f in files:
      os.remove(f)
    return self.cache
    
  def getArchive(self):
    cdir=self.clearArchive()
    try:  
      n = self.randList[self.randListIndex]
      self.randListIndex += 1
      if self.randListIndex == len(self.archives) :
        self.randListIndex = 0
        self.randList = random.sample(range(len(self.archives)),len(self.archives))
      Debug().p("n: %d archive %s"%(n,self.archives[n]))
      cmd=["tar","xzf",self.archives[n],"-C",cdir]
      Debug().p("cmd: %s"%cmd)
      subprocess.check_output(cmd)
    except subprocess.CalledProcessError, e:
      print("archive problem: "+', '.join(cmd)+str(e.output))
    images=[]
    choices=[]
    try:
      for a in glob.glob(cdir+"/*.jpg"):
        Debug().p("archive image %s"%a)
        images.append(a);
    except:
      e = sys.exc_info()[0]
      print("return from archive image append "+str(e))
  
    textName=cdir+"/"+Specs().s['archiveTextName']
    Debug().p("textName %s"%textName)
    try:  
      with open(textName) as fp:
        for line in fp:
          Debug().p(line.rstrip())
          choices.append(line.rstrip())
    except:
      traceback.print_exc()
      e = sys.exc_info()[0]
      print("choice name append "+str(e))

    return [images,choices]
  
  def putArchive(self,choices):
    if Specs().s['doArchive']:
      try:
        Debug().p ("doing archive")
        tmpFile="%s/%s"%(Specs().s['tmpdir'],"tarFiles")
        cdir=self.cache
        textName=cdir+"/"+Specs().s['archiveTextName']
        cf=open(textName,"w")
        cf.write("%s\n"%choices[0])
        cf.write("%s\n"%choices[1])
        cf.close()
        afiles=glob.glob("%s/*.jpg"%cdir)
        tfiles=glob.glob("%s/*.lkp"%cdir)
        tf = open(tmpFile,"w")
        for file in afiles:
          Debug().p ("writing %s to %s"%(file,tmpFile))
          fb = os.path.basename(file)
          tf.write("%s\n"%fb)
        for file in tfiles:
          Debug().p("writing %s to %s"%(file,tmpFile))
          fb = os.path.basename(file)
          tf.write("%s\n"%fb)
        tf.close()
        cmd = ["tar","-czf",self.adir+"/"+str(uuid.uuid4())+".tgz","-C",cdir,"-T",tmpFile]
        Debug().p("cmd %s"%cmd)
        subprocess.check_output(cmd)
      except subprocess.CalledProcessError, e:
        print "Error %s"%(e)

if __name__ == '__main__':
  Debug(["__main__","archive","specs","hosts"])
  os.environ['DISPLAY']=":0.0"
  os.chdir(os.path.dirname(sys.argv[0]))
  os.chdir("..") # sigh: get to default app path
  Specs("%s/%s"%("speclib","commontest.json"))
  rval = Archive().getArchive()
  images=rval[0]
  choices=rval[1]
  for i in images:
    print i
  for i in choices:
    print i
