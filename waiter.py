#!/usr/bin/env python
from specs import Specs
import time
import random
from utils import print_dbg


class TimeWaiter(object):
  def wait(self,cs=None):
    nt = random.randint(Specs().s['eventMin'],Specs().s['eventMax'])/1000.0;
    print_dbg("wait next play: %f"%nt)
    time.sleep(nt)
    