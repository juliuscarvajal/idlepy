# This only works on Windows
# TODO: Detect player crash (chrome) and react to it.

import ctypes
from ctypes import Structure, c_ulong, byref

import sys
import os
import subprocess
from idle import idle_check

import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read('config.ini')

# constants
# https://msdn.microsoft.com/en-us/library/windows/desktop/ms633548(v=vs.85).aspx
try:
  IDLE_TRIGGER = int(Config.get('DEFAULT', 'IDLE_TRIGGER'))
  PLAYER_CLASS_NAME = Config.get('DEFAULT', 'PLAYER_CLASS_NAME')
  SHOW_WIN = 3
  HIDE_WIN = 6
  PROCESS_NAME = Config.get('DEFAULT', 'PROCESS_NAME')
  BROWSER_PATH = Config.get('DEFAULT', 'BROWSER_PATH')
  URL = Config.get('DEFAULT', 'URL')
except:
  IDLE_TRIGGER = 5
  PLAYER_CLASS_NAME = 'Chrome_WidgetWin_1'
  SHOW_WIN = 3
  HIDE_WIN = 6
  PROCESS_NAME = 'chrome.exe'
  BROWSER_PATH = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
  URL = ''

# Shortcuts to win32 apis
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetClassName = ctypes.windll.user32.GetClassNameW
ShowWindow = ctypes.windll.user32.ShowWindow
SetConsoleCtrlHandler = ctypes.windll.kernel32.SetConsoleCtrlHandler
IsHungAppWindow = ctypes.windll.user32.IsHungAppWindow
GetCursorPos = ctypes.windll.user32.GetCursorPos
SetCursorPos = ctypes.windll.user32.SetCursorPos
mouse_event = ctypes.windll.user32.mouse_event

class Player:
  def __init__(self):
    self.hwnd = None
    self.player = None
    self.visible = False
    os.system('taskkill /f /im ' + PROCESS_NAME)
  
  def get_global_mouse_position(self):
    class POINT(Structure):
      _fields_ = [("x", c_ulong), ("y", c_ulong)]

    pt = POINT()
    GetCursorPos(byref(pt))
    return { "x": pt.x, "y": pt.y }

  def get_player_window(self):
    self.hwnd = None
    def foreach_window(hwnd, lParam):
      if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetClassName(hwnd, buff, length + 1)
 
        if buff.value == PLAYER_CLASS_NAME:
            print buff.value
            self.hwnd = hwnd

      return True
    EnumWindows(EnumWindowsProc(foreach_window), 0)    

  def ready(self):
    if self.player is None or self.player.poll() is not None:
      self.run()
    
    if self.hwnd is None:
      self.get_player_window()
    
    return self.hwnd is not None

  def run(self):
    print "running player"
    self.kill()    
    self.player = subprocess.Popen([BROWSER_PATH, '--disable-session-crashed-bubble', '--disable-infobars', '--kiosk', URL])            

  def hide(self):
    ShowWindow(self.hwnd, HIDE_WIN)
    if self.visible is True:
      self.clickthru()
    
    self.visible = False

  def clickthru(self):
    #print self.get_global_mouse_position()
    SetCursorPos(1, 1)
    mouse_event(2, 0, 0, 0, 0) # left down
    mouse_event(4, 0, 0, 0, 0) # left up
    

  def show(self):
    # if the player hangs, restart again. cannot test to see if it works
    if IsHungAppWindow(self.hwnd):
      print "hang"
      self.kill()
      return

    ShowWindow(self.hwnd, SHOW_WIN)
    self.visible = True

  def kill(self):
    self.hwnd = None
    if self.player is not None:
      self.player.kill()
      self.player = None
    
  def exit_handler(self):
    print "killed self"
    self.kill()

if __name__ == '__main__':
  player = Player()

  def set_exit_handler(func):
    SetConsoleCtrlHandler(func, 1)

  def exit_handler(dwCtrlType):
    retcode = 0
    if dwCtrlType == 0: # CTRL+C
      player.exit_handler()
      retcode = 1
    return retcode

  exit_handler = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_uint)(exit_handler)
  set_exit_handler(exit_handler)
  
  is_idle = idle_check(IDLE_TRIGGER)
  
  
  while True:
    if player.ready():
      if next(is_idle):
        player.show()
      else:
        player.hide()
    
