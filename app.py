from ctypes import Structure, windll, c_uint, sizeof, byref
from subprocess import call
​
class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]
​
def get_idle_duration():
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = sizeof(lastInputInfo)
    windll.user32.GetLastInputInfo(byref(lastInputInfo))
    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0
​
while True:
    idle = get_idle_duration()
    if idle > 30:
        print "idle for ", idle
        call('c:/nircmd/nircmd.exe win max class MozillaWindowClass')
​
    if idle == 0:
        call('c:/nircmd/nircmd.exe win min class MozillaWindowClass')

