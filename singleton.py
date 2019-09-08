#!/usr/bin/python

class Singleton(type):
    _instance = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance[cls]
        
       
       
if __name__ == '__main__':       
  class SingletonClass():
    __metaclass__=Singleton
    def __init__(self,v):
      self.v = v
      
  class RegularClass():
      pass
      
  x = SingletonClass(3)
  y = SingletonClass()
  print(x == y)
  print(x.v)
  print(y.v)
  x = RegularClass()
  y = RegularClass()
  print(x == y)
   

 