# This only works on Windows

import time
import ctypes
from ctypes import Structure, windll, c_uint, sizeof, byref

class LASTINPUTINFO(Structure):
  _fields_ = [
    ('cbSize', c_uint),
    ('dwTime', c_uint),
  ]

def get_idle_duration():
  lastInputInfo = LASTINPUTINFO()
  lastInputInfo.cbSize = sizeof(lastInputInfo)
  windll.user32.GetLastInputInfo(byref(lastInputInfo))
  millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
  return millis / 1000.0

def idle_check(idle_trigger):
  idle = True
  while True:
    idle_duration = get_idle_duration()    
    if idle_duration > idle_trigger:
      idle = True
    else:
      idle = False
      
    yield idle
    time.sleep(0.2);


