# This only works on Windows

import ctypes
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
  SHOW_WIN = 5 #3
  HIDE_WIN = 0 #6
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
  URL = 'https://mcdonalds.com.au/'

# Shortcuts to win32 apis
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetClassName = ctypes.windll.user32.GetClassNameW
ShowWindow = ctypes.windll.user32.ShowWindow
SetConsoleCtrlHandler = ctypes.windll.kernel32.SetConsoleCtrlHandler

class Player:
  def __init__(self):
    self.hwnd = None
    self.player = None
  
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
    if self.hwnd is None:
      self.get_player_window()
    
    return self.hwnd is not None

  def run(self):
    if self.player is None or self.player.poll() is not None:
      self.hwnd = None
      os.system('taskkill /f /im ' + PROCESS_NAME)
      self.player = subprocess.Popen([BROWSER_PATH, '--kiosk', '--disable-session-crashed-bubble', '--disable-infobars', URL])            

  def hide(self):
    print "hide"
    if self.hwnd is None:
      self.get_player_window()
    
    ShowWindow(self.hwnd, HIDE_WIN)

  def show(self):
    print "show"
    if self.hwnd is None:
      self.get_player_window()

    ShowWindow(self.hwnd, SHOW_WIN)

  def kill(self):
    self.hwnd = None
    if self.player is not None:
      self.player.terminate()
      self.player = None
    
    os.system('taskkill /f /im ' + PROCESS_NAME)

  def exit_handler(self):
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
    if player.ready() == False:
      player.run()
    else:      
      if next(is_idle):
        player.show()
      else:
        player.hide()
    

